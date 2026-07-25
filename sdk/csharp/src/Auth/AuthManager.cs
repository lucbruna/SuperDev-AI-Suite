namespace SuperDev.SDK.Auth;

/// <summary>
/// Manages authentication state including API keys and token pairs.
/// </summary>
public sealed class AuthManager
{
    private string? _apiKey;
    private TokenPair? _tokenPair;

    /// <summary>
    /// Creates a new <see cref="AuthManager"/>.
    /// </summary>
    /// <param name="apiKey">Optional API key for direct authentication.</param>
    public AuthManager(string? apiKey = null)
    {
        _apiKey = apiKey;
    }

    /// <summary>Whether valid credentials are currently available.</summary>
    public bool IsAuthenticated =>
        !string.IsNullOrEmpty(_apiKey) ||
        (_tokenPair is not null && !_tokenPair.IsExpired);

    /// <summary>
    /// Returns the current API key, or null if using token-based auth.
    /// </summary>
    public string? ApiKey => _apiKey;

    /// <summary>
    /// Sets tokens from a login response.
    /// </summary>
    public void SetTokens(string accessToken, string refreshToken, int expiresIn = 3600)
    {
        _tokenPair = new TokenPair
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken,
            ExpiresAt = DateTimeOffset.UtcNow.AddSeconds(expiresIn)
        };
    }

    /// <summary>
    /// Clears all stored credentials.
    /// </summary>
    public void ClearTokens()
    {
        _tokenPair = null;
    }

    /// <summary>
    /// Builds the Authorization header value.
    /// </summary>
    /// <exception cref="Exceptions.AuthenticationException">Thrown when no valid credentials are available.</exception>
    public string GetAuthorizationHeader()
    {
        if (!string.IsNullOrEmpty(_apiKey))
            return $"Bearer {_apiKey}";

        if (_tokenPair is { IsExpired: false })
            return _tokenPair.ToHeader();

        throw new Exceptions.AuthenticationException("No valid credentials available. Login first or provide an API key.");
    }
}

/// <summary>
/// An access/refresh token pair with expiry tracking.
/// </summary>
internal sealed class TokenPair
{
    public string AccessToken { get; set; } = string.Empty;
    public string RefreshToken { get; set; } = string.Empty;
    public DateTimeOffset? ExpiresAt { get; set; }
    public string TokenType { get; set; } = "Bearer";

    public bool IsExpired => ExpiresAt.HasValue && DateTimeOffset.UtcNow >= ExpiresAt.Value;

    public string ToHeader() => $"{TokenType} {AccessToken}";
}
