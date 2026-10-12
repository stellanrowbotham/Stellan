// FlowPilot Growth Engine public API (web-standard Request → Response).
//   POST /v1/leads         website lead intake (CORS, validated, rate-limited, idempotent)
//   GET  /v1/unsubscribe   confirmation page (GET never changes anything; mail scanners prefetch links)
//   POST /v1/unsubscribe   unsubscribe (the page's button, or RFC 8058 one-click from mail clients)
//   GET  /health           liveness + database reachability
import { deriveChannel, validateLeadSubmission } from './validation.ts';
import { hashIp, sha256Hex, verifyUnsubscribeToken } from './security.ts';
import type { Store } from './store.ts';

export interface AppConfig {
  allowedOrigins: string[];         // e.g. ["https://flowpilot-rob9iwxx.manus.space"]
  ownDomains: string[];             // referrers that count as "direct"
  ipHashSalt: string;
  unsubscribeSecret: string;
  contactEmail: string;
  testMode: boolean;                // marks every lead is_test (staging)
  limits: { perIpPerHour: number; globalPerHour: number; unsubscribePerIpPerHour: number };
  maxBodyBytes: number;
  basePath: string;                 // '' on a normal host; '/growth-api' on Supabase Edge Functions
}

export interface RequestContext {
  clientIp: string;
}

const SECURITY_HEADERS: Record<string, string> = {
  'cache-control': 'no-store',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'x-frame-options': 'DENY',
};

function json(status: number, body: unknown, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...SECURITY_HEADERS, ...extra },
  });
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);
}

