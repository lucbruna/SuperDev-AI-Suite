use std::fmt;

/// SuperDev SDK error types
#[derive(Debug, thiserror::Error)]
pub enum SuperDevError {
    /// HTTP request error
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    /// JSON serialization/deserialization error
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    /// URL parsing error
    #[error("URL error: {0}")]
    Url(#[from] url::ParseError),

    /// Authentication error (invalid API key or token)
    #[error("Authentication failed: {message}")]
    Auth {
        message: String,
    },

    /// Authorization error (insufficient permissions)
    #[error("Authorization failed: {message}")]
    Forbidden {
        message: String,
    },

    /// Resource not found
    #[error("Not found: {resource} with id '{id}'")]
    NotFound {
        resource: String,
        id: String,
    },

    /// Validation error (invalid request parameters)
    #[error("Validation error: {message}")]
    Validation {
        message: String,
    },

    /// Rate limit exceeded
    #[error("Rate limit exceeded. Retry after {retry_after_secs} seconds")]
    RateLimit {
        retry_after_secs: u64,
    },

    /// Server error (5xx responses)
    #[error("Server error ({status}): {message}")]
    Server {
        status: u16,
        message: String,
    },

    /// Conflict error (409 responses)
    #[error("Conflict: {message}")]
    Conflict {
        message: String,
    },

    /// Streaming error
    #[error("Streaming error: {0}")]
    Stream(String),

    /// Timeout error
    #[error("Request timed out after {timeout_ms}ms")]
    Timeout {
        timeout_ms: u64,
    },

    /// Connection error
    #[error("Connection error: {0}")]
    Connection(String),

    /// Invalid response format
    #[error("Invalid response: {message}")]
    InvalidResponse {
        message: String,
    },

    /// Operation was cancelled
    #[error("Operation cancelled")]
    Cancelled,

    /// Custom error message
    #[error("{0}")]
    Custom(String),
}

/// Result type alias for SuperDev SDK operations
pub type Result<T> = std::result::Result<T, SuperDevError>;

impl SuperDevError {
    /// Create a new authentication error
    pub fn auth(message: impl Into<String>) -> Self {
        Self::Auth {
            message: message.into(),
        }
    }

    /// Create a new forbidden error
    pub fn forbidden(message: impl Into<String>) -> Self {
        Self::Forbidden {
            message: message.into(),
        }
    }

    /// Create a new not found error
    pub fn not_found(resource: impl Into<String>, id: impl Into<String>) -> Self {
        Self::NotFound {
            resource: resource.into(),
            id: id.into(),
        }
    }

    /// Create a new validation error
    pub fn validation(message: impl Into<String>) -> Self {
        Self::Validation {
            message: message.into(),
        }
    }

    /// Create a new rate limit error
    pub fn rate_limit(retry_after_secs: u64) -> Self {
        Self::RateLimit { retry_after_secs }
    }

    /// Create a new server error
    pub fn server(status: u16, message: impl Into<String>) -> Self {
        Self::Server {
            status,
            message: message.into(),
        }
    }

    /// Create a new conflict error
    pub fn conflict(message: impl Into<String>) -> Self {
        Self::Conflict {
            message: message.into(),
        }
    }

    /// Create a new timeout error
    pub fn timeout(timeout_ms: u64) -> Self {
        Self::Timeout { timeout_ms }
    }

    /// Create a new connection error
    pub fn connection(message: impl Into<String>) -> Self {
        Self::Connection(message.into())
    }

    /// Create a new invalid response error
    pub fn invalid_response(message: impl Into<String>) -> Self {
        Self::InvalidResponse {
            message: message.into(),
        }
    }

    /// Create a new stream error
    pub fn stream(message: impl Into<String>) -> Self {
        Self::Stream(message.into())
    }

    /// Create a new custom error
    pub fn custom(message: impl Into<String>) -> Self {
        Self::Custom(message.into())
    }

    /// Create an error from an HTTP status code
    pub fn from_status(status: u16, body: Option<&str>) -> Self {
        let message = body.unwrap_or("No error details provided").to_string();

        match status {
            400 => Self::Validation { message },
            401 => Self::Auth { message },
            403 => Self::Forbidden { message },
            404 => Self::NotFound {
                resource: "resource".to_string(),
                id: "unknown".to_string(),
            },
            409 => Self::Conflict { message },
            429 => Self::RateLimit {
                retry_after_secs: 60,
            },
            500..=599 => Self::Server { status, message },
            _ => Self::Custom(format!("HTTP {}: {}", status, message)),
        }
    }

    /// Get the HTTP status code if this error corresponds to one
    pub fn status_code(&self) -> Option<u16> {
        match self {
            Self::Auth { .. } => Some(401),
            Self::Forbidden { .. } => Some(403),
            Self::NotFound { .. } => Some(404),
            Self::Validation { .. } => Some(400),
            Self::RateLimit { .. } => Some(429),
            Self::Conflict { .. } => Some(409),
            Self::Server { status, .. } => Some(*status),
            _ => None,
        }
    }

    /// Check if this error is retryable
    pub fn is_retryable(&self) -> bool {
        matches!(
            self,
            Self::RateLimit { .. } | Self::Timeout { .. } | Self::Server { status, .. } if *status >= 500
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_from_status() {
        let err = SuperDevError::from_status(401, Some("Unauthorized"));
        assert!(matches!(err, SuperDevError::Auth { .. }));
        assert_eq!(err.status_code(), Some(401));
    }

    #[test]
    fn test_error_retryable() {
        let err = SuperDevError::rate_limit(60);
        assert!(err.is_retryable());

        let err = SuperDevError::server(500, "Internal error");
        assert!(err.is_retryable());

        let err = SuperDevError::auth("Invalid key");
        assert!(!err.is_retryable());
    }
}
