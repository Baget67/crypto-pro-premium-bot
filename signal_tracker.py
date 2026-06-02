import time

tracked_signals = []


def track_signal(
    symbol,
    direction,
    score,
    entry_price
):

    tracked_signals.append({
        "symbol": symbol,
        "direction": direction,
        "score": score,
        "entry_price": entry_price,
        "timestamp": time.time(),
        "checked_1h": False
    })

    print(
        f"TRACKING {direction} "
        f"{symbol} "
        f"score={score}"
    )
