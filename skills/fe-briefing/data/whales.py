"""Whale movement tracking via Dune Analytics."""

import os
import json
from urllib.request import urlopen, Request


DUNE_BASE = "https://api.dune.com/api/v1"


def _dune_get(path: str) -> dict:
    key = os.environ.get("DUNE_API_KEY", "")
    url = f"{DUNE_BASE}{path}"
    req = Request(url, headers={"x-dune-api-key": key})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_large_transfers(min_usd: float = 1_000_000, query_id: int = None) -> list[dict]:
    """Fetch large token transfers from a pre-built Dune query.

    Args:
        min_usd: Minimum transfer value to include.
        query_id: Dune query ID for large transfers.
                  Build your own at dune.com or use a community query.

    Returns:
        [{token, from_label, to_label, amount_usd, tx_hash, timestamp}, ...]
    """
    if not query_id:
        # Placeholder — user needs to set up their own Dune query
        # or use a community query ID for large transfers
        return []

    try:
        data = _dune_get(f"/query/{query_id}/results")
        rows = data.get("result", {}).get("rows", [])
        return [
            {
                "token": r.get("token_symbol", ""),
                "from_label": r.get("from_label", r.get("from_address", "")[:10]),
                "to_label": r.get("to_label", r.get("to_address", "")[:10]),
                "amount_usd": r.get("amount_usd", 0),
                "tx_hash": r.get("tx_hash", ""),
                "timestamp": r.get("block_time", ""),
            }
            for r in rows
            if r.get("amount_usd", 0) >= min_usd
        ]
    except Exception:
        return []


def format_whale_alert(transfer: dict) -> str:
    """Format a whale transfer into readable text."""
    token = transfer["token"]
    amt = transfer["amount_usd"]
    src = transfer["from_label"]
    dst = transfer["to_label"]

    if amt >= 10_000_000:
        emoji = "whale"
    elif amt >= 1_000_000:
        emoji = "large"
    else:
        emoji = ""

    return f"[{emoji}] {token}: ${amt / 1_000_000:.1f}M moved {src} -> {dst}"
