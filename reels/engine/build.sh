#!/usr/bin/env bash
# Full pipeline for one episode: audio -> frames -> mp4 (Instagram-ready, <15 MB) + poster.
# usage: bash reels/engine/build.sh reels/episodes/epNN-slug [poster_second]
set -euo pipefail
EP=$(cd "$1" && pwd); POSTER=${2:-}; ENG=$(cd "$(dirname "$0")" && pwd); NAME=$(basename "$EP")
OUT=$(cd "$ENG/.." && pwd)/out; mkdir -p "$OUT"
( cd "$EP" && python3 audio.py )
[ -f "$EP/voice.json" ] && python3 "$ENG/voice.py" "$EP" mix
node "$ENG/render.js" "$EP" full 4
ls "$EP"/seg*.mp4 | sort -V | sed "s/^/file '/;s/$/'/" > "$EP/list.txt"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$EP/list.txt" -i "$EP/audio.wav" -c:v libx264 -crf 24 -preset slow \
  -profile:v high -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -shortest -movflags +faststart "$OUT/$NAME.mp4"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$NAME.mp4")
[ -z "$POSTER" ] && POSTER=$(python3 -c "print(max(0,$DUR-3))")
ffmpeg -loglevel error -y -ss "$POSTER" -i "$OUT/$NAME.mp4" -frames:v 1 "$OUT/$NAME.jpg"
rm -f "$EP"/seg*.mp4 "$EP/list.txt" "$EP/audio.wav"; rm -rf "$EP/prev"
ls -la "$OUT/$NAME.mp4"; echo "duration=$DUR"
