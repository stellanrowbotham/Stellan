"""ep11 Waitlist Control Tower: radar pings, radio squelch, 100 BPM E minor groove."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 33.5
T = {"cancel": 2.0, "open": 5.5, "scan": 7.8, "pins": [8.2, 8.6, 9.0, 9.4], "pick": 9.6, "cleared": 12.4,
     "text": 14.6, "reply": 15.9, "drive": [16.6, 19.2], "filled": 19.3, "logo": 20.6}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

def squelch(): d = .18; return hp(noise(d)) * env_exp(d, 18) * .5
def ping(f=1500): d = .6; t = tt(d); return np.sin(2*np.pi*f*t) * env_exp(d, 7) * .5
M = Mix(DUR)
M.add(squelch(), 0.45, .35); M.add(squelch(), 7.65, .35)
for k in range(9): M.add(ping(1400), 0.3 + k * 2.2, .12, -.3 + .07 * k)
M.add(ring(.5, 900), T["cancel"], .25)
for x in T["pins"]: M.add(blip(1600, .12), x, .3, .2)
M.add(riser(1.2), T["pick"] - 1.2, .25)
M.add(whoosh(.8), T["cleared"], .35)
M.add(pop(1200), T["text"], .35); M.add(pop(900), T["reply"], .35)
groove(M, 2.0, 20.6, 100, [[64, 67, 71], [60, 64, 67], [62, 66, 69], [59, 62, 66]], gain=.5, arp=True)
M.add(bell(note(88), 1.4), T["filled"], .12)
logo_sting(M, T["logo"], root=64, tail=12)
M.write("audio.wav"); print("ok")
