-- FlowPilot Growth Engine · 0007 lead intake and unsubscribe
-- One atomic, idempotent function per public action. The API validates and normalizes input first;
-- these functions enforce the rules again inside the transaction. Both are service_role only.

alter table growth.referral_partners add column referral_code text unique
  check (referral_code is null or referral_code ~ '^[a-z0-9-]{3,40}$');

-- Input (validated by the API):
-- { idempotency_key, purpose, source, source_detail, name, email, phone, business_name, business_website,
--   industry, message, utm: {}, referrer_domain, anonymous_id, ip_hash, referral_code, audit_session_id,
--   is_test, consents: [{channel, purpose, granted, wording, form_id, form_version, source_url}] }
-- Output: { lead_id, duplicate, needs_human, suppressed }
create or replace function growth.intake_lead(p jsonb)
returns jsonb language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  v_key text := p ->> 'idempotency_key';
  v_email text := growth.normalize_email(p ->> 'email');
  v_phone text := growth.normalize_phone(p ->> 'phone');
  v_is_test boolean := coalesce((p ->> 'is_test')::boolean, false);
  v_existing growth.leads;
  v_contact_id uuid;
  v_business_id uuid;
  v_partner_id uuid;
  v_lead_id uuid;
  v_suppressed boolean;
  v_needs_human boolean := false;
  v_reason text;
  c jsonb;
begin
  if coalesce(v_key, '') = '' then
    raise exception 'idempotency_key is required' using errcode = 'check_violation';
  end if;
  if v_email is null then
    raise exception 'email is required' using errcode = 'check_violation';
  end if;

  select * into v_existing from growth.leads where idempotency_key = v_key;
  if found then
    return jsonb_build_object('lead_id', v_existing.id, 'duplicate', true,
                              'needs_human', v_existing.needs_human, 'suppressed', growth.is_suppressed(v_email, v_phone));
  end if;

  perform set_config('growth.actor', 'api:intake', true);

  -- Contact: one per email. Keep known values unless new ones are supplied.
  insert into growth.contacts (email_normalized, name, phone_normalized, is_test)
  values (v_email, nullif(btrim(p ->> 'name'), ''), v_phone, v_is_test)
  on conflict (email_normalized) do update set
    name = coalesce(excluded.name, growth.contacts.name),
    phone_normalized = coalesce(excluded.phone_normalized, growth.contacts.phone_normalized)
  returning id into v_contact_id;

  if nullif(p ->> 'business_website', '') is not null then
    select business_id into v_business_id from growth.upsert_business(jsonb_build_object(
      'name', coalesce(nullif(p ->> 'business_name', ''), growth.normalize_domain(p ->> 'business_website')),
      'website_url', p ->> 'business_website',
      'service_category', p ->> 'industry',
      'source', 'inbound',
      'is_test', v_is_test));
    update growth.contacts set business_id = coalesce(business_id, v_business_id) where id = v_contact_id;
  end if;

  if nullif(p ->> 'referral_code', '') is not null then
    select id into v_partner_id from growth.referral_partners where referral_code = lower(p ->> 'referral_code');
  end if;

  v_suppressed := growth.is_suppressed(v_email, v_phone);
  if v_suppressed then
    v_needs_human := true;
    v_reason := 'This person is on the suppression list. Automated messages are blocked; reply personally if appropriate.';
  end if;

  insert into growth.leads (contact_id, business_id, purpose, source, source_detail, utm, referrer_domain, partner_id,
                            industry, business_name, business_website, message, needs_human, needs_human_reason,
                            idempotency_key, ip_hash, is_test)
  values (v_contact_id, v_business_id, p ->> 'purpose', p ->> 'source', p ->> 'source_detail',
          coalesce(p -> 'utm', '{}'::jsonb), p ->> 'referrer_domain', v_partner_id,
          p ->> 'industry', nullif(p ->> 'business_name', ''), nullif(p ->> 'business_website', ''),
          nullif(p ->> 'message', ''), v_needs_human, v_reason, v_key, p ->> 'ip_hash', v_is_test)
  returning id into v_lead_id;

  -- Replying to the person's own request needs no marketing consent; record the basis anyway.
  insert into growth.consent_records (contact_id, email_normalized, channel, purpose, basis, granted,
                                      wording_shown, form_id, form_version, source_url, lead_id, ip_hash)
  values (v_contact_id, v_email, 'email', 'request_response', 'exempt_response', true,
          null, p ->> 'source', null, null, v_lead_id, p ->> 'ip_hash');

  -- Every choice exactly as made, including boxes left unticked.
  for c in select * from jsonb_array_elements(coalesce(p -> 'consents', '[]'::jsonb)) loop
    if (c ->> 'purpose') not in ('demo_email', 'follow_up', 'marketing', 'sms_updates') then
      raise exception 'unsupported consent purpose %', c ->> 'purpose' using errcode = 'check_violation';
    end if;
    if coalesce((c ->> 'granted')::boolean, false) and coalesce(btrim(c ->> 'wording'), '') = '' then
      raise exception 'consent wording is required for %', c ->> 'purpose' using errcode = 'check_violation';
    end if;
    if (c ->> 'channel') = 'sms' and v_phone is null then
      raise exception 'sms consent needs a phone number' using errcode = 'check_violation';
    end if;
    insert into growth.consent_records (contact_id, email_normalized, phone_normalized, channel, purpose, basis, granted,
                                        wording_shown, form_id, form_version, source_url, lead_id, ip_hash)
    values (v_contact_id,
            case when c ->> 'channel' = 'email' then v_email end,
            case when c ->> 'channel' = 'sms' then v_phone end,
            c ->> 'channel', c ->> 'purpose', 'express', coalesce((c ->> 'granted')::boolean, false),
            nullif(c ->> 'wording', ''), c ->> 'form_id', c ->> 'form_version', c ->> 'source_url',
            v_lead_id, p ->> 'ip_hash');
  end loop;

  if nullif(p ->> 'audit_session_id', '') is not null then
    update growth.audit_sessions set lead_id = v_lead_id, business_id = coalesce(business_id, v_business_id)
     where id = (p ->> 'audit_session_id')::uuid and lead_id is null;
  end if;

  insert into growth.analytics_events (event_name, anonymous_id, lead_id, audit_session_id, partner_id, channel,
                                       source, medium, campaign, path, industry, dedupe_key, is_test, properties)
  values ('lead_submitted', p ->> 'anonymous_id', v_lead_id, nullif(p ->> 'audit_session_id', '')::uuid, v_partner_id,
          case when v_partner_id is not null then 'referral_partner' else coalesce(p ->> 'channel', 'unknown') end,
          p -> 'utm' ->> 'source', p -> 'utm' ->> 'medium', p -> 'utm' ->> 'campaign', p ->> 'source_detail',
          p ->> 'industry', 'lead_submitted:' || v_lead_id, v_is_test,
          jsonb_build_object('purpose', p ->> 'purpose', 'form_source', p ->> 'source'));

  -- No personal data in the event; consumers load the lead by id.
  insert into growth.event_outbox (topic, payload, dedupe_key)
  values ('lead.created',
          jsonb_build_object('lead_id', v_lead_id, 'purpose', p ->> 'purpose', 'source', p ->> 'source',
                             'needs_human', v_needs_human, 'suppressed', v_suppressed, 'is_test', v_is_test),
          'lead.created:' || v_lead_id);

  perform growth.log_audit('api:intake', 'lead.create', 'lead', v_lead_id::text,
                           jsonb_build_object('purpose', p ->> 'purpose', 'source', p ->> 'source',
                                              'consents', (select coalesce(jsonb_agg(jsonb_build_object(
                                                  'purpose', x ->> 'purpose', 'channel', x ->> 'channel',
                                                  'granted', coalesce((x ->> 'granted')::boolean, false))), '[]'::jsonb)
                                                 from jsonb_array_elements(coalesce(p -> 'consents', '[]'::jsonb)) x)));

  return jsonb_build_object('lead_id', v_lead_id, 'duplicate', false, 'needs_human', v_needs_human, 'suppressed', v_suppressed);
