-- FlowPilot Growth Engine · 0004 outbound messages, approvals and content
-- Every email or text the system could send is a row in growth.outbound_messages. The database itself
-- enforces the send gate (suppression, consent, CASL identification + unsubscribe, human approval),
-- so no workflow or AI agent can skip it.

-- ---------------------------------------------------------------------------
-- Message templates: wording Stellan approved once. Only non-commercial purposes
-- (replying to a request, the demo email, booking confirmations) may be sent from a template
-- without per-message approval.
-- ---------------------------------------------------------------------------
create table growth.message_templates (
  id           uuid primary key default gen_random_uuid(),
  key          text not null,
  version      integer not null default 1,
  channel      text not null check (channel in ('email', 'sms')),
  purpose      text not null,
  subject      text,
  body         text not null,
  approved_by  uuid,
  approved_at  timestamptz,
  active       boolean not null default false,
  created_at   timestamptz not null default now(),
  unique (key, version),
  check (not active or approved_by is not null)
);

-- ---------------------------------------------------------------------------
-- Outbound messages (drafts, approvals, sends).
--   Non-commercial purposes : request_response, demo_email, booking_confirmation
--   Commercial purposes     : follow_up, reminder, marketing, partner_outreach
-- ---------------------------------------------------------------------------
create table growth.outbound_messages (
  id                   uuid primary key default gen_random_uuid(),
  channel              text not null check (channel in ('email', 'sms')),
  purpose              text not null check (purpose in
                         ('request_response', 'demo_email', 'booking_confirmation',
                          'follow_up', 'reminder', 'marketing', 'partner_outreach')),
  contact_id           uuid references growth.contacts (id) on delete set null,
  to_email             text,
  to_phone             text,
  lead_id              uuid references growth.leads (id) on delete set null,
  partner_id           uuid references growth.referral_partners (id) on delete set null,
  business_id          uuid references growth.businesses (id) on delete set null,
  template_id          uuid references growth.message_templates (id),
  subject              text check (length(subject) <= 200),
  body                 text not null check (length(body) <= 10000),
  generated_by         text not null,     -- 'agent:WF-06', 'user:<uuid>', 'template'
  approval_mode        text not null default 'per_message' check (approval_mode in ('per_message', 'approved_template')),
  status               text not null default 'draft' check (status in
                         ('draft', 'pending_approval', 'approved', 'rejected', 'queued', 'sending',
                          'sent', 'failed', 'blocked', 'cancelled')),
  compliance           jsonb,             -- last send-gate result
  approved_by          uuid,
  approved_at          timestamptz,
  rejected_reason      text,
  scheduled_for        timestamptz,
  sent_at              timestamptz,
  provider             text,
  provider_message_id  text,
  attempt_count        integer not null default 0 check (attempt_count between 0 and 5),
  last_error           text,
  idempotency_key      text not null unique,
  created_at           timestamptz not null default now(),
  updated_at           timestamptz not null default now(),
  check (to_email is not null or to_phone is not null),
  check (channel <> 'email' or to_email is not null),
  check (channel <> 'sms' or to_phone is not null)
);
create index outbound_status_idx on growth.outbound_messages (status, scheduled_for);
create index outbound_lead_idx on growth.outbound_messages (lead_id, purpose);
create index outbound_email_idx on growth.outbound_messages (lower(to_email));
create trigger outbound_touch before update on growth.outbound_messages
  for each row execute function growth.touch_updated_at();

create or replace function growth.is_commercial(p_purpose text) returns boolean
language sql immutable as $$
  select p_purpose in ('follow_up', 'reminder', 'marketing', 'partner_outreach')
$$;

-- The send gate. Returns {"allowed": bool, "reasons": [..]} and never has side effects.
create or replace function growth.check_send_allowed(p_message_id uuid)
returns jsonb language plpgsql stable security definer set search_path = growth, pg_temp as $$
declare
  m growth.outbound_messages;
  v_reasons text[] := '{}';
  v_identifier text;
  v_lead growth.leads;
  v_has_consent boolean;
  v_sent_count integer;
