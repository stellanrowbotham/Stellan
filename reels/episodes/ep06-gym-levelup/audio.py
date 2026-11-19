"""ep06 Gym Lead: Level Up: chiptune arcade, 128 BPM, C minor -> Eb major on level-up."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 28.6
T = {"enter": 0.5, "fu1": 6.0, "combo1": 7.6, "fu2": 8.6, "combo2": 11.0, "reply": 13.0, "booked": 14.6,
     "levelup": 15.6, "secured": 17.9, "logo": 19.5}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

def sq(f, d, duty=.5): t = tt(d); return np.where((t * f) % 1 < duty, 1.0, -1.0) * .5
def coin(): a = sq(988, .07) * env_exp(.07, 10); b = sq(1319, .3) * env_exp(.3, 9); return np.concatenate([a, b])
M = Mix(DUR)
M.add(np.concatenate([sq(note(m), .09) * env_exp(.09, 6) for m in (60, 64, 67, 72, 76, 79, 84)]), 0.1, .25)   # insert-coin jingle
chords = [[60, 63, 67], [56, 60, 63], [51, 55, 58], [58, 62, 65]]
beat = 60 / 128
for b in range(int((T["levelup"] - .9) / beat)):
    bt = .9 + b * beat; ch = chords[(b // 4) % 4]
    M.add(kick(), bt, .55); M.add(hat(), bt + beat / 2, .25, .3)
    if b % 4 in (1, 3): M.add(clap(), bt, .22)
    M.add(lowpass(sq(note(ch[0] - 24), beat * .45), .2) * env_exp(beat * .45, 4), bt, .3)
    for q in range(2): M.add(sq(note(ch[(b * 2 + q) % 3] + 12), beat * .22, .25) * env_exp(beat * .22, 12), bt + q * beat / 2, .07, .4 if q else -.4)
for k in ("fu1", "fu2", "reply"): M.add(pop(1200), T[k], .35)
for k in ("combo1", "combo2", "booked"): M.add(coin(), T[k], .3)
M.add(np.concatenate([sq(note(m), .07) * env_exp(.07, 5) for m in (63, 67, 70, 75, 79, 82, 87, 91)]), T["levelup"], .3)   # level up
M.add(impact(1.4), T["levelup"], .5); M.add(crowd(2.0), T["levelup"] + .1, .3)
up = [[63, 67, 70], [68, 72, 75]]
for b in range(int((T["logo"] - .2 - T["levelup"]) / beat)):
    bt = T["levelup"] + b * beat; ch = up[(b // 4) % 2]; M.add(kick(), bt, .5); M.add(hat(), bt + beat / 2, .22, .3)
    for q in range(4): M.add(sq(note(ch[q % 3] + 12), beat * .2, .25) * env_exp(beat * .2, 12), bt + q * beat / 4, .06, .4 if q % 2 else -.4)
logo_sting(M, T["logo"], root=63, tail=9.0)
M.write("audio.wav"); print("ok")
