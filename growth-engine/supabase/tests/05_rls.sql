begin;
\ir _helpers.psql
select growth.intake_lead('{"idempotency_key":"rls-1","purpose":"consultation","source":"website_form","email":"rls@example.com","is_test":true}');
select growth.upsert_business('{"name":"Visible Co","website_url":"https://visible.example","is_test":true}');

-- anon: no access to anything.
set local role anon;
select pg_temp.expect_error($$select * from growth.leads$$, 'permission denied');
select pg_temp.expect_error($$select * from growth.businesses$$, 'permission denied');
select pg_temp.expect_error($$select growth.intake_lead('{}')$$, 'permission denied');
reset role;

-- Signed in but not an app user: sees nothing.
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a4","role":"authenticated"}', true);
do $$ begin
  assert (select count(*) from growth.leads) = 0, 'stranger sees no leads';
  assert (select count(*) from growth.businesses) = 0, 'stranger sees no businesses';
end $$;
select pg_temp.expect_error($$select growth.intake_lead('{}')$$, 'permission denied');
select pg_temp.expect_error($$select * from growth.event_outbox$$, 'permission denied');

-- Viewer: operational data yes, personal data no.
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a3","role":"authenticated"}', true);
do $$ begin
  assert (select count(*) from growth.businesses) >= 1, 'viewer sees businesses';
  assert (select count(*) from growth.leads) = 0, 'viewer sees no leads';
  assert (select count(*) from growth.contacts) = 0, 'viewer sees no contacts';
  assert (select count(*) from growth.consent_records) = 0, 'viewer sees no consent records';
end $$;
do $$ declare n integer; begin
  update growth.spending_limits set daily_usd = 999;
  get diagnostics n = row_count;
  assert n = 0, 'viewer cannot change spending limits';
end $$;
do $$ declare n integer; begin
  update growth.leads set stage = 'won';
  get diagnostics n = row_count;
  assert n = 0, 'viewer cannot change leads';
end $$;

-- Operator: works leads, but can't approve as someone else or change owner-only settings.
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a2","role":"authenticated"}', true);
do $$ declare n integer; begin
  assert (select count(*) from growth.leads) = 1, 'operator sees leads';
  update growth.leads set stage = 'qualified' where idempotency_key = 'rls-1';
  assert (select stage from growth.leads where idempotency_key = 'rls-1') = 'qualified', 'operator updates stage';
  update growth.spending_limits set daily_usd = 999 where scope = 'global';
  get diagnostics n = row_count;
  assert n = 0, 'operator cannot change spending limits';
end $$;
select pg_temp.expect_error($$update growth.leads set idempotency_key = 'x'$$, 'permission denied');
select pg_temp.expect_error($$delete from growth.leads$$, 'permission denied');
do $$ declare n integer; begin
  update growth.app_users set role = 'owner';
  get diagnostics n = row_count;
  assert n = 0, 'operator cannot promote anyone';
end $$;
reset role;

do $$ begin
  assert (select changed_by from growth.lead_stage_history where to_stage = 'qualified') is not null, 'stage change recorded';
  assert (select role from growth.app_users where user_id = '00000000-0000-0000-0000-0000000000a2') = 'operator', 'role unchanged';
end $$;

-- Owner can change settings.
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a1","role":"authenticated"}', true);
update growth.spending_limits set daily_usd = 5 where scope = 'global';
reset role;
do $$ begin assert (select daily_usd from growth.spending_limits where scope = 'global') = 5, 'owner updated limit'; end $$;
rollback;
