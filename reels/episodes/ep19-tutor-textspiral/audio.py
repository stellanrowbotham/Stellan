"""ep19 Nine texts to move one session: text-tone chaos into calm, 96 BPM C major."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 33.0
MSG = [0.6, 2.5, 4.7, 9.0, 10.6, 12.0, 13.2, 13.9, 14.6]
T = {"msg": MSG, "swirl": [11.6, 15.4], "suck": [15.8, 16.8], "card": 17.6, "slots": [18.2, 18.6, 19.0], "tap": 20.3, "booked": 21.2, "logo": 24.0}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
M = Mix(DUR)
for i, m in enumerate(MSG): M.add(pop(900 + 120 * (i % 4)), m, .3, -.4 if i % 2 else .4)
M.add(fade(lowpass(noise(4.0), .05) * np.linspace(0, 1, int(4.0 * SR)), .2, .3), 11.6, .3)   # swirl wind
M.add(whoosh(1.0), T["suck"][0], .4)
groove(M, 0.4, 15.6, 96, [[60, 64, 67], [65, 69, 72], [62, 65, 69], [67, 71, 74]], gain=.35, arp=True)
groove(M, 16.0, 24.0, 96, [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]], gain=.5)
for s in T["slots"]: M.add(blip(1200, .1), s, .2)
M.add(pop(1300), T["tap"], .35); M.add(bell(note(84), 1.4), T["booked"], .14)
logo_sting(M, T["logo"], root=60, tail=9)
M.write("audio.wav"); print("ok")
