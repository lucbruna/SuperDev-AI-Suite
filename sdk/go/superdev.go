// SuperDev Go SDK
// go get github.com/superdev/sdk

package superdev

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

const (
	DefaultBaseURL = "http://localhost:8000"
	DefaultTimeout = 60 * time.Second
)

type Config struct {
	BaseURL  string
	APIKey   string
	Timeout  time.Duration
	HTTPClient *http.Client
}

type Client struct {
	config    Config
	httpClient *http.Client
	baseURL   *url.URL
}

func NewClient(config Config) (*Client, error) {
	if config.BaseURL == "" {
		config.BaseURL = DefaultBaseURL
	}
	if config.Timeout == 0 {
		config.Timeout = DefaultTimeout
	}

	baseURL, err := url.Parse(config.BaseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid base URL: %w", err)
	}

	httpClient := config.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{Timeout: config.Timeout}
	}

	return &Client{
		config:     config,
		httpClient: httpClient,
		baseURL:    baseURL,
	}, nil
}

func (c *Client) request(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		bodyReader = bytes.NewReader(jsonBody)
	}

	fullURL := c.baseURL.ResolveReference(&url.URL{Path: path})
	req, err := http.NewRequestWithContext(ctx, method, fullURL.String(), bodyReader)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if c.config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.config.APIKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(respBody))
	}

	if result != nil {
		if err := json.Unmarshal(respBody, result); err != nil {
			return fmt.Errorf("failed to unmarshal response: %w", err)
		}
	}

	return nil
}

// Health Check
func (c *Client) HealthCheck(ctx context.Context) (*HealthResponse, error) {
	var result HealthResponse
	err := c.request(ctx, "GET", "/api/v1/health", nil, &result)
	return &result, err
}

func (c *Client) GetVersion(ctx context.Context) (*VersionResponse, error) {
	var result VersionResponse
	err := c.request(ctx, "GET", "/api/v1/version", nil, &result)
	return &result, err
}

// Chat
func (c *Client) Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error) {
	var result ChatResponse
	err := c.request(ctx, "POST", "/api/v1/chat/completions", req, &result)
	return &result, err
}

// Code Verification
func (c *Client) VerifyCode(ctx context.Context, req VerificationRequest) (*VerificationResult, error) {
	var result VerificationResult
	err := c.request(ctx, "POST", "/api/v1/verify", req, &result)
	return &result, err
}

// Workflows
func (c *Client) CreateWorkflow(ctx context.Context, req CreateWorkflowRequest) (*WorkflowResponse, error) {
	var result WorkflowResponse
	err := c.request(ctx, "POST", "/api/v1/workflows", req, &result)
	return &result, err
}

func (c *Client) ExecuteWorkflow(ctx context.Context, workflowID string, variables map[string]interface{}) (map[string]interface{}, error) {
	var result map[string]interface{}
	body := map[string]interface{}{"variables": variables}
	err := c.request(ctx, "POST", fmt.Sprintf("/api/v1/workflows/%s/execute", workflowID), body, &result)
	return result, err
}

// Knowledge Base
func (c *Client) CreateKnowledgeBase(ctx context.Context, req KnowledgeBaseCreate) (*KnowledgeBase, error) {
	var result KnowledgeBase
	err := c.request(ctx, "POST", "/api/v1/knowledge-bases", req, &result)
	return &result, err
}

func (c *Client) SearchKnowledge(ctx context.Context, req SearchRequest) (*SearchResponse, error) {
	var result SearchResponse
	err := c.request(ctx, "POST", "/api/v1/knowledge-bases/search", req, &result)
	return &result, err
}

// Projects
func (c *Client) CreateProject(ctx context.Context, req CreateProjectRequest) (*Project, error) {
	var result Project
	err := c.request(ctx, "POST", "/api/v1/projects", req, &result)
	return &result, err
}

func (c *Client) ListProjects(ctx context.Context) ([]Project, error) {
	var result struct {
		Success bool     `json:"success"`
		Data    []Project `json:"data"`
	}
	err := c.request(ctx, "GET", "/api/v1/projects", nil, &result)
	return result.Data, err
}

// Types

type HealthResponse struct {
	Success bool   `json:"success"`
	Data    struct {
		Status    string                 `json:"status"`
		Version   string                 `json:"version"`
		Environment string               `json:"environment"`
		Checks    map[string]interface{} `json:"checks"`
	} `json:"data"`
}

