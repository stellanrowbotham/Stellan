"""ep07 Is My Car Done Yet? Garage funk 100 BPM in E, phone-ring montage, kanban whooshes."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 32.2
T = {"calls": [0.1, 4.4, 5.0, 5.6, 6.2, 6.8], "owner": 6.9, "board": 8.3, "moves": [14.6, 15.6, 16.7], "thanks": 19.5, "poll": 22.6, "logo": 27.2}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
for i, c in enumerate(T["calls"]): M.add(ring(.45 if i else .9, 1400 + i * 60), c, .3 + i * .03, (i % 2) - .5)
for i in range(1, 6): M.add(pop(500 + i * 60), T["calls"][i] + .05, .3)
M.add(whoosh(.7), 7.9, .45)
groove(M, 8.3, 27.1, 100, [[52, 56, 59], [57, 61, 64], [59, 63, 66], [57, 61, 64]], gain=.6, swing=.3)
for m in T["moves"]: M.add(whoosh(.4), m - .15, .35); M.add(pop(1300), m + .25, .35)
M.add(bell(note(88), 1.4), T["thanks"], .2)
M.add(pop(900), T["poll"], .35); M.add(pop(1100), T["poll"] + .25, .35)
logo_sting(M, T["logo"], root=64, tail=5.0)
M.write("audio.wav"); print("ok")
