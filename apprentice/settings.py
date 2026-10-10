"""Load the protected config and check it against the approved hash.

The config files (settings.json, universe.json) are approved by Stellan. Their combined SHA-256
is stored in config/approved.sha256. If the files change without a matching approval, the
config is reported as *unapproved* and the risk engine refuses every simulated trade.
"""
import hashlib
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent
CONFIG_DIR = PKG / "config"
PROTECTED = ("settings.json", "universe.json")
APPROVED_FILE = CONFIG_DIR / "approved.sha256"


def config_hash(config_dir=CONFIG_DIR):
    h = hashlib.sha256()
    for name in PROTECTED:
        h.update(name.encode())
        h.update((Path(config_dir) / name).read_bytes())
    return h.hexdigest()


def approved_hash(config_dir=CONFIG_DIR):
    p = Path(config_dir) / "approved.sha256"
    if not p.exists():
        return None
    return p.read_text().split()[0].strip()


def is_approved(config_dir=CONFIG_DIR):
    return approved_hash(config_dir) == config_hash(config_dir)


class Settings:
    def __init__(self, config_dir=CONFIG_DIR):
        self.config_dir = Path(config_dir)
        self.raw = json.loads((self.config_dir / "settings.json").read_text())
        self.universe = json.loads((self.config_dir / "universe.json").read_text())["assets"]
        self.sources = json.loads((self.config_dir / "sources.json").read_text())["sources"]
        self.approved = is_approved(self.config_dir)
        self._assets = {a["symbol"]: a for a in self.universe}

    def __getitem__(self, k):
        return self.raw[k]

    @property
    def level(self):
        return int(self.raw["agent"]["level"])

    @property
    def risk(self):
        return self.raw["risk"]

    def asset(self, symbol):
        return self._assets.get(symbol)

    def strategy(self, name):
        return self.raw["strategies"].get(name)
