"""ep15 Holiday rush, a calm count: soft ASMR bed, music-box arpeggio 70 BPM D major, gentle pings, breath swell."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from music import *

DUR = 34.5
T = {"count": [4.7, 5.7, 6.7], "fill": [7.0, 8.4], "calc": 8.6, "rows": [10.0, 12.0, 14.0, 15.8], "bot": 17.8, "breathe": 20.3, "logo": 23.2}
json.dump({"dur": DUR, **T}, open("timeline.json", "w"))
M = Mix(DUR)
def soft(f, d=1.2): t = tt(d); return np.sin(2*np.pi*f*t) * np.exp(-t * 3) * (1 - np.exp(-t * 200))
# music box arpeggio
seq = [74, 78, 81, 86, 81, 78]; t = 0.5
while t < 23.0:
    for i, m in enumerate(seq): M.add(soft(note(m + 12), 1.0), t + i * .43, .05, -.4 + .16 * i)
    t += len(seq) * .43
M.add(fade(lowpass(noise(23), .02), 2, 2), 0, .25)                           # air / room tone
for i in range(3): M.add(soft(note(86 + 2 * i), .8), T["count"][i], .18)
k = 0
for k in range(24): M.add(soft(note(90), .3), T["fill"][0] + k * (T["fill"][1] - T["fill"][0]) / 24, .05, .5 * np.sin(k))
for x in T["rows"]: M.add(bell(note(86), 1.2), x, .06)
for k in range(8): M.add(soft(note(81 + (k % 3) * 4), .5), T["bot"] + .3 + k * .25, .1)
M.add(fade(lowpass(noise(3.0), .03) * np.sin(np.linspace(0, np.pi, int(3.0 * SR))), .1, .5), T["breathe"], .5)
logo_sting(M, T["logo"], root=62, tail=11)
M.write("audio.wav"); print("ok")