begin
  select * into m from growth.outbound_messages where id = p_message_id;
  if not found then
    return jsonb_build_object('allowed', false, 'reasons', jsonb_build_array('message_not_found'));
  end if;

  v_identifier := case when m.channel = 'email' then growth.normalize_email(m.to_email)
                       else growth.normalize_phone(m.to_phone) end;
  if v_identifier is null then
    v_reasons := array_append(v_reasons, 'invalid_recipient');
  end if;

  -- 1. Suppression applies to every purpose and every workflow.
  if growth.is_suppressed(m.to_email, m.to_phone) then
    v_reasons := array_append(v_reasons, 'suppressed');
  end if;
  if m.business_id is not null and exists (select 1 from growth.businesses where id = m.business_id and do_not_contact) then
    v_reasons := array_append(v_reasons, 'business_do_not_contact');
  end if;

  if m.lead_id is not null then
    select * into v_lead from growth.leads where id = m.lead_id;
    if v_lead.stage = 'spam' then
      v_reasons := array_append(v_reasons, 'lead_marked_spam');
    end if;
  end if;

  -- 2. Purpose-specific basis.
  if m.purpose = 'request_response' then
    if m.lead_id is null then
      v_reasons := array_append(v_reasons, 'request_response_needs_lead');
    elsif v_lead.created_at < now() - interval '30 days' then
      v_reasons := array_append(v_reasons, 'request_too_old_for_response');
    end if;

  elsif m.purpose = 'demo_email' then
    select exists (select 1 from growth.consent_current c
                    where c.identifier = v_identifier and c.channel = m.channel
                      and c.purpose = 'demo_email' and c.active) into v_has_consent;
    if not v_has_consent then v_reasons := array_append(v_reasons, 'no_demo_request'); end if;
    select count(*) into v_sent_count from growth.outbound_messages o
     where o.purpose = 'demo_email' and o.status in ('sending', 'sent') and o.id <> m.id
       and (lower(o.to_email) = growth.normalize_email(m.to_email));
    if v_sent_count > 0 then v_reasons := array_append(v_reasons, 'demo_already_sent'); end if;

  elsif m.purpose = 'booking_confirmation' then
    if m.lead_id is null or not exists (select 1 from growth.bookings b where b.lead_id = m.lead_id and b.status in ('scheduled', 'rescheduled')) then
      v_reasons := array_append(v_reasons, 'no_active_booking');
    end if;

  elsif m.purpose in ('follow_up', 'reminder') then
    select exists (select 1 from growth.consent_current c
                    where c.identifier = v_identifier and c.channel = m.channel
                      and c.purpose in ('follow_up', 'marketing') and c.active) into v_has_consent;
    if not v_has_consent then v_reasons := array_append(v_reasons, 'no_follow_up_consent'); end if;
    if m.lead_id is null then v_reasons := array_append(v_reasons, 'follow_up_needs_lead'); end if;
    select count(*) into v_sent_count from growth.outbound_messages o
     where o.lead_id = m.lead_id and o.purpose in ('follow_up', 'reminder')
       and o.status in ('sending', 'sent') and o.id <> m.id;
    if v_sent_count >= 3 then v_reasons := array_append(v_reasons, 'follow_up_limit_reached'); end if;

  elsif m.purpose = 'marketing' then
    select exists (select 1 from growth.consent_current c
                    where c.identifier = v_identifier and c.channel = m.channel
                      and c.purpose = 'marketing' and c.active) into v_has_consent;
    if not v_has_consent then v_reasons := array_append(v_reasons, 'no_marketing_consent'); end if;

  elsif m.purpose = 'partner_outreach' then
    if m.partner_id is null then v_reasons := array_append(v_reasons, 'partner_outreach_needs_partner'); end if;
    select exists (select 1 from growth.consent_current c
                    where c.identifier = v_identifier and c.channel = m.channel
                      and c.purpose = 'marketing' and c.active
                      and c.basis in ('express', 'implied_published', 'implied_ebr')) into v_has_consent;
    if not v_has_consent then v_reasons := array_append(v_reasons, 'no_partner_contact_basis'); end if;
    if m.partner_id is not null and not exists (select 1 from growth.referral_partners p
                     where p.id = m.partner_id and p.status in ('approved_to_contact', 'contacted', 'in_discussion', 'active')) then
      v_reasons := array_append(v_reasons, 'partner_not_approved_to_contact');
    end if;
  end if;

  -- 3. Commercial messages must identify the sender and carry a working unsubscribe mechanism.
  --    The sender replaces these tokens with the CASL block and a signed unsubscribe link.
  if growth.is_commercial(m.purpose) then
    if m.channel = 'email' and position('{{unsubscribe_url}}' in m.body) = 0 then
      v_reasons := array_append(v_reasons, 'missing_unsubscribe');
    end if;
    if m.channel = 'sms' and position('{{sms_opt_out}}' in m.body) = 0 then
      v_reasons := array_append(v_reasons, 'missing_sms_opt_out');
    end if;
    if position('{{sender_identification}}' in m.body) = 0 then
      v_reasons := array_append(v_reasons, 'missing_sender_identification');
    end if;
  end if;

  return jsonb_build_object('allowed', cardinality(v_reasons) = 0, 'reasons', to_jsonb(v_reasons),
                            'checked_at', now(), 'commercial', growth.is_commercial(m.purpose));
end $$;

