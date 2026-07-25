using System.Net;

namespace SuperDev.SDK.Exceptions;

/// <summary>
/// Raised when a requested resource is not found (HTTP 404).
/// </summary>
public class NotFoundException : SuperDevException
{
    public NotFoundException(string message = "Resource not found", Dictionary<string, object>? details = null)
        : base(message, HttpStatusCode.NotFound, details)
    {
    }
}
