-- FlowPilot Growth Engine · 0005 operations
-- Analytics events, workflow runs and errors (also the error queue for invalid AI output),
-- AI usage and spending limits, rate limiting, the event outbox for n8n, and retention.

-- ---------------------------------------------------------------------------
-- Analytics events: first-party funnel events (no third-party cookies). One row per event.
-- event_name examples: page_view, audit_started, audit_completed, demo_requested, lead_submitted,
-- lead_qualified, call_booked, proposal_sent, deal_won, deal_lost, content_impression (from Search Console).
-- ---------------------------------------------------------------------------
create table growth.analytics_events (
  id               bigint generated always as identity primary key,
  event_name       text not null check (event_name ~ '^[a-z][a-z0-9_]{1,63}$'),
  occurred_at      timestamptz not null default now(),
  anonymous_id     text check (length(anonymous_id) <= 64),     -- random first-party id, not a fingerprint
  lead_id          uuid references growth.leads (id) on delete set null,
  audit_session_id uuid references growth.audit_sessions (id) on delete set null,
  content_id       uuid references growth.content_drafts (id) on delete set null,
  partner_id       uuid references growth.referral_partners (id) on delete set null,
  channel          text,                -- organic_search, direct, referral_partner, social, email, paid, inquiry_check, unknown
  source           text,
  medium           text,
  campaign         text,
  path             text check (length(path) <= 500),
  industry         text,
  geography        text,
  value_cents      integer,
  properties       jsonb not null default '{}'::jsonb,
  dedupe_key       text unique,
  is_test          boolean not null default false
);
create index analytics_events_name_time_idx on growth.analytics_events (event_name, occurred_at desc);
create index analytics_events_channel_idx on growth.analytics_events (channel, occurred_at desc);
create index analytics_events_lead_idx on growth.analytics_events (lead_id) where lead_id is not null;

-- ---------------------------------------------------------------------------
-- Workflow runs and errors (WF-01 … WF-09)
-- ---------------------------------------------------------------------------
create table growth.workflow_runs (
  id             uuid primary key default gen_random_uuid(),
  workflow       text not null check (workflow ~ '^WF-[0-9]{2}$'),
  execution_id   text,                -- n8n execution id
  trigger        text,                -- schedule, webhook, manual, retry
  status         text not null default 'running' check (status in ('running', 'success', 'partial', 'failed', 'skipped_budget')),
  started_at     timestamptz not null default now(),
  finished_at    timestamptz,
  items_in       integer,
  items_out      integer,
  error_count    integer not null default 0,
  cost_usd_micros bigint not null default 0,
  summary        text,
  unique (workflow, execution_id)
);
create index workflow_runs_time_idx on growth.workflow_runs (workflow, started_at desc);

create table growth.workflow_errors (
  id              uuid primary key default gen_random_uuid(),
  workflow        text not null,
  run_id          uuid references growth.workflow_runs (id) on delete set null,
  node            text,
  error_class     text not null check (error_class in
                    ('http', 'timeout', 'rate_limited', 'invalid_input', 'invalid_ai_output', 'budget_exceeded',
                     'db', 'send_gate_blocked', 'auth', 'unknown')),
  message         text not null check (length(message) <= 2000),
  payload         jsonb,               -- minimal context for replay; no secrets, no full pages
  dedupe_key      text,                -- same failure for same item → one row, retry_count goes up
  retry_count     integer not null default 0,
  max_retries     integer not null default 3,
  next_retry_at   timestamptz,
  status          text not null default 'open' check (status in ('open', 'retrying', 'resolved', 'dead_letter', 'ignored')),
  alerted_at      timestamptz,
  created_at      timestamptz not null default now(),
  resolved_at     timestamptz
);
create unique index workflow_errors_dedupe on growth.workflow_errors (workflow, dedupe_key)
  where dedupe_key is not null and status in ('open', 'retrying');
create index workflow_errors_status_idx on growth.workflow_errors (status, next_retry_at);

