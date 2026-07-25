# Authentication

SuperDev supports two authentication methods: API keys and JWT tokens.

## API Key Authentication

Generate an API key in the Settings > API Keys section of the dashboard.

```bash
curl -H "Authorization: Bearer sk-your-api-key" http://localhost:8000/api/v1/users/me
```

## JWT Token Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "user": { "id": "usr_123", "email": "user@example.com" }
}
```

### Using the Token

```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/v1/projects
```

### Refresh Token

```bash
curl -X POST http://api/v1/auth/refresh \
  -H "Authorization: Bearer eyJ-refresh-token"
```

## SDK Examples

### Python
```python
from superdev_sdk import SuperDevClient

client = SuperDevClient(api_key="sk-...")
# or
client = SuperDevClient("http://localhost:8000")
client.login(email="user@example.com", password="password")
```

### TypeScript
```typescript
import { SuperDevClient } from "superdev-sdk";

const client = new SuperDevClient({ apiKey: "sk-..." });
```
