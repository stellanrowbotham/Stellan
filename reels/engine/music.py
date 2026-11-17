"""Shared synth kit for reel soundtracks. In an episode's audio.py:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
    from music import *
    M = Mix(dur)            # stereo buffer
    M.add(kick(), t, gain, pan) ...
    groove(M, t0, t1, bpm, chords, ...)   # drums + bass + arp + pads in one call
    M.write('audio.wav'); json.dump(timeline, open('timeline.json','w'))
Leave the music thinner where voices speak; voice.py ducks it further.
"""
import wave
import numpy as np

SR = 44100
_rng = np.random.default_rng(11)


def tt(d): return np.arange(int(d * SR)) / SR
def env_exp(d, k): return np.exp(-tt(d) * k)
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def hp(x): return np.diff(x, prepend=0)
def noise(d): return _rng.standard_normal(int(d * SR))


def lowpass(x, a):
    """one-pole lowpass, a in (0,1] (scalar or array): higher = brighter"""
    if np.ndim(a) == 0:
        try:
            from scipy.signal import lfilter
            return lfilter([float(a)], [1, float(a) - 1], x)
        except ImportError:
            a = np.full(x.shape, float(a))
    a = np.broadcast_to(np.asarray(a, dtype=float), x.shape); y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y


def saw(f, d, harm=8):
    t = tt(d); s = np.zeros_like(t)
    for h in range(1, harm + 1): s += np.sin(2 * np.pi * f * h * t) / h
    return s


def fade(sig, a=0.01, r=0.05):
    n = len(sig); e = np.ones(n); ai = min(int(a * SR), n); ri = min(int(r * SR), n)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return sig * e


def kick(punch=1.0):
    d = 0.4; t = tt(d); f = 45 + 90 * punch * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, 7)
def hat(): d = 0.05; return hp(hp(noise(d))) * env_exp(d, 90) * 0.35
def clap(): d = 0.18; return lowpass(hp(noise(d)), 0.5) * env_exp(d, 22) + np.sin(2 * np.pi * 190 * tt(d)) * env_exp(d, 30) * .4
def blip(f, d=0.15): return (np.sin(2 * np.pi * f * tt(d)) + .4 * np.sin(2 * np.pi * f * 1.5 * tt(d))) * env_exp(d, 28)
def bell(f, d=1.6):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.01 * t) * env_exp(d, 3) + .25 * np.sin(2 * np.pi * f * 3.02 * t) * env_exp(d, 6)) * env_exp(d, 3)
def whoosh(d=0.8):
    x = np.linspace(0, 1, int(d * SR)); e = np.sin(np.pi * x) ** 2
    return lowpass(noise(d), 0.06 + 0.3 * e) * e
def riser(d=2.0):
    x = np.linspace(0, 1, int(d * SR)); return lowpass(noise(d), 0.02 + 0.6 * x ** 2) * x ** 2
def impact(d=2.5):
    t = tt(d); return np.sin(2 * np.pi * np.cumsum(35 + 80 * np.exp(-t * 12)) / SR) * env_exp(d, 1.8) + lowpass(hp(noise(d)), .6) * env_exp(d, 2.2) * .25
def ring(d=1.0, f=1400):
    t = tt(d); trem = (np.sin(2 * np.pi * 20 * t) > 0).astype(float)
    return (np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.25 * t)) * trem * .3 * (t < d * .85)
def pop(f=900): d = .09; return np.sin(2 * np.pi * np.cumsum(np.linspace(f, f * 2, int(d * SR))) / SR) * env_exp(d, 40)
def whistle(d=0.6): t = tt(d); return np.sin(2 * np.pi * (2600 + 150 * np.sin(2 * np.pi * 30 * t)) * t) * np.exp(-((t - d / 2) / (d / 3)) ** 2) * .4
def crowd(d=2.5):
    x = np.linspace(0, 1, int(d * SR)); return lowpass(noise(d), .25) * (np.sin(np.pi * x) ** .5) * .6


class Mix:
    def __init__(self, dur):
        self.dur = dur; self.N = int(SR * dur); self.L = np.zeros(self.N); self.R = np.zeros(self.N)

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.N or i < 0: return
        sig = sig[: self.N - i]; l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
        self.L[i:i + len(sig)] += sig * gain * l; self.R[i:i + len(sig)] += sig * gain * r

    def write(self, path, fade_out=1.5):
        mix = np.stack([self.L, self.R]); mix = np.tanh(mix * 1.4) / np.tanh(1.4)
        fo = int(fade_out * SR); e = np.ones(self.N); e[-fo:] = np.linspace(1, 0, fo) ** 1.5; mix *= e
        mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype(np.int16).tobytes())


def groove(M, t0, t1, bpm, chords, drums=True, bass=True, arp=True, pad=True, gain=1.0, swing=0.0):
    """chords: list of MIDI triads, one per bar (4 beats), looped."""
    beat = 60 / bpm; nb = int((t1 - t0) / beat)
    for b in range(nb):
        bt = t0 + b * beat; ch = chords[(b // 4) % len(chords)]
        if drums:
            M.add(kick(), bt, .7 * gain); M.add(hat(), bt + beat / 2 + swing * beat * .25, .3 * gain, .35)
            if b % 4 in (1, 3): M.add(clap(), bt, .28 * gain, -.1)
        if bass:
            for h in range(2):
                d = beat * .48; s = lowpass(saw(note(ch[0] - 24), d, 6), 0.08) * env_exp(d, 6); M.add(fade(s, .003, .03), bt + h * beat / 2, .45 * gain)
        if arp:
            for q in range(4):
                m = ch[(b * 4 + q) % 3] + 12; d = beat * .44
                s = (np.sin(2 * np.pi * note(m) * tt(d)) + .3 * np.sin(2 * np.pi * note(m) * 2 * tt(d))) * env_exp(d, 16)
                M.add(fade(s, .002, .03), bt + q * beat / 4, .06 * gain, .5 if q % 2 else -.5)
    if pad:
        bar = beat * 4
        for k in range(int((t1 - t0) / bar)):
            ch = chords[k % len(chords)]; d = bar * 1.05
            s = lowpass(sum(saw(note(m) * 1.003, d, 5) + saw(note(m) * .997, d, 5) for m in ch), 0.05)
            M.add(fade(s, .25, .4), t0 + k * bar, .045 * gain, -.2); M.add(fade(s, .25, .4), t0 + k * bar + .012, .045 * gain, .2)


def logo_sting(M, t0, root=60, tail=7.0):
    M.add(impact(), t0, .8)
    for m, p in [(root - 12, 0), (root - 5, -.3), (root + 4, .3), (root + 7, -.5), (root + 11, .5), (root + 14, 0)]:
        s = lowpass(saw(note(m), tail, 4) * .5 + np.sin(2 * np.pi * note(m) * tt(tail)), .06) * np.exp(-tt(tail) * .25)
        M.add(fade(s, .02, 1.5), t0, .065, p)
    for i, m in enumerate([root + 24, root + 28, root + 31, root + 35, root + 36]): M.add(bell(note(m), 2.0), t0 + i * .11, .055, -.6 + i * .3)

