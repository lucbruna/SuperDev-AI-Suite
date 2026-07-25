using System.Net;

namespace SuperDev.SDK.Exceptions;

/// <summary>
/// Base exception for all SuperDev SDK errors.
/// </summary>
public class SuperDevException : Exception
{
    /// <summary>HTTP status code, or 0 for non-HTTP errors.</summary>
    public HttpStatusCode? StatusCode { get; }

    /// <summary>Structured error details from the API response.</summary>
    public Dictionary<string, object> Details { get; }

    public SuperDevException(string message, HttpStatusCode? statusCode = null, Dictionary<string, object>? details = null)
        : base(message)
    {
        StatusCode = statusCode;
        Details = details ?? new Dictionary<string, object>();
    }

    public SuperDevException(string message, Exception innerException, HttpStatusCode? statusCode = null)
        : base(message, innerException)
    {
        StatusCode = statusCode;
        Details = new Dictionary<string, object>();
    }
}
