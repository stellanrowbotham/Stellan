// FlowPilot website → Growth Engine lead capture (drop-in, no dependencies).
// Replaces the demo form's current stub, which waits 650 ms and returns { ok: false } without sending anything.
//
// Usage in the site (React or plain JS):
//   import { submitLead, formStartedAt } from './lead-capture.js';
//   const startedAt = formStartedAt();            // call when the form first renders
//   const result = await submitLead({ purpose: 'demo_reply', source: 'demo_form', name, email,
//                                     consents: { follow_up: followUpBoxTicked }, startedAt });
//   if (result.ok) showSuccess(); else showErrors(result.errors ?? {}, result.message);

// Set after deploying the API (docs/setup.md, step 4). Example for Supabase Edge Functions:
//   https://<project-ref>.supabase.co/functions/v1/growth-api
export const GROWTH_API_URL = 'https://REPLACE-ME.supabase.co/functions/v1/growth-api';
export const FORM_VERSION = '2026-10-12'; // must match api/src/consent-copy.ts

export function formStartedAt() {
  return Date.now();
}

function anonymousId() {
  try {
    let id = localStorage.getItem('fp_aid');
    if (!id) {
      id = crypto.randomUUID().replace(/-/g, '');
      localStorage.setItem('fp_aid', id);
    }
    return id;
  } catch {
    return undefined; // private mode / storage blocked: fine, attribution is best-effort
  }
}

function utmParams() {
  const p = new URLSearchParams(window.location.search);
  const utm = {};
  for (const k of ['source', 'medium', 'campaign', 'term', 'content']) {
    const v = p.get(`utm_${k}`);
    if (v) utm[k] = v.slice(0, 100);
  }
  return utm;
}

/**
 * @param {object} f
 * @param {'demo_reply'|'inquiry_review'|'consultation'|'general_inquiry'|'partnership'} f.purpose
 * @param {'demo_form'|'website_form'|'inquiry_check'} f.source
 * @param {string} f.name
 * @param {string} f.email
 * @param {string} [f.phone]
 * @param {string} [f.businessName]
 * @param {string} [f.businessWebsite]
 * @param {string} [f.industry]
 * @param {string} [f.message]
 * @param {{follow_up?: boolean, marketing?: boolean, sms_updates?: boolean}} [f.consents]
 *        Include ONLY the boxes the form actually shows. Unticked = false (recorded as declined).
 * @param {string} [f.honeypot]   value of the hidden "website_confirm" input
 * @param {number} [f.startedAt]  from formStartedAt()
 * @param {string} [f.submissionId] reuse the same id when retrying the same submission
 */
export async function submitLead(f) {
  const submissionId = f.submissionId || crypto.randomUUID();
  const body = {
    submission_id: submissionId,
    purpose: f.purpose,
    source: f.source,
    name: f.name,
    email: f.email,
    phone: f.phone || undefined,
    business_name: f.businessName || undefined,
    business_website: f.businessWebsite || undefined,
    industry: f.industry || undefined,
    message: f.message || undefined,
    consents: f.consents || {},
    form_version: FORM_VERSION,
    website_confirm: f.honeypot || '',
    started_at: f.startedAt,
    page_path: window.location.pathname,
    referrer: document.referrer || undefined,
    utm: utmParams(),
    anonymous_id: anonymousId(),
    referral_code: new URLSearchParams(window.location.search).get('ref') || undefined,
  };

  // One automatic retry on network failure, with the same submission_id (the server deduplicates).
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 10000);
      const res = await fetch(`${GROWTH_API_URL}/v1/leads`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timer);
      const data = await res.json().catch(() => ({}));
      if (res.ok) return { ok: true, submissionId };
      return { ok: false, status: res.status, errors: data.errors, message: data.message, submissionId };
    } catch {
      if (attempt === 1) {
        return { ok: false, status: 0, submissionId,
                 message: 'We couldn’t send that right now. Please try again, or email stellanrowbotham@gmail.com.' };
      }
      await new Promise((r) => setTimeout(r, 1500));
    }
  }
}
