package superdev

import "fmt"

type APIError struct {
	StatusCode int
	Message    string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Message)
}

func (e *APIError) IsAuthError() bool {
	return e.StatusCode == 401 || e.StatusCode == 403
}

func (e *APIError) IsNotFound() bool {
	return e.StatusCode == 404
}

func (e *APIError) IsRateLimited() bool {
	return e.StatusCode == 429
}
