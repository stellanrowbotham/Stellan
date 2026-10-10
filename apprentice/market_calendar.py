"""Exchange hours and holidays for TSX and US (NYSE/Nasdaq). Crypto never closes.

Holiday lists were compiled on 2026-10-10 from the published holiday rules (general knowledge) and
must be checked against the official TMX and NYSE calendars once a year. Dates outside the covered
years are treated as CLOSED and reported, so the simulator fails safe instead of guessing.
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/Toronto")  # Toronto and New York share Eastern Time
COVERED_YEARS = {2026, 2027}

HOLIDAYS = {
    "TSX": {
        date(2026, 1, 1), date(2026, 2, 16), date(2026, 4, 3), date(2026, 5, 18), date(2026, 7, 1),
        date(2026, 8, 3), date(2026, 9, 7), date(2026, 10, 12), date(2026, 12, 25), date(2026, 12, 28),
        date(2027, 1, 1), date(2027, 2, 15), date(2027, 3, 26), date(2027, 5, 24), date(2027, 7, 1),
        date(2027, 8, 2), date(2027, 9, 6), date(2027, 10, 11), date(2027, 12, 27), date(2027, 12, 28),
    },
    "US": {
        date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3), date(2026, 5, 25),
        date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7), date(2026, 11, 26), date(2026, 12, 25),
        date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26), date(2027, 5, 31),
        date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6), date(2027, 11, 25), date(2027, 12, 24),
    },
}
EARLY_CLOSE = {  # 1:00 PM ET
    "TSX": {date(2026, 12, 24), date(2027, 12, 24)},
    "US": {date(2026, 11, 27), date(2026, 12, 24), date(2027, 11, 26)},
}
REGULAR_OPEN, REGULAR_CLOSE, EARLY = time(9, 30), time(16, 0), time(13, 0)


class CalendarGap(Exception):
    """Raised when asked about a year the calendar doesn't cover."""


def _ex(exchange):
    exchange = exchange.upper()
    if exchange in ("NYSE", "NASDAQ", "US"):
        return "US"
    if exchange in ("TSX", "TSXV"):
        return "TSX"
    if exchange in ("KRAKEN", "CRYPTO"):
        return "CRYPTO"
    raise ValueError(f"unknown exchange {exchange}")


def is_trading_day(exchange, d):
    ex = _ex(exchange)
    if ex == "CRYPTO":
        return True
    if d.year not in COVERED_YEARS:
        raise CalendarGap(f"{ex} holiday calendar does not cover {d.year}; update market_calendar.py")
    return d.weekday() < 5 and d not in HOLIDAYS[ex]


def session(exchange, d):
    """(open, close) aware datetimes for a trading day, or None if closed."""
    ex = _ex(exchange)
    if ex == "CRYPTO":
        start = datetime.combine(d, time(0, 0), ET)
        return start, start + timedelta(days=1)
    if not is_trading_day(ex, d):
        return None
    close = EARLY if d in EARLY_CLOSE[ex] else REGULAR_CLOSE
    return datetime.combine(d, REGULAR_OPEN, ET), datetime.combine(d, close, ET)


def is_open(exchange, dt):
    if _ex(exchange) == "CRYPTO":
        return True
    local = dt.astimezone(ET)
    try:
        s = session(exchange, local.date())
    except CalendarGap:
        return False  # fail safe
    return bool(s) and s[0] <= local < s[1]


def trading_days_between(exchange, start, end):
    """Count trading days in [start, end] (dates)."""
    n, d = 0, start
    while d <= end:
        try:
            n += is_trading_day(exchange, d)
        except CalendarGap:
            pass
        d += timedelta(days=1)
    return n


def next_open(exchange, dt):
    """The first moment at or after dt when the exchange is open."""
    local = dt.astimezone(ET)
    d = local.date()
    for _ in range(15):
        s = session(exchange, d)
        if s:
            if local < s[0]:
                return s[0]
            if local < s[1]:
                return local
        d += timedelta(days=1)
    raise CalendarGap("no open session found in 15 days")
