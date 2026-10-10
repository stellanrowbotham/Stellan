"""Portfolio accounting: everything is rebuilt from the append-only fills ledger."""
from dataclasses import dataclass, field

TOL = 1e-6


@dataclass
class Position:
    trade_id: str
    symbol: str
    qty: float = 0.0
    cost_basis_cad: float = 0.0  # includes buy fees
    opened_at: str = ""
    strategy: str = ""


@dataclass
class Portfolio:
    starting_balance: float
    cash: float
    positions: dict = field(default_factory=dict)  # trade_id -> Position
    realized: dict = field(default_factory=dict)  # trade_id -> realized P&L (CAD, after all fees)
    fees_cad: float = 0.0
    slippage_cad: float = 0.0
    spread_cost_cad: float = 0.0

    @classmethod
    def from_fills(cls, starting_balance, fills):
        p = cls(starting_balance, starting_balance)
        for f in sorted(fills, key=lambda f: f["seq"]):
            p.apply(f)
        return p

    def apply(self, f):
        self.cash += f["cash_delta_cad"]
        self.fees_cad += f["fees_cad"]
        self.slippage_cad += f.get("slippage_cad", 0.0)
        self.spread_cost_cad += f.get("spread_cost_cad", 0.0)
        pos = self.positions.get(f["trade_id"])
        if f["side"] == "buy":
            if pos is None:
                pos = self.positions[f["trade_id"]] = Position(f["trade_id"], f["symbol"], opened_at=f["filled_at"],
                                                               strategy=f.get("strategy", ""))
            pos.qty += f["qty"]
            pos.cost_basis_cad += -f["cash_delta_cad"]
        else:
            if pos is None or f["qty"] > pos.qty + TOL:
                raise ValueError(f"sell of {f['qty']} {f['symbol']} exceeds position in trade {f['trade_id']}")
            share = f["qty"] / pos.qty
            basis = pos.cost_basis_cad * share
            self.realized[f["trade_id"]] = self.realized.get(f["trade_id"], 0.0) + f["cash_delta_cad"] - basis
            pos.cost_basis_cad -= basis
            pos.qty -= f["qty"]
            if pos.qty <= TOL:
                del self.positions[f["trade_id"]]

    # ------------------------------------------------------------ valuation
    def market_values(self, marks):
        """marks: symbol -> CAD price per unit (mark at bid, or last price when no bid)."""
        out = {}
        for tid, pos in self.positions.items():
            px = marks.get(pos.symbol)
            out[tid] = None if px is None else px * pos.qty
        return out

    def equity(self, marks):
        mv = self.market_values(marks)
        missing = [self.positions[t].symbol for t, v in mv.items() if v is None]
        # A position with no mark is valued at cost and reported as missing (never invented).
        total = self.cash + sum(v if v is not None else self.positions[t].cost_basis_cad for t, v in mv.items())
        return total, missing

    def unrealized(self, marks):
        mv = self.market_values(marks)
        return {t: (v - self.positions[t].cost_basis_cad) if v is not None else None for t, v in mv.items()}

    @property
    def realized_total(self):
        return sum(self.realized.values())

    def reconcile(self):
        """cash + open cost basis must equal starting balance + realized P&L."""
        lhs = self.cash + sum(p.cost_basis_cad for p in self.positions.values())
        rhs = self.starting_balance + self.realized_total
        return abs(lhs - rhs) < 1e-6, lhs, rhs

    def exposure(self, marks, settings):
        """CAD exposure by sector and crypto share, at marks (cost if unmarked)."""
        by_sector, crypto = {}, 0.0
        mv = self.market_values(marks)
        for t, pos in self.positions.items():
            v = mv[t] if mv[t] is not None else pos.cost_basis_cad
            a = settings.asset(pos.symbol) or {}
            by_sector[a.get("sector", "unknown")] = by_sector.get(a.get("sector", "unknown"), 0.0) + v
            if a.get("asset_type") == "crypto":
                crypto += v
        return by_sector, crypto
