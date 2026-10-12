// Small crypto helpers. Uses Web Crypto so it runs on Node 22+, Deno (Supabase Edge Functions) and Workers.

const enc = new TextEncoder();

function b64url(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function fromB64url(s: string): Uint8Array | null {
  if (!/^[A-Za-z0-9_-]*$/.test(s)) return null;
  try {
    const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (s.length % 4)) % 4));
    return Uint8Array.from(bin, (c) => c.charCodeAt(0));
  } catch {
    return null;
  }
}

async function hmac(secret: string, data: string): Promise<Uint8Array> {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(data)));
}

function constantTimeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

export async function sha256Hex(data: string): Promise<string> {
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(data)));
  return Array.from(digest, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Salted, keyed hash of a client IP: lets us rate-limit without storing the address. */
export async function hashIp(ip: string, salt: string): Promise<string> {
  return b64url(await hmac(salt, `ip:${ip}`)).slice(0, 32);
}

/**
 * Unsubscribe token: base64url(email) + "." + HMAC. It doesn't expire, so a link in an old email
 * keeps working (CASL requires at least 60 days).
 */
export async function signUnsubscribeToken(email: string, secret: string): Promise<string> {
  const e = email.trim().toLowerCase();
  return `${b64url(enc.encode(e))}.${b64url(await hmac(secret, `unsub:${e}`))}`;
}

export async function verifyUnsubscribeToken(token: string, secret: string): Promise<string | null> {
  if (typeof token !== 'string' || token.length > 600) return null;
  const [p, sig] = token.split('.');
  if (!p || !sig) return null;
  const emailBytes = fromB64url(p);
  const sigBytes = fromB64url(sig);
  if (!emailBytes || !sigBytes) return null;
  // Reject non-canonical encodings (base64 has spare bits; two strings can decode to the same bytes).
  if (b64url(emailBytes) !== p || b64url(sigBytes) !== sig) return null;
  const email = new TextDecoder().decode(emailBytes);
  const expected = await hmac(secret, `unsub:${email}`);
  return constantTimeEqual(sigBytes, expected) ? email : null;
}
