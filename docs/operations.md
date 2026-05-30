# Operations Runbook

This runbook covers day-two operations for GasBot after the owner deploys the
production stack.

## View Logs

### Railway Backend

1. Open the Railway project and select the backend service.
2. Use the Deployments tab for deploy logs and the Logs tab for live runtime logs.
3. Filter by request ID when debugging API issues. Responses include `X-Request-ID`.
4. Check `/health` for basic liveness and `/health/detailed` for database, Redis, and LLM status.

### Vercel Frontend

1. Open the Vercel project and inspect the latest deployment.
2. Use Build Logs for failed builds and Function Logs for runtime SSR/proxy failures.
3. Confirm `NEXT_PUBLIC_API_URL` points to the Railway backend URL.

### Supabase Database

1. Use Supabase Dashboard > Logs > Postgres for query and connection errors.
2. Use Supabase Dashboard > Database > Replication/Backups for recovery state.
3. Use SQL editor for read-only investigation. Avoid manual writes during incidents unless approved.

## Debug Production Issues

- **Sentry:** backend errors are captured when `SENTRY_DSN` is set and `ENVIRONMENT=production`.
  Start with the exception stack, request path, release/deployment time, and request ID.
- **Health checks:** call `/health/detailed` from a trusted terminal. `database=error` points to
  Supabase credentials/networking; `redis=error` points to Railway Redis URL or service health.
- **Langfuse:** LLM traces are recorded when `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are
  set. Use traces to inspect prompt, provider latency, and token usage.
- **Railway metrics:** inspect CPU/memory spikes before changing code. Embedding model cold starts
  can temporarily increase memory.
- **Database:** use `EXPLAIN ANALYZE` for slow SQL found in logs. Do not add indexes manually in
  production; create migrations.

## Scale Services

- **Railway backend:** increase CPU/memory first for model-loading or connection pressure. Add
  replicas only after confirming the app is stateless and Redis/database connection limits can
  support it.
- **Vercel frontend:** Vercel scales automatically for static and server-rendered routes. Check
  build output and edge/function logs before changing plan limits.
- **Supabase:** monitor CPU, RAM, disk, active connections, and slow queries. Upgrade the database
  plan before connection saturation affects checkout or chat.
- **Redis:** watch memory and eviction metrics. Increase capacity if rate-limit/session keys are
  evicted unexpectedly.

## Backup And Restore

### Supabase PITR

Use Supabase point-in-time recovery for production-impacting data loss when available on the
project plan. Record the target timestamp in UTC and announce expected downtime before restore.

### Manual Dump

```bash
pg_dump "$DATABASE_URL" --format=custom --file=gasbot-$(date +%Y%m%d-%H%M%S).dump
```

Store dumps in an encrypted location. Never commit dumps to the repository.

### Manual Restore

```bash
pg_restore --clean --if-exists --no-owner --dbname "$DATABASE_URL" gasbot-YYYYMMDD-HHMMSS.dump
```

Restore to staging first when possible. For production, pause writes, restore, run smoke tests, and
then re-enable traffic.

## Incident Response

1. **Triage:** identify affected surface: frontend, backend, database, Redis, LLM provider, or
   observability.
2. **Stabilize:** if deploy-related, rollback frontend via Vercel deployment history or backend via
   Railway previous deployment.
3. **Communicate:** record start time, impact, suspected cause, and owner actions.
4. **Database changes:** downgrade migrations only when the downgrade path is known safe and data
   loss has been assessed. Prefer forward-fix migrations for non-critical issues.
5. **Verify:** run `/health`, checkout smoke test, chat smoke test, and admin login after recovery.
6. **Follow up:** write a short post-incident note with root cause, detection gap, and prevention.
