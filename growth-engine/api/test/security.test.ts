import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hashIp, signUnsubscribeToken, verifyUnsubscribeToken } from '../src/security.ts';

const SECRET = 'test-secret-that-is-at-least-32-characters';

test('unsubscribe token round-trips and is case-insensitive on email', async () => {
  const t = await signUnsubscribeToken('Sam@Example.ca', SECRET);
  assert.equal(await verifyUnsubscribeToken(t, SECRET), 'sam@example.ca');
});

test('tampered, re-targeted or foreign-secret tokens fail', async () => {
  const t = await signUnsubscribeToken('sam@example.ca', SECRET);
  const [, sig] = t.split('.');
  const other = Buffer.from('victim@example.ca').toString('base64url');
  assert.equal(await verifyUnsubscribeToken(`${other}.${sig}`, SECRET), null);
  assert.equal(await verifyUnsubscribeToken(t, SECRET + 'x'), null);
  assert.equal(await verifyUnsubscribeToken(t.slice(0, -2), SECRET), null);
  assert.equal(await verifyUnsubscribeToken('garbage', SECRET), null);
  assert.equal(await verifyUnsubscribeToken('a.b.c!', SECRET), null);
  // Same bytes, non-canonical last character → rejected.
  const last = sig.at(-1)!;
  const alt = 'AEIMQUYcgkosw048'.includes(last) ? String.fromCharCode(last.charCodeAt(0) + 1) : last;
  if (alt !== last) assert.equal(await verifyUnsubscribeToken(t.slice(0, -1) + alt, SECRET), null);
});

test('ip hash is stable, salted, and not the ip', async () => {
  const a = await hashIp('203.0.113.7', 'salt-one-salt-one-salt-one-salt-one');
  assert.equal(a, await hashIp('203.0.113.7', 'salt-one-salt-one-salt-one-salt-one'));
  assert.notEqual(a, await hashIp('203.0.113.7', 'salt-two-salt-two-salt-two-salt-two'));
  assert.ok(!a.includes('203'));
});