-- Records a failure once per item; repeated failures increase retry_count with exponential backoff
-- (1, 2, 4, 8 … minutes) and move to dead_letter after max_retries.
create or replace function growth.record_workflow_error(p_workflow text, p_run_id uuid, p_node text, p_class text,
                                                        p_message text, p_payload jsonb, p_dedupe_key text,
                                                        p_max_retries integer default 3)
returns growth.workflow_errors
language plpgsql security definer set search_path = growth, pg_temp as $$
declare r growth.workflow_errors;
begin
  insert into growth.workflow_errors (workflow, run_id, node, error_class, message, payload, dedupe_key, max_retries, next_retry_at)
  values (p_workflow, p_run_id, p_node, p_class, left(p_message, 2000), p_payload, p_dedupe_key, p_max_retries, now() + interval '1 minute')
  on conflict (workflow, dedupe_key) where dedupe_key is not null and status in ('open', 'retrying')
  do update set
    retry_count   = growth.workflow_errors.retry_count + 1,
    message       = excluded.message,
    run_id        = excluded.run_id,
    status        = case when growth.workflow_errors.retry_count + 1 >= growth.workflow_errors.max_retries
                         then 'dead_letter' else 'retrying' end,
    next_retry_at = case when growth.workflow_errors.retry_count + 1 >= growth.workflow_errors.max_retries
                         then null
                         else now() + make_interval(mins => power(2, growth.workflow_errors.retry_count + 1)::int) end
  returning * into r;
  return r;
end $$;

-- ---------------------------------------------------------------------------
-- AI usage and spending limits
-- ---------------------------------------------------------------------------
create table growth.ai_usage (
  id                 bigint generated always as identity primary key,
  workflow           text not null,
  run_id             uuid references growth.workflow_runs (id) on delete set null,
  provider           text not null,       -- anthropic, openai, brave, google_places, ...
  model              text,
  purpose            text,
  input_tokens       integer not null default 0,
  output_tokens      integer not null default 0,
  request_count      integer not null default 1,
  est_cost_usd_micros bigint not null default 0,
  created_at         timestamptz not null default now()
);
create index ai_usage_time_idx on growth.ai_usage (created_at desc);
create index ai_usage_workflow_idx on growth.ai_usage (workflow, created_at desc);

create table growth.spending_limits (
  scope        text primary key,         -- 'global' or a workflow id like 'WF-03'
  daily_usd    numeric(10, 2) not null check (daily_usd >= 0),
  monthly_usd  numeric(10, 2) not null check (monthly_usd >= 0),
  updated_at   timestamptz not null default now()
);
-- Conservative starting caps. Change them in the dashboard or here.
insert into growth.spending_limits (scope, daily_usd, monthly_usd) values
  ('global', 3.00, 40.00),
  ('WF-02', 1.00, 15.00),
  ('WF-03', 1.00, 15.00),
  ('WF-04', 0.50, 5.00);

-- {"allowed": bool, "spent_today_usd": n, "spent_month_usd": n, ...}. Workflows call this before each paid call.
create or replace function growth.check_budget(p_scope text, p_planned_usd numeric default 0)
returns jsonb language plpgsql stable security definer set search_path = growth, pg_temp as $$
declare
  v_today numeric; v_month numeric; v_g_today numeric; v_g_month numeric;
  l growth.spending_limits; g growth.spending_limits;
  v_start_day timestamptz := date_trunc('day', now() at time zone 'America/Toronto') at time zone 'America/Toronto';
  v_start_month timestamptz := date_trunc('month', now() at time zone 'America/Toronto') at time zone 'America/Toronto';
