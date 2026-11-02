#!/usr/bin/env python3
"""Make Stellan's Echo speak, via the Voice Monkey v3 API (stdlib only).

Needs two environment variables (set in the cloud environment's settings, never in this repo):
  VOICEMONKEY_TOKEN   API token from voicemonkey.io → Dashboard → API
  ALEXA_DEVICE        Voice Monkey Speaker device ID (run `alexa.py devices` to list them)

Usage:
  python3 tools/alexa.py devices
  python3 tools/alexa.py announce --text "Good morning Stellan."
  python3 tools/alexa.py announce --file spoken.txt --chime wake
  python3 tools/alexa.py announce --file spoken.txt --dry-run   # print, don't send
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api-v3.voicemonkey.io"
CHIMES = {
    "wake": "soundbank://soundlibrary/alarms/beeps_and_bloops/bell_02",
    "bell": "soundbank://soundlibrary/home/amzn_sfx_doorbell_chime_01",
    "none": "",
}
MAX_CHARS = 4000  # keep the brief to ~90 s of speech; Alexa TTS gets flaky beyond this


def _call(method, path, payload=None):
    token = os.environ.get("VOICEMONKEY_TOKEN")
    if not token:
        sys.exit("VOICEMONKEY_TOKEN is not set. Add it in the cloud environment settings.")
    url = f"{API}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if method == "GET":
        url += f"?token={token}"
    else:
        data = json.dumps({"token": token, **(payload or {})}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code in (429, 500) and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            sys.exit(f"Voice Monkey error {e.code}: {body}")
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            sys.exit(f"Could not reach Voice Monkey: {e.reason}")


def cmd_devices(_):
    print(json.dumps(_call("GET", "/devices"), indent=2))


def cmd_announce(a):
    text = a.text if a.text else open(a.file, encoding="utf-8").read()
    text = " ".join(text.split())
    if not text:
        sys.exit("Nothing to say.")
    if len(text) > MAX_CHARS:
        sys.exit(f"Speech is {len(text)} chars; keep it under {MAX_CHARS}.")
    payload = {"device": a.device or os.environ.get("ALEXA_DEVICE", ""), "speech": text}
    if not payload["device"]:
        sys.exit("ALEXA_DEVICE is not set (or pass --device).")
    chime = CHIMES.get(a.chime, a.chime)
    if chime:
        payload["chime"] = chime
    if a.voice:
        payload["voice"] = a.voice
    if a.dry_run:
        print(json.dumps({**payload, "token": "***"}, indent=2))
        return
    print(json.dumps(_call("POST", "/announce", payload)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("devices", help="list Voice Monkey devices").set_defaults(fn=cmd_devices)
    an = sub.add_parser("announce", help="speak text on the Echo")
    src = an.add_mutually_exclusive_group(required=True)
    src.add_argument("--text")
    src.add_argument("--file")
    an.add_argument("--device", help="override ALEXA_DEVICE")
    an.add_argument("--chime", default="none", help="wake | bell | none | a soundbank:// URL")
    an.add_argument("--voice", help="Alexa voice id, e.g. Matthew")
    an.add_argument("--dry-run", action="store_true")
    an.set_defaults(fn=cmd_announce)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
