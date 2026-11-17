#!/usr/bin/env bash
# Contact sheet of preview frames, for checking a scene before the full render.
# usage: bash reels/engine/sheet.sh reels/episodes/epNN-slug 2,6,10,14,18,22  -> <ep>/prev/sheet.jpg
set -euo pipefail
EP=$1; T=$2; ENG=$(cd "$(dirname "$0")" && pwd)
( cd "$EP" && [ -f timeline.json ] || python3 audio.py )
node "$ENG/render.js" "$EP" preview "$T"
ARGS=(); N=0; for t in ${T//,/ }; do ARGS+=(-i "$EP/prev/t$t.jpg"); N=$((N+1)); done
ffmpeg -loglevel error -y "${ARGS[@]}" -filter_complex "hstack=$N,scale=$((N*300)):-1" "$EP/prev/sheet.jpg"
echo "$EP/prev/sheet.jpg"
