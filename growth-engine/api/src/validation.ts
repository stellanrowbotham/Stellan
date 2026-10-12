// Input validation for public submissions. Pure functions, no I/O.
import { CONSENT_COPY, type ConsentPurpose } from './consent-copy.ts';

export const PURPOSES = ['inquiry_review', 'audit_report', 'demo_reply', 'consultation', 'general_inquiry', 'partnership'] as const;
export const PUBLIC_SOURCES = ['website_form', 'inquiry_check', 'demo_form', 'request_page'] as const;
export const INDUSTRIES = [
  'landscaping', 'lawn_care', 'snow_removal', 'hvac', 'plumbing', 'electrical', 'roofing', 'general_contractor',
  'renovation', 'painting', 'flooring', 'fencing_decks', 'pest_control', 'cleaning', 'pool_spa', 'garage_doors',
  'windows_doors', 'moving', 'junk_removal', 'pressure_washing', 'tree_service', 'other_home_service', 'other',
] as const;
const UTM_KEYS = ['source', 'medium', 'campaign', 'term', 'content'] as const;

export type Purpose = (typeof PURPOSES)[number];
export type PublicSource = (typeof PUBLIC_SOURCES)[number];

export interface ConsentChoice {
  channel: 'email' | 'sms';
  purpose: ConsentPurpose;
  granted: boolean;
  wording: string;
  form_id: string;
  form_version: string;
  source_url: string | null;
}

export interface LeadSubmission {
  submissionId: string | null;
  purpose: Purpose;
  source: PublicSource;
  name: string;
  email: string;
  phone: string | null;
  businessName: string | null;
  businessWebsite: string | null;
  industry: string | null;
  message: string | null;
  utm: Partial<Record<(typeof UTM_KEYS)[number], string>>;
  pagePath: string | null;
  referrerDomain: string | null;
  anonymousId: string | null;
  referralCode: string | null;
  auditSessionId: string | null;
  formVersion: string;
  consents: ConsentChoice[];
}

