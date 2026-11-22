"""ep08 POV: 10 PM. Late-night lo-fi 84 BPM A minor, a dark 'without' detour, a tape rewind, then a warm resolve."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 28.6
T = {"notif": 0.5, "skip": 7.0, "lost": 10.4, "rewind": 12.2, "reply": 13.2, "buyer": 19.1, "booked": 20.0, "stamp": 20.6, "logo": 21.5}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
groove(M, 0.0, 6.9, 84, [[57, 60, 64], [53, 57, 60]], drums=True, bass=True, arp=False, pad=True, gain=.5, swing=.5)
M.add(bell(note(88), 1.0), T["notif"], .25); M.add(bell(note(93), 1.0), T["notif"] + .12, .2)
t = tt(5.3); drone = (np.sin(2*np.pi*55*t) + .5*np.sin(2*np.pi*58.3*t)) * np.clip(t/1.0, 0, 1) * np.clip((5.3-t)/.4, 0, 1)   # uneasy detour
M.add(drone, 6.9, .3)
for k in range(12): M.add(pop(2600), 7.0 + k * .25, .05)                     # clock ticks forward
M.add(blip(220, .6), T["lost"], .35); M.add(blip(165, .8), T["lost"] + .3, .3)  # sad trombone-ish
x = np.linspace(0, 1, int(.9 * SR)); rew = np.sin(2*np.pi*np.cumsum(1800 - 1500*x)/SR) * (1-x) * .5 + lowpass(noise(.9), .4) * x * .3
M.add(rew, T["rewind"], .5)                                                     # tape rewind
groove(M, 12.9, 21.4, 84, [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], gain=.6, swing=.5)
for k in ("reply", "buyer", "booked"): M.add(pop(1200), T[k], .35)
M.add(impact(.5), T["stamp"], .3); M.add(bell(note(84), 1.2), T["stamp"], .15)
logo_sting(M, T["logo"], root=60, tail=7.0)
M.write("audio.wav"); print("ok")