begin
  select * into g from growth.spending_limits where scope = 'global';
  select * into l from growth.spending_limits where scope = p_scope;
  select coalesce(sum(est_cost_usd_micros), 0) / 1e6 into v_today from growth.ai_usage where workflow = p_scope and created_at >= v_start_day;
  select coalesce(sum(est_cost_usd_micros), 0) / 1e6 into v_month from growth.ai_usage where workflow = p_scope and created_at >= v_start_month;
  select coalesce(sum(est_cost_usd_micros), 0) / 1e6 into v_g_today from growth.ai_usage where created_at >= v_start_day;
  select coalesce(sum(est_cost_usd_micros), 0) / 1e6 into v_g_month from growth.ai_usage where created_at >= v_start_month;
  return jsonb_build_object(
    'allowed',
      (g.scope is null or (v_g_today + p_planned_usd <= g.daily_usd and v_g_month + p_planned_usd <= g.monthly_usd))
      and (l.scope is null or (v_today + p_planned_usd <= l.daily_usd and v_month + p_planned_usd <= l.monthly_usd)),
    'scope', p_scope,
    'spent_today_usd', round(v_today, 4), 'spent_month_usd', round(v_month, 4),
    'global_today_usd', round(v_g_today, 4), 'global_month_usd', round(v_g_month, 4),
    'limit_daily_usd', l.daily_usd, 'limit_monthly_usd', l.monthly_usd,
    'global_limit_daily_usd', g.daily_usd, 'global_limit_monthly_usd', g.monthly_usd);
end $$;

-- ---------------------------------------------------------------------------
-- Rate limiting (fixed window). hit_rate_limit('audit:ip:<hash>', 5, 3600) → true when allowed.
-- ---------------------------------------------------------------------------
create table growth.rate_limits (
  bucket        text not null,
  window_start  timestamptz not null,
  hits          integer not null default 0,
  primary key (bucket, window_start)
);

create or replace function growth.hit_rate_limit(p_bucket text, p_limit integer, p_window_seconds integer)
returns boolean language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  v_window timestamptz := to_timestamp(floor(extract(epoch from now()) / p_window_seconds) * p_window_seconds);
  v_hits integer;
begin
  insert into growth.rate_limits (bucket, window_start, hits) values (p_bucket, v_window, 1)
  on conflict (bucket, window_start) do update set hits = growth.rate_limits.hits + 1
  returning hits into v_hits;
  return v_hits <= p_limit;
end $$;

-- ---------------------------------------------------------------------------
-- Event outbox: the database tells n8n what happened (lead.created, audit.completed, ...).
-- n8n claims events with claim_outbox_events(); dedupe_key makes producers idempotent.
-- ---------------------------------------------------------------------------
create table growth.event_outbox (
  id              bigint generated always as identity primary key,
  topic           text not null,
  payload         jsonb not null,
  dedupe_key      text not null unique,
  status          text not null default 'pending' check (status in ('pending', 'processing', 'done', 'failed', 'dead_letter')),
  attempts        integer not null default 0,
  next_attempt_at timestamptz not null default now(),
  locked_until    timestamptz,
  last_error      text,
  created_at      timestamptz not null default now(),
  processed_at    timestamptz
);
create index event_outbox_due_idx on growth.event_outbox (status, next_attempt_at);

create or replace function growth.claim_outbox_events(p_topics text[], p_limit integer default 20)
returns setof growth.event_outbox
language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  return query
  update growth.event_outbox e set status = 'processing', attempts = e.attempts + 1,
         locked_until = now() + interval '5 minutes'
   where e.id in (
     select id from growth.event_outbox
      where topic = any (p_topics)
        and ((status in ('pending', 'failed') and next_attempt_at <= now())
             or (status = 'processing' and locked_until < now()))   -- recover crashed consumers
      order by id
      limit least(greatest(p_limit, 1), 100)
      for update skip locked)
  returning e.*;
end $$;

create or replace function growth.complete_outbox_event(p_id bigint, p_ok boolean, p_error text default null)
returns void language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  update growth.event_outbox set
    status = case when p_ok then 'done' when attempts >= 5 then 'dead_letter' else 'failed' end,
    processed_at = case when p_ok then now() else processed_at end,
    last_error = case when p_ok then null else left(p_error, 1000) end,
    next_attempt_at = case when p_ok then next_attempt_at else now() + make_interval(mins => power(2, attempts)::int) end,
    locked_until = null
  where id = p_id;
