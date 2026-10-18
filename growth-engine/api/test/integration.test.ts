// End-to-end: starts the real Node server against a local database (scripts/db-local.sh reset), sends
// HTTP requests like the website would, and checks the database as an admin.
// Skips unless TEST_DATABASE_URL (API user) and TEST_ADMIN_DATABASE_URL are set.
import { after, before, describe, test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import postgres from 'postgres';
import { signUnsubscribeToken } from '../src/security.ts';

const API_DB = process.env.TEST_DATABASE_URL;
const ADMIN_DB = process.env.TEST_ADMIN_DATABASE_URL;
const ORIGIN = 'https://flowpilot-rob9iwxx.manus.space';
const PORT = 18787;
const BASE = `http://127.0.0.1:${PORT}`;
const UNSUB_SECRET = 'integration-unsubscribe-secret-0123456789';

describe('growth-api over HTTP', { skip: !API_DB || !ADMIN_DB ? 'set TEST_DATABASE_URL and TEST_ADMIN_DATABASE_URL' : false }, () => {
  let server: ChildProcess;
  let admin: ReturnType<typeof postgres>;
  const runId = randomUUID().slice(0, 8);
  const email = (tag: string) => `${tag}-${runId}@example.com`;

  const submit = (body: Record<string, unknown>, headers: Record<string, string> = {}) =>
    fetch(`${BASE}/v1/leads`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', origin: ORIGIN, 'x-forwarded-for': `198.51.100.${Math.floor(Math.random() * 250)}`, ...headers },
      body: JSON.stringify(body),
    });

  const lead = (tag: string, extra: Record<string, unknown> = {}) => ({
    submission_id: randomUUID(), purpose: 'inquiry_review', source: 'website_form', name: 'Integration Test',
    email: email(tag), form_version: '2026-10-12', started_at: Date.now() - 20_000, page_path: '/', ...extra,
  });

  before(async () => {
    admin = postgres(ADMIN_DB!, { max: 2, onnotice: () => {} });
    server = spawn(process.execPath, ['src/server.ts'], {
      env: {
        ...process.env, PORT: String(PORT), DATABASE_URL: API_DB, ALLOWED_ORIGINS: ORIGIN,
        OWN_DOMAINS: 'flowpilot-rob9iwxx.manus.space', IP_HASH_SALT: 'integration-salt-0123456789-0123456789',
        UNSUBSCRIBE_SECRET: UNSUB_SECRET, TRUST_PROXY: 'true', GROWTH_TEST_MODE: 'true',
        LEAD_LIMIT_PER_IP_PER_HOUR: '3',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('server did not start')), 10_000);
      server.stdout!.on('data', (d) => { if (String(d).includes('listening')) { clearTimeout(timer); resolve(); } });
      server.stderr!.on('data', (d) => process.stderr.write(d));
      server.on('exit', (code) => reject(new Error(`server exited ${code}`)));
    });
  });

  after(async () => {
    server?.kill('SIGTERM');
    await admin?.end();
  });

  test('health reports the database', async () => {
    const r = await fetch(`${BASE}/health`);
    assert.deepEqual(await r.json(), { ok: true, db: true });
  });

  test('a website submission reaches the CRM with exact consent choices', async () => {
    const body = lead('crm', { phone: '519-555-0142', business_name: 'Maple Test HVAC', business_website: 'maple-test.example',
      industry: 'hvac', message: 'Missed calls on jobs', consents: { follow_up: true, marketing: false },
      utm: { source: 'google', medium: 'organic' }, referrer: 'https://www.google.ca/' });
    const r = await submit(body);
    assert.equal(r.status, 201);
    assert.equal(r.headers.get('access-control-allow-origin'), ORIGIN);
    assert.deepEqual(await r.json(), { ok: true, duplicate: false });

    const [row] = await admin`
      select l.id, l.stage, l.purpose, l.source, l.is_test, l.ip_hash, c.email_normalized, c.phone_normalized, b.normalized_domain
        from growth.leads l join growth.contacts c on c.id = l.contact_id left join growth.businesses b on b.id = l.business_id
       where l.idempotency_key = ${'sub:' + body.submission_id}`;
    assert.equal(row.stage, 'new');
    assert.equal(row.email_normalized, email('crm'));
    assert.equal(row.phone_normalized, '15195550142');
    assert.equal(row.normalized_domain, 'maple-test.example');
    assert.equal(row.is_test, true);
    assert.ok(row.ip_hash && !String(row.ip_hash).includes('198.51'), 'ip stored only as a hash');

    const consents = await admin`select purpose, basis, granted, wording_shown, form_version from growth.consent_records
                                  where lead_id = ${row.id} order by purpose`;
    assert.deepEqual(consents.map((c) => [c.purpose, c.basis, c.granted]), [
      ['follow_up', 'express', true], ['marketing', 'express', false], ['request_response', 'exempt_response', true]]);
    assert.match(consents[0].wording_shown, /^Stellan can follow up/);

    const [ev] = await admin`select channel from growth.analytics_events where lead_id = ${row.id}`;
    assert.equal(ev.channel, 'organic_search');
    const [ob] = await admin`select topic, status from growth.event_outbox where dedupe_key = ${'lead.created:' + row.id}`;
    assert.deepEqual({ ...ob }, { topic: 'lead.created', status: 'pending' });
  });

  test('a retried submission does not create a duplicate', async () => {
    const body = lead('dup');
    assert.equal((await submit(body)).status, 201);
    const again = await submit(body);
    assert.equal(again.status, 200);
    assert.deepEqual(await again.json(), { ok: true, duplicate: true });
    const [{ n }] = await admin`select count(*)::int as n from growth.leads where idempotency_key = ${'sub:' + body.submission_id}`;
    assert.equal(n, 1);
  });

  test('origin, content type, size and validation are enforced', async () => {
    assert.equal((await submit(lead('o'), { origin: 'https://evil.example' })).status, 403);
    const noJson = await fetch(`${BASE}/v1/leads`, { method: 'POST', headers: { origin: ORIGIN, 'content-type': 'text/plain' }, body: 'x' });
    assert.equal(noJson.status, 415);
    assert.equal((await submit({ ...lead('big'), message: 'x'.repeat(20_000) })).status, 413);
    const bad = await submit({ ...lead('bad'), email: 'nope' });
    assert.equal(bad.status, 400);
    assert.ok((await bad.json()).errors.email);
    const pre = await fetch(`${BASE}/v1/leads`, { method: 'OPTIONS', headers: { origin: ORIGIN } });
    assert.equal(pre.status, 204);
  });

  test('bots get a normal answer and nothing is stored', async () => {
    const body = lead('bot', { website_confirm: 'http://spam.example' });
    const r = await submit(body);
    assert.equal(r.status, 201);
    const [{ n }] = await admin`select count(*)::int as n from growth.contacts where email_normalized = ${email('bot')}`;
    assert.equal(n, 0);
  });

  test('rate limit per IP', async () => {
    const ip = { 'x-forwarded-for': '192.0.2.77' };
    const statuses = [];
    for (let i = 0; i < 4; i++) statuses.push((await submit(lead(`rl${i}`), ip)).status);
    assert.deepEqual(statuses, [201, 201, 201, 429]);
  });

  test('unsubscribe: GET changes nothing, POST suppresses and cancels pending messages', async () => {
    const addr = email('unsub');
    assert.equal((await submit(lead('unsub', { consents: { follow_up: true } }))).status, 201);
    const [l] = await admin`select l.id from growth.leads l join growth.contacts c on c.id = l.contact_id where c.email_normalized = ${addr}`;
    await admin`insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
                values ('email', 'follow_up', ${addr}, ${l.id}, 'Hi {{sender_identification}} {{unsubscribe_url}}', 'agent:WF-06',
                        'pending_approval', ${'it-' + runId})`;

    const token = await signUnsubscribeToken(addr, UNSUB_SECRET);
    const view = await fetch(`${BASE}/v1/unsubscribe?t=${encodeURIComponent(token)}`);
    assert.equal(view.status, 200);
    assert.match(await view.text(), /<form method="post"/);
    const [{ s1 }] = await admin`select growth.is_suppressed(${addr}) as s1`;
    assert.equal(s1, false, 'GET must not unsubscribe (mail scanners prefetch links)');

    const done = await fetch(`${BASE}/v1/unsubscribe?t=${encodeURIComponent(token)}`, { method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: 'List-Unsubscribe=One-Click' });
    assert.equal(done.status, 200);
    const [{ s2 }] = await admin`select growth.is_suppressed(${addr}) as s2`;
    assert.equal(s2, true);
    const [m] = await admin`select status from growth.outbound_messages where idempotency_key = ${'it-' + runId}`;
    assert.equal(m.status, 'cancelled');

    const [e, sig] = token.split('.');
    const flipped = sig.slice(0, 10) + (sig[10] === 'A' ? 'B' : 'A') + sig.slice(11);
    const forged = await fetch(`${BASE}/v1/unsubscribe?t=${encodeURIComponent(`${e}.${flipped}`)}`, { method: 'POST' });
    assert.equal(forged.status, 400);
  });

  test('a suppressed person can still ask for help; the lead is flagged for a human', async () => {
    const addr = email('unsub');
    assert.equal((await submit(lead('unsub-again', { email: addr }))).status, 201);
    const [l] = await admin`select needs_human from growth.leads l join growth.contacts c on c.id = l.contact_id
                             where c.email_normalized = ${addr} order by l.created_at desc limit 1`;
    assert.equal(l.needs_human, true);
  });
});
