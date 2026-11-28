"""ep20 Storm-season lead forecast: TV-news weather theme 118 BPM A major, thunder, race whooshes."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 36.5
T = {"race": 7.0, "inquiry": 9.2, "bstart": 10.8, "reply": 14.0, "bfinish": 15.2, "booked": 19.6, "forecast": 22.4, "logo": 26.6}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
def thunder(d=2.5): t = tt(d); return lowpass(noise(d), .02) * np.exp(-t * 1.6) * (1 - np.exp(-t * 30)) * 3
M = Mix(DUR)
for i, m in enumerate([69, 73, 76, 81]): M.add(bell(note(m + 12), 1.0), 0.2 + i * .14, .08)   # news stinger
groove(M, 0.6, 26.6, 118, [[69, 73, 76], [66, 69, 73], [62, 66, 69], [64, 68, 71]], gain=.4)
M.add(thunder(), 2.4, .5); M.add(thunder(), 5.8, .4)
M.add(fade(lowpass(noise(26), .02), 1, 1), 0, .25)                                            # rain bed
M.add(pop(1000), T["inquiry"], .35); M.add(whoosh(.8), T["bstart"], .35); M.add(pop(1300), T["reply"], .35)
M.add(bell(note(88), 1.2), T["booked"], .14); M.add(crowd(2.0), T["booked"], .15)
logo_sting(M, T["logo"], root=69, tail=10)
M.write("audio.wav"); print("ok")
