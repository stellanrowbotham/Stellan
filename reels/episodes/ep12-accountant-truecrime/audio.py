"""ep12 The Case of the Missing Receipts: noir true-crime bed, ticking clock, stamps, 84 BPM C minor."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 35.5
T = {"title": 0.3, "spin": [6.0, 14.2], "bot": 14.9, "logo": 25.4}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

def tick(): d = .04; return hp(hp(noise(d))) * env_exp(d, 120) * .5
def stamp(): d = .35; return (lowpass(noise(d), .3) * env_exp(d, 25) + np.sin(2*np.pi*70*tt(d)) * env_exp(d, 12)) * .8
def drone(f, d): t = tt(d); return lowpass(saw(f, d, 5), .04) * (0.6 + .4 * np.sin(2*np.pi*.15*t))
M = Mix(DUR)
M.add(fade(drone(note(36), 14.9), 1.5, 1.0), 0, .35); M.add(fade(drone(note(43), 14.9), 1.5, 1.0), 0, .18, .3)
for k in range(12): M.add(tick(), 0.4 + k * .5, .35)
k = 0; t = 6.0
while t < 14.2: M.add(tick(), t, .3, .2 * np.sin(k)); t += max(.07, .5 - k * .02); k += 1
for x, m in [(1.6, 60), (3.2, 63), (4.4, 58)]: M.add(fade(np.sin(2*np.pi*note(m)*tt(1.5)) * env_exp(1.5, 2), .01, .3), x, .08)
M.add(riser(1.2), 13.7, .25); M.add(impact(), 14.9, .45)
groove(M, 14.9, 25.4, 84, [[60, 63, 67], [56, 60, 63], [58, 62, 65], [55, 59, 62]], gain=.45, arp=True, drums=True)
logo_sting(M, T["logo"], root=60, tail=10)
M.write("audio.wav")
json.dump({"dur": DUR, **T}, open("timeline.json", "w")); print("ok")