type VersionResponse struct {
	Success bool `json:"success"`
	Data    struct {
		Version string `json:"version"`
		Name    string `json:"name"`
	} `json:"data"`
}

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Messages    []ChatMessage `json:"messages"`
	Model       string        `json:"model,omitempty"`
	Provider    string        `json:"provider,omitempty"`
	Temperature float64       `json:"temperature,omitempty"`
	MaxTokens   int           `json:"max_tokens,omitempty"`
	Stream      bool          `json:"stream,omitempty"`
}

type ChatResponse struct {
	ID          string         `json:"id"`
	Content     string         `json:"content"`
	Model       string         `json:"model"`
	Usage       map[string]interface{} `json:"usage"`
	FinishReason string        `json:"finish_reason"`
}

type VerificationRequest struct {
	TaskDescription string            `json:"task_description"`
	Language        string            `json:"language,omitempty"`
	Context         string            `json:"context,omitempty"`
	Requirements    []string          `json:"requirements,omitempty"`
	ExistingCode    string            `json:"existing_code,omitempty"`
	TestFiles       map[string]string `json:"test_files,omitempty"`
	MaxIterations   int               `json:"max_iterations,omitempty"`
	Provider        string            `json:"provider,omitempty"`
}

type VerificationResult struct {
	TaskID       string                 `json:"task_id"`
	Success      bool                   `json:"success"`
	Stage        string                 `json:"stage"`
	FinalCode    string                 `json:"final_code,omitempty"`
	Error        string                 `json:"error,omitempty"`
	Iterations   int                    `json:"iterations"`
	Generation   map[string]interface{} `json:"generation,omitempty"`
	Execution    map[string]interface{} `json:"execution,omitempty"`
	Testing      map[string]interface{} `json:"testing,omitempty"`
	Review       map[string]interface{} `json:"review,omitempty"`
	Correction   map[string]interface{} `json:"correction,omitempty"`
}

type WorkflowStep struct {
	ID              string                 `json:"id,omitempty"`
	Name            string                 `json:"name"`
	StepType        string                 `json:"step_type"`
	Config          map[string]interface{} `json:"config,omitempty"`
	DependsOn       []string               `json:"depends_on,omitempty"`
	MaxRetries      int                    `json:"max_retries,omitempty"`
	TimeoutSeconds  int                    `json:"timeout_seconds,omitempty"`
	ContinueOnError bool                   `json:"continue_on_error,omitempty"`
}

type CreateWorkflowRequest struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Steps       []WorkflowStep         `json:"steps"`
	Variables   map[string]interface{} `json:"variables,omitempty"`
	Tags        []string               `json:"tags,omitempty"`
}

type WorkflowResponse struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Steps       []interface{}          `json:"steps"`
	Tags        []string               `json:"tags"`
}

type KnowledgeBaseCreate struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	Type        string `json:"type,omitempty"`
	IsPublic    bool   `json:"is_public,omitempty"`
}

type KnowledgeBase struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Type        string `json:"type"`
	IsPublic    bool   `json:"is_public"`
	CreatedAt   string `json:"created_at"`
	UpdatedAt   string `json:"updated_at"`
}

type SearchRequest struct {
	Query                 string   `json:"query"`
	KnowledgeBaseIDs      []string `json:"knowledge_base_ids,omitempty"`
	TopK                  int      `json:"top_k,omitempty"`
	SimilarityThreshold   float64  `json:"similarity_threshold,omitempty"`
}

type SearchResult struct {
	EntryID     string  `json:"entry_id"`
	ChunkID     string  `json:"chunk_id"`
	Title       string  `json:"title"`
	Content     string  `json:"content"`
	Similarity  float64 `json:"similarity"`
	Language    string  `json:"language,omitempty"`
	Tags        []string `json:"tags"`
}

type SearchResponse struct {
	Results []SearchResult `json:"results"`
	Total   int            `json:"total"`
}

type CreateProjectRequest struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	Template    string `json:"template,omitempty"`
}

type Project struct {
	ID        string                 `json:"id"`
	Name      string                 `json:"name"`
	Description string               `json:"description"`
	CreatedAt string                 `json:"created_at"`
	UpdatedAt string                 `json:"updated_at"`
	OwnerID   string                 `json:"owner_id"`
	Settings  map[string]interface{} `json:"settings"`
}