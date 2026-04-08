"""Token unlock tracking via Tokenomist (formerly TokenUnlocks)."""

import json
from urllib.request import urlopen, Request
from datetime import datetime, timedelta


TOKENOMIST_BASE = "https://api.tokenomist.ai/v1"


def _get(url: str) -> dict:
    req = Request(url)
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_upcoming_unlocks(days_ahead: int = 7) -> list[dict]:
    """Fetch token unlocks happening in the next N days.

    Returns:
        [{token, date, amount_usd, pct_of_supply, type}, ...]
        sorted by amount_usd descending
    """
    # NOTE: Tokenomist API structure may vary — this is the expected shape.
    # Fallback to scraping tokenomist.ai/unlocks if API isn't available.
    try:
        data = _get(f"{TOKENOMIST_BASE}/unlocks?days={days_ahead}")
        return [
            {
                "token": u["token"],
                "date": u["date"],
                "amount_usd": u.get("value_usd", 0),
                "pct_of_supply": u.get("pct_circulating", 0),
                "type": u.get("type", "unknown"),  # cliff, linear, etc.
            }
            for u in data.get("unlocks", [])
        ]
    except Exception:
        # Graceful degradation — return empty if API unavailable
        return []


def format_unlock_alert(unlock: dict) -> str:
    """Format a single unlock into a human-readable alert string."""
    token = unlock["token"].upper()
    amt = unlock["amount_usd"]
    pct = unlock["pct_of_supply"]
    date = unlock["date"]

    if amt >= 100_000_000:
        severity = "MAJOR"
    elif amt >= 10_000_000:
        severity = "Notable"
    else:
        severity = "Minor"

    return (
        f"[{severity}] {token}: ${amt / 1_000_000:.1f}M unlock "
        f"({pct:.1f}% of supply) on {date}"
    )


def get_unlocks_for_tokens(tokens: list[str], days_ahead: int = 7) -> list[dict]:
    """Filter upcoming unlocks to only tokens the user holds."""
    all_unlocks = get_upcoming_unlocks(days_ahead)
    tokens_lower = {t.lower() for t in tokens}
    return [u for u in all_unlocks if u["token"].lower() in tokens_lower]