end $$;

-- Unsubscribe: suppress the address, record the withdrawal for every commercial purpose, and cancel
-- anything not yet sent. Idempotent and immediate (CASL allows up to 10 business days; we do it now).
create or replace function growth.process_unsubscribe(p_email text, p_phone text, p_source text)
returns jsonb language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  v_email text := growth.normalize_email(p_email);
  v_phone text := growth.normalize_phone(p_phone);
  v_contact_id uuid;
  v_cancelled integer;
  v_purpose text;
begin
  if v_email is null and v_phone is null then
    raise exception 'email or phone is required' using errcode = 'check_violation';
  end if;
  perform set_config('growth.actor', coalesce(p_source, 'unsubscribe'), true);
  perform growth.add_suppression(v_email, v_phone, null, 'unsubscribe', coalesce(p_source, 'unsubscribe_link'));

  select id into v_contact_id from growth.contacts where email_normalized = v_email;
  foreach v_purpose in array array['follow_up', 'marketing'] loop
    if v_email is not null then
      insert into growth.consent_records (contact_id, email_normalized, channel, purpose, basis, granted, form_id)
      values (v_contact_id, v_email, 'email', v_purpose, 'withdrawn', false, p_source);
    end if;
  end loop;
  if v_phone is not null then
    insert into growth.consent_records (contact_id, phone_normalized, channel, purpose, basis, granted, form_id)
    values (v_contact_id, v_phone, 'sms', 'sms_updates', 'withdrawn', false, p_source);
  end if;

  update growth.outbound_messages set status = 'cancelled', last_error = 'recipient unsubscribed'
   where status in ('draft', 'pending_approval', 'approved', 'queued', 'failed')
     and ((v_email is not null and lower(to_email) = v_email) or (v_phone is not null and growth.normalize_phone(to_phone) = v_phone));
  get diagnostics v_cancelled = row_count;

  return jsonb_build_object('suppressed', true, 'cancelled_messages', v_cancelled);
end $$;

revoke all on function growth.intake_lead(jsonb), growth.process_unsubscribe(text, text, text) from public, anon, authenticated;
grant execute on function growth.intake_lead(jsonb), growth.process_unsubscribe(text, text, text) to service_role;
