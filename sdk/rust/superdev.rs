// SuperDev Rust SDK
// cargo add superdev-sdk

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

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

#[derive(Debug, Clone)]
pub struct Client {
    config: Config,
    client: reqwest::Client,
}

impl Client {
    pub fn new(config: Config) -> Result<Self, Box<dyn std::error::Error>> {
        let client = reqwest::Client::builder()
            .timeout(config.timeout)
            .build()?;

        Ok(Self { config, client })
    }

    async fn request<T: for<'de> Deserialize<'de>>(
        &self,
        method: reqwest::Method,
        path: &str,
        body: Option<&impl Serialize>,
    ) -> Result<T, Box<dyn std::error::Error>> {
        let url = format!("{}{}", self.config.base_url, path);
        let mut request = self.client.request(method, &url);

        if let Some(api_key) = &self.config.api_key {
            request = request.bearer_auth(api_key);
        }

        if let Some(body) = body {
            request = request.json(body);
        }

        let response = request.send().await?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await?;
            return Err(format!("API error: {} - {}", status, text).into());
        }

        let result = response.json().await?;
        Ok(result)
    }

    // Health Check
    pub async fn health_check(&self) -> Result<HealthResponse, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::GET, "/api/v1/health", None::<&()>).await
    }

    // Version
    pub async fn get_version(&self) -> Result<VersionResponse, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::GET, "/api/v1/version", None::<&()>).await
    }

    // Chat
    pub async fn chat(&self, req: ChatRequest) -> Result<ChatResponse, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/chat/completions", Some(&req)).await
    }

    // Code Verification
    pub async fn verify_code(&self, req: VerificationRequest) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/verify", Some(&req)).await
    }

    // Workflows
    pub async fn create_workflow(&self, req: CreateWorkflowRequest) -> Result<WorkflowResponse, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/workflows", Some(&req)).await
    }

    pub async fn execute_workflow(&self, workflow_id: &str, variables: HashMap<String, serde_json::Value>) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let body = serde_json::json!({ "variables": variables });
        self.request(reqwest::Method::POST, &format!("/api/v1/workflows/{}/execute", workflow_id), Some(&body)).await
    }

    // Knowledge Base
    pub async fn create_knowledge_base(&self, req: KnowledgeBaseCreate) -> Result<KnowledgeBase, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/knowledge-bases", Some(&req)).await
    }

    pub async fn search_knowledge(&self, req: SearchRequest) -> Result<SearchResponse, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/knowledge-bases/search", Some(&req)).await
    }

    // Projects
    pub async fn create_project(&self, req: CreateProjectRequest) -> Result<Project, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, "/api/v1/projects", Some(&req)).await
    }

    pub async fn list_projects(&self) -> Result<Vec<Project>, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::GET, "/api/v1/projects", None::<&()>).await
    }

    // Agents
    pub async fn list_agents(&self) -> Result<Vec<Agent>, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::GET, "/api/v1/agents", None::<&()>).await
    }

    pub async fn execute_agent_task(&self, agent_id: &str, req: ExecuteAgentRequest) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        self.request(reqwest::Method::POST, &format!("/api/v1/agents/{}/execute", agent_id), Some(&req)).await
    }

    // Plugins
    pub async fn list_plugins(&self, plugin_type: Option<&str>, tag: Option<&str>, search: Option<&str>) -> Result<Vec<Plugin>, Box<dyn std::error::Error>> {
        let mut path = "/api/v1/plugins/registry".to_string();
        let mut params = vec![];
        if let Some(t) = plugin_type {
            params.push(format!("plugin_type={}", t));
        }
        if let Some(t) = tag {
            params.push(format!("tag={}", t));
        }
        if let Some(t) = search {
            params.push(format!("search={}", t));
        }
        if !params.is_empty() {
            path.push('?');
            path.push_str(&params.join("&"));
        }
        self.request(reqwest::Method::GET, &path, None::<&()>).await
    }
}

// Types

#[derive(Debug, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
    pub environment: String,
    pub timestamp: String,
}

#[derive(Debug, Deserialize)]
pub struct VersionResponse {
    pub version: String,
    pub name: String,
}

#[derive(Debug, Serialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize)]
pub struct ChatRequest {
    pub messages: Vec<ChatMessage>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stream: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct ChatResponse {
    pub id: String,
    pub content: String,
    pub model: String,
    pub usage: serde_json::Value,
    pub finish_reason: String,
}

#[derive(Debug, Serialize)]
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
    pub max_iterations: Option<i32>,
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
    pub iterations: i32,
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

#[derive(Debug, Serialize)]
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
    pub max_retries: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout_seconds: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub continue_on_error: Option<bool>,
}

#[derive(Debug, Serialize)]
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

#[derive(Debug, Serialize)]
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

#[derive(Debug, Serialize)]
pub struct SearchRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub knowledge_base_ids: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_k: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub similarity_threshold: Option<f64>,
}

#[derive(Debug, Deserialize)]
pub struct SearchResult {
    pub entry_id: String,
    pub chunk_id: String,
    pub title: String,
    pub content: String,
    pub similarity: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
    pub tags: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub total: i32,
}

#[derive(Debug, Serialize)]
pub struct CreateProjectRequest {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub template: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub description: String,
    pub created_at: String,
    pub updated_at: String,
    pub owner_id: String,
    pub settings: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Deserialize)]
pub struct Agent {
    pub id: String,
    pub name: String,
    pub r#type: String,
    pub status: String,
    pub config: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Serialize)]
pub struct ExecuteAgentRequest {
    pub task: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context: Option<HashMap<String, serde_json::Value>>,
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
    pub downloads: i32,
    pub rating: f64,
    pub is_official: bool,
}