-- FlowPilot Growth Engine · 0002 prospects
-- Businesses (prospects, partners, customers), source observations and evidence, research reports,
-- the configurable scoring model, lead scores, and referral partners.

-- ---------------------------------------------------------------------------
-- Businesses: one row per real-world business, deduplicated by normalized domain,
-- or by (name, city) when there is no website.
-- ---------------------------------------------------------------------------
create table growth.businesses (
  id                 uuid primary key default gen_random_uuid(),
  name               text not null check (length(name) between 1 and 200),
  website_url        text check (website_url is null or website_url ~* '^https?://'),
  normalized_domain  text generated always as (growth.normalize_domain(website_url)) stored,
  phone_normalized   text,
  service_category   text,              -- landscaping, hvac, plumbing, electrical, roofing, web_design, ...
  service_area       text,              -- free text as published, e.g. "Kitchener-Waterloo and Guelph"
  city               text,
  province           text not null default 'ON',
  relationship       text not null default 'prospect'
                     check (relationship in ('prospect', 'partner_candidate', 'partner', 'customer', 'excluded')),
  status             text not null default 'discovered'
                     check (status in ('discovered', 'researching', 'researched', 'qualified', 'not_a_fit', 'archived')),
  first_source       text,              -- provider that first found it: google_places, brave_search, manual, inbound, ...
  first_source_url   text,
  discovered_at      timestamptz not null default now(),
  last_seen_at       timestamptz not null default now(),
  do_not_contact     boolean not null default false,   -- business asked not to be contacted, or a published no-solicitation notice
  is_test            boolean not null default false,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);
create unique index businesses_domain_uniq on growth.businesses (normalized_domain) where normalized_domain is not null;
create unique index businesses_name_city_uniq on growth.businesses (lower(name), lower(coalesce(city, '')))
  where normalized_domain is null;
create index businesses_category_idx on growth.businesses (service_category, status);
create index businesses_phone_idx on growth.businesses (phone_normalized) where phone_normalized is not null;
create trigger businesses_touch before update on growth.businesses
  for each row execute function growth.touch_updated_at();

-- Insert-or-merge used by WF-01 and WF-07. Returns the id and whether the row is new.
-- Never overwrites a known value with null; refreshes last_seen_at.
create or replace function growth.upsert_business(p jsonb)
returns table (business_id uuid, created boolean)
language plpgsql security definer set search_path = growth, pg_temp as $$
declare
  v_domain text := growth.normalize_domain(p ->> 'website_url');
  v_id uuid;
begin
  if coalesce(btrim(p ->> 'name'), '') = '' then
    raise exception 'upsert_business: name is required' using errcode = 'check_violation';
  end if;

  if v_domain is not null then
    select id into v_id from growth.businesses where normalized_domain = v_domain;
  else
    select id into v_id from growth.businesses
     where normalized_domain is null
       and lower(name) = lower(btrim(p ->> 'name'))
       and lower(coalesce(city, '')) = lower(coalesce(p ->> 'city', ''));
  end if;

  if v_id is not null then
    update growth.businesses b set
      phone_normalized = coalesce(growth.normalize_phone(p ->> 'phone'), b.phone_normalized),
      service_category = coalesce(p ->> 'service_category', b.service_category),
      service_area     = coalesce(p ->> 'service_area', b.service_area),
      city             = coalesce(b.city, p ->> 'city'),
      last_seen_at     = now()
    where b.id = v_id;
    return query select v_id, false;
    return;
  end if;

  insert into growth.businesses (name, website_url, phone_normalized, service_category, service_area, city,
                                 province, relationship, first_source, first_source_url, is_test)
  values (btrim(p ->> 'name'),
          nullif(p ->> 'website_url', ''),
          growth.normalize_phone(p ->> 'phone'),
          p ->> 'service_category',
          p ->> 'service_area',
          p ->> 'city',
          coalesce(p ->> 'province', 'ON'),
          coalesce(p ->> 'relationship', 'prospect'),
          p ->> 'source',
          p ->> 'source_url',
          coalesce((p ->> 'is_test')::boolean, false))
  returning id into v_id;
  return query select v_id, true;
