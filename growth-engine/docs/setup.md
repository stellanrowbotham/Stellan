# Setup, deployment, backups

## Local development and tests (no accounts needed)

Needs PostgreSQL 15+ and Node 22.18+.

```bash
# SQL: build a throwaway database from the migrations and run the 6 SQL test suites
growth-engine/scripts/db-local.sh test          # (run as a Postgres superuser, e.g. `sudo -u postgres`)

# API: unit tests
cd growth-engine/api && npm install && npm test

# API: unit + HTTP end-to-end against the local database
TEST_DATABASE_URL=postgres://growth_api_test:local-test-only@127.0.0.1:5432/growth_engine_test \
TEST_ADMIN_DATABASE_URL=postgres://postgres:<pw>@127.0.0.1:5432/growth_engine_test npm test
```

`supabase/local/00_supabase_shim.sql` fakes the bits of Supabase the schema needs (roles, `auth.uid()`).
It runs locally only.

## Production

### 1. Supabase project
1. Create a project at supabase.com. Region: **Canada (Central)**. Save the database password in a password manager.
2. Settings → API → Exposed schemas: leave `growth` **out** (the dashboard phase revisits this).

### 2. Apply the migrations
Either the Supabase CLI (`supabase link --project-ref <ref>` then `supabase db push`), or psql:
```bash
for f in growth-engine/supabase/migrations/*.sql; do psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$f"; done
```
Never run `supabase/local/00_supabase_shim.sql` against Supabase.

### 3. Create the least-privileged login users
In the SQL editor (generate each password with `openssl rand -base64 32`):
```sql
create role growth_api login password '<generated>' in role growth_intake;  -- the public API
create role growth_n8n login password '<generated>' in role growth_worker;  -- n8n (Phase 4+)
insert into growth.app_users (user_id, email, role)                       -- after you sign up in Auth
  select id, email, 'owner' from auth.users where email = 'stellanrowbotham@gmail.com';
```
The API's `DATABASE_URL` uses `growth_api`. Port 5432 is the direct connection, and the 6543 pooler also
works (prepared statements are turned off automatically).

### 4. Deploy the API
**Option A, Supabase Edge Function (recommended, no extra host):**
```bash
growth-engine/scripts/build-edge.sh
cd growth-engine
supabase secrets set DATABASE_URL=... ALLOWED_ORIGINS=https://flowpilot-rob9iwxx.manus.space \
  OWN_DOMAINS=flowpilot-rob9iwxx.manus.space IP_HASH_SALT=$(openssl rand -base64 48) \
  UNSUBSCRIBE_SECRET=$(openssl rand -base64 48)
supabase functions deploy growth-api --no-verify-jwt
curl https://<ref>.supabase.co/functions/v1/growth-api/health   # → {"ok":true,"db":true}
```
**Option B, any Node 22.18+ host:** `cd api && npm ci && npm start`, with the variables from `api/.env.example`
and `TRUST_PROXY=true` behind a load balancer.

Store `UNSUBSCRIBE_SECRET` in n8n too (Phase 5 signs unsubscribe links with it). Rotating it breaks
links already sent, so rotate only if it leaks.

### 5. Connect the website
Follow [`website/manus-integration.md`](../website/manus-integration.md).

### 6. Retention
On Supabase, enable `pg_cron` and schedule the daily cleanup:
```sql
select cron.schedule('growth-retention', '17 3 * * *', $$select growth.apply_retention()$$);
```
(Or WF-09 calls `growth.apply_retention()` daily.) Policies live in `growth.retention_policies`.

## Backups and recovery
- **Supabase backups:** daily backups on Pro (7 days). Point-in-time recovery is an add-on. On the free
  plan, take your own: `pg_dump "$SUPABASE_DB_URL" -n growth -Fc -f growth-$(date +%F).dump` weekly, stored
  encrypted off-site (not in this repo).
- **Restore:** `pg_restore -d "$TARGET_DB_URL" --no-owner -n growth growth-YYYY-MM-DD.dump`, then re-run step 3's grants.
- **Consent and suppression** must survive any restore. After restoring an older backup, re-import any
  `suppression_list` rows newer than the backup (export them first with `copy … to stdout`).
- **Test a restore** into a scratch project once a quarter.

## Secrets inventory
| Secret | Lives in | Used by |
|---|---|---|
| Supabase DB password (postgres) | Password manager | Migrations only |
| `growth_api` password → `DATABASE_URL` | Supabase function secrets / host env | growth-api |
| `growth_n8n` password | n8n credential "Growth DB" | WF-01…09 |
| `IP_HASH_SALT`, `UNSUBSCRIBE_SECRET` | Supabase secrets (and n8n for the second) | growth-api, WF-05/06 |
| LLM, search, email, scheduling keys | n8n credentials | workflows |
