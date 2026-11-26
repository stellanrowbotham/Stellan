"""ep16 The furnace died at 2 AM: horror-trailer bed (drones, braams, heartbeat), phone rings, then warm resolve 90 BPM G major."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 37.5
T = {"cards": [1.2, 2.9, 4.3], "house": 5.6, "rings": [6.6, 8.6, 10.6], "vm": 12.4, "title": 14.6, "answer": 18.3,
     "bubbles": [18.8, 20.6, 22.6, 24.6], "logo": 27.4}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
def braam(d=2.5):
    t = tt(d); return lowpass(saw(note(31), d, 8) + saw(note(31) * 1.01, d, 8) + saw(note(38), d, 6) * .6, .05) * np.exp(-t * 1.2) * (1 - np.exp(-t * 40))
def heart(): d = .5; t = tt(d); return np.sin(2*np.pi*55*t) * np.exp(-t * 18) + np.sin(2*np.pi*50*np.clip(t-.18, 0, None)) * np.exp(-np.clip(t-.18, 0, None) * 18) * (t > .18) * .7
def phring(d=1.4): t = tt(d); return (np.sin(2*np.pi*440*t) + np.sin(2*np.pi*480*t)) * .25 * (np.sin(2*np.pi*20*t) > 0) * (t < 1.0)
M = Mix(DUR)
M.add(fade(lowpass(saw(note(26), 18.3, 6), .03), 2, 1), 0, .4)
M.add(fade(lowpass(noise(18.3), .015), 1, 1), 0, .5)                          # wind
for c in T["cards"]: M.add(braam(), c, .55)
for k in range(22): M.add(heart(), 5.6 + k * .58, .45)
for r in T["rings"]: M.add(phring(), r, .3, .2)
M.add(fade(hp(noise(.5)) * .3, .01, .2), T["vm"], .25); M.add(sum(np.sin(2*np.pi*f*tt(.6)) for f in (1000,)) * .3, T["vm"] + .3, .3)
M.add(braam(3.5), T["title"], .7); M.add(impact(3), T["title"], .4)
M.add(riser(.8), T["answer"] - .8, .2)
groove(M, T["answer"], 27.4, 90, [[67, 71, 74], [64, 67, 71], [60, 64, 67], [62, 66, 69]], gain=.45, drums=False)
for b in T["bubbles"]: M.add(pop(1000), b, .3)
logo_sting(M, T["logo"], root=67, tail=10)
M.write("audio.wav"); print("ok")
