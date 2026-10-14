begin;
\ir _helpers.psql

do $$
declare r jsonb; r2 jsonb; v_lead uuid; n integer; v_audit uuid;
begin
  insert into growth.audit_sessions (submitted_url, status, is_test) values ('https://maple-hvac.example', 'complete', true)
  returning id into v_audit;

  r := growth.intake_lead(jsonb_build_object(
    'idempotency_key', 'test-key-1', 'purpose', 'inquiry_review', 'source', 'inquiry_check', 'source_detail', '/inquiry-check',
    'name', 'Test Person', 'email', '  Test.Person@Example.COM ', 'phone', '519-555-0199',
    'business_name', 'Maple HVAC', 'business_website', 'https://www.maple-hvac.example/', 'industry', 'hvac',
    'message', 'We miss calls when on jobs.', 'utm', '{"source":"google","medium":"organic"}', 'channel', 'organic_search',
    'ip_hash', 'abc', 'audit_session_id', v_audit, 'is_test', true,
    'consents', jsonb_build_array(
      jsonb_build_object('channel','email','purpose','follow_up','granted',true,
                         'wording','Stellan can follow up with me about setting this up for my business.','form_id','inquiry_check','form_version','2026-10-12'),
      jsonb_build_object('channel','email','purpose','marketing','granted',false,
                         'wording','Send me occasional tips from FlowPilot. Unsubscribe anytime.','form_id','inquiry_check','form_version','2026-10-12'))));
  v_lead := (r ->> 'lead_id')::uuid;
  assert not (r ->> 'duplicate')::boolean, 'first intake not duplicate';
  assert (select email_normalized from growth.contacts c join growth.leads l on l.contact_id = c.id where l.id = v_lead) = 'test.person@example.com', 'email normalized';
  assert (select stage from growth.leads where id = v_lead) = 'new', 'stage new';
  assert (select count(*) from growth.lead_stage_history where lead_id = v_lead) = 1, 'stage history row';
  assert (select business_id is not null from growth.leads where id = v_lead), 'business linked from website';
  assert (select lead_id from growth.audit_sessions where id = v_audit) = v_lead, 'audit session linked';

  -- Consent: exempt reply + the two explicit choices, including the unticked one.
  select count(*) into n from growth.consent_records where lead_id = v_lead;
  assert n = 3, format('expected 3 consent rows, got %s', n);
  assert exists (select 1 from growth.consent_current where identifier = 'test.person@example.com' and purpose = 'follow_up' and active), 'follow_up active';
  assert exists (select 1 from growth.consent_current where identifier = 'test.person@example.com' and purpose = 'marketing' and not active), 'marketing declined recorded';
  assert (select wording_shown from growth.consent_records where lead_id = v_lead and purpose = 'follow_up') like 'Stellan can follow up%', 'exact wording stored';

  assert (select count(*) from growth.event_outbox where dedupe_key = 'lead.created:' || v_lead) = 1, 'outbox event';
  assert (select payload ? 'email' from growth.event_outbox where dedupe_key = 'lead.created:' || v_lead) = false, 'no PII in outbox';
  assert (select channel from growth.analytics_events where lead_id = v_lead) = 'organic_search', 'analytics channel';

  -- Same submission again → same lead, nothing duplicated.
  r2 := growth.intake_lead(jsonb_build_object('idempotency_key', 'test-key-1', 'purpose', 'inquiry_review', 'source', 'inquiry_check',
                                              'email', 'test.person@example.com'));
  assert (r2 ->> 'duplicate')::boolean and (r2 ->> 'lead_id')::uuid = v_lead, 'idempotent';
  assert (select count(*) from growth.leads where idempotency_key = 'test-key-1') = 1, 'one lead';
  assert (select count(*) from growth.consent_records where lead_id = v_lead) = 3, 'no duplicate consents';

  -- A second request from the same person → second lead, same contact.
  r2 := growth.intake_lead(jsonb_build_object('idempotency_key', 'test-key-2', 'purpose', 'audit_report', 'source', 'inquiry_check',
                                              'email', 'TEST.person@example.com', 'is_test', true));
  assert (select count(distinct contact_id) from growth.leads where idempotency_key in ('test-key-1','test-key-2')) = 1, 'contact reused';

  -- Suppressed person can still reach out, but is flagged for a human and never auto-messaged.
  perform growth.add_suppression('gone@example.com', null, null, 'unsubscribe', 'test');
  r := growth.intake_lead(jsonb_build_object('idempotency_key', 'test-key-3', 'purpose', 'consultation', 'source', 'website_form',
                                             'email', 'Gone@Example.com', 'is_test', true));
  assert (r ->> 'suppressed')::boolean and (r ->> 'needs_human')::boolean, 'suppressed flagged';
