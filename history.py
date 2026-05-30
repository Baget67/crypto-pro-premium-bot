# =====================================
# history.py
# Crypto Pro Premium Bot V2
# =====================================

import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

MAX_HISTORY_PER_SYMBOL = 100


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def add_snapshot(
    history,
    symbol,
    oi,
    volume,
    price,
    funding
):
    if symbol not in history:
        history[symbol] = []

    history[symbol].append({
        "timestamp": datetime.utcnow().isoformat(),
        "oi": oi,
        "volume": volume,
        "price": price,
        "funding": funding
    })

    if len(history[symbol]) > MAX_HISTORY_PER_SYMBOL:
        history[symbol] = history[symbol][-MAX_HISTORY_PER_SYMBOL:]


def get_snapshot_minutes_ago(
    history,
    symbol,
    minutes_back
):
    if symbol not in history:
        return None

    snapshots = history[symbol]

    if len(snapshots) < 2:
        return None

    target_seconds = minutes_back * 60

    latest = snapshots[-1]

    latest_ts = datetime.fromisoformat(
        latest["timestamp"]
    )

    closest = None
    best_diff = float("inf")

    for snap in snapshots:

        snap_ts = datetime.fromisoformat(
            snap["timestamp"]
        )

        diff = abs(
            (
                latest_ts -
                snap_ts
            ).total_seconds()
            - target_seconds
        )

        if diff < best_diff:
            best_diff = diff
            closest = snap

    return closest


def percent_change(
    current,
    previous
):
    if previous is None:
        return 0

    if previous == 0:
        return 0

    return (
        (current - previous)
        / previous
    ) * 100


def get_changes(
    history,
    symbol
):
    if symbol not in history:
        return None

    snapshots = history[symbol]

    if len(snapshots) < 2:
        return None

    latest = snapshots[-1]

    snap_15m = get_snapshot_minutes_ago(
        history,
        symbol,
        15
    )

    snap_1h = get_snapshot_minutes_ago(
        history,
        symbol,
        60
    )

    snap_4h = get_snapshot_minutes_ago(
        history,
        symbol,
        240
    )

    result = {}

    if snap_15m:
        result["oi_15m"] = percent_change(
            latest["oi"],
            snap_15m["oi"]
        )

        result["volume_15m"] = percent_change(
            latest["volume"],
            snap_15m["volume"]
        )

        result["price_15m"] = percent_change(
            latest["price"],
            snap_15m["price"]
        )

    if snap_1h:
        result["oi_1h"] = percent_change(
            latest["oi"],
            snap_1h["oi"]
        )

        result["volume_1h"] = percent_change(
            latest["volume"],
            snap_1h["volume"]
        )

        result["price_1h"] = percent_change(
            latest["price"],
            snap_1h["price"]
        )

    if snap_4h:
        result["oi_4h"] = percent_change(
            latest["oi"],
            snap_4h["oi"]
        )

        result["volume_4h"] = percent_change(
            latest["volume"],
            snap_4h["volume"]
        )

        result["price_4h"] = percent_change(
            latest["price"],
            snap_4h["price"]
        )

    return result