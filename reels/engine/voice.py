"""Mix ElevenLabs voice lines into an episode's soundtrack, with ducking and captions.

usage:
  python3 reels/engine/voice.py <episodeDir> info   # durations of vo/*.mp3 and where each line lands
  python3 reels/engine/voice.py <episodeDir> mix    # after audio.py: adds the voice into audio.wav, captions into timeline.json

<episodeDir>/voice.json:
{
  "lines": [ {"file": "vo/01.mp3", "at": 1.0, "who": "owner", "text": "Eleven forty-seven...",
              "speed": 1.0, "cut": null, "gain_db": 0} ],
  "pa_chime": [12.05],       # optional airline "ding-dong" before the Pilot speaks
  "duck_db": -11             # how far the music drops under the voice
}
- at: start time in seconds. speed: 0.8-1.3 (ffmpeg atempo, keeps pitch). cut: hard stop time (s) or null.
- text: what is said WITHOUT [tags]. It becomes on-screen captions (timeline["captions"]: [{t0,t1,text,who}]),
  chunked into 2-5 word pieces spread over the line. Draw them in scene.html (most people watch muted).
"""
import json, os, re, subprocess, sys, wave
import numpy as np

SR = 44100


def decode(path, speed=1.0):
    af = []
    s = speed
    while s > 2.0: af.append("atempo=2.0"); s /= 2.0
    while s < 0.5: af.append("atempo=0.5"); s /= 0.5
    if abs(s - 1.0) > 1e-3: af.append(f"atempo={s:.4f}")
    cmd = ["ffmpeg", "-loglevel", "error", "-i", path] + (["-af", ",".join(af)] if af else []) + \
          ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    x = np.frombuffer(subprocess.run(cmd, check=True, capture_output=True).stdout, dtype=np.float32).astype(np.float64)
    # trim leading/trailing silence so 'at' means "first word"
    a = np.abs(x); thr = 0.02 * (a.max() + 1e-9); idx = np.where(a > thr)[0]
    if len(idx): x = x[max(0, idx[0] - int(.02 * SR)): idx[-1] + int(.12 * SR)]
    return x


def chime():
    t = np.arange(int(.9 * SR)) / SR
    def tone(f, d): return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)) * np.exp(-np.clip(t - d, 0, None) * 5) * (t >= d)
    return (tone(784, 0) + tone(622, .32)) * .35


def chunks(text, t0, t1):
    words = text.split()
    if not words: return []
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or (len(cur) >= 2 and re.search(r"[.,!?…]$", w)): groups.append(cur); cur = []
    if cur: groups.append(cur)
    total = sum(len(" ".join(g)) for g in groups); out, t = [], t0
    for g in groups:
        d = (t1 - t0) * len(" ".join(g)) / total
        out.append({"t0": round(t, 3), "t1": round(t + d, 3), "text": " ".join(g)}); t += d
    return out


def main():
    ep, mode = sys.argv[1], sys.argv[2]
    cfg = json.load(open(os.path.join(ep, "voice.json")))
    placed = []
    for ln in cfg["lines"]:
        x = decode(os.path.join(ep, ln["file"]), ln.get("speed", 1.0))
        if ln.get("cut") is not None: x = x[: max(0, int((ln["cut"] - ln["at"]) * SR))]
        x = x / (np.abs(x).max() + 1e-9) * 0.8 * 10 ** (ln.get("gain_db", 0) / 20)
        f = int(.015 * SR); x[-f:] *= np.linspace(1, 0, f)
        placed.append((ln, x, ln["at"], ln["at"] + len(x) / SR))
    if mode == "info":
        prev = 0
        for ln, x, a, b in placed:
            flag = "  <-- OVERLAPS previous line" if a < prev - 0.05 else ""
            print(f'{ln["file"]:12s} {ln.get("who",""):8s} {a:6.2f} -> {b:6.2f}  ({b-a:4.2f}s){flag}')
            prev = b
        return
    w = wave.open(os.path.join(ep, "audio.wav")); n = w.getnframes()
    music = np.frombuffer(w.readframes(n), np.int16).reshape(-1, 2).astype(np.float64) / 32768; w.close()
    voice = np.zeros(len(music)); env = np.zeros(len(music))
    for ln, x, a, b in placed:
        i = int(a * SR); j = min(len(music), i + len(x)); voice[i:j] += x[: j - i]; env[i:j] = 1
    for c in cfg.get("pa_chime", []):
        y = chime(); i = int(c * SR); j = min(len(music), i + len(y)); voice[i:j] += y[: j - i]; env[i:j] = 1
    # smooth the ducking envelope: 80 ms attack, 350 ms release
    k_att, k_rel = 1 / (0.08 * SR), 1 / (0.35 * SR); s = 0.0; sm = np.empty_like(env)
    for i, v in enumerate(env):
        s += (v - s) * (k_att if v > s else k_rel); sm[i] = s
    gain = 10 ** (cfg.get("duck_db", -11) * sm / 20)
    mix = music * gain[:, None] + voice[:, None] * 0.95
    mix = np.tanh(mix * 1.2) / np.tanh(1.2); mix /= max(1.0, np.abs(mix).max() / 0.89)
    with wave.open(os.path.join(ep, "audio.wav"), "wb") as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix * 32767).astype(np.int16).tobytes())
    tl_path = os.path.join(ep, "timeline.json"); tl = json.load(open(tl_path))
    tl["captions"] = [dict(c, who=ln.get("who", "")) for ln, x, a, b in placed for c in chunks(ln.get("text", ""), a, b)]
    tl["voice"] = [{"t0": round(a, 3), "t1": round(b, 3), "who": ln.get("who", "")} for ln, x, a, b in placed]
    json.dump(tl, open(tl_path, "w"))
    print("mixed", len(placed), "lines;", len(tl["captions"]), "captions")


if __name__ == "__main__":
    main()
