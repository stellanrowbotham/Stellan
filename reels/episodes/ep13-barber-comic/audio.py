"""ep13 Barber vs the Missed Call gremlin: bouncy comic-strip groove 112 BPM F major, page flips, ZAP, poof."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 40.5
T = {"p": [0.4, 6.6, 15.8, 20.4], "flip": [9.5, 12.5], "mop": 11.0, "zap": 18.4, "msg": 21.0, "yes": 25.0,
     "foiled": 26.8, "booked": 27.8, "logo": 29.8}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
M = Mix(DUR)
for x in T["p"]: M.add(whoosh(.5), x, .3)
for k in range(8): M.add(hp(noise(.06)) * env_exp(.06, 50), T["flip"][0] + k * .37, .25, .3)
groove(M, 0.4, 15.8, 112, [[65, 69, 72], [70, 74, 77], [67, 70, 74], [72, 76, 79]], gain=.45, swing=.4)
M.add(riser(1.4), T["zap"] - 1.4, .3); M.add(impact(1.5), T["zap"], .5)
groove(M, T["zap"], 29.8, 112, [[65, 69, 72], [70, 74, 77], [72, 76, 79], [65, 69, 72]], gain=.5, swing=.4)
M.add(pop(1100), T["msg"], .35); M.add(pop(800), T["yes"], .35)
M.add(lowpass(noise(.6), .2) * env_exp(.6, 6), T["foiled"], .5); M.add(whistle(.5), T["foiled"] + .1, .2)
M.add(bell(note(84), 1.2), T["booked"], .12)
logo_sting(M, T["logo"], root=65, tail=10.5)
M.write("audio.wav"); print("ok")
