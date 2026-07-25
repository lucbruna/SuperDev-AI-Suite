using System.Net;

namespace SuperDev.SDK.Exceptions;

/// <summary>
/// Raised when authentication or authorization fails (HTTP 401 or 403).
/// </summary>
public class AuthenticationException : SuperDevException
{
    public AuthenticationException(string message = "Authentication failed", Dictionary<string, object>? details = null)
        : base(message, HttpStatusCode.Unauthorized, details)
    {
    }
}