end $$;

-- Consent and suppression are append-only, even for the service role.
set local role service_role;
select pg_temp.expect_error($$update growth.consent_records set granted = true$$, 'append-only');
select pg_temp.expect_error($$delete from growth.consent_records$$, 'append-only');
select pg_temp.expect_error($$delete from growth.suppression_list$$, 'append-only');
select pg_temp.expect_error($$update growth.suppression_list set lifted_at = now()$$, 'append-only');
select pg_temp.expect_error($$delete from growth.audit_log$$, 'append-only');
-- Setting the bypass flag yourself doesn't help: only the owner-checked function may use it.
select set_config('growth.allow_mutation', 'on', true);
select pg_temp.expect_error($$delete from growth.suppression_list$$, 'append-only');
select pg_temp.expect_error($$update growth.consent_records set granted = true$$, 'append-only');
select set_config('growth.allow_mutation', 'off', true);
reset role;
set local role growth_worker;
select set_config('growth.allow_mutation', 'on', true);
select pg_temp.expect_error($$delete from growth.suppression_list$$, 'append-only|permission denied');
select pg_temp.expect_error($$update growth.suppression_list set lifted_at = now()$$, 'append-only');
select pg_temp.expect_error($$select growth.remove_suppression(gen_random_uuid(), 'x')$$, 'permission denied');
select set_config('growth.allow_mutation', 'off', true);
reset role;

-- Bad input is rejected inside the transaction.
select pg_temp.expect_error($$select growth.intake_lead('{"purpose":"consultation","source":"website_form","email":"a@b.co"}')$$, 'idempotency_key');
select pg_temp.expect_error($$select growth.intake_lead('{"idempotency_key":"k","purpose":"consultation","source":"website_form"}')$$, 'email is required');
select pg_temp.expect_error($$select growth.intake_lead('{"idempotency_key":"k","purpose":"bogus","source":"website_form","email":"a@b.co"}')$$, 'check constraint');
select pg_temp.expect_error($$select growth.intake_lead('{"idempotency_key":"k","purpose":"consultation","source":"website_form","email":"a@b.co",
  "consents":[{"channel":"email","purpose":"marketing","granted":true}]}')$$, 'wording is required');
select pg_temp.expect_error($$select growth.intake_lead('{"idempotency_key":"k","purpose":"consultation","source":"website_form","email":"a@b.co",
  "consents":[{"channel":"sms","purpose":"sms_updates","granted":true,"wording":"Text me"}]}')$$, 'needs a phone');

-- Only the owner can lift a suppression, and it's audited.
do $$
declare v_id uuid;
begin
  select id into v_id from growth.suppression_list where email_normalized = 'gone@example.com';
  perform set_config('test.sid', v_id::text, true);
end $$;
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a2","role":"authenticated"}', true);
select pg_temp.expect_error(format($$select growth.remove_suppression(%L, 'asked again')$$, current_setting('test.sid')), 'only the owner');
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a1","role":"authenticated"}', true);
select pg_temp.expect_error(format($$select growth.remove_suppression(%L, '')$$, current_setting('test.sid')), 'reason is required');
select growth.remove_suppression(current_setting('test.sid')::uuid, 'Person re-subscribed in writing on 2026-10-12');
reset role;
do $$ begin
  assert not growth.is_suppressed('gone@example.com'), 'lifted';
  assert exists (select 1 from growth.audit_log where action = 'suppression.lift'), 'lift audited';
end $$;
rollback;
