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
#  BYBIT API
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

            print(
                f"URL={url} STATUS={response.status}"
            )

            text = await response.text()

            print(
                text[:300]
            )

            if response.status != 200:
                return None

            return await response.json()

    except Exception as e:

        print(
            f"FETCH ERROR: {e}"
        )

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
# =====================================
# TREND SCORE
# =====================================

def calculate_trend_score(
    price_15m,
    price_1h,
    price_4h
):
    score = 0

    if price_15m > 0:
        score += 3

    if price_1h > 0:
        score += 3

    if price_4h > 0:
        score += 4

    return min(score, 10)


# =====================================
# BREAKDOWN SCORE
# =====================================

def calculate_breakdown_score(
    price_15m,
    price_1h,
    price_4h
):
    score = 0

    if price_15m < 0:
        score += 8

    if price_1h < 0:
        score += 8

    if price_4h < 0:
        score += 9

    return min(score, 25)


# =====================================
# MAIN SCANNER
# =====================================

async def scan_market(
    history
):

    longs = []
    shorts = []

    async with aiohttp.ClientSession() as session:

        tickers = await fetch_tickers(
            session
        )

        print(f"TICKERS RECEIVED: {len(tickers)}")

        for t in tickers[:10]:
            print(
                f"{t.get('symbol')} | "
                f"VOL={t.get('turnover24h')}"
            )

        for ticker in tickers:

            try:

                symbol = ticker["symbol"]

                volume_24h = float(
                    ticker.get(
                        "turnover24h",
                        0
                    )
                )

                price = float(
                    ticker.get(
                        "lastPrice",
                        0
                    )
                )

                if volume_24h < MIN_VOLUME_24H:
                    continue

                funding = await fetch_funding(
                    session,
                    symbol
                )

                oi = await fetch_open_interest(
                    session,
                    symbol
                )

                if oi < MIN_OPEN_INTEREST:
                    continue

                add_snapshot(
                    history,
                    symbol,
                    oi,
                    volume_24h,
                    price,
                    funding
                )

                changes = get_changes(
                    history,
                    symbol
                )

                if not changes:

                    changes = {
                        "oi_1h": 0,
                        "oi_4h": 0,
                        "volume_1h": 0,
                        "price_15m": 0,
                        "price_1h": 0,
                        "price_4h": 0
                    }

                oi_1h = changes.get(
                    "oi_1h",
                    0
                )

                oi_4h = changes.get(
                    "oi_4h",
                    0
                )

                volume_change = changes.get(
                    "volume_1h",
                    0
                )

                price_15m = changes.get(
                    "price_15m",
                    0
                )

                price_1h = changes.get(
                    "price_1h",
                    0
                )

                price_4h = changes.get(
                    "price_4h",
                    0
                )

                trend_score = (
                    calculate_trend_score(
                        price_15m,
                        price_1h,
                        price_4h
                    )
                )

                breakdown_score = (
                    calculate_breakdown_score(
                        price_15m,
                        price_1h,
                        price_4h
                    )
                )

                long_score, long_reasons = (
                    score_long(
                        oi_1h,
                        oi_4h,
                        volume_change,
                        price_1h,
                        funding,
                        trend_score
                    )
                )

                short_score, short_reasons = (
                    score_short(
                        oi_1h,
                        oi_4h,
                        volume_change,
                        price_1h,
                        funding,
                        breakdown_score
                    )
                )

                longs.append({
                    "symbol": symbol,
                    "score": long_score,
                    "price": price,
                    "funding": funding,
                    "oi_1h": oi_1h,
                    "oi_4h": oi_4h,
                    "volume_change": volume_change,
                    "reasons": long_reasons
                })

                shorts.append({
                    "symbol": symbol,
                    "score": short_score,
                    "price": price,
                    "funding": funding,
                    "oi_1h": oi_1h,
                    "oi_4h": oi_4h,
                    "volume_change": volume_change,
                    "reasons": short_reasons
                })

            except Exception as e:

                print(
                    f"ERROR {symbol}: {e}"
                )

                continue

                print(
                    f"FINAL LONGS: {len(longs)}"
                )
            
                print(
                    f"FINAL SHORTS: {len(shorts)}"
                )
            
                print("=" * 50)
                print("TOP LONGS RIGHT NOW")
            
                for i, coin in enumerate(
                    longs,
                    start=1
                ):
            
                    print(
                        f"#{i} "
                        f"{coin['symbol']} "
                        f"Score={coin['score']} "
                        f"OI1H={coin['oi_1h']:.2f}% "
                        f"OI4H={coin['oi_4h']:.2f}% "
                        f"VOL={coin['volume_change']:.2f}%"
                    )
            
                print("=" * 50)
                print("TOP SHORTS RIGHT NOW")
            
                for i, coin in enumerate(
                    shorts,
                    start=1
                ):
            
                    print(
                        f"#{i} "
                        f"{coin['symbol']} "
                        f"Score={coin['score']} "
                        f"OI1H={coin['oi_1h']:.2f}% "
                        f"OI4H={coin['oi_4h']:.2f}% "
                        f"VOL={coin['volume_change']:.2f}%"
                    )
            
                print("=" * 50)
            
                return longs, shorts