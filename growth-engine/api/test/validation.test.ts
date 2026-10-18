import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deriveChannel, isValidEmail, normalizePhone, normalizeWebsite, validateLeadSubmission } from '../src/validation.ts';

const NOW = 1_800_000_000_000;
const base = {
  purpose: 'inquiry_review', source: 'website_form', name: 'Sam Test', email: 'Sam@Example.ca',
  form_version: '2026-10-12', started_at: NOW - 30_000,
};

test('valid submission is normalized', () => {
  const r = validateLeadSubmission({ ...base, phone: '(519) 555-0100', business_website: 'www.greenacres.example',
    industry: 'landscaping', consents: { follow_up: true, marketing: false } }, NOW);
  assert.ok(r.ok);
  if (!r.ok) return;
  assert.equal(r.value.email, 'sam@example.ca');
  assert.equal(r.value.phone, '15195550100');
  assert.equal(r.value.businessWebsite, 'https://www.greenacres.example/');
  assert.deepEqual(r.value.consents.map((c) => [c.purpose, c.granted]), [['follow_up', true], ['marketing', false]]);
  // Wording comes from the server's copy, never from the browser.
  assert.match(r.value.consents[0].wording, /^Stellan can follow up with me/);
});

test('browser-supplied consent wording is ignored', () => {
  const r = validateLeadSubmission({ ...base, consents: { marketing: true }, consent_wording: 'I agree to anything' }, NOW);
  assert.ok(r.ok);
  if (r.ok) assert.match(r.value.consents[0].wording, /FlowPilot Automation by email/);
});

test('unticked boxes are recorded as declined; options not shown are not recorded', () => {
  const r = validateLeadSubmission({ ...base, consents: { marketing: false } }, NOW);
  assert.ok(r.ok);
  if (r.ok) assert.deepEqual(r.value.consents.map((c) => [c.purpose, c.granted]), [['marketing', false]]);
});

test('demo form records the single demo-email request and nothing else', () => {
  const r = validateLeadSubmission({ ...base, purpose: 'demo_reply', source: 'demo_form' }, NOW);
  assert.ok(r.ok);
  if (r.ok) assert.deepEqual(r.value.consents.map((c) => [c.purpose, c.granted]), [['demo_email', true]]);
});

test('required fields and bad values produce field errors', () => {
  const r = validateLeadSubmission({ purpose: 'buy_stuff', source: 'x', email: 'not-an-email', phone: '12',
    business_website: 'javascript:alert(1)', form_version: 'old', consents: { demo_email: true, whatever: true } }, NOW);
  assert.equal(r.ok, false);
  if (r.ok || !('errors' in r)) return;
  for (const k of ['purpose', 'source', 'name', 'email', 'phone', 'business_website', 'form_version', 'consents.demo_email', 'consents.whatever']) {
    assert.ok(r.errors[k], `expected error for ${k}`);
  }
});

test('oversized fields are rejected', () => {
  const r = validateLeadSubmission({ ...base, message: 'x'.repeat(2001), name: 'n'.repeat(101) }, NOW);
  assert.equal(r.ok, false);
  if (!r.ok && 'errors' in r) {
    assert.ok(r.errors.message);
    assert.ok(r.errors.name);
  }
});

test('sms consent without a phone number is rejected', () => {
  const r = validateLeadSubmission({ ...base, consents: { sms_updates: true } }, NOW);
  assert.equal(r.ok, false);
});

test('honeypot and too-fast submissions are flagged as bots', () => {
  assert.deepEqual(validateLeadSubmission({ ...base, website_confirm: 'http://spam' }, NOW), { ok: false, bot: true });
  assert.deepEqual(validateLeadSubmission({ ...base, started_at: NOW - 500 }, NOW), { ok: false, bot: true });
});

test('control characters are stripped and unknown industries become "other"', () => {
  const r = validateLeadSubmission({ ...base, name: 'Sam\u0000 Test\u0007', industry: 'crypto mining' }, NOW);
  assert.ok(r.ok);
  if (r.ok) {
    assert.equal(r.value.name, 'Sam  Test');
    assert.equal(r.value.industry, 'other');
  }
});

test('helpers', () => {
  assert.ok(isValidEmail('a.b+c@example.co.uk'));
  for (const bad of ['a@b', 'a..b@example.com', '.a@example.com', 'a@exa mple.com', 'a@@example.com']) assert.ok(!isValidEmail(bad), bad);
  assert.equal(normalizePhone('+1 (519) 555-0100'), '15195550100');
  assert.equal(normalizePhone('555-0100'), null);
  assert.equal(normalizeWebsite('http://user:pw@example.com'), null);
  assert.equal(normalizeWebsite('ftp://example.com'), null);
  assert.equal(normalizeWebsite('localhost'), null);
});

test('deriveChannel', () => {
  const d = (o: Partial<{ utm: Record<string, string>; referralCode: string | null; referrerDomain: string | null }>) =>
    deriveChannel({ utm: {}, referralCode: null, referrerDomain: null, ...o }, ['flowpilot-rob9iwxx.manus.space']);
  assert.equal(d({}), 'direct');
  assert.equal(d({ referrerDomain: 'google.ca' }), 'organic_search');
  assert.equal(d({ referrerDomain: 'm.facebook.com' }), 'social');
  assert.equal(d({ referrerDomain: 'somebusiness.ca' }), 'referral');
  assert.equal(d({ referrerDomain: 'flowpilot-rob9iwxx.manus.space' }), 'direct');
  assert.equal(d({ utm: { medium: 'cpc' } }), 'paid');
  assert.equal(d({ utm: { medium: 'email' } }), 'email');
  assert.equal(d({ referralCode: 'pixel-web' }), 'referral_partner');
});
