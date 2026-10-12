-- FlowPilot Growth Engine · 0006 security
-- Row-level security on every table, least-privilege grants, and locked-down functions.
--   anon           : no access at all. Public traffic goes through the API, which runs server-side.
--   authenticated  : dashboard users; what they see depends on growth.app_users.role.
--   service_role   : the API and n8n (server-side only, never in a browser). Bypasses RLS but NOT the
--                    triggers, so the send gate, append-only tables and approval rules still apply.

revoke all on schema growth from public;
revoke all on all tables in schema growth from public, anon, authenticated;
revoke all on all functions in schema growth from public, anon, authenticated;
revoke all on all sequences in schema growth from public, anon, authenticated;

grant usage on schema growth to authenticated, service_role;
grant all on all tables in schema growth to service_role;
grant all on all sequences in schema growth to service_role;
grant execute on all functions in schema growth to service_role;

alter default privileges in schema growth revoke all on tables from public, anon, authenticated;
alter default privileges in schema growth revoke execute on functions from public, anon, authenticated;
alter default privileges in schema growth grant all on tables to service_role;
alter default privileges in schema growth grant execute on functions to service_role;

-- Helpers the policies call (they only read the caller's own role).
grant execute on function growth.current_app_role(), growth.is_staff(), growth.is_member(),
  growth.normalize_domain(text), growth.normalize_email(text), growth.normalize_phone(text),
  growth.is_commercial(text) to authenticated;
-- Owner-only inside; safe to expose.
grant execute on function growth.remove_suppression(uuid, text), growth.check_budget(text, numeric),
  growth.current_actor() to authenticated;

-- Views evaluate RLS as the querying user.
alter view growth.consent_current set (security_invoker = true);
alter view growth.approval_queue set (security_invoker = true);

-- ---------------------------------------------------------------------------
-- Enable RLS everywhere.
-- ---------------------------------------------------------------------------
do $$
declare t record;
begin
  for t in select tablename from pg_tables where schemaname = 'growth' loop
    execute format('alter table growth.%I enable row level security', t.tablename);
  end loop;
end $$;

-- ---------------------------------------------------------------------------
-- Personal data: owner + operator only.
-- ---------------------------------------------------------------------------
do $$
declare t text;
begin
  foreach t in array array['contacts', 'leads', 'lead_stage_history', 'consent_records', 'suppression_list',
                           'audit_sessions', 'outbound_messages', 'bookings', 'deals', 'audit_log'] loop
    execute format('grant select on growth.%I to authenticated', t);
    execute format('create policy staff_read on growth.%I for select to authenticated using (growth.is_staff())', t);
  end loop;
end $$;

-- Non-personal operational data: any app member (viewer too).
do $$
declare t text;
begin
  foreach t in array array['businesses', 'source_observations', 'research_reports', 'lead_scores', 'scoring_models',
                           'referral_partners', 'content_drafts', 'content_publications', 'analytics_events',
                           'workflow_runs', 'workflow_errors', 'ai_usage', 'spending_limits', 'retention_policies',
                           'message_templates'] loop
    execute format('grant select on growth.%I to authenticated', t);
    execute format('create policy member_read on growth.%I for select to authenticated using (growth.is_member())', t);
  end loop;
end $$;

-- app_users: everyone sees their own row; the owner sees and manages all.
grant select, insert, update, delete on growth.app_users to authenticated;
create policy self_read on growth.app_users for select to authenticated
  using (user_id = auth.uid() or growth.current_app_role() = 'owner');
create policy owner_write on growth.app_users for all to authenticated
  using (growth.current_app_role() = 'owner') with check (growth.current_app_role() = 'owner');

-- ---------------------------------------------------------------------------
-- Staff writes (dashboard actions). Triggers still enforce the business rules.
-- ---------------------------------------------------------------------------
grant update (stage, qualification, needs_human, needs_human_reason, lost_reason, industry, partner_id)
  on growth.leads to authenticated;
create policy staff_update on growth.leads for update to authenticated
  using (growth.is_staff()) with check (growth.is_staff());

grant update (status, approved_by, approved_at, rejected_reason, subject, body, scheduled_for)
  on growth.outbound_messages to authenticated;
create policy staff_update on growth.outbound_messages for update to authenticated
  using (growth.is_staff())
  -- Staff can only approve as themselves.
  with check (growth.is_staff() and (approved_by is null or approved_by = auth.uid()));

grant update (status, reviewed_by, review_note, title, body_md, claims, sources, slug)
  on growth.content_drafts to authenticated;
create policy staff_update on growth.content_drafts for update to authenticated
  using (growth.is_staff()) with check (growth.is_staff() and (reviewed_by is null or reviewed_by = auth.uid()));

grant insert on growth.content_publications to authenticated;
create policy staff_insert on growth.content_publications for insert to authenticated
  with check (growth.is_staff() and published_by = auth.uid());

grant update (status, relevance, approved_contact_method, agreement_notes, agreement_recorded_by)
  on growth.referral_partners to authenticated;
create policy staff_update on growth.referral_partners for update to authenticated
  using (growth.is_staff())
  with check (growth.is_staff() and (agreement_recorded_by is null or agreement_recorded_by = auth.uid()));

grant update (status, relationship, do_not_contact, service_category, service_area) on growth.businesses to authenticated;
create policy staff_update on growth.businesses for update to authenticated
  using (growth.is_staff()) with check (growth.is_staff());

grant insert, update on growth.deals to authenticated;
create policy staff_insert on growth.deals for insert to authenticated with check (growth.is_staff());
create policy staff_update on growth.deals for update to authenticated using (growth.is_staff()) with check (growth.is_staff());

grant insert, update on growth.bookings to authenticated;
create policy staff_insert on growth.bookings for insert to authenticated with check (growth.is_staff());
create policy staff_update on growth.bookings for update to authenticated using (growth.is_staff()) with check (growth.is_staff());

-- Recording an opt-out by hand (e.g. someone replied "stop"). Lifting one goes through remove_suppression().
grant insert on growth.suppression_list to authenticated;
create policy staff_insert on growth.suppression_list for insert to authenticated with check (growth.is_staff());
grant insert on growth.consent_records to authenticated;
create policy staff_insert on growth.consent_records for insert to authenticated with check (growth.is_staff());

grant update (status, resolved_at) on growth.workflow_errors to authenticated;
create policy staff_update on growth.workflow_errors for update to authenticated
  using (growth.is_staff()) with check (growth.is_staff());

-- Owner-only configuration.
grant insert, update on growth.scoring_models, growth.spending_limits, growth.message_templates to authenticated;
create policy owner_insert on growth.scoring_models for insert to authenticated with check (growth.current_app_role() = 'owner');
create policy owner_update on growth.scoring_models for update to authenticated
  using (growth.current_app_role() = 'owner') with check (growth.current_app_role() = 'owner');
create policy owner_insert on growth.spending_limits for insert to authenticated with check (growth.current_app_role() = 'owner');
create policy owner_update on growth.spending_limits for update to authenticated
  using (growth.current_app_role() = 'owner') with check (growth.current_app_role() = 'owner');
create policy owner_insert on growth.message_templates for insert to authenticated with check (growth.current_app_role() = 'owner');
create policy owner_update on growth.message_templates for update to authenticated
  using (growth.current_app_role() = 'owner') with check (growth.current_app_role() = 'owner');

-- rate_limits and event_outbox stay service_role only (no policies for authenticated = no rows).