end $$;

-- ---------------------------------------------------------------------------
-- Source observations: every fact about a business or audited site, with where and when it was seen.
-- Shared by discovery (WF-01), research (WF-02) and the public Inquiry Check (WF-03).
-- ---------------------------------------------------------------------------
create table growth.source_observations (
  id                 uuid primary key default gen_random_uuid(),
  business_id        uuid references growth.businesses (id) on delete cascade,
  audit_session_id   uuid,              -- FK added in 0003 once audit_sessions exists
  observation_type   text not null,     -- listing, contact_form, quote_form, booking_link, phone_visible, email_visible,
                                        -- click_to_call, mobile_viewport, next_step_clarity, services_listed, ...
  value              jsonb not null,    -- structured value, e.g. {"present": true, "fields": 7}
  evidence_excerpt   text check (length(evidence_excerpt) <= 1000),  -- short quote from the page, never a whole page
  source_url         text not null,
  method             text not null check (method in ('search_api', 'places_api', 'directory', 'page_fetch', 'manual', 'inbound')),
  provider           text,
  verification       text not null default 'verified' check (verification in ('verified', 'inferred', 'unverifiable')),
  observed_at        timestamptz not null default now(),
  last_confirmed_at  timestamptz not null default now(),
  stale_after        timestamptz not null default now() + interval '30 days',
  value_hash         text generated always as (md5(observation_type || '|' || source_url || '|' || value::text)) stored,
  created_at         timestamptz not null default now(),
  check (business_id is not null or audit_session_id is not null)
);
create unique index source_observations_dedupe
  on growth.source_observations (coalesce(business_id, audit_session_id), value_hash);
create index source_observations_business_idx on growth.source_observations (business_id, observation_type);
create index source_observations_stale_idx on growth.source_observations (stale_after);

-- ---------------------------------------------------------------------------
-- Scoring model: versioned, configurable 100-point model. Exactly one active version.
-- ---------------------------------------------------------------------------
create table growth.scoring_models (
  version     text primary key,
  weights     jsonb not null,           -- {"component": max_points, ...}; must sum to 100
  rubric      jsonb not null default '{}'::jsonb,   -- human-readable criteria per component
  active      boolean not null default false,
  created_at  timestamptz not null default now()
);
create unique index scoring_models_one_active on growth.scoring_models (active) where active;

create or replace function growth.check_scoring_weights() returns trigger
language plpgsql as $$
declare v_sum numeric;
begin
  select coalesce(sum(value::numeric), 0) into v_sum from jsonb_each_text(new.weights);
  if v_sum <> 100 then
    raise exception 'scoring model % weights sum to %, expected 100', new.version, v_sum
      using errcode = 'check_violation';
  end if;
  return new;
end $$;
create trigger scoring_models_weights before insert or update on growth.scoring_models
  for each row execute function growth.check_scoring_weights();

insert into growth.scoring_models (version, weights, rubric, active) values (
  'v1',
  '{"target_fit": 30, "observable_opportunity": 30, "service_area": 15, "suitability": 15, "evidence_quality": 10}',
  '{
     "target_fit": "Home-service business in a priority segment that takes inquiries or estimate requests.",
     "observable_opportunity": "Publicly visible gaps: no quote form, hard-to-find contact, no booking or next step, no mobile click-to-call.",
     "service_area": "Serves southwestern Ontario communities FlowPilot can support in person.",
     "suitability": "Size and setup suggest a $300-$1,000 system fits (independent operator, existing website, active listing).",
     "evidence_quality": "Share of findings that are verified from a fresh page fetch rather than inferred."
   }',
  true
);

