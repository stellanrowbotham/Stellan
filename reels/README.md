# FlowPilot reels

Daily Instagram reels for **@flowpilot2026**, made entirely in code (canvas animation + synthesized music)
by the **FlowPilot · Daily reel** scheduled task. Instructions for the agent: `agents/flowpilot-reels.md`.

```
reels/
├── calendar.md          ← what gets made next (first `planned` row)
├── posted.md            ← log of every reel posted
├── engine/              ← render.js (frames), voice.py (voice mix + captions), sheet.sh (preview), build.sh (full pipeline)
├── episodes/epNN-slug/  ← scene.html + audio.py + voice.json + vo/*.mp3 for each reel (ep00 is the reference)
└── out/                 ← finished epNN-slug.mp4 + .jpg (served to Instagram from GitHub raw)
```

## Brand kit
- **Name:** FlowPilot (one word, capital F and P). Tagline: "AI automations for local businesses".
- **Logo mark:** glowing paper plane inside a ring (see ep00, 44–52 s).
- **Colours:** navy `#05081A`/`#0B1235`, cyan `#3CF2FF`, violet `#8B6CFF`, mint `#3DFFA8` (success),
  red `#FF4D6D` (problems), amber `#FFB547` (warmth). Each episode may pick one extra accent.
- **Type:** Inter (installed): 900 for headlines, 600–700 for UI.
- **Format:** 1080×1920, 30 fps, 20–45 s, safe area: keep text 90 px from the edges and out of the bottom 260 px
  (Instagram's caption overlay).
- **Every reel ends** with the plane/ring logo, "FlowPilot", and the episode's CTA in a pill button.

## Voices & cast (ElevenLabs, model `eleven_v4`)
Every reel has a voice track: 2–6 short lines, 12–35 s of speech in total, plus on-screen captions (most people watch
muted). Audio tags like `[sighs]`, `[whispers]`, `[laughs]`, `[stressed, talking fast]` make the delivery funny.
Recurring characters build a series people recognise:

| Character | Voice (id) | Personality / running gags |
|---|---|---|
| **The Pilot** (mascot) | Brian `nPczCjzI2devNBz1zQrb` | Calm airline captain over the PA, with a "ding-dong" chime (`pa_chime`). "This is your FlowPilot speaking." Sign-off: "You're still the captain." |
| **The Owner** | Jacob L. `bcXKpJEti28IoAWz1NfD` | Frazzled, relatable, talks too fast, small wins at the end |
| Customer (impatient) | Laura `FGY2WhTYpPnrIDTdsKH5` | Texts at midnight, "hellooo??" |
| The Old-School Owner | Bill `pqHfZKP75CvOlQylNhV4` | "Back in my day we answered every call ourselves…" |
| The Missed Call (villain) | Callum `N2lVS1w4EtoT3dr4eOWO` | Sneaky gremlin who steals leads |
| Boss-fight narrator | Grav `6qtlupOXBYtv2nYY2VgL` | Epic villain voice: "THE NO-SHOW… has arrived." |
| Hype / hook narrator | Ian `uC1r2TVqMMkHyjSAteKk` | Punchy first-second hooks |
| Game announcer | Caliph `GzrA7L2rl4TVlFYss7aF` | "Level up!", combo counters |

Voice styles to rotate (parodies of genres, never impressions of real people): airline PA · nature documentary
("here we observe the small business owner in its natural habitat") · movie-trailer ("in a world…") · sports
commentary on a race · villain monologue · game-show host · true-crime ("the case of the missing lead") ·
calm ASMR "satisfying automation" · two-character skit (Owner vs Customer, Owner vs Missed Call).

## Formats (rotate; never the same format two days running)
F1 Night-shift chaos → flow · F2 Phone chat demo (bubbles typing) · F3 Split screen without vs with ·
F4 Race / timer (human vs bot) · F5 Myth vs fact flip cards · F6 Day-in-the-life clock spin ·
F7 Robot assembles from parts (each part = a step) · F8 Time calculator (clearly labeled "example") ·
F9 POV text story · F10 Quiz · F11 Town map with pins · F12 Receipt / ticket printing ·
F13 Game level-up / XP bar · F14 Kanban board that moves itself · F15 Retro terminal · F16 Comic panels.
New formats are welcome; add them here as F17+.

## Tactics (rotate)
DM keyword (PLAN, BOOK, CALL…) · comment keyword · "save this" · "send to a business-owner friend" ·
caption poll · quiz · myth-busting · behind the scenes · seasonal hook · local pride (Southwestern Ontario) ·
"Part 2 tomorrow" series cliffhanger (only if the next calendar row continues it).

## Honesty rules (never break)
No prices, no invented statistics or percentages, no fake testimonials or reviews, no promised results,
no real business or person names (use fictional first names only). Numbers on screen are either clearly
labeled "example" or are counts inside the story (e.g. "47 unread"). Always "you stay in control".
