"""ep03 The No-Show: villain horror-parody intro, then a bright 104 BPM split-screen groove in A minor -> C major."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 33.8
T = {"split": 7.7, "remind": 8.4, "reply": 10.5, "offer": 12.5, "ok": 13.6, "wait": 14.6, "filled": 15.3,
     "nine": 15.3, "villain2": 16.0, "poof": 21.6, "logo": 23.4}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
# villain intro: low drone, thunder hits, organ-ish minor chord
t = tt(7.6); drone = (np.sin(2*np.pi*41.2*t) + .5*np.sin(2*np.pi*82.4*t) + .3*np.sin(2*np.pi*98*t)) * np.clip(t/1.2, 0, 1) * np.clip((7.6-t)/.6, 0, 1)
M.add(drone, 0, .35)
for th in (0.15, 3.9): M.add(impact(2.2), th, .55); M.add(lowpass(noise(1.6), .3) * env_exp(1.6, 2.5), th, .3)
organ = sum(saw(note(m), 6.5, 6) for m in (45, 48, 52, 57)); M.add(fade(lowpass(organ, .06), 1.0, 1.2), 0.6, .05)
M.add(whoosh(.7), 7.25, .55)
# split-screen groove
groove(M, 7.7, 15.3, 104, [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]], gain=.65)
for k in ("remind", "reply", "offer", "ok", "wait"): M.add(pop(1100 if k != "reply" else 800), T[k], .35)
M.add(bell(note(84), 1.4), T["filled"], .2); M.add(bell(note(88), 1.4), T["filled"] + .1, .18)
# villain shock: record scratch + dramatic stab, then poof
M.add(lowpass(hp(noise(.35)), .7) * env_exp(.35, 8), 15.95, .4)
groove(M, 16.0, 22.9, 104, [[48, 52, 55], [53, 57, 60]], drums=False, arp=True, pad=True, gain=.6)
M.add(impact(1.0), T["poof"], .45); M.add(whoosh(.5), T["poof"], .5)
logo_sting(M, T["logo"], root=60, tail=10.5)
M.write("audio.wav"); print("ok")
