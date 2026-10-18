// Offline unit tests for the Code nodes in FlowPilot Follow-ups (mocked n8n globals).
// Run: cd growth-engine/n8n/tests && npm install && npm test
const fs = require('fs');
const { DateTime } = require('luxon');
// Reads the exported workflow so the tested code is exactly what runs in n8n.
const wf = JSON.parse(fs.readFileSync(__dirname + '/../workflows/followups.json', 'utf8'));
function codeOf(name) {
  const n = wf.nodes.find(x => x.name === name);
  if (!n || !n.parameters.jsCode) throw new Error('no code for ' + name);
  return n.parameters.jsCode;
}
const NOW = DateTime.fromISO('2026-10-14T11:00:00', { zone: 'America/Toronto' }); // Wednesday
function run(name, nodes, opts) {
  opts = opts || {};
  const $ = n => ({ all: () => (nodes[n] || []).map(j => ({ json: j })), first: () => ({ json: (nodes[n] || [])[0] }), isExecuted: !!opts.manual && n === 'Run now' });
  const input = opts.input || [];
  const f = new Function('$', '$now', '$execution', '$input', '$json', 'DateTime', 'Buffer', '"use strict";' + codeOf(name));
  return f($, opts.now || NOW, { id: '999' }, { all: () => input.map(j => ({ json: j })) }, input[0] || {}, DateTime, Buffer);
}
let pass = 0, fail = 0;
function ok(cond, msg) { if (cond) { pass++; console.log('  PASS', msg); } else { fail++; console.log('  FAIL', msg); } }

const settings = [['paused','false'],['send_mode','DRAFT_ONLY'],['dry_run','false'],['max_followups','2'],['followup_2_business_days','7'],['followup_1_business_days','4'],['followup_batch','5'],['min_quality_score','80'],['campaign_id','C1']].map(([key, value]) => ({ key, value }));
const past = '2026-10-13T09:30:00.000-04:00', future = '2026-10-20T09:30:00.000-04:00';
const base = { status: 'SENT', public_email: 'a@x.ca', gmail_thread_id: 't', gmail_message_id: 'm', claim_token: 'exec-1', next_followup_at: past, followup_count: 0, kind: 'prospect', business_name: 'Biz', email_subject: 'Quick idea', createdAt: '2026-10-12T15:05:33.829Z' };
const leads = [
  { ...base, id: 1, public_email: 'one@x.ca' },
  { ...base, id: 2, public_email: 'two@x.ca', reply_class: 'NOT_NOW' },
  { ...base, id: 3, public_email: 'sup@x.ca' },
  { ...base, id: 4, public_email: 'four@x.ca', followup_count: 2 },
  { ...base, id: 5, public_email: 'five@x.ca', next_followup_at: future },
  { ...base, id: 6, public_email: 'six@x.ca', kind: 'test' },
  { ...base, id: 7, public_email: 'seven@x.ca', status: 'NEEDS_REVIEW', gmail_draft_id: 'r1', gmail_thread_id: null },
  { ...base, id: 8, public_email: 'eight@x.ca', followup_count: 1 },
  { ...base, id: 9, public_email: 'nine@blocked.ca' },
  { ...base, id: 10, public_email: 'ten@x.ca', no_solicitation_notice: true },
  { ...base, id: 11, public_email: 'eleven@x.ca', claim_token: null },
  { ...base, id: 12, public_email: 'twelve@x.ca', status: 'NEEDS_REVIEW', gmail_draft_id: null }
];
const sup = [{ email: 'sup@x.ca' }, { domain: 'blocked.ca' }];
const nodes = { 'Load settings': settings, 'Load leads': leads, 'Load suppression': sup };