-- Status machine. Runs for every role, including the service role used by n8n.
create or replace function growth.enforce_message_transition() returns trigger
language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  v_gate jsonb;
  v_template growth.message_templates;
  v_approver_role text;
begin
  if tg_op = 'INSERT' then
    if new.status not in ('draft', 'pending_approval') then
      raise exception 'new messages must start as draft or pending_approval' using errcode = 'check_violation';
    end if;
    return new;
  end if;

  if new.status = old.status then
    -- Content can't change after approval.
    if old.status in ('approved', 'queued', 'sending', 'sent')
       and (new.body is distinct from old.body or new.subject is distinct from old.subject
            or new.to_email is distinct from old.to_email or new.to_phone is distinct from old.to_phone) then
      raise exception 'message content is locked once approved' using errcode = 'check_violation';
    end if;
    return new;
  end if;

  if new.status in ('approved', 'queued', 'sending')
     and (new.body is distinct from old.body or new.subject is distinct from old.subject
          or new.to_email is distinct from old.to_email or new.to_phone is distinct from old.to_phone
          or new.purpose is distinct from old.purpose or new.channel is distinct from old.channel) then
    raise exception 'change the content first, then change the status' using errcode = 'check_violation';
  end if;

  if old.status in ('sent', 'rejected', 'cancelled') then
    raise exception 'message % is final (%)', old.id, old.status using errcode = 'check_violation';
  end if;

  if new.status = 'approved' then
    select role into v_approver_role from growth.app_users where user_id = new.approved_by;
    if v_approver_role is null or v_approver_role not in ('owner', 'operator') then
      raise exception 'approval requires a human owner or operator' using errcode = 'insufficient_privilege';
    end if;
    if old.status not in ('draft', 'pending_approval') then
      raise exception 'cannot approve from %', old.status using errcode = 'check_violation';
    end if;
    new.approved_at := coalesce(new.approved_at, now());
  end if;

  if new.status = 'queued' then
    if old.status = 'approved' then
      null;
    elsif old.status in ('draft', 'pending_approval') and new.approval_mode = 'approved_template' then
      select * into v_template from growth.message_templates where id = new.template_id;
      if v_template.id is null or not v_template.active or v_template.approved_by is null then
        raise exception 'template is not approved and active' using errcode = 'insufficient_privilege';
      end if;
      if growth.is_commercial(new.purpose) then
        raise exception 'commercial messages always need per-message approval' using errcode = 'insufficient_privilege';
      end if;
      if v_template.purpose <> new.purpose or v_template.channel <> new.channel then
        raise exception 'template purpose/channel does not match message' using errcode = 'check_violation';
      end if;
    elsif old.status = 'failed' and new.attempt_count < 5 then
      null;  -- bounded retry
    else
      raise exception 'cannot queue from % without approval', old.status using errcode = 'insufficient_privilege';
    end if;
  end if;

  if new.status = 'sending' and old.status <> 'queued' then
    raise exception 'only queued messages can be sent' using errcode = 'check_violation';
  end if;
  if new.status = 'sent' and old.status <> 'sending' then
    raise exception 'only sending messages can be marked sent' using errcode = 'check_violation';
  end if;

  -- Re-check the gate at every step that moves a message toward the outside world.
  if new.status in ('approved', 'queued', 'sending') then
    v_gate := growth.check_send_allowed(new.id);
    new.compliance := v_gate;
    if not (v_gate ->> 'allowed')::boolean then
      raise exception 'send gate blocked message %: %', new.id, v_gate -> 'reasons'
        using errcode = 'check_violation';
    end if;
  end if;

  if new.status = 'sent' then
    new.sent_at := coalesce(new.sent_at, now());
  end if;

  perform growth.log_audit(growth.current_actor(),
                           'message.' || new.status, 'outbound_message', new.id::text,
                           jsonb_build_object('from', old.status, 'purpose', new.purpose, 'approved_by', new.approved_by));
  return new;
end $$;

create trigger outbound_transition before insert or update on growth.outbound_messages
  for each row execute function growth.enforce_message_transition();

-- Used by the sending workflow. Atomically claims due messages (queued → sending). Messages that no
-- longer pass the gate (for example, the person unsubscribed after approval) are marked blocked instead.
create or replace function growth.claim_messages_for_sending(p_limit integer default 10)
returns setof growth.outbound_messages
language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  r growth.outbound_messages;
  v_gate jsonb;
begin
  for r in
    select * from growth.outbound_messages
     where status = 'queued' and (scheduled_for is null or scheduled_for <= now())
     order by created_at
     limit least(greatest(p_limit, 1), 50)
     for update skip locked
  loop
    v_gate := growth.check_send_allowed(r.id);
    if (v_gate ->> 'allowed')::boolean then
      update growth.outbound_messages set status = 'sending', attempt_count = attempt_count + 1
       where id = r.id returning * into r;
      return next r;
    else
      update growth.outbound_messages set status = 'blocked', compliance = v_gate where id = r.id;
    end if;
  end loop;
