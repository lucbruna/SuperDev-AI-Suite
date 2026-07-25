# Security Policy

## Supported Versions

The following versions of SuperDev AI Suite are currently being supported with security updates:

| Version | Supported          |
|---------|--------------------|
| 5.0.x   | :white_check_mark: |
| 4.x.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

We take the security of SuperDev AI Suite seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Do NOT

- Do not publicly disclose the vulnerability before it has been addressed
- Do not create a public GitHub issue for the vulnerability
- Do not exploit the vulnerability for any purpose

### Do

- Email your findings to **security@superdev.ai**
- Include a clear description of the vulnerability
- Include steps to reproduce the issue
- Include the version(s) affected
- Include any potential impact or exploit scenarios

### What to Expect

- **Acknowledgment:** You will receive an acknowledgment within 48 hours
- **Investigation:** Our security team will investigate and validate the report
- **Resolution:** We will work on a fix and release it as soon as possible
- **Disclosure:** We will coordinate disclosure with you once the fix is released

We appreciate your responsible disclosure and will acknowledge your contribution in our security advisories.

## Security Best Practices

### For Deployments

- Always use environment variables or a secrets manager for sensitive configuration
- Enable HTTPS with valid TLS certificates in production
- Configure rate limiting on API endpoints
- Use the principle of least privilege for database and service accounts
- Regularly update dependencies to patch known vulnerabilities
- Enable audit logging for all administrative actions

### For Development

- Never commit secrets, API keys, or credentials to version control
- Use pre-commit hooks to prevent secret leakage
- Run dependency vulnerability scans (`pip audit`, `npm audit`)
- Use the provided `.env.example` template and never commit `.env` files

## Disclosure Policy

When a vulnerability is reported and confirmed, we follow this disclosure process:

1. The security team confirms the vulnerability and assesses impact
2. A fix is developed and tested internally
3. A security patch release is prepared
4. The fix is deployed to supported versions
5. A public advisory is published after the fix is released
