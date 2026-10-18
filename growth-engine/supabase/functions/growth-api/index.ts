// Supabase Edge Function adapter (Deno). Build first: scripts/build-edge.sh copies api/src into ./_lib.
// Deploy: supabase functions deploy growth-api --no-verify-jwt   (it's a public endpoint; it does its own checks)
// Secrets: supabase secrets set DATABASE_URL=... ALLOWED_ORIGINS=... IP_HASH_SALT=... UNSUBSCRIBE_SECRET=... BASE_PATH=/growth-api
import postgres from 'npm:postgres@3.4.5';
import { createApp } from './_lib/app.ts';
import { loadConfig } from './_lib/config.ts';
import { createPgStore, type SqlClient } from './_lib/store.ts';

const env = Deno.env.toObject();
const config = loadConfig({ BASE_PATH: '/growth-api', ...env });
const sql = postgres(env.DATABASE_URL, {
  max: 3,
  idle_timeout: 20,
  connect_timeout: 10,
  prepare: !env.DATABASE_URL.includes(':6543'),
  connection: { statement_timeout: 8000, application_name: 'growth-api-edge' },
});
const handle = createApp(config, createPgStore(sql as unknown as SqlClient));

Deno.serve((req, info) => {
  // Supabase's edge network sets x-forwarded-for; the first entry is the client. A client can prepend its own
  // value, so the per-IP limit is best-effort; the global hourly limit is the hard cap.
  const forwarded = req.headers.get('x-forwarded-for')?.split(',')[0].trim();
  const remote = (info.remoteAddr as Deno.NetAddr).hostname;
  return handle(req, { clientIp: forwarded || remote || 'unknown' });
});
