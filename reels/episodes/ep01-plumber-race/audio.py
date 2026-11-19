"""ep01 The Missed-Call Dash: 128 BPM, E minor, sports-broadcast energy."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 33.5
CP = [13.95, 14.75, 16.25]      # bot passes: text sent, question asked, job booked
FINISH = 17.25
LOGO = 22.5
tl = {"dur": DUR, "cp": CP, "finish": FINISH, "logo": LOGO, "missed": 2.6, "whip": 5.2, "go": 5.55}
json.dump(tl, open("timeline.json", "w"))

M = Mix(DUR)
for k in range(5): M.add(ring(0.45), 0.15 + k * 0.5, .35)                     # phone ringing
M.add(impact(1.2), 2.6, .5); M.add(blip(180, .4), 2.6, .4)                     # MISSED slam
for k in range(6): M.add(pop(420 + 30 * (k % 3)), 3.1 + k * .38, .25, -.3)     # drips
M.add(whoosh(.6), 4.95, .6)                                                     # whip pan
M.add(whistle(.5), 5.35, .5)                                                    # race start
groove(M, 5.55, 17.25, 128, [[64, 67, 71], [60, 64, 67], [55, 59, 62], [62, 66, 69]], gain=.85)
for i, c in enumerate(CP): M.add(pop(900 + i * 200), c, .5); M.add(bell(note(83 + i * 2), 1.2), c, .12)
M.add(riser(1.8), 15.45, .35)
M.add(impact(), FINISH, .7); M.add(crowd(3.5), FINISH, .55)
for k in range(8): M.add(pop(700 + k * 90), FINISH + .05 * k, .15, (k % 2) - .5)
groove(M, FINISH, 22.2, 128, [[64, 67, 71], [60, 64, 67]], drums=True, arp=True, pad=True, gain=.75)
M.add(whoosh(.7), 22.0, .5)
logo_sting(M, LOGO, root=64, tail=10.5)
M.write("audio.wav")
print("ok")
