package superdev

import "time"

type User struct {
	ID        string     `json:"id"`
	Email     string     `json:"email"`
	Name      string     `json:"name"`
	AvatarURL string     `json:"avatar_url,omitempty"`
	IsActive  bool       `json:"is_active"`
	CreatedAt *time.Time `json:"created_at,omitempty"`
}

type Project struct {
	ID             string `json:"id"`
	Name           string `json:"name"`
	Description    string `json:"description,omitempty"`
	OrganizationID string `json:"organization_id,omitempty"`
	Status         string `json:"status"`
}

type Agent struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Type   string `json:"type"`
	Status string `json:"status"`
}

type Workflow struct {
	ID          string         `json:"id"`
	Name        string         `json:"name"`
	Description string         `json:"description,omitempty"`
	Graph       map[string]any `json:"graph,omitempty"`
	Status      string         `json:"status"`
	Version     int            `json:"version"`
}

type WorkflowRun struct {
	ID         string         `json:"id"`
	WorkflowID string         `json:"workflow_id"`
	Status     string         `json:"status"`
	Inputs     map[string]any `json:"inputs,omitempty"`
	Outputs    map[string]any `json:"outputs,omitempty"`
	Error      string         `json:"error,omitempty"`
}

type Plugin struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Version     string `json:"version"`
	Description string `json:"description,omitempty"`
	Installed   bool   `json:"is_installed"`
}

type Provider struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Type    string `json:"type"`
	Enabled bool   `json:"is_enabled"`
	Health  string `json:"health"`
}

type ChatResponse struct {
	Message      string         `json:"message"`
	Model        string         `json:"model,omitempty"`
	Provider     string         `json:"provider,omitempty"`
	Usage        map[string]int `json:"usage,omitempty"`
	FinishReason string         `json:"finish_reason,omitempty"`
}

type StreamingChunk struct {
	Delta        string         `json:"delta,omitempty"`
	Model        string         `json:"model,omitempty"`
	FinishReason string         `json:"finish_reason,omitempty"`
	Usage        map[string]int `json:"usage,omitempty"`
}

type PaginatedResponse[T any] struct {
	Items        []T   `json:"items"`
	Total        int   `json:"total"`
	Page         int   `json:"page"`
	PageSize     int   `json:"page_size"`
	HasNext      bool  `json:"has_next"`
	HasPrevious  bool  `json:"has_previous"`
}
