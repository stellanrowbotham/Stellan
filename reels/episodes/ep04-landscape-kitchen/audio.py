"""ep04 Bot Kitchen: cooking-show parody, 116 BPM swing, F major."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 32.3
T = {"ing": [6.6, 8.2, 10.9, 11.6, 12.3], "oven": 13.4, "ding": 15.6, "card": 16.3, "inbox": 17.2,
     "taste": 19.7, "logo": 23.0}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
for i, m in enumerate([77, 81, 84, 89]): M.add(bell(note(m), 1.6), 0.05 + i * .12, .14, -.4 + i * .25)   # show sting
groove(M, 0.4, 13.3, 116, [[65, 69, 72], [62, 65, 69], [55, 58, 62], [60, 64, 67]], gain=.6, swing=.6)
for i, t in enumerate(T["ing"]): M.add(pop(700 + i * 120), t, .35); M.add(pop(300), t + .45, .25)      # drop + plop
M.add(whoosh(.6), 13.2, .4)
t = 13.6
while t < T["ding"] - .1: M.add(pop(2600), t, .06); t += .18                                          # oven timer tick
M.add(bell(note(96), 1.8), T["ding"], .35); M.add(bell(note(91), 1.6), T["ding"] + .02, .2)
M.add(lowpass(noise(1.2), .15) * env_exp(1.2, 2), T["ding"] + .1, .2)                                 # steam
groove(M, T["ding"], 22.8, 116, [[65, 69, 72], [70, 74, 77]], gain=.7, swing=.6)
M.add(whoosh(.5), T["card"], .4); M.add(pop(1500), T["inbox"], .4)
M.add(bell(note(84), 1.0), T["taste"] + 1.2, .15)
logo_sting(M, T["logo"], root=65, tail=9.3)
M.write("audio.wav"); print("ok")
