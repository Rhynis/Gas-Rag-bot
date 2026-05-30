# Deployment

GasBot Vietnam deploys to Vercel, Railway, and Supabase.

This document is a production deployment runbook. It does not create cloud accounts or set secrets
for you; the owner performs those manual steps after the deployment-prep PR is merged.

## Targets

- Frontend: Vercel
- Backend: Railway
- Database: Supabase PostgreSQL with pgvector
- LLM provider: Gemini Flash in production
- Observability: Sentry, Langfuse, UptimeRobot

## Pre-Deployment Checklist

- CI is green on `main`.
- Backend checks pass locally: `ruff format --check . && ruff check .`, `mypy app/`,
  `pytest --cov=app --cov-report=term-missing --cov-fail-under=70`, `pip-audit --strict`.
- Frontend checks pass locally: `npm run lint && npm run format:check && npm run build`.
- Alembic migrations have been tested against a fresh database.
- Supabase project exists and the production `DATABASE_URL` is available.
- Railway backend environment variables are set.
- Vercel frontend environment variables are set.
- `CORS_ORIGINS` includes the exact Vercel production origin.
- `/health` and `/health/detailed` are reachable after backend deploy.
- Security headers are verified with `backend/scripts/verify_security_headers.py`.
- Smoke-test account and admin account are ready.

## Required GitHub Secrets

| Secret | Purpose | Where to get it |
| --- | --- | --- |
| `VERCEL_TOKEN` | Deploy frontend from GitHub Actions | Vercel account settings |
| `VERCEL_ORG_ID` | Vercel organization identifier | Vercel project settings |
| `VERCEL_PROJECT_ID` | Vercel project identifier | Vercel project settings |
| `RAILWAY_TOKEN` | Deploy backend from GitHub Actions | Railway account settings |

## Environment Variable Reference

### Backend

These variables come from `backend/app/core/config.py`.

| Name | Required in production? | Default | Description | Example |
| --- | --- | --- | --- | --- |
| `ENVIRONMENT` | Yes | `development` | Runtime mode. Use `production` for live deploys. | `production` |
| `DEBUG` | No | `False` | Enables debug behavior when true. Keep false in production. | `false` |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://gasbot:gasbot_dev_password@localhost:5432/gasbot_dev` | Async SQLAlchemy URL for Supabase PostgreSQL. | `postgresql+asyncpg://user:pass@host:5432/postgres` |
| `SUPABASE_URL` | If Supabase APIs are used | empty | Supabase project URL. | `https://abc.supabase.co` |
| `SUPABASE_KEY` | If Supabase APIs are used | empty | Supabase anon key for backend integrations that need anon access. | `eyJ...` |
| `SUPABASE_SERVICE_KEY` | If service-role calls are used | empty | Supabase service-role key. Treat as secret. | `eyJ...` |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis URL for auth/session/rate-limit support. | `redis://default:pass@host:6379/0` |
| `LLM_PROVIDER` | Yes | `ollama` | LLM provider. Production should use `gemini`. | `gemini` |
| `OLLAMA_BASE_URL` | Only when `LLM_PROVIDER=ollama` | `http://localhost:11434` | Ollama API base URL. | `http://ollama:11434` |
| `OLLAMA_MODEL` | Only when `LLM_PROVIDER=ollama` | `qwen2.5:7b-instruct-q4_K_M` | Ollama chat model. | `qwen2.5:7b-instruct-q4_K_M` |
| `OLLAMA_EMBED_MODEL` | Only when `LLM_PROVIDER=ollama` | `nomic-embed-text` | Ollama embedding model. | `nomic-embed-text` |
| `OLLAMA_TIMEOUT` | Only when `LLM_PROVIDER=ollama` | `60` | Ollama request timeout in seconds. | `60` |
| `GEMINI_API_KEY` | Yes when `LLM_PROVIDER=gemini` | `None` | Google Gemini API key. | `AIza...` |
| `GEMINI_MODEL` | Yes when `LLM_PROVIDER=gemini` | `gemini-2.0-flash-exp` | Gemini chat model. | `gemini-2.0-flash-exp` |
| `GEMINI_EMBED_MODEL` | Yes when Gemini embeddings are used | `text-embedding-004` | Gemini embedding model. | `text-embedding-004` |
| `EMBEDDING_MODEL` | Yes | `keepitreal/vietnamese-sbert` | Local SBERT model for Vietnamese embeddings. | `keepitreal/vietnamese-sbert` |
| `EMBEDDING_DIMENSIONS` | Yes | `768` | Embedding vector dimension. Must match database vector dimension. | `768` |
| `LANGFUSE_PUBLIC_KEY` | Optional | empty | Langfuse public key for LLM tracing. | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | Optional | empty | Langfuse secret key for LLM tracing. | `sk-lf-...` |
| `LANGFUSE_HOST` | Optional | `https://cloud.langfuse.com` | Langfuse host. | `https://cloud.langfuse.com` |
| `SENTRY_DSN` | Optional | empty | Backend Sentry DSN. Used only in production when set. | `https://...@sentry.io/...` |
| `JWT_SECRET_KEY` | Yes | `development_secret_key_change_me_32_chars_minimum` | JWT signing secret, minimum 32 chars. Generate a unique production value. | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | Yes | `HS256` | JWT signing algorithm. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token lifetime. | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token lifetime. | `7` |
| `BCRYPT_ROUNDS` | No | `12` | Password hashing cost. | `12` |
| `CORS_ORIGINS` | Yes | `http://localhost:3000` | Comma-separated allowed browser origins. | `https://gasbot.example.com` |
| `RATE_LIMIT_PER_MINUTE` | No | `60` | Default API rate limit. | `60` |
| `RATE_LIMIT_AUTH_PER_MINUTE` | No | `5` | Auth endpoint rate limit. | `5` |
| `RATE_LIMIT_LLM_PER_MINUTE` | No | `10` | LLM/chat endpoint rate limit. | `10` |

