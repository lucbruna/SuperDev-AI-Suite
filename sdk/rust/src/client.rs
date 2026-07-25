use crate::error::SuperDevError;
use crate::types::*;

pub struct SuperDevClient {
    base_url: String,
    api_key: String,
    client: reqwest::Client,
}

impl SuperDevClient {
    pub fn new(base_url: &str, api_key: &str) -> Self {
        Self {
            base_url: base_url.trim_end_matches('/').to_string(),
            api_key: api_key.to_string(),
            client: reqwest::Client::new(),
        }
    }

    pub async fn get_user(&self) -> Result<User, SuperDevError> {
        self.get("/api/v1/users/me").await
    }

    pub async fn list_projects(&self, page: u32, page_size: u32) -> Result<PaginatedResponse<Project>, SuperDevError> {
        self.get(&format!("/api/v1/projects?page={}&page_size={}", page, page_size)).await
    }

    pub async fn get_project(&self, id: &str) -> Result<Project, SuperDevError> {
        self.get(&format!("/api/v1/projects/{}", id)).await
    }

    pub async fn create_project(&self, name: &str, description: &str) -> Result<Project, SuperDevError> {
        self.post("/api/v1/projects", serde_json::json!({"name": name, "description": description})).await
    }

    pub async fn list_agents(&self, page: u32, page_size: u32) -> Result<PaginatedResponse<Agent>, SuperDevError> {
        self.get(&format!("/api/v1/agents?page={}&page_size={}", page, page_size)).await
    }

    pub async fn list_workflows(&self, page: u32, page_size: u32) -> Result<PaginatedResponse<Workflow>, SuperDevError> {
        self.get(&format!("/api/v1/workflows?page={}&page_size={}", page, page_size)).await
    }

    pub async fn run_workflow(&self, id: &str, inputs: serde_json::Value) -> Result<WorkflowRun, SuperDevError> {
        self.post(&format!("/api/v1/workflows/{}/run", id), serde_json::json!({"inputs": inputs})).await
    }

    pub async fn send_chat(&self, message: &str, model: Option<&str>) -> Result<ChatResponse, SuperDevError> {
        let mut payload = serde_json::json!({"message": message});
        if let Some(m) = model {
            payload["model"] = serde_json::json!(m);
        }
        self.post("/api/v1/chat", payload).await
    }

    pub async fn list_providers(&self) -> Result<serde_json::Value, SuperDevError> {
        self.get("/api/v1/providers").await
    }

    pub async fn list_plugins(&self) -> Result<serde_json::Value, SuperDevError> {
        self.get("/api/v1/plugins").await
    }

    async fn get<T: serde::de::DeserializeOwned>(&self, path: &str) -> Result<T, SuperDevError> {
        let resp = self.client
            .get(format!("{}{}", self.base_url, path))
            .bearer_auth(&self.api_key)
            .send()
            .await
            .map_err(|e| SuperDevError::Connection(e.to_string()))?;

        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let body = resp.text().await.unwrap_or_default();
            return Err(SuperDevError::Api { status, message: body });
        }

        resp.json::<T>().await.map_err(|e| SuperDevError::Parse(e.to_string()))
    }

    async fn post<T: serde::de::DeserializeOwned>(&self, path: &str, body: serde_json::Value) -> Result<T, SuperDevError> {
        let resp = self.client
            .post(format!("{}{}", self.base_url, path))
            .bearer_auth(&self.api_key)
            .json(&body)
            .send()
            .await
            .map_err(|e| SuperDevError::Connection(e.to_string()))?;

        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let body = resp.text().await.unwrap_or_default();
            return Err(SuperDevError::Api { status, message: body });
        }

        resp.json::<T>().await.map_err(|e| SuperDevError::Parse(e.to_string()))
    }
}
