# Security

This document outlines practical security practices for Swali-AI development.

## Secrets Management
- Never commit `.env` with real credentials.
- Keep `GEMINI_API_KEY` only in local/secret stores.
- Rotate keys if accidental exposure occurs.

## Dependency Hygiene
- Keep Python and npm dependencies updated.
- Run vulnerability checks regularly:
  - `poetry run pip-audit` (if installed)
  - `npm audit` in `frontend/`

## API Safety
- Validate all request payloads with Pydantic models.
- Avoid returning raw stack traces in production.
- Add request rate limiting for public deployments.

## Data Safety
- Treat stored interview interaction data as sensitive.
- Minimize stored personal data.
- Back up vector store and logs responsibly.

## Local Development Hardening
- Use separate dev/test API keys.
- Do not expose local backend publicly without auth.
- Prefer HTTPS + auth if deployed beyond localhost.

## Incident Response (Basic)
1. Identify what was exposed (key, data, logs).
2. Revoke/rotate affected credentials.
3. Audit recent access and suspicious activity.
4. Patch root cause and add prevention step.
