use wasmtime::*;
use wasmtime_wasi::*;
use wasmtime_wasi::preview1::*;
use std::sync::Arc;
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, Instant};
use anyhow::{Result, Context, anyhow};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::Semaphore;
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WasmPluginConfig {
    pub max_memory_mb: u32,
    pub max_cpu_time_ms: u64,
    pub max_fuel: u64,
    pub allowed_hosts: Vec<String>,
    pub allowed_env_vars: Vec<String>,
    pub allowed_syscalls: Vec<String>,
    pub network_access: bool,
    pub filesystem_access: bool,
    pub enable_threads: bool,
    pub enable_simd: bool,
    pub enable_bulk_memory: bool,
    pub enable_reference_types: bool,
    pub enable_multi_memory: bool,
    pub enable_multi_value: bool,
    pub enable_atomics: bool,
    pub enable_exception_handling: bool,
    pub enable_memory64: bool,
    pub enable_extended_const: bool,
    pub enable_relaxed_simd: bool,
    pub enable_tail_call: bool,
    pub enable_extended_const: bool,
}

impl Default for WasmPluginConfig {
    fn default() -> Self {
        Self {
            max_memory_mb: 128,
            max_cpu_time_ms: 5000,
            max_fuel: 10_000_000,
            allowed_hosts: vec![],
            allowed_env_vars: vec![],
            allowed_syscalls: vec![],
            network_access: false,
            filesystem_access: false,
            enable_threads: false,
            enable_simd: false,
            enable_bulk_memory: true,
            enable_reference_types: true,
            enable_multi_memory: false,
            enable_multi_value: true,
            enable_atomics: false,
            enable_exception_handling: false,
            enable_memory64: false,
            enable_extended_const: false,
            enable_relaxed_simd: false,
            enable_tail_call: true,
            enable_extended_const: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    pub name: String,
    pub version: String,
    pub entrypoint: String,
    pub exports: Vec<String>,
    pub imports: Vec<String>,
    pub memory: Option<MemoryConfig>,
    pub resources: ResourceLimits,
    pub permissions: Permissions,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryConfig {
    pub initial_pages: u32,
    pub maximum_pages: Option<u32>,
    pub shared: bool,
}

impl Default for MemoryConfig {
    fn default() -> Self {
        Self {
            initial_pages: 256, // 16MB
            maximum_pages: Some(8192), // 128MB
            shared: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceLimits {
    pub max_memory_mb: u32,
    pub max_cpu_time_ms: u64,
    pub max_fuel: u64,
    pub max_table_size: u32,
    pub max_instances: u32,
}

impl Default for ResourceLimits {
    fn default() -> Self {
        Self {
            max_memory_mb: 128,
            max_cpu_time_ms: 5000,
            max_fuel: 10_000_000,
            max_table_size: 10000,
            max_instances: 10,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Permissions {
    pub network: Vec<String>,
    pub filesystem: Vec<String>,
    pub environment: Vec<String>,
    pub syscalls: Vec<String>,
}

impl Default for Permissions {
    fn default() -> Self {
        Self {
            network: vec![],
            filesystem: vec![],
            environment: vec![],
            syscalls: vec![],
        }
    }
}

#[derive(Debug, Clone)]
pub struct WasmPluginInstance {
    pub id: Uuid,
    pub manifest: PluginManifest,
    pub engine: Engine,
    pub store: Store<WasiCtx>,
    pub instance: Instance,
    pub memory: Memory,
    pub created_at: Instant,
    pub last_used: Instant,
    pub execution_count: u64,
    pub total_cpu_time: Duration,
    pub total_fuel_consumed: u64,
}

impl WasmPluginInstance {
    pub fn new(manifest: PluginManifest, config: &WasmPluginConfig) -> Result<Self> {
        let mut config_builder = Config::new();
        
        config_builder.wasm_multi_memory(manifest.resources.max_memory_mb > 128);
        config_builder.wasm_simd(true);
        config_builder.wasm_bulk_memory(true);
        config_builder.wasm_reference_types(true);
        config_builder.wasm_multi_value(true);
        config_builder.wasm_threads(true);
        config_builder.wasm_multi_memory(false);
        config_builder.wasm_memory64(false);
        config_builder.wasm_exceptions(false);
        config_builder.wasm_relaxed_simd(true);
        config_builder.wasm_tail_call(true);
        config_builder.wasm_extended_const(true);
        config_builder.wasm_relaxed_simd(true);
        config_builder.wasm_memory64(false);
        
        config_builder.consume_fuel(true);
        config_builder.epoch_interruption(true);
        
        let engine = Engine::new(&config_builder)
            .context("Failed to create Wasm engine")?;
        
        let mut linker = Linker::new(&engine);
        
        let wasi_ctx = WasiCtxBuilder::new()
            .inherit_stdio()
            .inherit_args()?
            .envs(std::env::vars().collect())?
            .build();
        
        let mut store = Store::new(&engine, wasi_ctx);
        
        store.limiter(|store| store.data().limiter());
        
        let instance = Self {
            id: Uuid::new_v4(),
            manifest: manifest.clone(),
            engine,
            store,
            instance: Instance::new(&mut store, &module, &imports)?,
            memory: store.get_memory(0)?,
            created_at: Instant::now(),
            last_used: Instant::now(),
            execution_count: 0,
            total_cpu_time: Duration::ZERO,
            total_fuel_consumed: 0,
        };
        
        Ok(instance)
    }
    
    pub async fn execute(
        &mut self,
        function: &str,
        args: &[Val],
        timeout: Duration,
        fuel_limit: u64,
    ) -> Result<Vec<Val>> {
        self.store.add_fuel(fuel_limit)
            .context("Failed to add fuel")?;
        
        let start = Instant::now();
        
        let func = self.instance.get_typed_func::<(), ()>(&mut self.store, function)
            .context("Function not found")?;
        
        let result = tokio::time::timeout(timeout, async {
            func.call_async(&mut self.store, ()).await
        }).await;
        
        let elapsed = start.elapsed();
        let fuel_consumed = self.store.consume_fuel()
            .unwrap_or(0);
        
        self.last_used = Instant::now();
        self.execution_count += 1;
        self.total_cpu_time += elapsed;
        self.total_fuel_consumed += fuel_consumed;
        
        match result {
            Ok(Ok(result)) => Ok(result),
            Ok(Err(e)) => Err(anyhow!("Execution error: {}", e)),
            Err(_) => Err(anyhow!("Execution timeout")),
        }
    }
    
    pub fn get_memory_usage(&self) -> u64 {
        self.memory.data_size(&self.store) as u64
    }
    
    pub fn get_stats(&self) -> PluginStats {
        PluginStats {
            id: self.id,
            execution_count: self.execution_count,
            total_cpu_time: self.total_cpu_time,
            total_fuel_consumed: self.total_fuel_consumed,
            memory_usage: self.get_memory_usage(),
            created_at: self.created_at,
            last_used: self.last_used,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginStats {
    pub id: Uuid,
    pub execution_count: u64,
    pub total_cpu_time: Duration,
    pub total_fuel_consumed: u64,
    pub memory_usage: u64,
    pub created_at: Instant,
    pub last_used: Instant,
}

#[derive(Debug, Clone)]
pub struct WasmSandbox {
    config: WasmPluginConfig,
    instances: Arc<Mutex<HashMap<Uuid, WasmPluginInstance>>>,
    semaphore: Arc<Semaphore>,
    module_cache: Arc<Mutex<HashMap<String, Module>>>,
}

impl WasmSandbox {
    pub fn new(config: WasmPluginConfig) -> Self {
        let max_instances = config.max_instances.unwrap_or(10);
        Self {
            config,
            instances: Arc::new(Mutex::new(HashMap::new())),
            semaphore: Arc::new(Semaphore::new(10)),
            module_cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    pub async fn load_plugin(
        &self,
        wasm_bytes: &[u8],
        manifest: PluginManifest,
    ) -> Result<Uuid> {
        let _permit = self.semaphore.acquire().await
            .context("Failed to acquire semaphore")?;
        
        let engine = self.get_or_create_engine()?;
        let module = Module::new(&engine, wasm_bytes)
            .context("Failed to compile WASM module")?;
        
        let instance = WasmPluginInstance::new(manifest, &self.config)?;
        
        let id = instance.id;
        self.instances.lock().unwrap().insert(id, instance);
        
        Ok(id)
    }
    
    pub async fn execute(
        &self,
        plugin_id: Uuid,
        function: &str,
        args: Vec<Val>,
        timeout: Duration,
    ) -> Result<Vec<Val>> {
        let mut instances = self.instances.lock().unwrap();
        let instance = instances.get_mut(&plugin_id)
            .ok_or_else(|| anyhow!("Plugin not found: {}", plugin_id))?;
        
        instance.execute("execute", &[], Duration::from_secs(30), 10_000_000).await
    }
    
    pub async fn call_function(
        &self,
        plugin_id: Uuid,
        function: &str,
        args: Vec<Val>,
    ) -> Result<Vec<Val>> {
        let mut instances = self.instances.lock().unwrap();
        let instance = instances.get_mut(&plugin_id)
            .ok_or_else(|| anyhow!("Plugin not found: {}", plugin_id))?;
        
        instance.execute(function, &args, Duration::from_secs(30), 10_000_000).await
    }
    
    pub async fn unload_plugin(&self, plugin_id: Uuid) -> Result<()> {
        let mut instances = self.instances.lock().unwrap();
        if let Some(instance) = instances.remove(&plugin_id) {
            // Cleanup resources
            drop(instance);
        }
        Ok(())
    }
    
    pub fn get_plugin_stats(&self, plugin_id: Uuid) -> Option<PluginStats> {
        let instances = self.instances.lock().unwrap();
        instances.get(&plugin_id).map(|i| i.get_stats())
    }
    
    pub fn list_plugins(&self) -> Vec<PluginStats> {
        let instances = self.instances.lock().unwrap();
        instances.values().map(|i| i.get_stats()).collect()
    }
    
    fn get_or_create_engine(&self) -> Result<Engine> {
        let mut config = Config::new();
        
        config.wasm_simd(true);
        config.wasm_bulk_memory(true);
        config.wasm_reference_types(true);
        config.wasm_multi_value(true);
        config.wasm_threads(true);
        config.wasm_bulk_memory(true);
        config.wasm_reference_types(true);
        config.wasm_multi_value(true);
        config.wasm_threads(true);
        config.wasm_multi_memory(false);
        config.wasm_memory64(false);
        config.wasm_exceptions(false);
        config.wasm_relaxed_simd(true);
        config.wasm_tail_call(true);
        config.wasm_extended_const(true);
        config.wasm_relaxed_simd(true);
        config.wasm_memory64(false);
        
        config.consume_fuel(true);
        config.epoch_interruption(true);
        
        Engine::new(&config).context("Failed to create engine")
    }
    
    pub async fn compile_wasm(&self, wasm_bytes: &[u8]) -> Result<Vec<u8>> {
        let engine = self.get_or_create_engine()?;
        let module = Module::new(&engine, wasm_bytes)
            .context("Failed to compile WASM module")?;
        
        Ok(module.serialize()?)
    }
    
    pub async fn get_module(&self, key: &str) -> Option<Module> {
        self.module_cache.lock().unwrap().get(key).cloned()
    }
    
    pub async fn cache_module(&self, key: String, module: Module) {
        self.module_cache.lock().unwrap().insert(key, module);
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WasmExecutionResult {
    pub success: bool,
    pub result: Option<Vec<Val>>,
    pub error: Option<String>,
    pub execution_time_ms: u64,
    pub fuel_consumed: u64,
    pub memory_used_mb: f64,
}

impl WasmSandbox {
    pub async fn execute_with_result(
        &self,
        plugin_id: Uuid,
        function: &str,
        args: Vec<Val>,
    ) -> WasmExecutionResult {
        let start = Instant::now();
        
        match self.call_function(plugin_id, function, args).await {
            Ok(result) => {
                let elapsed = start.elapsed();
                let stats = self.get_plugin_stats(plugin_id).unwrap_or_default();
                
                WasmExecutionResult {
                    success: true,
                    result: Some(result),
                    error: None,
                    execution_time_ms: start.elapsed().as_millis() as u64,
                    fuel_consumed: stats.total_fuel_consumed,
                    memory_used_mb: stats.memory_usage as f64 / 1024.0 / 1024.0,
                }
            }
            Err(e) => {
                WasmExecutionResult {
                    success: false,
                    result: None,
                    error: Some(e.to_string()),
                    execution_time_ms: start.elapsed().as_millis() as u64,
                    fuel_consumed: 0,
                    memory_used_mb: 0.0,
                }
            }
        }
    }
}

impl Default for WasmExecutionResult {
    fn default() -> Self {
        Self {
            success: false,
            result: None,
            error: None,
            execution_time_ms: 0,
            fuel_consumed: 0,
            memory_used_mb: 0.0,
        }
    }
}

impl Default for PluginStats {
    fn default() -> Self {
        Self {
            id: Uuid::nil(),
            execution_count: 0,
            total_cpu_time: Duration::ZERO,
            total_fuel_consumed: 0,
            memory_usage: 0,
            created_at: Instant::now(),
            last_used: Instant::now(),
        }
    }
}

// Plugin Manager for lifecycle management
pub struct PluginManager {
    sandbox: WasmSandbox,
    plugins: Arc<Mutex<HashMap<String, PluginInfo>>>,
    marketplace_client: Option<MarketplaceClient>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginInfo {
    pub id: Uuid,
    pub name: String,
    slug: String,
    version: String,
    manifest: PluginManifest,
    status: PluginStatus,
    installed_at: Instant,
    last_used: Option<Instant>,
    config: PluginConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PluginStatus {
    Pending,
    Installing,
    Installed,
    Enabled,
    Disabled,
    Error,
    Updating,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginConfig {
    pub enabled: bool,
    settings: HashMap<String, serde_json::Value>,
    permissions: Permissions,
}

impl PluginManager {
    pub fn new(sandbox: WasmSandbox, marketplace_client: Option<MarketplaceClient>) -> Self {
        Self {
            sandbox,
            plugins: Arc::new(Mutex::new(HashMap::new())),
            marketplace_client,
        }
    }
    
    pub async fn install_from_marketplace(
        &self,
        slug: &str,
        version: Option<String>,
    ) -> Result<PluginInfo> {
        let client = self.marketplace_client.as_ref()
            .ok_or_else(|| anyhow!("Marketplace not configured"))?;
        
        let plugin_data = client.download_plugin(slug, version).await
            .context("Failed to download plugin")?;
        
        let manifest: PluginManifest = serde_json::from_slice(&plugin_data.manifest)
            .context("Invalid manifest")?;
        
        let plugin_id = self.sandbox.load_plugin(&plugin_data.wasm_bytes, manifest.clone()).await
            .context("Failed to load plugin")?;
        
        let info = PluginInfo {
            id: plugin_id,
            name: manifest.name.clone(),
            slug: manifest.slug.clone(),
            version: manifest.version.clone(),
            manifest,
            status: PluginStatus::Installed,
            installed_at: Instant::now(),
            last_used: None,
            config: PluginConfig {
                enabled: true,
                settings: HashMap::new(),
                permissions: Default::default(),
            },
        };
        
        self.plugins.lock().unwrap().insert(manifest.slug.clone(), info.clone());
        
        Ok(info)
    }
    
    pub async fn install_from_file(
        &self,
        path: &Path,
    ) -> Result<PluginInfo> {
        let wasm_bytes = std::fs::read(path)
            .context("Failed to read plugin file")?;
        
        let manifest_path = path.with_extension("superdev.yaml");
        let manifest_data = std::fs::read_to_string(manifest_path)
            .context("Failed to read manifest")?;
        
        let manifest: PluginManifest = serde_yaml::from_str(&manifest_data)
            .context("Invalid manifest")?;
        
        let plugin_id = self.sandbox.load_plugin(&wasm_bytes, manifest.clone()).await
            .context("Failed to load plugin")?;
        
        let info = PluginInfo {
            id: plugin_id,
            name: manifest.name.clone(),
            slug: manifest.slug.clone(),
            version: manifest.version.clone(),
            manifest,
            status: PluginStatus::Installed,
            installed_at: Instant::now(),
            last_used: None,
            config: PluginConfig {
                enabled: true,
                settings: HashMap::new(),
                permissions: Default::default(),
            },
        };
        
        self.plugins.lock().unwrap().insert(manifest.slug.clone(), info.clone());
        
        Ok(info)
    }
    
    pub async fn enable_plugin(&self, slug: &str) -> Result<()> {
        let mut plugins = self.plugins.lock().unwrap();
        if let Some(plugin) = plugins.get_mut(slug) {
            plugin.status = PluginStatus::Enabled;
            plugin.config.enabled = true;
        }
        Ok(())
    }
    
    pub async fn disable_plugin(&self, slug: &str) -> Result<()> {
        let mut plugins = self.plugins.lock().unwrap();
        if let Some(plugin) = plugins.get_mut(slug) {
            plugin.status = PluginStatus::Disabled;
            plugin.config.enabled = false;
        }
        Ok(())
    }
    
    pub async fn uninstall_plugin(&self, slug: &str) -> Result<()> {
        let mut plugins = self.plugins.lock().unwrap();
        if let Some(plugin) = plugins.remove(slug) {
            self.sandbox.unload_plugin(plugin.id).await
                .context("Failed to unload plugin")?;
        }
        Ok(())
    }
    
    pub async fn update_plugin_config(
        &self,
        slug: &str,
        config: HashMap<String, serde_json::Value>,
    ) -> Result<()> {
        let mut plugins = self.plugins.lock().unwrap();
        if let Some(plugin) = plugins.get_mut(slug) {
            plugin.config.settings = config;
        }
        Ok(())
    }
    
    pub async fn execute_plugin(
        &self,
        slug: &str,
        function: &str,
        args: Vec<Val>,
    ) -> WasmExecutionResult {
        let plugin_id = {
            let plugins = self.plugins.lock().unwrap();
            plugins.get(slug).map(|p| p.id)
        };
        
        let plugin_id = plugin_id.ok_or_else(|| anyhow!("Plugin not found: {}", slug))?;
        
        self.sandbox.execute_with_result(plugin_id, function, vec![]).await
    }
    
    pub fn get_plugin_info(&self, slug: &str) -> Option<PluginInfo> {
        self.plugins.lock().unwrap().get(slug).cloned()
    }
    
    pub fn list_plugins(&self) -> Vec<PluginInfo> {
        self.plugins.lock().unwrap().values().cloned().collect()
    }
    
    pub fn get_plugin_stats(&self, slug: &str) -> Option<PluginStats> {
        let plugins = self.plugins.lock().unwrap();
        plugins.get(slug).and_then(|p| self.sandbox.get_plugin_stats(p.id))
    }
}

// Marketplace Client
pub struct MarketplaceClient {
    base_url: String,
    api_key: Option<String>,
    client: reqwest::Client,
}

impl MarketplaceClient {
    pub fn new(base_url: String, api_key: Option<String>) -> Self {
        Self {
            base_url,
            api_key,
            client: reqwest::Client::new(),
        }
    }
    
    pub async fn search_plugins(&self, query: &str, category: Option<String>) -> Result<Vec<PluginSearchResult>> {
        let mut url = format!("{}/api/v1/plugins/search", self.base_url);
        if !query.is_empty() {
            url.push_str(&format!("?q={}", query));
        }
        if let Some(cat) = category {
            url.push_str(&format!("&category={}", cat));
        }
        
        let response = self.client.get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key.as_deref().unwrap_or("")))
            .send()
            .await
            .context("Failed to search plugins")?;
        
        response.json().await.context("Failed to parse response")
    }
    
    pub async fn get_plugin(&self, slug: &str) -> Result<PluginDetail> {
        let url = format!("{}/api/v1/plugins/{}", self.base_url, slug);
        
        let response = self.client.get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key.as_deref().unwrap_or("")))
            .send()
            .await
            .context("Failed to get plugin")?;
        
        response.json().await.context("Failed to parse response")
    }
    
    pub async fn download_plugin(&self, slug: &str, version: Option<String>) -> Result<PluginDownload> {
        let mut url = format!("{}/api/v1/plugins/{}/download", self.base_url, slug);
        if let Some(v) = version {
            url.push_str(&format!("?version={}", v));
        }
        
        let response = self.client.get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key.as_deref().unwrap_or("")))
            .send()
            .await
            .context("Failed to download plugin")?;
        
        let download = PluginDownload {
            wasm_bytes: response.bytes().await.context("Failed to read response")?.to_vec(),
            manifest: response.headers()
                .get("x-plugin-manifest")
                .and_then(|h| h.to_str().ok())
                .and_then(|s| serde_json::from_str(s).ok())
                .unwrap_or_default(),
        };
        
        Ok(download)
    }
    
    pub async fn publish_plugin(
        &self,
        package: Vec<u8>,
        manifest: PluginManifest,
    ) -> Result<PluginPublishResult> {
        let mut form = reqwest::multipart::Form::new()
            .part("package", reqwest::multipart::Part::bytes(package)
                .file_name("plugin.superdev-plugin")
                .mime_str("application/zip")?)
            .part("manifest", reqwest::multipart::Part::text(
                serde_json::to_string(&manifest).context("Failed to serialize manifest")?
            ));
        
        let response = self.client.post(&format!("{}/api/v1/plugins/publish", self.base_url))
            .header("Authorization", format!("Bearer {}", self.api_key.as_deref().unwrap_or("")))
            .multipart(form)
            .send()
            .await
            .context("Failed to publish plugin")?;
        
        response.json().await.context("Failed to parse response")
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginSearchResult {
    pub slug: String,
    name: String,
    version: String,
    description: String,
    author: String,
    category: String,
    downloads: u64,
    rating: f32,
    is_official: bool,
    tags: Vec<String>,
    updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginDetail {
    pub slug: String,
    pub name: String,
    version: String,
    description: String,
    author: String,
    author_email: String,
    homepage: String,
    repository: String,
    license: String,
    category: String,
    tags: Vec<String>,
    downloads: u64,
    rating: f32,
    is_official: bool,
    is_verified: bool,
    readme: String,
    changelog: String,
    screenshots: Vec<String>,
    versions: Vec<PluginVersion>,
    dependencies: Vec<PluginDependency>,
    permissions: Permissions,
    config_schema: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginVersion {
    version: String,
    release_date: String,
    changelog: String,
    download_url: String,
    size_bytes: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginDependency {
    slug: String,
    version: String,
    optional: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginDownload {
    wasm_bytes: Vec<u8>,
    manifest: PluginManifest,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginPublishResult {
    slug: String,
    version: String,
    published_at: String,
    download_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WasmExecutionResult {
    success: bool,
    result: Option<Vec<Val>>,
    error: Option<String>,
    execution_time_ms: u64,
    fuel_consumed: u64,
    memory_used_mb: f64,
}

impl Default for WasmExecutionResult {
    fn default() -> Self {
        Self {
            success: false,
            result: None,
            error: None,
            execution_time_ms: 0,
            fuel_consumed: 0,
            memory_used_mb: 0.0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_wasm_sandbox_creation() {
        let config = WasmPluginConfig::default();
        let sandbox = WasmSandbox::new(config);
        assert!(sandbox.list_plugins().is_empty());
    }
    
    #[tokio::test]
    async fn test_plugin_manager() {
        let config = WasmPluginConfig::default();
        let sandbox = WasmSandbox::new(config);
        let manager = PluginManager::new(sandbox, None);
        
        assert!(manager.list_plugins().is_empty());
    }
    
    #[test]
    fn test_plugin_manifest_serialization() {
        let manifest = PluginManifest {
            name: "test-plugin".to_string(),
            version: "1.0.0".to_string(),
            slug: "test-plugin".to_string(),
            description: "Test plugin".to_string(),
            author: "Test Author".to_string(),
            author_email: "test@example.com".to_string(),
            homepage: "https://example.com".to_string(),
            repository: "https://github.com/test/plugin".to_string(),
            license: "MIT".to_string(),
            entrypoint: "plugin.py".to_string(),
            category: "tool".to_string(),
            tags: vec!["test".to_string()],
            min_platform_version: "5.0.0".to_string(),
            max_platform_version: None,
            dependencies: vec![],
            config_schema: serde_json::json!({}),
            permissions: Default::default(),
            resources: Default::default(),
            exports: vec!["execute".to_string()],
            imports: vec![],
            is_official: false,
            is_verified: false,
        };
        
        let json = serde_json::to_string(&manifest).unwrap();
        let parsed: PluginManifest = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed.name, "test-plugin");
    }
}