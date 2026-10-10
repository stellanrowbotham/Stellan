"""Test fixtures. ALL prices here are FICTIONAL test data (provider 'FICTIONAL-TEST'),
never real market data and never evidence of performance."""
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apprentice.ledger import Ledger, iso, new_id
from apprentice.market_calendar import ET
from apprentice.settings import CONFIG_DIR, Settings, config_hash

FICTIONAL = "FICTIONAL-TEST"


def et(y, m, d, hh=10, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=ET)


class Env:
    """Temporary config + ledger directories."""

    def __init__(self, level=1, **overrides):
        self.root = Path(tempfile.mkdtemp(prefix="apprentice-test-"))
        self.cfg = self.root / "config"
        shutil.copytree(CONFIG_DIR, self.cfg)
        self.ledger = self.root / "ledger"
        self.ledger.mkdir()
        s = json.loads((self.cfg / "settings.json").read_text())
        s["agent"]["level"] = level
        for path, val in overrides.items():
            node = s
            keys = path.split(".")
            for k in keys[:-1]:
                node = node[k]
            node[keys[-1]] = val
        (self.cfg / "settings.json").write_text(json.dumps(s))
        self.approve()

    def approve(self):
        (self.cfg / "approved.sha256").write_text(config_hash(self.cfg) + "\n")

    def settings(self):
        return Settings(self.cfg)

    def L(self, name):
        return Ledger(name, self.ledger)

    def quote(self, symbol, at, price=None, bid=None, ask=None, exchange="TSX", asset_type="stock", currency="CAD", data_ts=None):
        return self.L("quotes").append({"id": new_id("q"), "symbol": symbol, "exchange": exchange, "asset_type": asset_type,
                                        "currency": currency, "price": price, "bid": bid, "ask": ask,
                                        "spread_source": "quoted" if bid is not None else "none",
                                        "data_ts": iso(data_ts or at), "observed_at": iso(at), "provider": FICTIONAL,
                                        "source_id": "twelve_data"}, now=at)

    def note(self, at, title="Fictional test headline", source_id="sec_edgar", published=None, **kw):
        return self.L("research").append({"id": new_id("r"), "kind": "headline", "title": title, "url": "https://example.invalid/" + new_id("u"),
                                          "source_id": source_id, "published_at": iso(published or at), "observed_at": iso(at),
                                          "claim_type": "fact", **kw}, now=at)

    def usdcad(self, at, value=1.37):
        return self.L("research").append({"id": new_id("m"), "kind": "macro", "series": "FXUSDCAD", "value": value,
                                          "data_date": (at - timedelta(days=1)).date().isoformat(), "observed_at": iso(at),
                                          "source_id": "bank_of_canada_valet"}, now=at)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def proposal(symbol, at, evidence, stop, target, strategy="swing", **kw):
    return {"symbol": symbol, "strategy": strategy, "decided_at": iso(at), "evidence_ids": evidence, "stop_price": stop,
            "target_price": target, "thesis": "Fictional test thesis", "invalidation": "Fictional: breaks support",
            "exit_rules": "Sell at target or stop", **kw}
