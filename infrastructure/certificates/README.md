# TLS Certificates

## Production

Use Let's Encrypt via Traefik ACME:

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@superdev.io
      storage: acme.json
      httpChallenge:
        entryPoint: web
```

## Self-Signed (Development)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/CN=localhost"
```
