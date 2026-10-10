"""Effective agent level. Promotions happen only when Stellan approves a config change (the level
lives in the hash-locked settings.json). Demotions are automatic and take effect immediately."""
from .settings import config_hash

NAMES = {1: "Research Apprentice", 2: "Paper-Trading Apprentice", 3: "Research Analyst",
         4: "Senior Analyst", 5: "Trusted Research Agent"}


def effective_level(settings, level_events):
    lvl = settings.level
    h = config_hash(settings.config_dir)
    for e in level_events:
        if e.get("event") == "demotion" and e.get("config_hash") == h:
            lvl = min(lvl, int(e["to_level"]))
    return lvl