### Frontend

| Name | Required in production? | Default | Description | Example |
| --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` in code fallback | Public backend base URL. | `https://gasbot-api.up.railway.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes for auth helpers | empty in example | Supabase project URL exposed to browser. | `https://abc.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes for auth helpers | empty in example | Supabase anon key exposed to browser. | `eyJ...` |

## Vercel Setup

1. Create a Vercel project from the GitHub repository.
2. Set the root directory to `frontend`.
3. Set environment variables from `frontend/.env.example`.
4. Confirm the region is close to users, preferably Singapore when available.
5. Run a production deployment.
6. Confirm all public pages load and browser API calls hit the Railway backend.

Frontend Sentry is an optional manual follow-up. Do not install `@sentry/nextjs` unless a separate
phase or owner instruction adds it to scope.

## Railway Setup

1. Create a Railway service from the GitHub repository.
2. Set the root directory to `backend`.
3. Configure the Dockerfile builder using `backend/railway.json`.
4. Set backend environment variables from the reference above.
5. Deploy and confirm `/health` returns `200`.
6. Confirm `/health/detailed` reports database and Redis as `ok`.

## Supabase Setup

1. Create a Supabase PostgreSQL project.
2. Set `DATABASE_URL` in Railway using the asyncpg URL format.
3. Run `alembic upgrade head` against production.
4. Confirm migrations enable `uuid-ossp`, `vector`, and `pg_trgm`.
5. Load seed data only when the owner wants demo/staging content in that environment.

## Monitoring Setup

### Sentry

1. Create a backend Sentry project.
2. Set `SENTRY_DSN` in Railway.
3. Keep `ENVIRONMENT=production`; backend Sentry initialization is production-gated.
4. Trigger a controlled backend error in staging first and confirm it appears in Sentry.

### Langfuse

1. Create a Langfuse project.
2. Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optionally `LANGFUSE_HOST`.
3. Run a chat/RAG request and confirm an LLM generation trace appears.
4. If Langfuse is unavailable, the app should degrade gracefully and keep serving traffic.

### UptimeRobot

1. Create an HTTPS monitor for `GET /health`.
2. Use a 1-5 minute interval depending on the plan.
3. Send downtime alerts to the owner email.
4. Add a second monitor for frontend homepage availability.

## Security Audit Commands

Backend:

```bash
cd backend
pip-audit --strict
python -m scripts.verify_security_headers --url https://YOUR_BACKEND_DOMAIN/health
```

Frontend:

```bash
cd frontend
npm audit --audit-level=high
```

Manual header check:

```bash
curl -I https://YOUR_BACKEND_DOMAIN/health | grep -E "X-Frame|X-Content|Strict-Transport|Content-Security"
```

## Common Issues And Solutions

| Issue | Likely cause | Solution |
| --- | --- | --- |
| Migration fails on Supabase | Missing extension permissions or wrong database URL | Confirm URL targets the primary database, run migrations once, and inspect the first failing statement. |
| Browser CORS errors | `CORS_ORIGINS` does not match the Vercel origin exactly | Set `CORS_ORIGINS=https://your-domain` and redeploy Railway. Include preview domains only if needed. |
| Redis timeout or auth failures | `REDIS_URL` missing, wrong password, or Redis service asleep | Verify Railway Redis connection string and check `/health/detailed`. |
| Embedding model load is slow or memory spikes | SBERT cold start or insufficient Railway memory | Increase memory, keep one warm replica, or move heavy imports away from startup paths when scoped. |
| LLM rate limit errors | Gemini API quota exhausted or too many chat requests | Check provider dashboard, reduce traffic, tune rate limits, or switch keys after owner approval. |
| Security header script fails for HSTS locally | App is not running with `ENVIRONMENT=production` | Verify headers against staging/production, or run local app with production env for the header check. |
| Frontend points to localhost after deploy | Missing `NEXT_PUBLIC_API_URL` in Vercel | Set the production backend URL and redeploy frontend. |

## Rollback

- Frontend: use Vercel deployment history to promote a previous deployment.
- Backend: redeploy a previous Railway deployment or revert the commit and redeploy.
- Database: use Alembic downgrade only when the migration is known to be reversible and safe.
  Prefer a forward-fix migration when production data may be affected.
