"""ep17 The daily special posted itself: cafe lo-fi 88 BPM Bb major, espresso hiss, DM pops, pipeline blips."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 35.5
T = {"dm": 8.6, "shock": 13.4, "post": 14.6, "bts": 18.2, "nodes": [18.8, 20.6, 22.6, 24.4], "logo": 26.7}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
M = Mix(DUR)
M.add(fade(hp(noise(2.2)) * .25, .3, .8), 1.0, .3)                    # espresso steam
for k in range(6): M.add(blip(700 + 60 * k, .08), 2.5 + k * .9, .06)   # register beeps
groove(M, 0.3, 26.7, 88, [[70, 74, 77], [67, 70, 74], [63, 67, 70], [65, 69, 72]], gain=.45, swing=.5)
M.add(pop(1100), T["dm"], .35); M.add(whoosh(.6), T["post"] - .3, .3); M.add(bell(note(86), 1.2), T["post"], .1)
for n in T["nodes"]: M.add(blip(1300, .12), n, .25)
logo_sting(M, T["logo"], root=70, tail=9)
M.write("audio.wav"); print("ok")
