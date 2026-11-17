"""Timeline + synthesized soundtrack for the FlowPilot promo. Writes timeline.json and audio.wav."""
import json, wave
import numpy as np

SR = 44100
DUR = 54.5
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

# ---------------- shared timeline ----------------
NCARDS = 28
NODE_T = [15.8, 18.4, 21.0, 23.6, 26.2]
cards = []
for k in range(NCARDS):
    spawn = 4.8 + 6.5 * (k / (NCARDS - 1)) ** 0.62
    node = k % 5
    j = k // 5
    cards.append({"spawn": round(spawn, 3), "node": node, "absorb": round(NODE_T[node] + 0.25 + j * 0.13, 3)})
LINES_T = [30.0, 32.1, 34.2, 36.3]
CHECK_T = [40.6, 41.2, 41.8]
tl = {"dur": DUR, "cards": cards, "nodes": NODE_T, "lines": LINES_T, "checks": CHECK_T}
json.dump(tl, open("timeline.json", "w"))

# ---------------- helpers ----------------
def idx(t): return int(t * SR)

def add(sig, t, gain=1.0, pan=0.0):
    i = idx(t)
    if i >= N: return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gain * l * 1.414
    R[i:i + len(sig)] += sig * gain * r * 1.414

def tt(d): return np.arange(int(d * SR)) / SR

def env_exp(d, k): return np.exp(-tt(d) * k)

def lowpass(x, a):
    """one-pole lowpass; a may be array of coefficients (0..1, higher = brighter)"""
    y = np.zeros_like(x); s = 0.0
    a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

def hp(x):
    return np.diff(x, prepend=0)

def note(m): return 440.0 * 2 ** ((m - 69) / 12)

def saw(f, d, harm=8):
    t = tt(d); s = np.zeros_like(t)
    for h in range(1, harm + 1):
        s += np.sin(2 * np.pi * f * h * t) / h
    return s

def fade(sig, a=0.01, r=0.05):
    n = len(sig); ai = min(int(a * SR), n); ri = min(int(r * SR), n)
    e = np.ones(n)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return sig * e

# ---------------- ACT 1-2: drone, ticks, blips, riser ----------------
t = tt(12.0)
drone = (np.sin(2*np.pi*55*t) + 0.6*np.sin(2*np.pi*110.3*t) + 0.35*np.sin(2*np.pi*164.8*t) + 0.2*np.sin(2*np.pi*220.7*t))
drone *= (0.6 + 0.4*np.sin(2*np.pi*0.25*t)) * np.clip(t/3, 0, 1) * (0.5 + 0.5*np.clip((t-4)/7, 0, 1))
add(drone, 0, 0.16)

ticks = [0.5, 1.5, 2.5, 3.5, 4.5]
cur, iv = 4.5, 0.85
while cur < 11.8:
    cur += iv; iv = max(0.12, iv * 0.86); ticks.append(cur)
for i, tk in enumerate(ticks):
    if tk >= 11.95: break
    d = 0.03
    s = hp(rng.standard_normal(int(d*SR))) * env_exp(d, 180) * 0.5 + np.sin(2*np.pi*2400*tt(d)) * env_exp(d, 250)
    add(s, tk, 0.22 if i % 2 == 0 else 0.15, pan=-0.3 if i % 2 else 0.3)

for c in cards:
    f = rng.uniform(900, 1700); d = 0.18
    s = (np.sin(2*np.pi*f*tt(d)) + 0.4*np.sin(2*np.pi*f*1.5*tt(d))) * env_exp(d, 28)
    add(fade(s, 0.002, 0.02), c["spawn"], 0.11, pan=rng.uniform(-0.7, 0.7))

d = 4.0
rz = rng.standard_normal(int(d*SR)); e = np.linspace(0, 1, len(rz)) ** 2.5
rz = lowpass(rz, 0.03 + 0.5*np.linspace(0, 1, len(rz))**2) * e
sweep = np.sin(2*np.pi*np.cumsum(200 + 1400*np.linspace(0, 1, len(rz))**2)/SR) * e
add(rz*0.9 + sweep*0.25, 7.95, 0.35)

# ---------------- ACT 3: freeze + whoosh ----------------
d = 1.2; add(np.sin(2*np.pi*(40+30*env_exp(d, 8))*tt(d)) * env_exp(d, 3.5), 12.0, 0.55)  # sub thump
d = 2.0
wz = rng.standard_normal(int(d*SR)); x = np.linspace(0, 1, len(wz))
wenv = np.exp(-((x-0.45)/0.18)**2)
wz = lowpass(wz, 0.02 + 0.35*wenv) * wenv
add(wz, 13.25, 0.9, pan=-0.2)
d = 1.0; x = np.linspace(0, 1, int(d*SR))
sw = lowpass(rng.standard_normal(len(x)), 0.05 + 0.6*x**3) * x**3
add(sw, 14.0, 0.5)

# ---------------- ACT 4-5: groove 15.0 -> 38.5 ----------------
BEAT = 0.5
G0, G1 = 15.0, 38.5
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G

