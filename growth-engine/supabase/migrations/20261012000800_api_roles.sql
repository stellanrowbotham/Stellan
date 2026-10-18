-- FlowPilot Growth Engine · 0008 least-privilege roles for server code
-- growth_intake : the public website API. It can ONLY call the intake, unsubscribe and rate-limit
--                 functions. It can't read a single row, so a compromised API leaks nothing.
-- growth_worker : n8n. Reads and writes growth tables. RLS still applies to it (no BYPASSRLS),
--                 so it gets explicit policies; triggers enforce the send gate and approvals.
-- Both are NOLOGIN groups. Create the login users yourself with generated passwords (see docs/setup.md):
--   create role growth_api    login password '<generated>' in role growth_intake;
--   create role growth_n8n    login password '<generated>' in role growth_worker;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'growth_intake') then
    create role growth_intake nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'growth_worker') then
    create role growth_worker nologin;
  end if;
end $$;

grant usage on schema growth to growth_intake, growth_worker;

grant execute on function growth.intake_lead(jsonb), growth.process_unsubscribe(text, text, text),
  growth.hit_rate_limit(text, integer, integer) to growth_intake;

grant select, insert, update on all tables in schema growth to growth_worker;
grant usage, select on all sequences in schema growth to growth_worker;
grant execute on all functions in schema growth to growth_worker;
-- Workers never delete history, never touch users, never lift suppressions.
revoke update on growth.app_users from growth_worker;
revoke insert on growth.app_users from growth_worker;
revoke execute on function growth.remove_suppression(uuid, text) from growth_worker;

do $$
declare t record;
begin
  for t in select tablename from pg_tables where schemaname = 'growth' and tablename <> 'app_users' loop
    execute format('create policy worker_all on growth.%I for all to growth_worker using (true) with check (true)', t.tablename);
  end loop;
end $$;
create policy worker_read on growth.app_users for select to growth_worker using (true);
