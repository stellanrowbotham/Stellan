// Reads configuration from environment variables. Secrets never have defaults: the process refuses to
// start without them, so a misconfigured deploy fails loudly instead of running insecurely.
import type { AppConfig } from './app.ts';

export function loadConfig(env: Record<string, string | undefined>): AppConfig {
  const missing: string[] = [];
  const required = (key: string, minLength = 1): string => {
    const v = env[key];
    if (!v || v.length < minLength) missing.push(minLength > 1 ? `${key} (at least ${minLength} chars)` : key);
    return v ?? '';
  };
  const list = (key: string): string[] =>
    (env[key] ?? '').split(',').map((s) => s.trim()).filter(Boolean);
  const int = (key: string, fallback: number): number => {
    const n = Number(env[key]);
    return Number.isInteger(n) && n > 0 ? n : fallback;
  };

  const config: AppConfig = {
    allowedOrigins: list('ALLOWED_ORIGINS'),
    ownDomains: list('OWN_DOMAINS'),
    ipHashSalt: required('IP_HASH_SALT', 32),
    unsubscribeSecret: required('UNSUBSCRIBE_SECRET', 32),
    contactEmail: env.CONTACT_EMAIL ?? 'stellanrowbotham@gmail.com',
    testMode: env.GROWTH_TEST_MODE === 'true',
    limits: {
      perIpPerHour: int('LEAD_LIMIT_PER_IP_PER_HOUR', 5),
      globalPerHour: int('LEAD_LIMIT_GLOBAL_PER_HOUR', 200),
      unsubscribePerIpPerHour: int('UNSUBSCRIBE_LIMIT_PER_IP_PER_HOUR', 30),
    },
    maxBodyBytes: int('MAX_BODY_BYTES', 16_384),
    basePath: (env.BASE_PATH ?? '').replace(/\/+$/, ''),
  };
  if (!env.DATABASE_URL) missing.push('DATABASE_URL');
  if (config.allowedOrigins.length === 0) missing.push('ALLOWED_ORIGINS');
  for (const o of config.allowedOrigins) {
    if (!/^https?:\/\/[^/]+$/.test(o)) throw new Error(`ALLOWED_ORIGINS entry "${o}" must be an origin like https://example.ca`);
  }
  if (missing.length) throw new Error(`Missing or invalid configuration: ${missing.join(', ')}`);
  return config;
}