export type ValidationResult =
  | { ok: true; value: LeadSubmission }
  | { ok: false; bot: true }
  | { ok: false; bot?: false; errors: Record<string, string> };

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
// Deliberately practical: one @, no spaces, a dot in the domain, no leading/trailing/double dots.
const EMAIL_RE = /^(?!\.)(?!.*\.\.)[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}(?<!\.)@(?=.{4,253}$)([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$/;

/** Trim, drop control characters, collapse to null when empty, enforce a max length. */
export function cleanText(v: unknown, max: number, opts: { multiline?: boolean } = {}): string | null | undefined {
  if (v === undefined || v === null) return null;
  if (typeof v !== 'string') return undefined; // wrong type
  const stripped = opts.multiline
    ? v.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').replace(/\r\n?/g, '\n')
    : v.replace(/[\u0000-\u001F\u007F]/g, ' ');
  const t = stripped.trim();
  if (t === '') return null;
  if (t.length > max) return undefined;
  return t;
}

export function normalizeEmail(v: string): string {
  return v.trim().toLowerCase();
}

export function isValidEmail(v: string): boolean {
  return v.length <= 254 && EMAIL_RE.test(v);
}

/** 10-digit NANP numbers become 1XXXXXXXXXX; 11–15 digits pass through; anything else is invalid. */
export function normalizePhone(v: string): string | null {
  const digits = v.replace(/\D/g, '');
  if (digits.length === 10) return '1' + digits;
  if (digits.length >= 11 && digits.length <= 15) return digits;
  return null;
}

/** http(s) URL with a dotted hostname; no credentials. Returns the normalized href or null. */
export function normalizeWebsite(v: string): string | null {
  const withScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(v) ? v : `https://${v}`;
  let u: URL;
  try {
    u = new URL(withScheme);
  } catch {
    return null;
  }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
  if (u.username || u.password) return null;
  if (!/^[a-z0-9-]+(\.[a-z0-9-]+)+$/i.test(u.hostname)) return null;
  return u.href.length <= 2048 ? u.href : null;
}

export function referrerDomain(v: unknown): string | null {
  if (typeof v !== 'string' || v.length > 2048) return null;
  try {
    const u = new URL(v);
    return u.protocol === 'http:' || u.protocol === 'https:' ? u.hostname.toLowerCase().replace(/^www\./, '') : null;
  } catch {
    return null;
  }
}

/**
 * Validates a lead form submission.
 * Bot signals (filled honeypot, impossibly fast submit) return { bot: true } so the caller can answer
 * "ok" without storing anything.
 */
export function validateLeadSubmission(input: unknown, now: number = Date.now()): ValidationResult {
  if (typeof input !== 'object' || input === null || Array.isArray(input)) {
    return { ok: false, errors: { body: 'Expected a JSON object.' } };
  }
  const b = input as Record<string, unknown>;

  // Honeypot: a visually hidden field people never fill in.
  if (typeof b.website_confirm === 'string' && b.website_confirm.trim() !== '') return { ok: false, bot: true };
  // Timing: forms filled in under 2 seconds are bots. Missing started_at is allowed (no-JS clients).
  if (typeof b.started_at === 'number' && Number.isFinite(b.started_at) && now - b.started_at < 2000) {
    return { ok: false, bot: true };
  }

  const errors: Record<string, string> = {};
  const field = <T>(key: string, value: T | undefined, msg: string): T | null => {
    if (value === undefined) {
      errors[key] = msg;
      return null;
    }
    return value;
  };

  const purpose = PURPOSES.includes(b.purpose as Purpose) ? (b.purpose as Purpose) : undefined;
  field('purpose', purpose, 'Unknown request type.');
  const source = PUBLIC_SOURCES.includes(b.source as PublicSource) ? (b.source as PublicSource) : undefined;
  field('source', source, 'Unknown form.');

  const name = field('name', cleanText(b.name, 100), 'Name must be 100 characters or fewer.');
  if (!name && !errors.name) errors.name = 'Please enter your name.';

  const rawEmail = cleanText(b.email, 254);
  let email: string | null = null;
  if (!rawEmail) errors.email = 'Please enter your email address.';
  else if (!isValidEmail(rawEmail)) errors.email = 'Please enter a valid email address.';
  else email = normalizeEmail(rawEmail);

  let phone: string | null = null;
  const rawPhone = cleanText(b.phone, 30);
  if (rawPhone === undefined) errors.phone = 'Phone number is too long.';
  else if (rawPhone) {
    phone = normalizePhone(rawPhone);
    if (!phone) errors.phone = 'Please enter a valid phone number.';
  }

  const businessName = field('business_name', cleanText(b.business_name, 200), 'Business name must be 200 characters or fewer.');

  let businessWebsite: string | null = null;
  const rawSite = cleanText(b.business_website, 2048);
  if (rawSite === undefined) errors.business_website = 'Website address is too long.';
  else if (rawSite) {
    businessWebsite = normalizeWebsite(rawSite);
    if (!businessWebsite) errors.business_website = 'Please enter a website address like example.ca.';
  }

  const rawIndustry = cleanText(b.industry, 60);
  const industry = rawIndustry ? (INDUSTRIES.includes(rawIndustry as never) ? rawIndustry : 'other') : null;

  const message = field('message', cleanText(b.message, 2000, { multiline: true }), 'Message must be 2,000 characters or fewer.');

  const utm: LeadSubmission['utm'] = {};
  if (b.utm && typeof b.utm === 'object' && !Array.isArray(b.utm)) {
    for (const k of UTM_KEYS) {
      const v = cleanText((b.utm as Record<string, unknown>)[k], 100);
      if (v) utm[k] = v;
    }
  }

  const pagePath = typeof b.page_path === 'string' && b.page_path.startsWith('/') ? b.page_path.slice(0, 500) : null;
  const anonymousId = typeof b.anonymous_id === 'string' && /^[A-Za-z0-9_-]{8,64}$/.test(b.anonymous_id) ? b.anonymous_id : null;
  const referralCode = typeof b.referral_code === 'string' && /^[a-z0-9-]{3,40}$/i.test(b.referral_code) ? b.referral_code.toLowerCase() : null;

  let auditSessionId: string | null = null;
  if (b.audit_session_id !== undefined && b.audit_session_id !== null) {
    if (typeof b.audit_session_id === 'string' && UUID_RE.test(b.audit_session_id)) auditSessionId = b.audit_session_id.toLowerCase();
    else errors.audit_session_id = 'Invalid audit reference.';
  }

  let submissionId: string | null = null;
  if (b.submission_id !== undefined && b.submission_id !== null) {
    if (typeof b.submission_id === 'string' && UUID_RE.test(b.submission_id)) submissionId = b.submission_id.toLowerCase();
    else errors.submission_id = 'Invalid submission id.';
  }

  // Consent: the browser sends only booleans + the form version; wording comes from the server copy.
  const formVersion = typeof b.form_version === 'string' ? b.form_version : '';
  const copy = CONSENT_COPY[formVersion];
  if (!copy) errors.form_version = 'This form is out of date. Please refresh the page.';
  const consents: ConsentChoice[] = [];
  const rawConsents = (b.consents && typeof b.consents === 'object' && !Array.isArray(b.consents) ? b.consents : {}) as Record<string, unknown>;
  for (const key of Object.keys(rawConsents)) {
    if (!(key in (copy?.purposes ?? {})) || key === 'demo_email') errors[`consents.${key}`] = 'Unknown consent option.';
    else if (typeof rawConsents[key] !== 'boolean') errors[`consents.${key}`] = 'Consent must be true or false.';
  }
  if (copy && Object.keys(errors).length === 0) {
    const sourceUrl = pagePath;
    const formId = source as string;
    // The demo form's submission is itself the request for the one demo email.
    if (purpose === 'demo_reply') {
      consents.push({ channel: 'email', purpose: 'demo_email', granted: true, wording: copy.purposes.demo_email.wording,
                      form_id: formId, form_version: formVersion, source_url: sourceUrl });
    }
    for (const key of ['follow_up', 'marketing', 'sms_updates'] as const) {
      if (!(key in rawConsents)) continue; // only record choices the form actually offered
      const granted = rawConsents[key] === true;
      if (key === 'sms_updates' && granted && !phone) {
        errors['consents.sms_updates'] = 'Add a phone number to get text updates.';
        continue;
      }
      consents.push({ channel: copy.purposes[key].channel, purpose: key, granted, wording: copy.purposes[key].wording,
                      form_id: formId, form_version: formVersion, source_url: sourceUrl });
    }
  }

  if (Object.keys(errors).length > 0) return { ok: false, errors };

  return {
    ok: true,
    value: {
      submissionId, purpose: purpose!, source: source!, name: name!, email: email!, phone, businessName, businessWebsite,
      industry, message, utm, pagePath, referrerDomain: referrerDomain(b.referrer), anonymousId, referralCode,
      auditSessionId, formVersion, consents,
    },
  };
}

const SEARCH = /(^|\.)(google|bing|duckduckgo|yahoo|ecosia|search\.brave|startpage)\./;
const SOCIAL = /(^|\.)(facebook|fb|instagram|linkedin|lnkd|t|twitter|x|reddit|youtube|tiktok|nextdoor|threads)\.(com|co|net|in)$/;

/** Marketing channel from UTM tags, referral code and referrer. Self-referrals count as direct. */
export function deriveChannel(s: Pick<LeadSubmission, 'utm' | 'referralCode' | 'referrerDomain'>, ownDomains: string[] = []): string {
  if (s.referralCode) return 'referral_partner';
  const medium = s.utm.medium?.toLowerCase();
  if (medium) {
    if (['cpc', 'ppc', 'paid', 'paidsearch', 'paid_social'].includes(medium)) return 'paid';
    if (medium === 'email' || medium === 'newsletter') return 'email';
    if (medium === 'social' || medium === 'social_organic') return 'social';
    if (medium === 'organic') return 'organic_search';
    if (medium === 'referral') return s.utm.source === 'partner' ? 'referral_partner' : 'referral';
  }
  const ref = s.referrerDomain;
  if (!ref || ownDomains.some((d) => ref === d || ref.endsWith('.' + d))) return 'direct';
  if (SEARCH.test(ref)) return 'organic_search';
  if (SOCIAL.test(ref)) return 'social';
  return 'referral';
}