function page(status: number, title: string, bodyHtml: string): Response {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>${escapeHtml(title)} | FlowPilot Automation</title>
<style>body{margin:0;background:#0b0b0b;color:#f5efe5;font:16px/1.6 system-ui,-apple-system,"DM Sans",sans-serif;display:grid;place-items:center;min-height:100vh;padding:16px}
main{max-width:480px;background:#171513;border:1px solid #2a2622;border-radius:16px;padding:32px}h1{font-size:1.4rem;margin:0 0 12px}
button{background:#d7b873;color:#11100d;border:0;border-radius:999px;padding:12px 22px;font-weight:600;font-size:1rem;cursor:pointer}a{color:#d7b873}p{color:#cfc7b8}</style>
</head><body><main><h1>${escapeHtml(title)}</h1>${bodyHtml}</main></body></html>`;
  return new Response(html, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'",
      ...SECURITY_HEADERS,
    },
  });
}

async function readBody(req: Request, max: number): Promise<string | null> {
  const declared = Number(req.headers.get('content-length') ?? '0');
  if (declared > max) return null;
  const text = await req.text();
  return new TextEncoder().encode(text).length > max ? null : text;
}

export function createApp(config: AppConfig, store: Store) {
  const corsHeaders = (origin: string | null): Record<string, string> | null => {
    if (!origin || !config.allowedOrigins.includes(origin)) return null;
    return {
      'access-control-allow-origin': origin,
      'access-control-allow-methods': 'POST, OPTIONS',
      'access-control-allow-headers': 'content-type',
      'access-control-max-age': '600',
      vary: 'Origin',
    };
  };

  async function handleLead(req: Request, ctx: RequestContext): Promise<Response> {
    const cors = corsHeaders(req.headers.get('origin'));
    if (!cors) return json(403, { ok: false, error: 'origin_not_allowed' });
    if (!(req.headers.get('content-type') ?? '').toLowerCase().startsWith('application/json')) {
      return json(415, { ok: false, error: 'expected_json' }, cors);
    }
    const text = await readBody(req, config.maxBodyBytes);
    if (text === null) return json(413, { ok: false, error: 'too_large' }, cors);
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      return json(400, { ok: false, errors: { body: 'Invalid JSON.' } }, cors);
    }

    const ipHash = await hashIp(ctx.clientIp, config.ipHashSalt);
    const [ipOk, globalOk] = await Promise.all([
      store.hitRateLimit(`lead:ip:${ipHash}`, config.limits.perIpPerHour, 3600),
      store.hitRateLimit('lead:global', config.limits.globalPerHour, 3600),
    ]);
    if (!ipOk || !globalOk) {
      return json(429, { ok: false, error: 'rate_limited', message: `Too many requests. Please try again later or email ${config.contactEmail}.` },
                  { ...cors, 'retry-after': '3600' });
    }

    const result = validateLeadSubmission(body);
    if (!result.ok) {
      // Bots get the same answer as people, and nothing is stored.
      if ('bot' in result && result.bot) return json(201, { ok: true }, cors);
      return json(400, { ok: false, errors: (result as { errors: Record<string, string> }).errors }, cors);
    }
    const s = result.value;
    const day = new Date().toISOString().slice(0, 10);
    const idempotencyKey = s.submissionId
      ? `sub:${s.submissionId}`
      : `h:${await sha256Hex([s.email, s.purpose, s.source, s.message ?? '', day].join('|'))}`;

    const payload = {
      idempotency_key: idempotencyKey,
      purpose: s.purpose,
      source: s.source,
      source_detail: s.pagePath,
      name: s.name,
      email: s.email,
      phone: s.phone,
      business_name: s.businessName,
      business_website: s.businessWebsite,
      industry: s.industry,
      message: s.message,
      utm: s.utm,
      channel: deriveChannel(s, config.ownDomains),
      referrer_domain: s.referrerDomain,
      anonymous_id: s.anonymousId,
      referral_code: s.referralCode,
      audit_session_id: s.auditSessionId,
      ip_hash: ipHash,
      is_test: config.testMode,
      consents: s.consents,
    };

    try {
      const r = await store.intakeLead(payload);
      return json(r.duplicate ? 200 : 201, { ok: true, duplicate: r.duplicate }, cors);
    } catch (err) {
      // Log the database error code only, never the submission.
      console.error('intake_failed', (err as { code?: string }).code ?? 'unknown');
      return json(500, { ok: false, error: 'server_error', message: `Something went wrong. Please email ${config.contactEmail}.` }, cors);
    }
  }

  async function handleUnsubscribe(req: Request, url: URL, ctx: RequestContext): Promise<Response> {
    const token = url.searchParams.get('t') ?? '';
    const email = await verifyUnsubscribeToken(token, config.unsubscribeSecret);
    if (!email) {
      return page(400, 'Link not recognized',
        `<p>This unsubscribe link is incomplete or has been changed. Reply to the email with “unsubscribe”, or write to
         <a href="mailto:${escapeHtml(config.contactEmail)}">${escapeHtml(config.contactEmail)}</a>, and you’ll be removed right away.</p>`);
    }
    if (req.method === 'GET') {
      return page(200, 'Unsubscribe from FlowPilot emails',
        `<p>Stop all follow-up and marketing emails from FlowPilot Automation to <strong>${escapeHtml(email)}</strong>?</p>
         <form method="post" action="${escapeHtml(url.pathname)}?t=${encodeURIComponent(token)}"><button type="submit">Unsubscribe</button></form>`);
    }
    const ipHash = await hashIp(ctx.clientIp, config.ipHashSalt);
    if (!(await store.hitRateLimit(`unsub:ip:${ipHash}`, config.limits.unsubscribePerIpPerHour, 3600))) {
      return page(429, 'Please try again shortly', `<p>Too many requests from your network. Try again in an hour, or email ${escapeHtml(config.contactEmail)}.</p>`);
    }
    try {
      await store.processUnsubscribe(email, null, 'unsubscribe_link');
    } catch (err) {
      console.error('unsubscribe_failed', (err as { code?: string }).code ?? 'unknown');
      return page(500, 'Something went wrong',
        `<p>Your request didn’t go through. Please email <a href="mailto:${escapeHtml(config.contactEmail)}">${escapeHtml(config.contactEmail)}</a> with “unsubscribe” and you’ll be removed right away.</p>`);
    }
    return page(200, 'You’re unsubscribed',
      `<p>${escapeHtml(email)} won’t get any more follow-up or marketing emails from FlowPilot Automation. This took effect immediately.</p>`);
  }

  return async function handle(req: Request, ctx: RequestContext): Promise<Response> {
    const url = new URL(req.url);
    let path = url.pathname.replace(/\/+$/, '') || '/';
    if (config.basePath && path.startsWith(config.basePath)) path = path.slice(config.basePath.length) || '/';

    if (req.method === 'OPTIONS' && path === '/v1/leads') {
      const cors = corsHeaders(req.headers.get('origin'));
      return cors ? new Response(null, { status: 204, headers: cors }) : new Response(null, { status: 403 });
    }
    if (path === '/v1/leads' && req.method === 'POST') return handleLead(req, ctx);
    if (path === '/v1/unsubscribe' && (req.method === 'GET' || req.method === 'POST')) return handleUnsubscribe(req, url, ctx);
    if (path === '/health' && req.method === 'GET') return json(200, { ok: true, db: await store.ping() });
    return json(404, { ok: false, error: 'not_found' });
  };
}
