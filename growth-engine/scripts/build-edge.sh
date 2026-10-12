#!/usr/bin/env bash
# Copies the shared API source into the edge function so `supabase functions deploy` can bundle it.
set -euo pipefail
cd "$(dirname "$0")/.."
dest=supabase/functions/growth-api/_lib
rm -rf "$dest" && mkdir -p "$dest"
cp api/src/app.ts api/src/config.ts api/src/consent-copy.ts api/src/security.ts api/src/store.ts api/src/validation.ts "$dest/"
echo "copied API source to $dest"
