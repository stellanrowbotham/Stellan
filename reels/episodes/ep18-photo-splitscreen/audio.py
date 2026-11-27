"""ep18 Same inquiry, two replies: split-screen, slow robotic left vs instant friendly right, 104 BPM E major."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 34.0
T = {"ask": 0.6, "slow": 4.6, "fast": 13.4, "verdict": 20.6, "results": 23.0, "logo": 25.8}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
M = Mix(DUR)
M.add(pop(1000), T["ask"], .3)
for k in range(16): M.add(blip(300, .08), T["slow"] + k * .5, .08, -.6)        # slow robot ticks on the left
M.add(pop(1300), T["fast"], .35, .6)
groove(M, 0.3, 13.2, 104, [[64, 68, 71], [61, 64, 68]], gain=.25, drums=False, pad=True, arp=False)
groove(M, 13.4, 25.8, 104, [[64, 68, 71], [69, 73, 76], [66, 69, 73], [71, 75, 78]], gain=.5)
M.add(whoosh(.6), T["verdict"], .3); M.add(bell(note(88), 1.2), T["results"], .12)
logo_sting(M, T["logo"], root=64, tail=8.5)
M.write("audio.wav"); print("ok")
