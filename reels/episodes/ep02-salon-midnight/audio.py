"""ep02 Midnight Booking: 92 BPM lo-fi, D major, then a bright morning."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 27.3
T = {"notif": 0.3, "open": 3.8, "typing": 4.2, "reply": 5.0, "chips": 5.6, "c1": 8.4, "c2": 11.0, "booked": 11.9,
     "lapse": 12.6, "morning": 15.0, "slots": [15.6, 16.0, 16.4, 16.8], "logo": 19.3}
tl = {"dur": DUR, **T}
json.dump(tl, open("timeline.json", "w"))

M = Mix(DUR)
lofi = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]]
groove(M, 0.0, 12.6, 92, lofi, drums=True, bass=True, arp=False, pad=True, gain=.6, swing=.5)
M.add(bell(note(88), 1.0), T["notif"], .25); M.add(bell(note(93), 1.0), T["notif"] + .12, .2)
for k in range(3): M.add(pop(1200), T["typing"] + k * .22, .08)
for key, f in [("reply", 1300), ("chips", 1600), ("c1", 900), ("c2", 950)]: M.add(pop(f), T[key], .35)
M.add(bell(note(86), 1.4), T["booked"], .2); M.add(bell(note(90), 1.4), T["booked"] + .1, .18)
# time-lapse: ticks speed up + riser
t, iv = T["lapse"], .3
while t < T["morning"] - .05: M.add(pop(2400), t, .08, .3); t += iv; iv = max(.05, iv * .82)
M.add(riser(2.4), T["lapse"], .35)
M.add(ring(1.2, 1700), T["morning"], .3)                                          # alarm clock
groove(M, T["morning"], 18.9, 112, [[62, 66, 69], [67, 71, 74]], drums=True, arp=True, pad=True, gain=.75)
for i, s in enumerate(T["slots"]): M.add(pop(1000 + i * 150), s, .35)
M.add(whoosh(.7), 18.8, .45)
logo_sting(M, T["logo"], root=62, tail=8.0)
M.write("audio.wav")
print("ok")
