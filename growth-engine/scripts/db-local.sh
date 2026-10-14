#!/usr/bin/env bash
# Rebuild a throwaway local database and run the SQL test suite.
#   scripts/db-local.sh reset   → drop + recreate DB, apply shim + migrations
#   scripts/db-local.sh test    → reset, then run supabase/tests/*.sql
# Needs a local PostgreSQL 15+. Connection: PGHOST/PGPORT/PGUSER (defaults: local socket, user postgres).
set -euo pipefail
cd "$(dirname "$0")/.."
DB="${GROWTH_TEST_DB:-growth_engine_test}"
PSQL=(psql -v ON_ERROR_STOP=1 -q -X)
[[ -n "${PGUSER:-}" ]] || export PGUSER=postgres

reset() {
  "${PSQL[@]}" -d postgres -c "drop database if exists ${DB} with (force)" -c "create database ${DB}"
  "${PSQL[@]}" -d "$DB" -f supabase/local/00_supabase_shim.sql
  for f in supabase/migrations/*.sql; do
    echo "apply $(basename "$f")"
    "${PSQL[@]}" -d "$DB" -f "$f"
  done
  # Login user for the API integration tests: same privileges as production's growth_api (intake only).
  "${PSQL[@]}" -d "$DB" -c "do \$\$ begin
    if not exists (select 1 from pg_roles where rolname = 'growth_api_test') then
      create role growth_api_test login password 'local-test-only' in role growth_intake;
    end if; end \$\$;"
}

run_tests() {
  local failed=0
  for f in supabase/tests/*.sql; do
    if "${PSQL[@]}" -d "$DB" -o /dev/null -f "$f" >/tmp/growth-test.out 2>&1; then
      echo "PASS $(basename "$f")"
    else
      echo "FAIL $(basename "$f")"; cat /tmp/growth-test.out; failed=1
    fi
  done
  return $failed
}

case "${1:-test}" in
  reset) reset ;;
  test) reset; run_tests ;;
  *) echo "usage: $0 reset|test" >&2; exit 2 ;;
esac
