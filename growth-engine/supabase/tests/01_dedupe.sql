begin;
\ir _helpers.psql

do $$
declare a uuid; b uuid; c uuid; created1 boolean; created2 boolean; n integer;
begin
  assert growth.normalize_domain('HTTPS://www.Example-Landscaping.ca:443/contact?x=1') = 'example-landscaping.ca', 'normalize_domain full';
  assert growth.normalize_domain('example.ca/') = 'example.ca', 'normalize_domain bare';
  assert growth.normalize_domain('http://user:pw@WWW.Example.ca.') = 'example.ca', 'normalize_domain creds + trailing dot';
  assert growth.normalize_domain('') is null, 'normalize_domain empty';
  assert growth.normalize_phone('(519) 555-0100') = '15195550100', 'normalize_phone 10 digits';
  assert growth.normalize_phone('+1 519 555 0100') = '15195550100', 'normalize_phone +1';
  assert growth.normalize_phone('555') is null, 'normalize_phone short';

  select business_id, created into a, created1 from growth.upsert_business(
    '{"name":"Green Acres Landscaping","website_url":"https://www.greenacres.example/","service_category":"landscaping","city":"Guelph","source":"test","is_test":true}');
  select business_id, created into b, created2 from growth.upsert_business(
    '{"name":"Green Acres Landscaping Inc.","website_url":"http://greenacres.example/contact","phone":"519-555-0100","is_test":true}');
  assert a = b, 'same domain must dedupe to one business';
  assert created1 and not created2, 'created flags';
  assert (select phone_normalized from growth.businesses where id = a) = '15195550100', 'merge fills missing phone';
  assert (select service_category from growth.businesses where id = a) = 'landscaping', 'merge keeps known values';

  -- No website: dedupe by name + city (case-insensitive).
  select business_id into a from growth.upsert_business('{"name":"Bob''s Roofing","city":"London","is_test":true}');
  select business_id into b from growth.upsert_business('{"name":"BOB''S ROOFING","city":"london","is_test":true}');
  select business_id into c from growth.upsert_business('{"name":"Bob''s Roofing","city":"Sarnia","is_test":true}');
  assert a = b and a <> c, 'name+city dedupe';

  -- Same observation twice → one row.
  insert into growth.source_observations (business_id, observation_type, value, source_url, method)
  values (a, 'phone_visible', '{"present":true}', 'https://example.invalid/', 'manual');
  insert into growth.source_observations (business_id, observation_type, value, source_url, method)
  values (a, 'phone_visible', '{"present":true}', 'https://example.invalid/', 'manual')
  on conflict do nothing;
  select count(*) into n from growth.source_observations where business_id = a;
  assert n = 1, 'observation dedupe';
end $$;

select pg_temp.expect_error($$select growth.upsert_business('{"name":""}')$$, 'name is required');
select pg_temp.expect_error($$insert into growth.businesses (name, website_url) values ('x', 'ftp://bad')$$, 'check constraint');
rollback;
