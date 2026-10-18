// Node adapter: `node src/server.ts` (Node 22.18+ runs TypeScript directly). Deploys to any Node host
// (Render, Railway, Fly.io, a VPS). For Supabase Edge Functions use supabase/functions/growth-api instead.
import { createServer } from 'node:http';
import postgres from 'postgres';
import { createApp } from './app.ts';
import { loadConfig } from './config.ts';
import { createPgStore, type SqlClient } from './store.ts';

const config = loadConfig(process.env);
const sql = postgres(process.env.DATABASE_URL!, {
  max: Number(process.env.DB_POOL_MAX ?? 5),
  idle_timeout: 20,
  connect_timeout: 10,
  connection: { statement_timeout: 8000, application_name: 'growth-api' },
  // Supabase's transaction pooler (port 6543) doesn't support prepared statements.
  prepare: !(process.env.DATABASE_URL ?? '').includes(':6543'),
});
const handle = createApp(config, createPgStore(sql as unknown as SqlClient));
const trustProxy = process.env.TRUST_PROXY === 'true';
const port = Number(process.env.PORT ?? 8787);

const server = createServer(async (req, res) => {
  try {
    const chunks: Buffer[] = [];
    let size = 0;
    for await (const chunk of req) {
      size += chunk.length;
      if (size > config.maxBodyBytes) {
        res.writeHead(413, { 'content-type': 'application/json' }).end('{"ok":false,"error":"too_large"}');
        return;
      }
      chunks.push(chunk);
    }
    const forwarded = trustProxy ? String(req.headers['x-forwarded-for'] ?? '').split(',')[0].trim() : '';
    const clientIp = forwarded || req.socket.remoteAddress || 'unknown';
    const headers = new Headers();
    for (const [k, v] of Object.entries(req.headers)) if (typeof v === 'string') headers.set(k, v);
    const method = req.method ?? 'GET';
    const request = new Request(`http://${req.headers.host ?? 'localhost'}${req.url ?? '/'}`, {
      method,
      headers,
      body: method === 'GET' || method === 'HEAD' ? undefined : Buffer.concat(chunks),
    });
    const response = await handle(request, { clientIp });
    res.writeHead(response.status, Object.fromEntries(response.headers));
    res.end(Buffer.from(await response.arrayBuffer()));
  } catch (err) {
    console.error('unhandled', (err as Error).name);
    if (!res.headersSent) res.writeHead(500, { 'content-type': 'application/json' });
    res.end('{"ok":false,"error":"server_error"}');
  }
});

server.requestTimeout = 15_000;
server.headersTimeout = 10_000;
server.listen(port, () => console.log(`growth-api listening on :${port}${config.testMode ? ' (TEST MODE)' : ''}`));

for (const sig of ['SIGTERM', 'SIGINT'] as const) {
  process.on(sig, () => server.close(() => sql.end({ timeout: 5 }).then(() => process.exit(0))));
}
