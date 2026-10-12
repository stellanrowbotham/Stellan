// Canonical consent wording, by form version. The server records THIS text as what the person saw,
// so a browser can't forge the wording. When the website copy changes, add a new version here and
// update the form's `form_version`; never edit an existing version (old records point to it).

export type ConsentPurpose = 'demo_email' | 'follow_up' | 'marketing' | 'sms_updates';

export interface ConsentCopy {
  privacyNotice: string;
  purposes: Record<ConsentPurpose, { channel: 'email' | 'sms'; wording: string }>;
}

export const CONSENT_COPY: Record<string, ConsentCopy> = {
  '2026-10-12': {
    privacyNotice:
      'FlowPilot Automation (Stellan Rowbotham, southwestern Ontario) uses the details you enter to respond to this ' +
      'request. Nothing is sold or shared. You can ask to see, correct or delete your information at any time by ' +
      'emailing stellanrowbotham@gmail.com.',
    purposes: {
      demo_email: {
        channel: 'email',
        // Shown next to the demo form; submitting the form is the request.
        wording: 'Your email is only used to send this one demo reply unless you tick the box below.',
      },
      follow_up: {
        channel: 'email',
        wording: 'Stellan can follow up with me about setting this up for my business.',
      },
      marketing: {
        channel: 'email',
        wording:
          'Send me occasional practical tips from FlowPilot Automation by email. I can unsubscribe at any time.',
      },
      sms_updates: {
        channel: 'sms',
        wording: 'Text me about this request at the number above. Reply STOP to opt out.',
      },
    },
  },
};

export const CURRENT_FORM_VERSION = '2026-10-12';
