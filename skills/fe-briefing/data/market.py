"""Market data pulls: prices, TVL, gas."""

import os
import json
from urllib.request import urlopen, Request


COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE = "https://api.llama.fi"
ETHERSCAN_BASE = "https://api.etherscan.io/api"


def _get(url: str, headers: dict | None = None) -> dict:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_prices(tokens: list[str] = None) -> dict:
    """Fetch current prices from CoinGecko.

    Args:
        tokens: CoinGecko IDs, e.g. ["bitcoin", "ethereum", "solana"]

    Returns:
        {token_id: {usd, usd_24h_change, usd_market_cap}}
    """
    tokens = tokens or ["bitcoin", "ethereum", "solana", "arbitrum"]
    ids = ",".join(tokens)
    url = f"{COINGECKO_BASE}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"

    key = os.environ.get("COINGECKO_API_KEY")
    headers = {"x-cg-demo-api-key": key} if key else {}

    return _get(url, headers)


def get_tvl_top(n: int = 10) -> list[dict]:
    """Top protocols by TVL from DeFi Llama.

    Returns:
        [{name, tvl, change_1d, chain, ...}, ...]
    """
    data = _get(f"{DEFILLAMA_BASE}/protocols")
    # Sort by TVL descending, take top N
    sorted_protocols = sorted(data, key=lambda p: p.get("tvl", 0), reverse=True)
    return [
        {
            "name": p["name"],
            "tvl": p.get("tvl", 0),
            "change_1d": p.get("change_1d", 0),
            "chain": p.get("chain", "Multi"),
        }
        for p in sorted_protocols[:n]
    ]


def get_tvl_changes(threshold_pct: float = 5.0) -> list[dict]:
    """Protocols with significant TVL changes in last 24h.

    Args:
        threshold_pct: Minimum absolute % change to include.

    Returns:
        [{name, tvl, change_1d, chain}, ...] sorted by abs change desc
    """
    data = _get(f"{DEFILLAMA_BASE}/protocols")
    movers = [
        {
            "name": p["name"],
            "tvl": p.get("tvl", 0),
            "change_1d": p.get("change_1d", 0),
            "chain": p.get("chain", "Multi"),
        }
        for p in data
        if abs(p.get("change_1d", 0)) >= threshold_pct and p.get("tvl", 0) > 1_000_000
    ]
    return sorted(movers, key=lambda x: abs(x["change_1d"]), reverse=True)


def get_gas() -> dict:
    """Current Ethereum gas prices from Etherscan.

    Returns:
        {low, average, high} in gwei
    """
    key = os.environ.get("ETHERSCAN_API_KEY", "")
    url = f"{ETHERSCAN_BASE}?module=gastracker&action=gasoracle&apikey={key}"
    data = _get(url)
    result = data.get("result", {})
    return {
        "low": int(result.get("SafeGasPrice", 0)),
        "average": int(result.get("ProposeGasPrice", 0)),
        "high": int(result.get("FastGasPrice", 0)),
    }
