"""Technical indicators from daily bars (lists of floats, oldest first). Pure functions."""
import math


def sma(xs, n):
    return sum(xs[-n:]) / n if len(xs) >= n else None


def ema(xs, n):
    if len(xs) < n:
        return None
    k = 2 / (n + 1)
    e = sum(xs[:n]) / n
    for x in xs[n:]:
        e = x * k + e * (1 - k)
    return e


def rsi(closes, n=14):
    """Wilder's RSI."""
    if len(closes) < n + 1:
        return None
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        ag = (ag * (n - 1) + g) / n
        al = (al * (n - 1) + l) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def atr(highs, lows, closes, n=14):
    if len(closes) < n + 1:
        return None
    trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(1, len(closes))]
    a = sum(trs[:n]) / n
    for t in trs[n:]:
        a = (a * (n - 1) + t) / n
    return a


def volatility(closes, n=20, periods_per_year=252):
    if len(closes) < n + 1:
        return None
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(len(closes) - n, len(closes))]
    m = sum(rets) / n
    var = sum((r - m) ** 2 for r in rets) / (n - 1)
    return math.sqrt(var) * math.sqrt(periods_per_year)


def momentum(closes, n=20):
    return closes[-1] / closes[-1 - n] - 1 if len(closes) > n else None


def summary(bars):
    c = [b["close"] for b in bars]
    h = [b["high"] for b in bars]
    l = [b["low"] for b in bars]
    out = {"last_close": c[-1] if c else None, "sma20": sma(c, 20), "sma50": sma(c, 50), "ema20": ema(c, 20),
           "rsi14": rsi(c), "atr14": atr(h, l, c), "vol20_annual": volatility(c), "mom20": momentum(c, 20),
           "high_52w": max(h[-252:]) if h else None, "low_52w": min(l[-252:]) if l else None, "bars": len(c)}
    if out["sma20"] and out["sma50"]:
        out["trend"] = "up" if c[-1] > out["sma20"] > out["sma50"] else "down" if c[-1] < out["sma20"] < out["sma50"] else "mixed"
    return out
