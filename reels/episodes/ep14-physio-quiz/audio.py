"""ep14 Which bot do you need? Physio quiz show: 124 BPM A major game-show groove, ticks, drumroll, reveal."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 40.0
T = {"intro": 0.3, "q": [6.0, 12.0, 17.2], "qend": [10.8, 16.4, 22.4], "reveal": 23.0, "flip": 25.2, "chips": [27.6, 29.8], "logo": 32.4}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
def tick(): d = .05; return hp(noise(d)) * env_exp(d, 90) * .5
M = Mix(DUR)
M.add(impact(1.5), 0.3, .35)
groove(M, 0.3, 5.9, 124, [[69, 73, 76], [66, 69, 73], [62, 66, 69], [64, 68, 71]], gain=.5)
for q, e in zip(T["q"], T["qend"]):
    M.add(whoosh(.5), q - .2, .3)
    t = q + .6
    while t < e: M.add(tick(), t, .25, .2); t += .5
    M.add(bell(note(81), 1.0), e, .12); M.add(bell(note(88), 1.0), e + .1, .1)
    groove(M, q, e, 124, [[69, 73, 76], [64, 68, 71]], gain=.3, drums=False, bass=True, arp=True, pad=False)
t = T["reveal"]
while t < T["flip"]: M.add(hp(noise(.05)) * env_exp(.05, 40) * .6, t, .3); t += .06
M.add(impact(2.0), T["flip"], .5); M.add(crowd(2.5), T["flip"], .2)
groove(M, T["flip"], 32.4, 124, [[69, 73, 76], [74, 78, 81], [71, 74, 78], [76, 80, 83]], gain=.45)
for c in T["chips"]: M.add(pop(1000), c, .3)
logo_sting(M, T["logo"], root=69, tail=7.5)
M.write("audio.wav"); print("ok")
