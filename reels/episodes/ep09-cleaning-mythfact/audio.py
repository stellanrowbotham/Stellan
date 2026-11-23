"""ep09 Myth or Fact: game-show brass-ish stabs, 120 BPM Bb, buzzer, ding, applause."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 32.6
T = {"card": 3.4, "answer": 7.6, "buzz": 11.65, "flip": 12.0, "job": 14.6, "text": 15.8, "stars": 17.6, "posted": 19.0, "logo": 21.2}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
for i, m in enumerate([70, 74, 77, 82]): M.add(lowpass(saw(note(m), .35, 6), .3) * env_exp(.35, 5), .05 + i * .1, .18)   # show fanfare
groove(M, 0.5, 11.6, 120, [[58, 62, 65], [63, 67, 70], [65, 69, 72], [58, 62, 65]], gain=.55, arp=True)
M.add(pop(800), T["card"], .4)
t = .6; d = tt(.6); M.add(np.sin(2*np.pi*np.cumsum(300 + 400*np.linspace(0, 1, len(d)))/SR) * env_exp(.6, 3), 9.4, .15)   # think-music swoop
buzz = (np.sign(np.sin(2*np.pi*110*tt(.8))) * .5 + np.sign(np.sin(2*np.pi*116*tt(.8))) * .5) * env_exp(.8, 1.5)
M.add(lowpass(buzz, .25), T["buzz"], .4)                                                                                  # wrong-answer buzzer
M.add(whoosh(.5), T["flip"], .4)
groove(M, 12.6, 21.0, 120, [[58, 62, 65], [63, 67, 70]], gain=.55)
M.add(pop(1200), T["text"], .35)
for k in range(5): M.add(bell(note(84 + k * 2), .5), T["stars"] + k * .16, .1)
M.add(crowd(2.4), T["posted"], .45); M.add(bell(note(91), 1.2), T["posted"], .15)
logo_sting(M, T["logo"], root=58, tail=10.5)
M.write("audio.wav"); print("ok")
