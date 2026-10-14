begin;
\ir _helpers.psql

-- Fixtures: a demo request (demo consent only), an audit-only request (no follow-up consent),
-- and a consultation request where the person ticked "follow up with me".
do $$
declare r jsonb; t uuid;
begin
  r := growth.intake_lead(jsonb_build_object('idempotency_key','demo-1','purpose','demo_reply','source','demo_form',
        'name','Dee','email','demo@example.com','is_test',true,
        'consents', jsonb_build_array(jsonb_build_object('channel','email','purpose','demo_email','granted',true,
          'wording','Send me the demo reply.','form_id','demo','form_version','1'))));
  perform set_config('t.demo_lead', r ->> 'lead_id', true);

  r := growth.intake_lead(jsonb_build_object('idempotency_key','audit-1','purpose','audit_report','source','inquiry_check',
        'email','auditonly@example.com','is_test',true));
  perform set_config('t.audit_lead', r ->> 'lead_id', true);

  r := growth.intake_lead(jsonb_build_object('idempotency_key','consult-1','purpose','consultation','source','website_form',
        'email','consult@example.com','is_test',true,
        'consents', jsonb_build_array(jsonb_build_object('channel','email','purpose','follow_up','granted',true,
          'wording','Stellan can follow up with me about setting this up for my business.','form_id','contact','form_version','1'))));
  perform set_config('t.consult_lead', r ->> 'lead_id', true);

  insert into growth.message_templates (key, channel, purpose, subject, body, approved_by, approved_at, active)
  values ('demo-reply', 'email', 'demo_email', 'Your FlowPilot demo reply', 'Hi {{name}}, thanks for reaching out!',
          '00000000-0000-0000-0000-0000000000a1', now(), true) returning id into t;
  perform set_config('t.demo_tpl', t::text, true);
  insert into growth.message_templates (key, channel, purpose, subject, body, approved_by, approved_at, active)
  values ('nudge', 'email', 'follow_up', 'Checking in', 'Hi {{unsubscribe_url}} {{sender_identification}}',
          '00000000-0000-0000-0000-0000000000a1', now(), true) returning id into t;
  perform set_config('t.fu_tpl', t::text, true);
end $$;

-- 1. Demo email from an approved template: allowed once, never twice.
do $$
declare m1 uuid; m2 uuid;
begin
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, template_id, body, generated_by, approval_mode, idempotency_key)
  values ('email','demo_email','demo@example.com', current_setting('t.demo_lead')::uuid, current_setting('t.demo_tpl')::uuid,
          'Hi Dee, thanks for reaching out!', 'template', 'approved_template', 'demo-msg-1') returning id into m1;
  update growth.outbound_messages set status = 'queued' where id = m1;
  assert (select count(*) from growth.claim_messages_for_sending(10)) = 1, 'claimed demo';
  update growth.outbound_messages set status = 'sent', provider = 'test', provider_message_id = 'p1' where id = m1;

  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, template_id, body, generated_by, approval_mode, idempotency_key)
  values ('email','demo_email','demo@example.com', current_setting('t.demo_lead')::uuid, current_setting('t.demo_tpl')::uuid,
          'Hi again', 'template', 'approved_template', 'demo-msg-2') returning id into m2;
  perform set_config('t.m2', m2::text, true);
end $$;
select pg_temp.expect_error($$update growth.outbound_messages set status = 'queued' where id = current_setting('t.m2')::uuid$$, 'demo_already_sent');

-- 2. Idempotency: the same message key can't be inserted twice.
select pg_temp.expect_error($$insert into growth.outbound_messages (channel, purpose, to_email, body, generated_by, idempotency_key)
  values ('email','marketing','x@example.com','b','agent:WF-06','demo-msg-1')$$, 'duplicate key');

-- 3. Messages can't be born approved or sent.
select pg_temp.expect_error($$insert into growth.outbound_messages (channel, purpose, to_email, body, generated_by, status, idempotency_key)
  values ('email','request_response','x@example.com','b','agent:WF-06','sent','born-sent')$$, 'must start as draft');

-- 4. An audit-only request never gets follow-ups (no silent enrolment), even with approval.
do $$ declare m uuid; begin
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
  values ('email','follow_up','auditonly@example.com', current_setting('t.audit_lead')::uuid,
          'Hi! {{sender_identification}} {{unsubscribe_url}}', 'agent:WF-06', 'pending_approval', 'audit-fu') returning id into m;
  perform set_config('t.audit_fu', m::text, true);
end $$;
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1'
  where id = current_setting('t.audit_fu')::uuid$$, 'no_follow_up_consent');
-- …but replying to their own request is fine.
do $$ declare m uuid; begin
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
  values ('email','request_response','auditonly@example.com', current_setting('t.audit_lead')::uuid,
          'Here is your report.', 'agent:WF-03', 'pending_approval', 'audit-reply') returning id into m;
  update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a2' where id = m;
  assert (select status from growth.outbound_messages where id = m) = 'approved', 'request_response approved';
end $$;

-- 5. Follow-up with consent: needs unsubscribe + sender identification, and a human approver.
do $$ declare m uuid; begin
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
  values ('email','follow_up','consult@example.com', current_setting('t.consult_lead')::uuid,
          'Hi, just checking in.', 'agent:WF-06', 'pending_approval', 'consult-fu-bad') returning id into m;
  perform set_config('t.fu_bad', m::text, true);
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
  values ('email','follow_up','consult@example.com', current_setting('t.consult_lead')::uuid,
          'Hi, just checking in. {{sender_identification}} Unsubscribe: {{unsubscribe_url}}', 'agent:WF-06', 'pending_approval', 'consult-fu')
  returning id into m;
  perform set_config('t.fu', m::text, true);
