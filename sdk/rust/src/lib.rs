//! SuperDev Rust SDK
//!
//! Add to your Cargo.toml:
//! ```toml
//! [dependencies]
//! superdev = "0.1"
//! reqwest = { version = "0.12", features = ["json"] }
//! serde = { version = "1.0", features = ["derive"] }
//! serde_json = "1.0"
//! tokio = { version = "1.0", features = ["full"] }
//! thiserror = "1.0"
//! ```

use std::collections::HashMap;
use std::time::Duration;

use reqwest::{Client, Method, RequestBuilder};
use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Client configuration
#[derive(Debug, Clone)]
pub struct Config {
    pub base_url: String,
    pub api_key: Option<String>,
    pub ws_url: Option<String>,
    pub timeout: Duration,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            base_url: "http://localhost:8000".to_string(),
            api_key: None,
            ws_url: None,
            timeout: Duration::from_secs(60),
        }
    }
}

/// SDK errors
#[derive(Error, Debug)]
pub enum Error {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("API error: {status} - {message}")]
    Api { status: u16, message: String },
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("URL parse error: {0}")]
    UrlParse(#[from] url::ParseError),
}

/// Main client
#[derive(Debug, Clone)]
pub struct Client {
    config: Config,
    http_client: Client,
}

impl Client {
    /// Create a new client
    pub fn new(config: Config) -> Result<Self, Error> {
        let http_client = Client::builder()
            .timeout(config.timeout)
            .build()?;

        Ok(Self {
            config,
            http_client,
        })
    }

    async fn request<T: for<'de> Deserialize<'de>>(
        &self,
        method: Method,
        path: &str,
        body: Option<&impl Serialize>,
    ) -> Result<T, Error> {
        let url = format!("{}{}", self.config.base_url, path);
        let mut request: RequestBuilder = self.http_client.request(method, &url);

        if let Some(api_key) = &self.config.api_key {
            request = request.bearer_auth(api_key);
        }

        if let Some(body) = body {
            request = request.json(body);
        }

        let response = request.send().await?;

        if !response.status().is_success() {
            let status = response.status().as_u16();
            let message = response.text().await.unwrap_or_default();
            return Err(Error::Api { status, message });
        }

        let result = response.json().await?;
        Ok(result)
    }

    // Health check
    pub async fn health_check(&self) -> Result<HealthResponse, Error> {
        self.request(Method::GET, "/api/v1/health", None::<&()>).await
    }

    // Chat completion
    pub async fn chat(&self, req: ChatRequest) -> Result<ChatResponse, Error> {
        self.request(Method::POST, "/api/v1/chat/completions", Some(&req)).await
    }

    // Code verification
    pub async fn verify_code(&self, req: VerificationRequest) -> Result<VerificationResult, Error> {
        self.request(Method::POST, "/api/v1/verify", Some(&req)).await
    }

    // Workflows
    pub async fn create_workflow(&self, req: CreateWorkflowRequest) -> Result<WorkflowResponse, Error> {
        self.request(Method::POST, "/api/v1/workflows", Some(&req)).await
    }

    pub async fn execute_workflow(
        &self,
        workflow_id: &str,
        variables: HashMap<String, serde_json::Value>,
    ) -> Result<serde_json::Value, Error> {
        let body = serde_json::json!({ "variables": variables });
        let path = format!("/api/v1/workflows/{}/execute", workflow_id);
        self.request(Method::POST, &path, Some(&body)).await
    }

    pub async fn list_workflows(&self, tags: Option<Vec<String>>) -> Result<Vec<WorkflowResponse>, Error> {
        let mut path = "/api/v1/workflows".to_string();
        if let Some(tags) = tags {
            path.push_str(&format!("?tags={}", tags.join(",")));
        }
        self.request(Method::GET, &path, None::<&()>).await
    }

    // Knowledge Base
    pub async fn create_knowledge_base(&self, req: KnowledgeBaseCreate) -> Result<KnowledgeBase, Error> {
        self.request(Method::POST, "/api/v1/knowledge-bases", Some(&req)).await
    }