-- ---------------------------------------------------------------------------
-- Research reports (Agent B). One row per run; the AI output is stored only after schema validation.
-- ---------------------------------------------------------------------------
create table growth.research_reports (
  id                  uuid primary key default gen_random_uuid(),
  business_id         uuid not null references growth.businesses (id) on delete cascade,
  summary             text not null check (length(summary) <= 2000),
  findings            jsonb not null default '[]'::jsonb,   -- [{claim, verification, source_url, observation_id}]
  assumptions         jsonb not null default '[]'::jsonb,   -- things believed but not verified
  unknowns            jsonb not null default '[]'::jsonb,   -- what could not be checked
  recommended_action  text not null check (recommended_action in
                        ('offer_inquiry_check', 'partner_outreach_review', 'monitor', 'not_a_fit', 'needs_human')),
  llm_provider        text,
  llm_model           text,
  prompt_version      text,
  output_schema       text not null default 'research_report.v1',
  workflow_run_id     uuid,
  created_at          timestamptz not null default now(),
  check (jsonb_typeof(findings) = 'array' and jsonb_typeof(assumptions) = 'array' and jsonb_typeof(unknowns) = 'array')
);
create index research_reports_business_idx on growth.research_reports (business_id, created_at desc);

create table growth.lead_scores (
  id                  uuid primary key default gen_random_uuid(),
  business_id         uuid not null references growth.businesses (id) on delete cascade,
  research_report_id  uuid references growth.research_reports (id) on delete set null,
  model_version       text not null references growth.scoring_models (version),
  components          jsonb not null,           -- {"target_fit": 24, ...}
  total               integer not null check (total between 0 and 100),
  rationale           text,
  scored_at           timestamptz not null default now()
);
create index lead_scores_business_idx on growth.lead_scores (business_id, scored_at desc);
create index lead_scores_total_idx on growth.lead_scores (total desc);

-- Components must match the model's keys, stay within each weight, and add up to total.
create or replace function growth.check_lead_score() returns trigger
language plpgsql as $$
declare
  v_weights jsonb;
  v_key text;
  v_sum integer := 0;
  v_val integer;
begin
  select weights into v_weights from growth.scoring_models where version = new.model_version;
  for v_key in select jsonb_object_keys(new.components) loop
    if not v_weights ? v_key then
      raise exception 'unknown score component %', v_key using errcode = 'check_violation';
    end if;
    v_val := (new.components ->> v_key)::integer;
    if v_val < 0 or v_val > (v_weights ->> v_key)::integer then
      raise exception 'component % = % outside 0..%', v_key, v_val, v_weights ->> v_key using errcode = 'check_violation';
    end if;
    v_sum := v_sum + v_val;
  end loop;
  if (select count(*) from jsonb_object_keys(v_weights)) <> (select count(*) from jsonb_object_keys(new.components)) then
    raise exception 'score must include every component of model %', new.model_version using errcode = 'check_violation';
  end if;
  if v_sum <> new.total then
    raise exception 'components sum to % but total is %', v_sum, new.total using errcode = 'check_violation';
  end if;
  return new;
end $$;
create trigger lead_scores_check before insert or update on growth.lead_scores
  for each row execute function growth.check_lead_score();

-- ---------------------------------------------------------------------------
-- Referral partners (Agent F). No agreement terms are stored unless Stellan records them.
-- ---------------------------------------------------------------------------
create table growth.referral_partners (
  id                       uuid primary key default gen_random_uuid(),
  business_id              uuid not null unique references growth.businesses (id) on delete cascade,
  partner_type             text not null check (partner_type in
                             ('web_designer', 'marketing_consultant', 'it_provider', 'bookkeeper', 'business_service', 'other')),
  public_services          text,           -- as published, with the source in source_observations
  relevance                text,           -- why a partnership might make sense (draft, reviewed by Stellan)
  status                   text not null default 'identified' check (status in
                             ('identified', 'researched', 'proposal_drafted', 'approved_to_contact', 'contacted',
                              'in_discussion', 'active', 'declined', 'paused')),
  approved_contact_method  text check (approved_contact_method in ('warm_intro', 'inbound', 'email', 'phone', 'in_person', 'linkedin')),
  agreement_notes          text,           -- only what Stellan actually agreed; never AI-generated
  agreement_recorded_by    uuid,
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now(),
  check (agreement_notes is null or agreement_recorded_by is not null)
);
create trigger referral_partners_touch before update on growth.referral_partners
  for each row execute function growth.touch_updated_at();
