# Deployment

GasBot Vietnam deploys to Vercel, Railway, and Supabase.

## Targets

- Frontend: Vercel
- Backend: Railway
- Database: Supabase PostgreSQL
- LLM provider: Gemini Flash in production

## Required GitHub Secrets

| Secret | Purpose | Where to get it |
| --- | --- | --- |
| `VERCEL_TOKEN` | Deploy frontend from GitHub Actions | Vercel account settings |
| `VERCEL_ORG_ID` | Vercel organization identifier | Vercel project settings |
| `VERCEL_PROJECT_ID` | Vercel project identifier | Vercel project settings |
| `RAILWAY_TOKEN` | Deploy backend from GitHub Actions | Railway account settings |

## Vercel Setup

1. Create a Vercel project from the GitHub repository.
2. Set the root directory to `frontend`.
3. Set required environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. Confirm the region is `sin1`.
5. Run a production deployment.

## Railway Setup

1. Create a Railway service from the GitHub repository.
2. Set the root directory to `backend`.
3. Configure the Dockerfile builder using `backend/railway.json`.
4. Set backend environment variables from `.env.example`.
5. Confirm `/health` returns `200`.

## Supabase Setup

1. Create a Supabase PostgreSQL project.
2. Enable `uuid-ossp`, `vector`, and `pg_trgm` extensions through migrations.
3. Set `DATABASE_URL` in Railway.
4. Run `alembic upgrade head`.
5. Load seed data only for demo or staging environments.

## Rollback

- Frontend: use Vercel deployment history to promote a previous deployment.
- Backend: redeploy a previous Railway deployment or revert the commit and redeploy.
- Database: use Alembic downgrade only when the migration is known to be reversible and safe.