    pub async fn search_knowledge(&self, req: SearchRequest) -> Result<SearchResponse, Error> {
        self.request(Method::POST, "/api/v1/knowledge-bases/search", Some(&req)).await
    }

    pub async fn get_context(
        &self,
        query: &str,
        knowledge_base_ids: Option<Vec<String>>,
        max_tokens: Option<u32>,
    ) -> Result<ContextResponse, Error> {
        let body = ContextRequest {
            query: query.to_string(),
            knowledge_base_ids,
            max_tokens,
        };
        self.request(Method::POST, "/api/v1/knowledge-bases/context", Some(&body)).await
    }

    // Plugins
    pub async fn list_plugins(
        &self,
        plugin_type: Option<String>,
        tag: Option<String>,
        search: Option<String>,
    ) -> Result<Vec<Plugin>, Error> {
        let mut path = "/api/v1/plugins/registry".to_string();
        let mut params = Vec::new();
        if let Some(pt) = plugin_type {
            params.push(format!("plugin_type={}", pt));
        }
        if let Some(t) = tag {
            params.push(format!("tag={}", t));
        }
        if let Some(s) = search {
            params.push(format!("search={}", s));
        }
        if !params.is_empty() {
            path.push('?');
            path.push_str(&params.join("&"));
        }
        self.request(Method::GET, &path, None::<&()>).await
    }
}

// Types

#[derive(Debug, Deserialize)]
pub struct HealthResponse {
    pub success: bool,
    pub data: HealthData,
}

#[derive(Debug, Deserialize)]
pub struct HealthData {
    pub status: String,
    pub version: String,
    pub environment: String,
    pub timestamp: String,
    pub checks: HashMap<String, CheckData>,
}

#[derive(Debug, Deserialize)]
pub struct CheckData {
    pub status: String,
    pub latency_ms: f64,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatRequest {
    pub messages: Vec<ChatMessage>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stream: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct ChatResponse {
    pub id: String,
    pub content: String,
    pub model: String,
    pub usage: Option<HashMap<String, serde_json::Value>>,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VerificationRequest {
    pub task_description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub requirements: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub existing_code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub test_files: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_iterations: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct VerificationResult {
    pub task_id: String,
    pub success: bool,
    pub stage: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub final_code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    pub iterations: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub generation: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub execution: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub testing: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub review: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub correction: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WorkflowStep {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,
    pub name: String,
    pub step_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub config: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub depends_on: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_retries: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout_seconds: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub continue_on_error: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateWorkflowRequest {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    pub steps: Vec<WorkflowStep>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub variables: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tags: Option<Vec<String>>,
}

#[derive(Debug, Deserialize)]
pub struct WorkflowResponse {
    pub id: String,
    pub name: String,
    pub description: String,
    pub steps: Vec<serde_json::Value>,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct KnowledgeBaseCreate {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub r#type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_public: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct KnowledgeBase {
    pub id: String,
    pub name: String,
    pub description: String,
    pub r#type: String,
    pub is_public: bool,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub knowledge_base_ids: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_k: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub similarity_threshold: Option<f32>,
}

#[derive(Debug, Deserialize)]
pub struct SearchResult {
    pub entry_id: String,
    pub chunk_id: String,
    pub title: String,
    pub content: String,
    pub similarity: f32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
    pub tags: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub total: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ContextRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub knowledge_base_ids: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<u32>,
}

#[derive(Debug, Deserialize)]
pub struct ContextResponse {
    pub context: String,
    pub total_tokens: u32,
}

#[derive(Debug, Deserialize)]
pub struct Plugin {
    pub name: String,
    pub slug: String,
    pub version: String,
    pub description: String,
    pub author: String,
    pub plugin_type: String,
    pub tags: Vec<String>,
    pub downloads: u32,
    pub rating: f32,
    pub is_official: bool,
}