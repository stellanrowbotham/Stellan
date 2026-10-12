-- FlowPilot Growth Engine · 0001 foundation
-- Schema, helper functions, app users/roles, and the append-only audit log.
-- Everything lives in the `growth` schema, which is NOT exposed through the Supabase Data API by default.
-- Server code and n8n reach it through a server-side connection; the dashboard reads it as an
-- authenticated user under row-level security (see 20261012000600_security.sql).

create extension if not exists pgcrypto;

create schema if not exists growth;
comment on schema growth is 'FlowPilot Growth Engine: CRM, consent, agents, analytics.';

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------

-- Lowercase host with scheme, credentials, "www.", port, path, query and trailing dot removed.
-- normalize_domain('HTTPS://www.Example-Landscaping.ca:443/contact?x=1') = 'example-landscaping.ca'
create or replace function growth.normalize_domain(input text) returns text
language sql immutable parallel safe as $$
  select nullif(
    regexp_replace(
      regexp_replace(
        regexp_replace(
          regexp_replace(lower(btrim(coalesce(input, ''))), '^[a-z][a-z0-9+.-]*://', ''),  -- scheme
        '^[^/@]*@', ''),                                                                    -- credentials
      '[:/?#].*$', ''),                                                                     -- port, path, query
    '^www\.|\.$', '', 'g'),                                                                 -- www. and trailing dot
  '')
$$;

create or replace function growth.normalize_email(input text) returns text
language sql immutable parallel safe as $$
  select nullif(lower(btrim(coalesce(input, ''))), '')
$$;

-- Digits only, North American numbers normalized to 11 digits starting with 1. Returns null if too short.
create or replace function growth.normalize_phone(input text) returns text
language sql immutable parallel safe as $$
  with d as (select regexp_replace(coalesce(input, ''), '[^0-9]', '', 'g') as digits)
  select case
    when length(digits) = 10 then '1' || digits
    when length(digits) between 11 and 15 then digits
    else null
  end from d
$$;

create or replace function growth.touch_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

-- Used by append-only tables. Only a SECURITY DEFINER function owned by the schema owner (for example
-- growth.remove_suppression) can allow a change: it sets growth.allow_mutation = 'on' for its transaction.
-- Anyone can set a custom setting, so the flag alone is not enough: the change must also run as the
-- schema owner, which ordinary sessions (service_role, n8n, dashboard users) never do.
create or replace function growth.forbid_mutation() returns trigger
language plpgsql as $$
begin
  if coalesce(current_setting('growth.allow_mutation', true), 'off') = 'on'
     and current_user = (select r.rolname from pg_namespace n join pg_roles r on r.oid = n.nspowner
                          where n.nspname = 'growth') then
    return coalesce(new, old);
  end if;
  raise exception '% on %.% is not allowed: table is append-only', tg_op, tg_table_schema, tg_table_name
    using errcode = 'insufficient_privilege';
end $$;

-- ---------------------------------------------------------------------------
-- App users and roles
--   owner    : Stellan. Everything, including approvals and suppression removal.
--   operator : a trusted helper. Reads everything, works leads, approves messages and content.
--   viewer   : reads aggregate/operational data, never personal data.
-- ---------------------------------------------------------------------------
create table growth.app_users (
  user_id     uuid primary key,              -- = auth.users.id
  email       text not null,
  role        text not null check (role in ('owner', 'operator', 'viewer')),
  created_at  timestamptz not null default now()
);

create or replace function growth.current_app_role() returns text
language sql stable security definer set search_path = growth, pg_temp as $$
  select role from growth.app_users where user_id = auth.uid()
$$;

create or replace function growth.is_staff() returns boolean
language sql stable security definer set search_path = growth, pg_temp as $$
  select coalesce(growth.current_app_role() in ('owner', 'operator'), false)
$$;

create or replace function growth.is_member() returns boolean
language sql stable security definer set search_path = growth, pg_temp as $$
  select growth.current_app_role() is not null
$$;

-- ---------------------------------------------------------------------------
-- Audit log: every approval, external action and privileged change. Append-only.
-- actor: 'user:<uuid>', 'agent:<WF-xx>', 'api:<endpoint>' or 'system'.
-- ---------------------------------------------------------------------------
create table growth.audit_log (
  id           bigint generated always as identity primary key,
  at           timestamptz not null default now(),
  actor        text not null,
  action       text not null,
  entity_type  text not null,
  entity_id    text,
  details      jsonb not null default '{}'::jsonb
);
create index audit_log_entity_idx on growth.audit_log (entity_type, entity_id, at desc);
create index audit_log_at_idx on growth.audit_log (at desc);

create trigger audit_log_append_only
  before update or delete on growth.audit_log
  for each row execute function growth.forbid_mutation();

-- Who is acting: a signed-in dashboard user, else the label a workflow set, else the database role.
create or replace function growth.current_actor() returns text
language sql stable as $$
  select coalesce('user:' || auth.uid()::text, nullif(current_setting('growth.actor', true), ''), 'db:' || session_user)
$$;

create or replace function growth.log_audit(p_actor text, p_action text, p_entity_type text,
                                            p_entity_id text, p_details jsonb default '{}'::jsonb)
returns void language sql security definer set search_path = growth, pg_temp as $$
  insert into growth.audit_log (actor, action, entity_type, entity_id, details)
  values (p_actor, p_action, p_entity_type, p_entity_id, coalesce(p_details, '{}'::jsonb))
$$;
