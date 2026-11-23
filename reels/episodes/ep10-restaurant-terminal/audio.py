"""ep10 FAQ Terminal: retro-computer synth, 96 BPM D minor, keyboard clicks and beeps."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 31.4
T = {"q1": 0.3, "count": 5.5, "result": 6.6, "also": 8.4, "list": [9.6, 11.0, 12.4], "deploy": 14.2, "online": 14.9,
     "chat": [15.5, 16.4, 17.4, 18.2], "logo": 20.2}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

def click(): d = .03; return hp(noise(d)) * env_exp(d, 200) * .6
def beep(f=1760, d=.12): t = tt(d); return np.sign(np.sin(2*np.pi*f*t)) * .3 * env_exp(d, 8)
M = Mix(DUR)
t = tt(DUR); M.add(np.sin(2*np.pi*60*t) * .03, 0, 1)   # CRT hum
for k in range(28): M.add(click(), T["q1"] + .4 + k * .16 + .04 * np.sin(k), .25, .2)
for k in range(10): M.add(beep(900 + k * 80, .05), T["count"] + k * .1, .15)
M.add(beep(440, .5), T["result"], .3)
groove(M, 7.0, 20.0, 96, [[62, 65, 69], [58, 62, 65], [60, 64, 67], [57, 61, 64]], gain=.55, arp=True)
for x in T["list"]: M.add(beep(1320, .1), x, .25)
for k in range(12): M.add(click(), T["deploy"] - .6 + k * .05, .2)
M.add(beep(1760, .25), T["online"], .3); M.add(beep(2349, .3), T["online"] + .15, .25)
for x in T["chat"]: M.add(pop(1200), x, .3)
logo_sting(M, T["logo"], root=62, tail=10.5)
M.write("audio.wav"); print("ok")
