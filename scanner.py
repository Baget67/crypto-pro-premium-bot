# =====================================
# scanner.py
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
async def scan_market(
    history
):

    longs = []
    shorts = []

    async with aiohttp.ClientSession() as session:

        tickers = await fetch_tickers(session)

        print(
            f"TICKERS RECEIVED: {len(tickers)}"
        )

        for ticker in tickers:

            try:

                symbol = ticker["symbol"]

                if symbol in [
                    "BTCUSDT",
                    "ETHUSDT",
                    "SOLUSDT"
                ]:

                    print(
                        f"CHECKING {symbol}"
                    )

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

                if symbol in [
                    "BTCUSDT",
                    "ETHUSDT",
                    "SOLUSDT"
                ]:

                    print(
                        f"{symbol} "
                        f"VOL={volume_24h} "
                        f"OI={oi} "
                        f"FUNDING={funding}"
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

                oi_1h = changes.get("oi_1h", 0)
                oi_4h = changes.get("oi_4h", 0)

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

    longs = sorted(
        longs,
        key=lambda x: x["score"],
        reverse=True
    )[:TOP_LONGS]

    shorts = sorted(
        shorts,
        key=lambda x: x["score"],
        reverse=True
    )[:TOP_SHORTS]

    print(
        f"FINAL LONGS: {len(longs)}"
    )

    print(
        f"FINAL SHORTS: {len(shorts)}"
    )

    return longs, shorts