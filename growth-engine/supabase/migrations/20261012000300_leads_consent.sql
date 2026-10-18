-- FlowPilot Growth Engine · 0003 leads, consent and suppression
-- Contacts (people), inbound leads and their pipeline, append-only consent records, the global
-- suppression list, Inquiry Check audit sessions, bookings and deals.

-- ---------------------------------------------------------------------------
-- Contacts: the people who reach out. Only what is needed to reply.
-- ---------------------------------------------------------------------------
create table growth.contacts (
  id                uuid primary key default gen_random_uuid(),
  email_normalized  text unique check (email_normalized is null or email_normalized ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  name              text check (length(name) <= 100),
  phone_normalized  text,
  business_id       uuid references growth.businesses (id) on delete set null,
  anonymized_at     timestamptz,
  is_test           boolean not null default false,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create index contacts_phone_idx on growth.contacts (phone_normalized) where phone_normalized is not null;
create trigger contacts_touch before update on growth.contacts
  for each row execute function growth.touch_updated_at();

-- ---------------------------------------------------------------------------
-- Leads: one row per inbound request. `purpose` is what the person actually asked for, and it limits
-- what may be sent to them (an audit request never enrols anyone in marketing).
-- ---------------------------------------------------------------------------
create table growth.leads (
  id                uuid primary key default gen_random_uuid(),
  contact_id        uuid references growth.contacts (id) on delete set null,
  business_id       uuid references growth.businesses (id) on delete set null,
  purpose           text not null check (purpose in
                      ('inquiry_review', 'audit_report', 'demo_reply', 'consultation', 'general_inquiry', 'partnership')),
  source            text not null check (source in
                      ('website_form', 'inquiry_check', 'demo_form', 'request_page', 'referral', 'email', 'phone', 'manual')),
  source_detail     text,                -- page path or form id
  utm               jsonb not null default '{}'::jsonb,
  referrer_domain   text,
  content_id        uuid,                -- content draft that brought them, if known (FK in 0004)
  partner_id        uuid references growth.referral_partners (id) on delete set null,
  industry          text,
  business_name     text check (length(business_name) <= 200),
  business_website  text,
  message           text check (length(message) <= 2000),
  stage             text not null default 'new' check (stage in
                      ('new', 'needs_info', 'qualified', 'booked', 'proposal_sent', 'won', 'lost', 'disqualified', 'spam')),
  stage_changed_at  timestamptz not null default now(),
  qualification     jsonb not null default '{}'::jsonb,   -- answers + classifier output (validated)
  needs_human       boolean not null default false,
  needs_human_reason text,
  lost_reason       text,
  idempotency_key   text not null unique,
  ip_hash           text,                 -- salted hash for abuse control; nulled by retention
  is_test           boolean not null default false,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create index leads_stage_idx on growth.leads (stage, created_at desc);
create index leads_source_idx on growth.leads (source, created_at desc);
create index leads_industry_idx on growth.leads (industry, created_at desc);
create index leads_contact_idx on growth.leads (contact_id);
create index leads_partner_idx on growth.leads (partner_id) where partner_id is not null;
create trigger leads_touch before update on growth.leads
  for each row execute function growth.touch_updated_at();

create table growth.lead_stage_history (
  id          bigint generated always as identity primary key,
  lead_id     uuid not null references growth.leads (id) on delete cascade,
  from_stage  text,
  to_stage    text not null,
  changed_by  text not null,
  reason      text,
  at          timestamptz not null default now()
);
create index lead_stage_history_lead_idx on growth.lead_stage_history (lead_id, at);

create or replace function growth.track_lead_stage() returns trigger
language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  if tg_op = 'INSERT' then
    insert into growth.lead_stage_history (lead_id, from_stage, to_stage, changed_by)
    values (new.id, null, new.stage, growth.current_actor());
  elsif new.stage is distinct from old.stage then
    new.stage_changed_at := now();
    insert into growth.lead_stage_history (lead_id, from_stage, to_stage, changed_by, reason)
    values (new.id, old.stage, new.stage, growth.current_actor(),
            nullif(current_setting('growth.reason', true), ''));
  end if;
  return new;
end $$;
create trigger leads_stage_insert after insert on growth.leads
  for each row execute function growth.track_lead_stage();
create trigger leads_stage_update before update of stage on growth.leads
  for each row execute function growth.track_lead_stage();

-- ---------------------------------------------------------------------------
-- Consent records: append-only proof of every consent choice, exactly as presented.
--   purpose  request_response : replying to the person's own request (CASL s.6(5)(b) exempt; recorded anyway)
--            demo_email       : the one demo email they asked for
--            follow_up        : follow-ups about their own request (e.g. the site's "Stellan can follow up with me" box)
--            marketing        : ongoing commercial messages (needs express consent or a live implied basis)
--            sms_updates      : texts about their request
--   basis    express | implied_inquiry (6 months from inquiry) | implied_ebr (2 years from purchase)
--            | implied_published (published business address + relevance, attested by a human) | exempt_response
-- A withdrawal is a new row with granted = false. The current state is in growth.consent_current.
-- ---------------------------------------------------------------------------
create table growth.consent_records (
  id                uuid primary key default gen_random_uuid(),
  contact_id        uuid references growth.contacts (id) on delete set null,
  email_normalized  text,
  phone_normalized  text,
  channel           text not null check (channel in ('email', 'sms')),
  purpose           text not null check (purpose in ('request_response', 'demo_email', 'follow_up', 'marketing', 'sms_updates')),
  basis             text not null check (basis in
                      ('express', 'implied_inquiry', 'implied_ebr', 'implied_published', 'exempt_response', 'withdrawn')),
  granted           boolean not null,
  wording_shown     text,                -- exact checkbox / notice text the person saw
  form_id           text,
  form_version      text,
  source_url        text,
  evidence_url      text,                -- implied_published: where the address is published
  attested_by       uuid,                -- implied_published: the human who checked relevance + no "no solicitation" notice
  lead_id           uuid references growth.leads (id) on delete set null,
  ip_hash           text,
  captured_at       timestamptz not null default now(),
  expires_at        timestamptz,         -- implied consents expire; express does not
  check (email_normalized is not null or phone_normalized is not null),
  check (granted = false or basis <> 'withdrawn'),
  check (basis <> 'express' or not granted or wording_shown is not null),
  check (basis <> 'implied_published' or (evidence_url is not null and attested_by is not null))
);
create index consent_records_email_idx on growth.consent_records (email_normalized, channel, purpose, captured_at desc);
create index consent_records_phone_idx on growth.consent_records (phone_normalized, channel, purpose, captured_at desc);
create trigger consent_records_append_only before update or delete on growth.consent_records
  for each row execute function growth.forbid_mutation();

-- Latest decision per identifier + channel + purpose, with expiry applied.
create or replace view growth.consent_current as
select distinct on (coalesce(email_normalized, phone_normalized), channel, purpose)
  coalesce(email_normalized, phone_normalized) as identifier,
  email_normalized, phone_normalized, channel, purpose, basis, granted, captured_at, expires_at,
  (granted and (expires_at is null or expires_at > now())) as active
from growth.consent_records
order by coalesce(email_normalized, phone_normalized), channel, purpose, captured_at desc, id desc;

-- ---------------------------------------------------------------------------
-- Suppression list: global, append-only for everyone, including agents and the service role.
-- Only growth.remove_suppression() (owner only, audited) can lift an entry.
-- ---------------------------------------------------------------------------
create table growth.suppression_list (
  id                uuid primary key default gen_random_uuid(),
  email_normalized  text,
  phone_normalized  text,
  domain            text,                -- suppress a whole business domain (e.g. "please don't contact us")
  reason            text not null check (reason in ('unsubscribe', 'complaint', 'bounce_hard', 'do_not_contact', 'legal', 'manual')),
  source            text not null,       -- 'unsubscribe_link', 'reply', 'wf-05', 'user:<uuid>' ...
  note              text,
  created_at        timestamptz not null default now(),
  lifted_at         timestamptz,
  lifted_by         uuid,
  lift_reason       text,
  check (num_nonnulls(email_normalized, phone_normalized, domain) = 1)
);
create unique index suppression_email_uniq on growth.suppression_list (email_normalized) where email_normalized is not null and lifted_at is null;
create unique index suppression_phone_uniq on growth.suppression_list (phone_normalized) where phone_normalized is not null and lifted_at is null;
create unique index suppression_domain_uniq on growth.suppression_list (domain) where domain is not null and lifted_at is null;
create trigger suppression_append_only before update or delete on growth.suppression_list
  for each row execute function growth.forbid_mutation();

-- True if the email, its domain, or the phone number is on the active suppression list.
create or replace function growth.is_suppressed(p_email text, p_phone text default null)
returns boolean language sql stable security definer set search_path = growth, pg_temp as $$
  select exists (
    select 1 from growth.suppression_list s
     where s.lifted_at is null
       and (   (s.email_normalized is not null and s.email_normalized = growth.normalize_email(p_email))
            or (s.domain is not null and s.domain = split_part(growth.normalize_email(p_email), '@', 2))
            or (s.phone_normalized is not null and s.phone_normalized = growth.normalize_phone(p_phone)))
  )
$$;

-- Idempotent: adding an identifier that is already suppressed is a no-op.
create or replace function growth.add_suppression(p_email text, p_phone text, p_domain text,
                                                  p_reason text, p_source text, p_note text default null)
returns void language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  if growth.normalize_email(p_email) is not null then
    insert into growth.suppression_list (email_normalized, reason, source, note)
    values (growth.normalize_email(p_email), p_reason, p_source, p_note)
    on conflict (email_normalized) where email_normalized is not null and lifted_at is null do nothing;
  end if;
  if growth.normalize_phone(p_phone) is not null then
    insert into growth.suppression_list (phone_normalized, reason, source, note)
    values (growth.normalize_phone(p_phone), p_reason, p_source, p_note)
    on conflict (phone_normalized) where phone_normalized is not null and lifted_at is null do nothing;
  end if;
  if growth.normalize_domain(p_domain) is not null then
    insert into growth.suppression_list (domain, reason, source, note)
    values (growth.normalize_domain(p_domain), p_reason, p_source, p_note)
    on conflict (domain) where domain is not null and lifted_at is null do nothing;
  end if;
  perform growth.log_audit(p_source, 'suppression.add', 'suppression', coalesce(growth.normalize_email(p_email), p_phone, p_domain),
                           jsonb_build_object('reason', p_reason));
end $$;

create or replace function growth.remove_suppression(p_id uuid, p_reason text)
returns void language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  if growth.current_app_role() is distinct from 'owner' then
    raise exception 'only the owner can lift a suppression' using errcode = 'insufficient_privilege';
  end if;
  if coalesce(btrim(p_reason), '') = '' then
    raise exception 'a reason is required' using errcode = 'check_violation';
  end if;
  perform set_config('growth.allow_mutation', 'on', true);
  update growth.suppression_list set lifted_at = now(), lifted_by = auth.uid(), lift_reason = p_reason
   where id = p_id and lifted_at is null;
  perform set_config('growth.allow_mutation', 'off', true);
  perform growth.log_audit('user:' || auth.uid(), 'suppression.lift', 'suppression', p_id::text,
                           jsonb_build_object('reason', p_reason));
end $$;

-- ---------------------------------------------------------------------------
-- Inquiry Check audit sessions (Agent C). Evidence rows live in source_observations.
-- ---------------------------------------------------------------------------
create table growth.audit_sessions (
  id                 uuid primary key default gen_random_uuid(),
  submitted_url      text not null check (length(submitted_url) <= 2048),
  normalized_domain  text generated always as (growth.normalize_domain(submitted_url)) stored,
  industry           text,
  challenge          text check (length(challenge) <= 500),
  status             text not null default 'queued' check (status in
                       ('queued', 'fetching', 'analyzing', 'complete', 'partial', 'blocked', 'failed')),
  blocked_reason     text,               -- e.g. 'private_address', 'robots_disallow', 'too_many_redirects'
  pages_fetched      jsonb not null default '[]'::jsonb,   -- [{url, status, fetched_at, bytes}]
  report             jsonb,              -- validated report (findings, improvements, unverifiable, sample workflow)
  methodology_version text,
  business_id        uuid references growth.businesses (id) on delete set null,
  lead_id            uuid references growth.leads (id) on delete set null,
  ip_hash            text,
  is_test            boolean not null default false,
  created_at         timestamptz not null default now(),
  completed_at       timestamptz
);
create index audit_sessions_created_idx on growth.audit_sessions (created_at desc);
create index audit_sessions_domain_idx on growth.audit_sessions (normalized_domain, created_at desc);
create index audit_sessions_ip_idx on growth.audit_sessions (ip_hash, created_at desc) where ip_hash is not null;

alter table growth.source_observations
  add constraint source_observations_audit_fk
  foreign key (audit_session_id) references growth.audit_sessions (id) on delete cascade;

-- ---------------------------------------------------------------------------
-- Bookings and deals (pipeline money). Amounts are integer cents, CAD.
-- ---------------------------------------------------------------------------
create table growth.bookings (
  id                 uuid primary key default gen_random_uuid(),
  lead_id            uuid not null references growth.leads (id) on delete cascade,
  provider           text not null,       -- cal_com, calendly, google_calendar, manual
  external_event_id  text,
  starts_at          timestamptz not null,
  ends_at            timestamptz not null check (ends_at > starts_at),
  status             text not null default 'scheduled' check (status in ('scheduled', 'rescheduled', 'cancelled', 'completed', 'no_show')),
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  unique (provider, external_event_id)
);
create index bookings_lead_idx on growth.bookings (lead_id);
create index bookings_starts_idx on growth.bookings (starts_at);
create trigger bookings_touch before update on growth.bookings
  for each row execute function growth.touch_updated_at();

create table growth.deals (
  id                    uuid primary key default gen_random_uuid(),
  lead_id               uuid not null references growth.leads (id) on delete cascade,
  offer                 text not null check (offer in ('instant_reply', 'follow_up_system', 'custom', 'care_plan_only')),
  setup_amount_cents    integer not null default 0 check (setup_amount_cents >= 0),
  monthly_amount_cents  integer not null default 0 check (monthly_amount_cents >= 0),
  currency              text not null default 'CAD',
  status                text not null default 'proposal_sent' check (status in ('draft', 'proposal_sent', 'won', 'lost')),
  proposal_sent_at      timestamptz,
  closed_at             timestamptz,
  care_plan_started_at  timestamptz,
  care_plan_ended_at    timestamptz,
  notes                 text,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),
  check (status not in ('won', 'lost') or closed_at is not null)
);
create index deals_lead_idx on growth.deals (lead_id);
create index deals_status_idx on growth.deals (status, closed_at);
create trigger deals_touch before update on growth.deals
  for each row execute function growth.touch_updated_at();
