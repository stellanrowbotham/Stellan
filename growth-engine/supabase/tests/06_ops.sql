begin;
\ir _helpers.psql

-- Workflow errors: one row per failing item, exponential backoff, dead letter after max retries.
do $$ declare e growth.workflow_errors; begin
  e := growth.record_workflow_error('WF-02', null, 'Claude: research', 'invalid_ai_output', 'schema mismatch', '{"business_id":"b1"}', 'b1', 3);
  assert e.status = 'open' and e.retry_count = 0, 'first error open';
  e := growth.record_workflow_error('WF-02', null, 'Claude: research', 'invalid_ai_output', 'schema mismatch again', '{}', 'b1', 3);
  assert e.status = 'retrying' and e.retry_count = 1, 'second → retrying';
  assert e.next_retry_at > now() + interval '90 seconds', 'backoff grows';
  e := growth.record_workflow_error('WF-02', null, 'Claude: research', 'invalid_ai_output', 'x', '{}', 'b1', 3);
  e := growth.record_workflow_error('WF-02', null, 'Claude: research', 'invalid_ai_output', 'x', '{}', 'b1', 3);
  assert e.status = 'dead_letter' and e.next_retry_at is null, 'dead letter after max retries';
  assert (select count(*) from growth.workflow_errors where dedupe_key = 'b1') = 1, 'one row per item';
end $$;

-- Outbox: claim once, complete, no double processing; failures back off and dead-letter.
do $$ declare n integer; ev growth.event_outbox; begin
  insert into growth.event_outbox (topic, payload, dedupe_key) values ('lead.created', '{"lead_id":"x"}', 'lead.created:x');
  insert into growth.event_outbox (topic, payload, dedupe_key) values ('lead.created', '{"lead_id":"x"}', 'lead.created:x') on conflict do nothing;
  select count(*) into n from growth.claim_outbox_events(array['lead.created'], 10);
  assert n = 1, 'claimed one';
  select count(*) into n from growth.claim_outbox_events(array['lead.created'], 10);
  assert n = 0, 'not claimable twice while processing';
  select * into ev from growth.event_outbox where dedupe_key = 'lead.created:x';
  perform growth.complete_outbox_event(ev.id, false, 'n8n timeout');
  select * into ev from growth.event_outbox where id = ev.id;
  assert ev.status = 'failed' and ev.next_attempt_at > now(), 'failed with backoff';
  update growth.event_outbox set next_attempt_at = now() - interval '1 second' where id = ev.id;
  select count(*) into n from growth.claim_outbox_events(array['lead.created'], 10);
  assert n = 1, 'retry claimable after backoff';
  perform growth.complete_outbox_event(ev.id, true);
  assert (select status from growth.event_outbox where id = ev.id) = 'done', 'done';
end $$;

-- Budget: blocks once the cap would be exceeded.
do $$ declare b jsonb; begin
  b := growth.check_budget('WF-03', 0.10);
  assert (b ->> 'allowed')::boolean, 'under budget';
  insert into growth.ai_usage (workflow, provider, model, input_tokens, output_tokens, est_cost_usd_micros)
  values ('WF-03', 'anthropic', 'test-model', 1000, 1000, 950000);
  b := growth.check_budget('WF-03', 0.10);
  assert not (b ->> 'allowed')::boolean, format('over budget should block: %s', b);
end $$;

-- Rate limit: 3 per window.
do $$ begin
  assert growth.hit_rate_limit('test:ip', 3, 3600) and growth.hit_rate_limit('test:ip', 3, 3600) and growth.hit_rate_limit('test:ip', 3, 3600), 'first 3 allowed';
  assert not growth.hit_rate_limit('test:ip', 3, 3600), '4th blocked';
end $$;

-- Content: unverified claims can't be approved; nothing publishes unapproved; agents can't approve.
do $$ declare d uuid; begin
  insert into growth.content_drafts (kind, title, slug, body_md, claims, created_by)
  values ('guide', 'Reply to estimate requests faster', 'reply-faster', '# Draft',
          '[{"claim":"Most homeowners contact 3 contractors","source_url":null,"verified":false}]', 'agent:WF-04')
  returning id into d;
  perform set_config('t.d', d::text, true);
end $$;
select pg_temp.expect_error($$update growth.content_drafts set status = 'approved', reviewed_by = '00000000-0000-0000-0000-0000000000a1' where id = current_setting('t.d')::uuid$$, 'unverified claims');
select pg_temp.expect_error($$update growth.content_drafts set status = 'approved', reviewed_by = '00000000-0000-0000-0000-0000000000a4' where id = current_setting('t.d')::uuid$$, 'human owner or operator');
select pg_temp.expect_error($$insert into growth.content_publications (draft_id, channel, published_by) values (current_setting('t.d')::uuid, 'website', '00000000-0000-0000-0000-0000000000a1')$$, 'must be approved');
select pg_temp.expect_error($$update growth.content_drafts set status = 'published' where id = current_setting('t.d')::uuid$$, 'only approved');
update growth.content_drafts set claims = '[{"claim":"Example scenario, no statistics","source_url":null,"verified":true}]' where id = current_setting('t.d')::uuid;
update growth.content_drafts set status = 'approved', reviewed_by = '00000000-0000-0000-0000-0000000000a1' where id = current_setting('t.d')::uuid;
insert into growth.content_publications (draft_id, channel, url, published_by) values (current_setting('t.d')::uuid, 'website', 'https://example.invalid/reply-faster', '00000000-0000-0000-0000-0000000000a1');
do $$ begin assert (select status from growth.content_drafts where id = current_setting('t.d')::uuid) = 'published', 'published'; end $$;

-- Retention: old anonymous audits and IP hashes go; leads with consent stay intact.
do $$ declare r jsonb; v_old uuid; begin
  insert into growth.audit_sessions (submitted_url, status, ip_hash, created_at) values ('https://old.example', 'complete', 'h', now() - interval '120 days') returning id into v_old;
  perform growth.intake_lead('{"idempotency_key":"ret-1","purpose":"consultation","source":"website_form","email":"keep@example.com","ip_hash":"h"}');
  update growth.leads set created_at = now() - interval '60 days' where idempotency_key = 'ret-1';
  r := growth.apply_retention();
  assert not exists (select 1 from growth.audit_sessions where id = v_old), 'old anonymous audit deleted';
  assert (select ip_hash from growth.leads where idempotency_key = 'ret-1') is null, 'ip hash nulled';
  assert (select email_normalized from growth.contacts where email_normalized = 'keep@example.com') is not null, 'open lead contact kept';
  assert exists (select 1 from growth.consent_records where email_normalized = 'keep@example.com'), 'consent kept';
end $$;

-- Closed, consent-less contacts older than 2 years are anonymized.
do $$ begin
  perform growth.intake_lead('{"idempotency_key":"ret-2","purpose":"consultation","source":"website_form","email":"old@example.com","name":"Old Lead","message":"hi"}');
  update growth.leads set stage = 'lost' where idempotency_key = 'ret-2';
  update growth.leads set stage_changed_at = now() - interval '800 days' where idempotency_key = 'ret-2';
  perform growth.apply_retention();
  assert (select c.anonymized_at is not null and c.email_normalized is null and c.name is null
            from growth.contacts c join growth.leads l on l.contact_id = c.id where l.idempotency_key = 'ret-2'), 'anonymized';
  assert (select message from growth.leads where idempotency_key = 'ret-2') is null, 'free text removed';
end $$;
rollback;
