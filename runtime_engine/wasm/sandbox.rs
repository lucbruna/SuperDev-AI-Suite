use wasmtime::*;
use wasmtime_wasi::*;
use wasmtime_wasi::preview1::*;
use std::sync::Arc;
use std::collections::HashMap;
use std::time::{Duration, Instant};
use anyhow::{Result, Context, anyhow};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
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
            enable_simd: true,
            enable_bulk_memory: true,
            enable_reference_types: true,
            enable_multi_memory: false,
            enable_multi_value: true,
            enable_atomics: false,
            enable_exception_handling: false,
            enable_memory64: false,
            enable_extended_const: true,
            enable_relaxed_simd: true,
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
    total_cpu_time: Duration,
    total_fuel_consumed: u64,
}

impl WasmPluginInstance {
    pub fn new(manifest: PluginManifest, config: &WasmPluginConfig) -> Result<Self> {
        let mut config_builder = Config::new();
        
        config_builder.wasm_simd(true);
        config_builder.wasm_bulk_memory(true);
        config_builder.wasm_reference_types(true);
        config_builder.wasm_multi_value(true);
        config_builder.wasm_threads(true);
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
        
        let module = Module::new(&engine, wasm_bytes)
            .context("Failed to compile WASM module")?;
        
        let instance = Instance::new(&mut store, &module, &imports)
            .context("Failed to instantiate module")?;
        
        let memory = instance.get_memory(&mut store, "memory")
            .ok_or_else(|| anyhow!("No memory export found"))?;
        
        Ok(Self {
            id: Uuid::new_v4(),
            manifest,
            engine,
            store,
            instance,
            memory,
            created_at: Instant::now(),
            last_used: Instant::now(),
            execution_count: 0,
            total_cpu_time: Duration::ZERO,
            total_fuel_consumed: 0,
        })
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
        config_builder.wasm_bulk_memory(true);
        config_builder.wasm_reference_types(true);
        config_builder.wasm_multi_value(true);
        config_builder.wasm_threads(true);
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
        
        Engine::new(&config_builder).context("Failed to create engine")
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

pub async fn create_wasm_sandbox(config: WasmPluginConfig) -> Result<WasmSandbox> {
    Ok(WasmSandbox::new(config))
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_sandbox_creation() {
        let config = WasmPluginConfig::default();
        let sandbox = WasmSandbox::new(config);
        assert!(sandbox.instances.lock().unwrap().is_empty());
    }
    
    #[tokio::test]
    async fn test_plugin_loading() {
        let config = WasmPluginConfig::default();
        let sandbox = WasmSandbox::new(config);
        
        // Simple WASM module that exports a function
        let wat = r#"
            (module
                (func $add (param i32 i32) (result i32)
                    local.get 0
                    local.get 1
                    i32.add)
                (export "add" (func $add))
            )
        "#;
        
        let wasm_bytes = wat::parse_str(wat).unwrap();
        
        let manifest = PluginManifest {
            name: "test-plugin".to_string(),
            version: "1.0.0".to_string(),
            entrypoint: "add".to_string(),
            exports: vec!["add".to_string()],
            imports: vec![],
            memory: None,
            resources: ResourceLimits::default(),
            permissions: Permissions::default(),
        };
        
        let plugin_id = sandbox.load_plugin(&wasm_bytes, manifest).await.unwrap();
        assert!(!plugin_id.is_nil());
    }
}