def kick(g=1.0):
    d = 0.4; tt_ = tt(d)
    f = 45 + 90*np.exp(-tt_*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env_exp(d, 7) * g

def hat():
    d = 0.05; return hp(hp(rng.standard_normal(int(d*SR)))) * env_exp(d, 90) * 0.35

def clap():
    d = 0.18; n = lowpass(hp(rng.standard_normal(int(d*SR))), 0.5) * env_exp(d, 22)
    return n + np.sin(2*np.pi*190*tt(d)) * env_exp(d, 30) * 0.4

nb = int((G1 - G0) / BEAT)
for b in range(nb):
    bt = G0 + b*BEAT
    bar = b // 4
    chord = prog[bar % 4]
    add(kick(), bt, 0.75)
    add(hat(), bt + BEAT/2, 0.35, pan=0.35)
    if b % 4 in (1, 3): add(clap(), bt, 0.32, pan=-0.1)
    # bass 8ths
    for h in range(2):
        d = 0.24
        s = saw(note(chord[0]-24), d, 6); s = lowpass(s, 0.08) * env_exp(d, 6)
        add(fade(s, 0.003, 0.03), bt + h*BEAT/2, 0.5)
    # arp 16ths
    for q in range(4):
        m = chord[(b*4+q) % 3] + 12 + (12 if (b*4+q) % 7 == 0 else 0)
        d = 0.22
        s = (np.sin(2*np.pi*note(m)*tt(d)) + 0.3*np.sin(2*np.pi*note(m)*2*tt(d))) * env_exp(d, 16)
        add(fade(s, 0.002, 0.03), bt + q*BEAT/4, 0.07, pan=0.5 if q % 2 else -0.5)
# pads per bar
for bar in range(int((G1 - G0) / 2)):
    chord = prog[bar % 4]; d = 2.1
    s = sum(saw(note(m)*1.003, d, 5) + saw(note(m)*0.997, d, 5) for m in chord)
    s = lowpass(s, 0.05)
    add(fade(s, 0.25, 0.4), G0 + bar*2, 0.05, pan=-0.2)
    add(fade(s, 0.25, 0.4), G0 + bar*2 + 0.012, 0.05, pan=0.2)

def bell(f, d=1.6):
    t_ = tt(d)
    return (np.sin(2*np.pi*f*t_) + 0.5*np.sin(2*np.pi*f*2.01*t_)*env_exp(d, 3) + 0.25*np.sin(2*np.pi*f*3.02*t_)*env_exp(d, 6)) * env_exp(d, 3)

for i, nt in enumerate(NODE_T):
    add(bell(note(76 + [0, 3, 7, 10, 12][i])), nt, 0.16, pan=(-0.4 if i % 2 else 0.4))
for c in cards:
    d = 0.08; s = np.sin(2*np.pi*rng.uniform(2000, 3000)*tt(d)) * env_exp(d, 60)
    add(s, c["absorb"], 0.05, pan=rng.uniform(-0.6, 0.6))
# line whooshes
for lt in LINES_T:
    d = 0.6; x = np.linspace(0, 1, int(d*SR)); e = np.sin(np.pi*x)**2
    add(lowpass(rng.standard_normal(len(x)), 0.08 + 0.25*e) * e, lt - 0.2, 0.45)
# downlifter into breakdown
d = 1.5; x = np.linspace(0, 1, int(d*SR))
add(np.sin(2*np.pi*np.cumsum(900 - 700*x)/SR) * (1-x)**2, 38.4, 0.08)

# ---------------- ACT 6: sunrise breakdown 38.5 -> 44 ----------------
sun = [[60, 64, 67, 71], [65, 69, 72, 76], [60, 64, 67, 74]]  # Cmaj7 Fmaj7 Cadd9
for i, ch in enumerate(sun):
    st = 38.5 + i*1.85; d = 2.4
    s = sum(np.sin(2*np.pi*note(m)*tt(d)) + 0.3*np.sin(2*np.pi*note(m)*2*tt(d)) for m in ch)
    add(fade(s, 0.5, 0.8), st, 0.06)
for k in range(22):
    m = [72, 76, 79, 83, 84, 79, 76, 74][k % 8]; d = 0.5
    s = np.sin(2*np.pi*note(m)*tt(d)) * env_exp(d, 7)
    add(s, 38.6 + k*0.25, 0.05, pan=np.sin(k))
for ct in CHECK_T:
    add(bell(note(84), 0.8), ct, 0.12)
# riser into logo
d = 1.6; x = np.linspace(0, 1, int(d*SR))
add(lowpass(rng.standard_normal(len(x)), 0.02 + 0.6*x**2) * x**2, 42.4, 0.45)

# ---------------- ACT 7: logo 44 -> 52 ----------------
d = 2.5; t_ = tt(d)
boom = np.sin(2*np.pi*np.cumsum(35 + 80*np.exp(-t_*12))/SR) * env_exp(d, 1.8)
crash = lowpass(hp(rng.standard_normal(len(t_))), 0.6) * env_exp(d, 2.2)
add(boom, 44.0, 0.9); add(crash, 44.0, 0.2, pan=0.2); add(crash[::-1][::-1], 44.01, 0.2, pan=-0.2)
for m, p in [(48, 0), (55, -0.3), (64, 0.3), (67, -0.5), (71, 0.5), (74, 0)]:
    d = 10.5
    s = saw(note(m), d, 4) * 0.5 + np.sin(2*np.pi*note(m)*tt(d))
    s = lowpass(s, 0.06) * np.exp(-tt(d)*0.22)
    add(fade(s, 0.02, 2.0), 44.0, 0.07, pan=p)
for i, m in enumerate([84, 88, 91, 95, 96]):
    add(bell(note(m), 2.0), 44.0 + i*0.11, 0.06, pan=-0.6 + i*0.3)
add(bell(note(91), 2.5), 47.2, 0.07)  # CTA ping

# ---------------- master ----------------
mix = np.stack([L, R])
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
e = np.ones(N); fo = idx(2.0); e[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= e
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix.T * 32767).astype(np.int16)
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", len(ticks), "ticks")