console.log('Plan');
let out = run('Plan sync and follow-ups', nodes).map(i => i.json);
const ids = k => out.filter(o => o.kind === k).map(o => o.lead_id).join(',');
ok(ids('sync') === '7', 'sync only lead 7 (NEEDS_REVIEW with a draft): ' + ids('sync'));
ok(ids('followup') === '1,8', 'follow-ups only due leads 1 and 8 (excludes replied, suppressed email/domain, max reached, not due, test, no-solicitation, no claim token): ' + ids('followup'));
const f1 = out.find(o => o.lead_id === 1), f8 = out.find(o => o.lead_id === 8);
ok(f1.followup_no === 1 && f1.next_after.startsWith('2026-10-23T09:30'), 'follow-up 1 schedules #2 seven business days later (Fri 2026-10-23): ' + f1.next_after);
ok(f8.followup_no === 2 && f8.next_after.startsWith('2076'), 'follow-up 2 is the last (next set 50 years out)');
ok(f1.release_at.startsWith('2026-10-15T09:30'), 'release/claim moves due date to next business day: ' + f1.release_at);
ok(f1.new_token === 'fu-999-1-1' && f1.old_token === 'exec-1', 'claim tokens');
const s7 = out.find(o => o.lead_id === 7);
ok(s7.after_epoch === Math.floor(DateTime.fromISO('2026-10-12T15:05:33.829Z').toSeconds()), 'sync searches only mail sent after the lead was created');
let n2 = { ...nodes, 'Load settings': settings.map(s => s.key === 'followup_batch' ? { key: s.key, value: '1' } : s) };
ok(run('Plan sync and follow-ups', n2).filter(i => i.json.kind === 'followup').length === 1, 'followup_batch caps follow-ups per run');
n2 = { ...nodes, 'Load settings': settings.map(s => s.key === 'paused' ? { key: 'paused', value: 'true' } : s) };
ok(run('Plan sync and follow-ups', n2).length === 0, 'paused = true: nothing planned');
ok(run('Plan sync and follow-ups', nodes, { now: DateTime.fromISO('2026-10-17T11:00:00', { zone: 'America/Toronto' }) }).length === 0, 'Saturday: nothing planned');
ok(run('Plan sync and follow-ups', nodes, { now: DateTime.fromISO('2026-10-14T19:00:00', { zone: 'America/Toronto' }) }).length === 0, 'after 18:00: nothing planned');

console.log('Inspect thread');
const L = { ...f1 };
let r = run('Inspect thread', { 'Loop leads': [L] }, { input: [{ id: 'm', labels: [{ id: 'SENT' }], 'Message-ID': '<abc@mail.gmail.com>' }] })[0].json;
ok(r.has_reply === false && r.msg_id_header === '<abc@mail.gmail.com>', 'only our sent message: no reply, header captured');
r = run('Inspect thread', { 'Loop leads': [L] }, { input: [{ id: 'm', labels: [{ id: 'SENT' }] }, { id: 'n', labels: [{ id: 'INBOX' }, { id: 'UNREAD' }] }] })[0].json;
ok(r.has_reply === true, 'inbound message in thread: reply detected');
r = run('Inspect thread', { 'Loop leads': [L] }, { input: [{ id: 'm', labels: [{ id: 'SENT' }] }, { id: 'd', labels: [{ id: 'DRAFT' }] }] })[0].json;
ok(r.has_reply === false, 'our own draft in thread is not a reply');
r = run('Inspect thread', { 'Loop leads': [L] }, { input: [{ messages: [{ id: 'm', labelIds: ['SENT'] }, { id: 'b', labelIds: ['INBOX'] }] }] })[0].json;
ok(r.has_reply === true, 'thread-object shape (messages array) also handled');