end $$;
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1'
  where id = current_setting('t.fu_bad')::uuid$$, 'missing_unsubscribe');
-- An agent / unknown user can't approve.
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a4'
  where id = current_setting('t.fu')::uuid$$, 'requires a human');
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a3'
  where id = current_setting('t.fu')::uuid$$, 'requires a human');
-- Can't skip approval.
select pg_temp.expect_error($$update growth.outbound_messages set status = 'queued' where id = current_setting('t.fu')::uuid$$, 'without approval');
-- Commercial messages can't ride an approved template.
select pg_temp.expect_error($$update growth.outbound_messages set status = 'queued', approval_mode = 'approved_template', template_id = current_setting('t.fu_tpl')::uuid
  where id = current_setting('t.fu')::uuid$$, 'per-message approval');
update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1' where id = current_setting('t.fu')::uuid;
-- Content is locked after approval.
select pg_temp.expect_error($$update growth.outbound_messages set body = body || ' P.S. 50% off!' where id = current_setting('t.fu')::uuid$$, 'locked');
update growth.outbound_messages set status = 'queued' where id = current_setting('t.fu')::uuid;

-- 6. They unsubscribe after approval → the claim blocks it instead of sending.
select growth.add_suppression('consult@example.com', null, null, 'unsubscribe', 'test');
do $$ begin
  assert (select count(*) from growth.claim_messages_for_sending(10)) = 0, 'nothing claimed';
  assert (select status from growth.outbound_messages where id = current_setting('t.fu')::uuid) = 'blocked', 'blocked after unsubscribe';
  assert (select compliance -> 'reasons' ? 'suppressed' from growth.outbound_messages where id = current_setting('t.fu')::uuid), 'reason recorded';
end $$;

-- 7. Marketing with no consent; process_unsubscribe cancels everything pending; partner outreach rules.
do $$ declare m uuid; r jsonb; begin
  insert into growth.outbound_messages (channel, purpose, to_email, body, generated_by, status, idempotency_key)
  values ('email','marketing','stranger@example.com','Tips! {{sender_identification}} {{unsubscribe_url}}','agent:WF-04','pending_approval','mkt-1')
  returning id into m;
  perform set_config('t.mkt', m::text, true);
  insert into growth.outbound_messages (channel, purpose, to_email, lead_id, body, generated_by, status, idempotency_key)
  values ('email','request_response','demo@example.com', current_setting('t.demo_lead')::uuid, 'Thanks', 'agent:WF-05','pending_approval','demo-reply-2');
  r := growth.process_unsubscribe('DEMO@example.com', null, 'unsubscribe_link');
  assert (r ->> 'cancelled_messages')::int = 2, format('cancelled %s', r ->> 'cancelled_messages');
  r := growth.process_unsubscribe('demo@example.com', null, 'unsubscribe_link');  -- idempotent
  assert growth.is_suppressed('demo@example.com'), 'suppressed';
  assert exists (select 1 from growth.consent_current where identifier = 'demo@example.com' and purpose = 'marketing' and not active), 'withdrawal recorded';
end $$;
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1'
  where id = current_setting('t.mkt')::uuid$$, 'no_marketing_consent');

-- A published business email is not consent: partner outreach needs an attested basis AND an approved partner.
do $$ declare b uuid; p uuid; m uuid; begin
  select business_id into b from growth.upsert_business('{"name":"Pixel Web Co","website_url":"https://pixelweb.example","relationship":"partner_candidate","is_test":true}');
  insert into growth.referral_partners (business_id, partner_type, status) values (b, 'web_designer', 'proposal_drafted') returning id into p;
  insert into growth.outbound_messages (channel, purpose, to_email, partner_id, business_id, body, generated_by, status, idempotency_key)
  values ('email','partner_outreach','hello@pixelweb.example', p, b, 'Hi {{sender_identification}} {{unsubscribe_url}}','agent:WF-07','pending_approval','partner-1')
  returning id into m;
  perform set_config('t.pm', m::text, true);
  perform set_config('t.partner', p::text, true);
end $$;
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1'
  where id = current_setting('t.pm')::uuid$$, 'no_partner_contact_basis');
select pg_temp.expect_error($$insert into growth.consent_records (email_normalized, channel, purpose, basis, granted)
  values ('hello@pixelweb.example','email','marketing','implied_published',true)$$, 'check constraint');
insert into growth.consent_records (email_normalized, channel, purpose, basis, granted, evidence_url, attested_by)
values ('hello@pixelweb.example','email','marketing','implied_published',true,'https://pixelweb.example/contact','00000000-0000-0000-0000-0000000000a1');
select pg_temp.expect_error($$update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1'
  where id = current_setting('t.pm')::uuid$$, 'partner_not_approved_to_contact');
update growth.referral_partners set status = 'approved_to_contact' where id = current_setting('t.partner')::uuid;
update growth.outbound_messages set status = 'approved', approved_by = '00000000-0000-0000-0000-0000000000a1' where id = current_setting('t.pm')::uuid;

-- Every status change is audited.
do $$ begin
  assert (select count(*) from growth.audit_log where entity_type = 'outbound_message' and action = 'message.approved') >= 2, 'approvals audited';
end $$;
rollback;
