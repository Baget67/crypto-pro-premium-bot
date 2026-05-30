# =====================================
# scanner.py
# Crypto Pro Premium Bot V2
# =====================================

import aiohttp
import asyncio

from scoring import (
    score_long,
    score_short
)

from history import (
    add_snapshot,
    get_changes
)

from config import (
    MIN_VOLUME_24H,
    MIN_OPEN_INTEREST,
    TOP_LONGS,
    TOP_SHORTS
)

# =====================================
# BYBIT API
# =====================================

BYBIT_BASE = "https://api.bybit.com"


# =====================================
# HTTP
# =====================================

async def fetch_json(
    session,
    url
):
    try:

        async with session.get(
            url,
            timeout=15
        ) as response:

            if response.status != 200:
                return None

            return await response.json()

    except Exception:
        return None


# =====================================
# TICKERS
# =====================================

async def fetch_tickers(
    session
):
    url = (
        f"{BYBIT_BASE}"
        "/v5/market/tickers"
        "?category=linear"
    )

    data = await fetch_json(
        session,
        url
    )

    if not data:
        return []

    return (
        data
        .get("result", {})
        .get("list", [])
    )


# =====================================
# FUNDING
# =====================================

async def fetch_funding(
    session,
    symbol
):
    url = (
        f"{BYBIT_BASE}"
        "/v5/market/funding/history"
        f"?category=linear"
        f"&symbol={symbol}"
        "&limit=1"
    )

    data = await fetch_json(
        session,
        url
    )

    if not data:
        return 0

    rows = (
        data
        .get("result", {})
        .get("list", [])
    )

    if not rows:
        return 0

    try:
        return float(
            rows[0]["fundingRate"]
        )
    except:
        return 0


# =====================================
# OPEN INTEREST
# =====================================

async def fetch_open_interest(
    session,
    symbol
):
    url = (
        f"{BYBIT_BASE}"
        "/v5/market/open-interest"
        f"?category=linear"
        f"&symbol={symbol}"
        "&intervalTime=5min"
    )

    data = await fetch_json(
        session,
        url
    )

    if not data:
        return 0

    rows = (
        data
        .get("result", {})
        .get("list", [])
    )

    if not rows:
        return 0

    try:
        return float(
            rows[0]["openInterest"]
        )
    except:
        return 0