console.log('Gate');
const goodBody = 'Hi, I wrote last week about answering quote requests on your website the moment they arrive. Your contact page asks people to leave a phone number, so an instant reply could confirm you got it and say when you will call. I could walk you through it on a 15 minute call, or I could show you over email, whichever is easier.';
const crit = (o) => ({ output: { quality_score: 86, personalization_score: 80, relevance_score: 85, credibility_score: 90, clarity_score: 88, cta_score: 85, factual_issues: [], compliance_flags: [], improvements: [], decision: 'APPROVE', revised_subject: '', revised_body: '', ...o } });
const gate = (loop, w, c) => run('Gate', { 'Loop leads': [loop], 'AI write follow-up': [w], 'AI critic': [c] })[0].json;
let g = gate(L, {}, {});
ok(g.route === 'ai_failed', 'writer failed -> ai_failed (retry next business day, nothing saved)');
g = gate(L, { output: { subject: 'x', body: goodBody } }, crit());
ok(g.route === 'draft' && g.decision === 'APPROVE', 'approved in DRAFT_ONLY -> Gmail draft, never sent');
ok(g.subject === 'Re: Quick idea' && g.final_body.includes('reply "stop"') && g.final_body.includes('privacy.html') && !/\d+ [A-Z][a-z]+ (St|Street|Ave|Rd)\b/.test(g.final_body), 'threaded subject, footer with opt-out and privacy link, no street address');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit());
ok(g.route === 'send', 'approved in SEND mode -> send');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit({ quality_score: 79 }));
ok(g.route === 'draft' && g.decision === 'HUMAN_REVIEW', 'score below 80 in SEND mode -> draft for review, not sent');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit({ compliance_flags: ['implies past results'] }));
ok(g.route === 'draft' && g.decision === 'HUMAN_REVIEW', 'compliance flag overrides a high score');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit({ factual_issues: ['claims a form that was not found'] }));
ok(g.decision === 'HUMAN_REVIEW', 'factual issue blocks approval');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit({ decision: 'REWRITE', revised_body: goodBody.replace('Hi,', 'Hello,') }));
ok(g.route === 'draft' && g.final_body.startsWith('Hello,'), 'critic rewrite is used but goes to review');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody + ' Results guaranteed.' } }, crit());
ok(g.decision === 'HUMAN_REVIEW' && /unsupported claim/.test(g.reasons), 'deterministic check catches "guarantee" even if the critic approved');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody + ' See https://x.ca' } }, crit());
ok(g.decision === 'HUMAN_REVIEW', 'links blocked');
g = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, {});
ok(g.decision === 'HUMAN_REVIEW' && g.route === 'draft', 'critic unavailable -> review draft, not sent');
g = gate({ ...L, mode: 'SEND', dry_run: true }, { output: { body: goodBody } }, crit());
ok(g.route === 'dry', 'dry_run -> nothing saved or sent');

console.log('Build reply email');
const G = gate({ ...L, mode: 'SEND' }, { output: { body: goodBody } }, crit());
const m = run('Build reply email', { 'Loop leads': [L], 'Gate': [G], 'Inspect thread': [{ msg_id_header: '<abc@mail.gmail.com>' }] })[0].json;
const mime = Buffer.from(m.raw.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8');
const [head, bodyB64] = mime.split('\r\n\r\n');
ok(/^To: one@x\.ca$/m.test(head) && /In-Reply-To: <abc@mail\.gmail\.com>/.test(head) && /References: <abc@mail\.gmail\.com>/.test(head), 'To is the prospect, threading headers set');
ok(Buffer.from(head.match(/Subject: =\?UTF-8\?B\?(.*)\?=/)[1], 'base64').toString() === 'Re: Quick idea', 'subject encoded');
ok(Buffer.from(bodyB64.replace(/\r\n/g, ''), 'base64').toString('utf8') === G.final_body, 'body round-trips');
ok(m.threadId === 't', 'threadId passed to Gmail API');

console.log('Prepare sync');
const ps = run('Prepare sync', { 'Loop leads': [s7] }, { input: [{ id: 'g1', threadId: 'th1', internalDate: String(DateTime.fromISO('2026-10-16T14:00:00', { zone: 'America/Toronto' }).toMillis()) }] })[0].json;
ok(ps.next_followup_at.startsWith('2026-10-22T09:30'), 'manual send Fri 2026-10-16 -> follow-up 1 Thu 2026-10-22 (4 business days): ' + ps.next_followup_at);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
