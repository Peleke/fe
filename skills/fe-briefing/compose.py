"""Compose a Fe Briefing from raw data into the newsletter template."""

from data.market import get_prices, get_gas, get_tvl_changes
from data.unlocks import get_upcoming_unlocks, format_unlock_alert


TEMPLATE = """ᚠ THE NUMBER
{the_number}

ᚠ MARKET SNAPSHOT
{market_snapshot}

ᚠ THE STORY
{the_story}

ᚠ ONE CONCEPT
{one_concept}

ᚠ WHAT WE'RE BUILDING
{building}

ᚠ POLL
{poll}

— ᚠ Fe
fe.peleke.me"""


def compose_market_snapshot(prices: dict, gas: dict) -> str:
    """Turn raw price + gas data into the MARKET SNAPSHOT section."""
    lines = []

    token_map = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "solana": "SOL",
        "arbitrum": "ARB",
    }

    for token_id, data in prices.items():
        symbol = token_map.get(token_id, token_id.upper())
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0)
        direction = "+" if change >= 0 else ""
        lines.append(f"• {symbol} ${price:,.0f} ({direction}{change:.1f}%)")

    if gas.get("average"):
        lines.append(f"• ETH gas: {gas['average']} gwei avg")

    return "\n".join(lines)


def compose_briefing(
    the_number: str,
    the_story: str,
    one_concept: str,
    building: str,
    poll: str,
) -> str:
    """Assemble a full briefing from pre-written sections + live data.

    The number, story, concept, building, and poll are written by the
    operator (or drafted by LLM and approved). Market snapshot is
    generated from live data.
    """
    prices = get_prices()
    gas = get_gas()
    market_snapshot = compose_market_snapshot(prices, gas)

    # Append notable TVL movers if any
    tvl_movers = get_tvl_changes(threshold_pct=10.0)
    if tvl_movers:
        top = tvl_movers[0]
        direction = "+" if top["change_1d"] > 0 else ""
        market_snapshot += f"\n• {top['name']} TVL {direction}{top['change_1d']:.0f}% (${top['tvl'] / 1e9:.1f}B)"

    # Append unlock alerts if any
    unlocks = get_upcoming_unlocks(days_ahead=3)
    if unlocks:
        top_unlock = unlocks[0]
        market_snapshot += f"\n• {format_unlock_alert(top_unlock)}"

    return TEMPLATE.format(
        the_number=the_number,
        market_snapshot=market_snapshot,
        the_story=the_story,
        one_concept=one_concept,
        building=building,
        poll=poll,
    )
