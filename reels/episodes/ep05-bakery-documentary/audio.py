"""ep05 Planet Bakery: nature-documentary score, 80 BPM, G major, birds + dot-matrix printer."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 33.6
T = {"flock": 7.6, "print": 16.1, "tickets": [17.6, 19.3, 21.0], "logo": 24.5}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))

M = Mix(DUR)
chords = [[55, 59, 62], [52, 55, 59], [48, 52, 55], [50, 54, 57]]
groove(M, 0.0, 16.0, 80, chords, drums=False, bass=True, arp=True, pad=True, gain=.55)
for k in range(10):   # gentle piano-ish melody
    m = [74, 71, 67, 69, 71, 74, 76, 74, 71, 67][k]; M.add(bell(note(m), 1.6), 0.6 + k * 1.5, .06, -.3 + (k % 3) * .3)
for i in range(7):    # birds (the order flock)
    t0 = T["flock"] + i * .6; M.add(whistle(.25), t0 + .1, .25, .6 - i * .15); M.add(whistle(.18), t0 + .35, .18, .5 - i * .15)
groove(M, 16.0, 24.3, 80, chords, drums=True, bass=True, arp=True, pad=True, gain=.6)
M.add(pop(900), T["print"], .4)
for t0 in T["tickets"]:   # dot-matrix printer buzz + stamp
    d = 1.0; tt_ = tt(d); buzz = hp(noise(d)) * (np.sin(2 * np.pi * 45 * tt_) > 0) * .5
    M.add(lowpass(buzz, .4) * env_exp(d, .5), t0, .3, .3); M.add(impact(.4), t0 + 1.6, .25); M.add(bell(note(88), .8), t0 + 1.6, .1)
logo_sting(M, T["logo"], root=67, tail=9.0)
M.write("audio.wav"); print("ok")
