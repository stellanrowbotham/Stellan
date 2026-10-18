begin;
\ir _helpers.psql
select pg_temp.expect_error($$insert into growth.scoring_models (version, weights) values ('bad', '{"a": 50, "b": 40}')$$, 'sum to 90');
do $$
declare b uuid;
begin
  select business_id into b from growth.upsert_business('{"name":"Score Co","website_url":"https://score.example","is_test":true}');
  insert into growth.lead_scores (business_id, model_version, components, total)
  values (b, 'v1', '{"target_fit":25,"observable_opportunity":20,"service_area":15,"suitability":10,"evidence_quality":8}', 78);
  perform set_config('test.b', b::text, true);
end $$;
-- Component over its weight, missing component, wrong total, unknown component.
select pg_temp.expect_error(format($$insert into growth.lead_scores (business_id, model_version, components, total)
  values (%L, 'v1', '{"target_fit":31,"observable_opportunity":20,"service_area":15,"suitability":10,"evidence_quality":8}', 84)$$, current_setting('test.b')), 'outside 0..30');
select pg_temp.expect_error(format($$insert into growth.lead_scores (business_id, model_version, components, total)
  values (%L, 'v1', '{"target_fit":20}', 20)$$, current_setting('test.b')), 'every component');
select pg_temp.expect_error(format($$insert into growth.lead_scores (business_id, model_version, components, total)
  values (%L, 'v1', '{"target_fit":25,"observable_opportunity":20,"service_area":15,"suitability":10,"evidence_quality":8}', 90)$$, current_setting('test.b')), 'sum to 78');
select pg_temp.expect_error(format($$insert into growth.lead_scores (business_id, model_version, components, total)
  values (%L, 'v1', '{"vibes":5}', 5)$$, current_setting('test.b')), 'unknown score component');
rollback;