end $$;

-- ---------------------------------------------------------------------------
-- Content drafts and publication history (Agent D). Nothing publishes without approval, and a draft
-- can't be approved while any factual claim is unverified.
-- ---------------------------------------------------------------------------
create table growth.content_drafts (
  id              uuid primary key default gen_random_uuid(),
  kind            text not null check (kind in
                    ('article', 'guide', 'checklist', 'calculator', 'demo_scenario', 'landing_page', 'social_post')),
  title           text not null check (length(title) <= 200),
  slug            text unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  target_segment  text,
  geography       text,
  body_md         text not null,
  research_question text,             -- the real owner question this answers
  sources         jsonb not null default '[]'::jsonb,   -- [{title, url, accessed_at}]
  claims          jsonb not null default '[]'::jsonb,   -- [{claim, source_url, verified}]
  status          text not null default 'draft' check (status in
                    ('draft', 'in_review', 'changes_requested', 'approved', 'published', 'rejected', 'archived')),
  created_by      text not null,
  reviewed_by     uuid,
  reviewed_at     timestamptz,
  review_note     text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index content_drafts_status_idx on growth.content_drafts (status, created_at desc);
create trigger content_drafts_touch before update on growth.content_drafts
  for each row execute function growth.touch_updated_at();

create or replace function growth.enforce_content_review() returns trigger
language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  if new.status = 'approved' and (tg_op = 'INSERT' or old.status is distinct from 'approved') then
    if not exists (select 1 from growth.app_users where user_id = new.reviewed_by and role in ('owner', 'operator')) then
      raise exception 'content approval requires a human owner or operator' using errcode = 'insufficient_privilege';
    end if;
    if exists (select 1 from jsonb_array_elements(new.claims) c where coalesce((c ->> 'verified')::boolean, false) = false) then
      raise exception 'content has unverified claims' using errcode = 'check_violation';
    end if;
    new.reviewed_at := coalesce(new.reviewed_at, now());
  end if;
  if new.status = 'published' and (tg_op = 'INSERT' or old.status <> 'approved') and
     (tg_op = 'INSERT' or old.status <> 'published') then
    raise exception 'only approved content can be published' using errcode = 'check_violation';
  end if;
  return new;
end $$;
create trigger content_drafts_review before insert or update on growth.content_drafts
  for each row execute function growth.enforce_content_review();

create table growth.content_publications (
  id            uuid primary key default gen_random_uuid(),
  draft_id      uuid not null references growth.content_drafts (id) on delete restrict,
  channel       text not null check (channel in ('website', 'blog', 'google_business_profile', 'linkedin', 'facebook', 'instagram', 'other')),
  url           text,
  published_by  uuid not null,
  published_at  timestamptz not null default now(),
  unpublished_at timestamptz,
  unique (draft_id, channel)
);

create or replace function growth.enforce_publication() returns trigger
language plpgsql security definer set search_path = growth, pg_temp as $$
begin
  if not exists (select 1 from growth.content_drafts where id = new.draft_id and status in ('approved', 'published')) then
    raise exception 'draft must be approved before publishing' using errcode = 'check_violation';
  end if;
  if not exists (select 1 from growth.app_users where user_id = new.published_by and role in ('owner', 'operator')) then
    raise exception 'publishing requires a human owner or operator' using errcode = 'insufficient_privilege';
  end if;
  update growth.content_drafts set status = 'published' where id = new.draft_id and status = 'approved';
  perform growth.log_audit('user:' || new.published_by, 'content.publish', 'content_draft', new.draft_id::text,
                           jsonb_build_object('channel', new.channel, 'url', new.url));
  return new;
end $$;
create trigger content_publications_check before insert on growth.content_publications
  for each row execute function growth.enforce_publication();

alter table growth.leads
  add constraint leads_content_fk foreign key (content_id) references growth.content_drafts (id) on delete set null;

-- One queue for everything waiting on a human.
create or replace view growth.approval_queue as
  select 'message'::text as item_type, id, purpose as subtype, coalesce(subject, left(body, 80)) as title,
         generated_by as requested_by, created_at
    from growth.outbound_messages where status = 'pending_approval'
  union all
  select 'content', id, kind, title, created_by, created_at
    from growth.content_drafts where status = 'in_review'
  union all
  select 'partner', p.id, p.partner_type, b.name, 'agent:WF-07', p.updated_at
    from growth.referral_partners p join growth.businesses b on b.id = p.business_id
   where p.status = 'proposal_drafted';