end $$;

-- ---------------------------------------------------------------------------
-- Retention. Policies are data; apply_retention() runs daily (pg_cron on Supabase, or WF-09).
-- Consent records and the suppression list are kept: they are the compliance record.
-- ---------------------------------------------------------------------------
create table growth.retention_policies (
  entity       text primary key,
  keep_days    integer not null check (keep_days > 0),
  action       text not null check (action in ('delete', 'anonymize', 'null_ip')),
  description  text not null
);
insert into growth.retention_policies values
  ('rate_limits',            2,   'delete',    'Rate-limit counters'),
  ('ip_hashes',              30,  'null_ip',   'Salted IP hashes on leads and audits'),
  ('anonymous_audits',       90,  'delete',    'Inquiry Check sessions that never became a lead (evidence cascades)'),
  ('event_outbox',           30,  'delete',    'Processed outbox events'),
  ('workflow_errors',        180, 'delete',    'Resolved or ignored workflow errors'),
  ('workflow_runs',          400, 'delete',    'Workflow run log'),
  ('analytics_events',       760, 'delete',    'Raw analytics events (about 25 months)'),
  ('closed_lead_contacts',   730, 'anonymize', 'Contacts whose leads all closed lost/disqualified/spam over 2 years ago, with no active consent');

create or replace function growth.apply_retention()
returns jsonb language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  d jsonb := '{}'::jsonb;
  n integer;
  v_days integer;
begin
  select keep_days into v_days from growth.retention_policies where entity = 'rate_limits';
  delete from growth.rate_limits where window_start < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('rate_limits', n);

  select keep_days into v_days from growth.retention_policies where entity = 'ip_hashes';
  update growth.leads set ip_hash = null where ip_hash is not null and created_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('lead_ip_hashes', n);
  update growth.audit_sessions set ip_hash = null where ip_hash is not null and created_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('audit_ip_hashes', n);

  select keep_days into v_days from growth.retention_policies where entity = 'anonymous_audits';
  delete from growth.audit_sessions where lead_id is null and created_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('anonymous_audits', n);

  select keep_days into v_days from growth.retention_policies where entity = 'event_outbox';
  delete from growth.event_outbox where status = 'done' and processed_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('event_outbox', n);

  select keep_days into v_days from growth.retention_policies where entity = 'workflow_errors';
  delete from growth.workflow_errors where status in ('resolved', 'ignored') and created_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('workflow_errors', n);

  select keep_days into v_days from growth.retention_policies where entity = 'workflow_runs';
  delete from growth.workflow_runs where started_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('workflow_runs', n);

  select keep_days into v_days from growth.retention_policies where entity = 'analytics_events';
  delete from growth.analytics_events where occurred_at < now() - make_interval(days => v_days);
  get diagnostics n = row_count; d := d || jsonb_build_object('analytics_events', n);

  select keep_days into v_days from growth.retention_policies where entity = 'closed_lead_contacts';
  update growth.contacts c set name = null, phone_normalized = null, email_normalized = null, anonymized_at = now()
   where c.anonymized_at is null
     and exists (select 1 from growth.leads l where l.contact_id = c.id)
     and not exists (select 1 from growth.leads l where l.contact_id = c.id
                      and (l.stage not in ('lost', 'disqualified', 'spam') or l.stage_changed_at > now() - make_interval(days => v_days)))
     and not exists (select 1 from growth.consent_current cc where cc.identifier = c.email_normalized and cc.active
                      and cc.purpose in ('marketing', 'follow_up'));
  get diagnostics n = row_count; d := d || jsonb_build_object('contacts_anonymized', n);
  -- Free text on those leads goes too.
  update growth.leads l set message = null, business_name = null, ip_hash = null
   where l.contact_id in (select id from growth.contacts where anonymized_at is not null) and l.message is not null;

  perform growth.log_audit('system', 'retention.apply', 'database', null, d);
  return d;
end $$;
