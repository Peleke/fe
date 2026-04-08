---
name: fe-briefing
description: Daily DeFi + market intelligence briefing generator
version: 0.1.0
context: fork
required_env:
  - COINGECKO_API_KEY
  - BEEHIIV_API_KEY
  - BEEHIIV_PUBLICATION_ID
  - TELEGRAM_BOT_TOKEN
optional_env:
  - DUNE_API_KEY
  - NANSEN_API_KEY
triggers:
  - "generate briefing"
  - "fe briefing"
  - "morning briefing"
  - "/fe-briefing"
---

# Fe Briefing Skill

Generates a daily DeFi + market intelligence briefing from live data sources, composes it into the Fe newsletter format, and publishes to Beehiiv and/or Telegram.

## Flow

```
Schedule (daily 6:30 AM) OR manual trigger
    │
    ▼
┌─────────────────────────┐
│  1. PULL DATA           │
│  - CoinGecko: prices    │
│  - DeFi Llama: TVL      │
│  - Tokenomist: unlocks  │
│  - Dune: whale moves    │
│  - Etherscan: gas       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  2. COMPOSE             │
│  - Fill template        │
│  - Select ONE CONCEPT   │
│  - Generate poll        │
│  - Personalize if       │
│    wallet connected     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  3. REVIEW              │
│  - Send draft to user   │
│    via Telegram/CLI      │
│  - User approves/edits  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  4. PUBLISH             │
│  - Beehiiv (newsletter) │
│  - Telegram (bot)       │
│  - Optional: LinWheel   │
│    (LinkedIn excerpt)   │
└─────────────────────────┘
```

## Template

```
ᚠ THE NUMBER
{one_stat} — {context_sentence}

ᚠ MARKET SNAPSHOT
• {price_1}
• {price_2}  
• {notable_move}

ᚠ THE STORY
{2-3 paragraphs on the biggest thing that happened.
 Opinionated. Connect to the reader's portfolio.}

ᚠ ONE CONCEPT
{Finance/DeFi concept in <150 words. Concrete, 
 no jargon. Why it matters to the reader specifically.}

ᚠ WHAT WE'RE BUILDING
{2-3 sentences on Fe progress. Link to landing page.}

ᚠ POLL
{One question, 4 options. Designed to generate replies.}
```

## Data Sources

| Data | Module | Source | Auth |
|------|--------|--------|------|
| Token prices | `data/market.py` | CoinGecko API | Free tier (demo key) |
| TVL / protocol stats | `data/market.py` | DeFi Llama API | No auth needed |
| Gas prices | `data/market.py` | Etherscan API | Free tier |
| Token unlocks | `data/unlocks.py` | Tokenomist API | Free tier |
| Whale movements | `data/whales.py` | Dune Analytics API | Free tier (rate limited) |
| User positions | `data/portfolio.py` | Wallet RPC (read-only) | No auth (public addresses) |

## Personalization Modes

**Newsletter (Beehiiv)**: Generic briefing. No wallet data. Same for all subscribers. This is the free tier.

**Telegram (personal)**: Wallet-connected briefing. Reads user's positions from connected addresses. Adds "Your Portfolio Impact" section with personalized P&L and alerts. This is the pro tier.

## Voice Rules

- Smart friend, not analyst. "Here's what happened and why you should care" not "Markets exhibited volatility."
- 400 words max for newsletter. 600 max for Telegram (more personal data).
- No em-dash clause connectors (Bragi rule). Vary sentence rhythm.
- Concrete numbers over vague descriptions. "$180M TVL increase" not "significant growth."
- One concept per issue, explained from zero. Assume the reader is technical but new to finance.
