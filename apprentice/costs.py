"""Transaction cost model: Questrade-like for stocks/ETFs, Kraken-like for crypto.

All numbers come from settings.json["costs"], and are UNVERIFIED until checked against the
official fee schedules. Prices returned are in the asset's currency; cash amounts in CAD.
"""
import math


def _spread_pct(settings, asset):
    est = settings["costs"]["questrade"]["estimated_spread_pct"]
    if asset["asset_type"] == "etf":
        return est["etf"]
    return est.get(asset.get("size", "large_cap"), est["default"])


def fill_price(settings, asset, quote, side):
    """Simulated execution price before fees. Uses the real bid/ask when quoted, otherwise
    last price +/- an estimated half-spread (and says so)."""
    side = side.lower()
    if asset["asset_type"] == "crypto":
        slip = settings["costs"]["kraken"]["slippage_pct"]
    else:
        slip = settings["costs"]["questrade"]["slippage_pct"]
    if quote.get("bid") is not None and quote.get("ask") is not None:
        base, spread_source = (quote["ask"] if side == "buy" else quote["bid"]), "quoted"
        half_spread = (quote["ask"] - quote["bid"]) / 2
    else:
        half = _spread_pct(settings, asset) / 2 * quote["price"]
        base = quote["price"] + half if side == "buy" else quote["price"] - half
        spread_source, half_spread = "estimated", half
    px = base * (1 + slip) if side == "buy" else base * (1 - slip)
    return {"price": px, "base": base, "slippage_per_unit": abs(px - base), "half_spread_per_unit": half_spread,
            "spread_source": spread_source}


def round_qty(settings, asset, qty):
    if asset["asset_type"] == "crypto":
        return math.floor(qty * 1e8) / 1e8
    fractional = settings["costs"]["questrade"]["fractional_shares"].get("TSX" if asset["exchange"] == "TSX" else "US", False)
    return math.floor(qty * 1e4) / 1e4 if fractional else float(math.floor(qty))


def execution(settings, asset, quote, side, qty, usdcad=None):
    """Full cost breakdown for a simulated fill. Returns CAD cash impact."""
    if qty <= 0:
        raise ValueError("quantity must be positive")
    fp = fill_price(settings, asset, quote, side)
    notional = fp["price"] * qty
    fx = 1.0
    if asset["currency"] == "USD":
        if not usdcad:
            raise ValueError("USD asset needs a USD/CAD rate (Bank of Canada)")
        fx = usdcad
    notional_cad = notional * fx
    commission = fx_fee = venue_fee = 0.0
    if asset["asset_type"] == "crypto":
        venue_fee = notional_cad * settings["costs"]["kraken"]["taker_fee_pct"]
    else:
        commission = settings["costs"]["questrade"]["stock_commission"]
        if asset["currency"] == "USD":
            fx_fee = notional_cad * settings["costs"]["questrade"]["fx_fee_pct"]
    fees = commission + fx_fee + venue_fee
    cash_delta = -(notional_cad + fees) if side == "buy" else notional_cad - fees
    return {
        "side": side, "qty": qty, "price": fp["price"], "base_price": fp["base"], "spread_source": fp["spread_source"],
        "fx_rate": fx, "notional_cad": notional_cad, "commission_cad": commission, "fx_fee_cad": fx_fee,
        "venue_fee_cad": venue_fee, "fees_cad": fees,
        "slippage_cad": fp["slippage_per_unit"] * qty * fx, "spread_cost_cad": fp["half_spread_per_unit"] * qty * fx,
        "cash_delta_cad": cash_delta,
    }
