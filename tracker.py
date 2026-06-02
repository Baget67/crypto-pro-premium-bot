import json
import os
from datetime import datetime

SIGNALS_FILE = "signals.json"


def load_signals():
    if not os.path.exists(SIGNALS_FILE):
        return []

    with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_signals(signals):
    with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2)


def signal_exists(
    symbol,
    direction,
    cooldown_hours=12
):

    signals = load_signals()

    now = datetime.utcnow().timestamp()

    cooldown_seconds = (
        cooldown_hours * 3600
    )

    for signal in signals:

        if (
            signal["symbol"] == symbol
            and signal["direction"] == direction
        ):

            age = (
                now - signal["timestamp"]
            )

            if age < cooldown_seconds:
                return True

    return False


def save_signal(
    symbol,
    direction,
    score,
    day_change,
    entry_price
):

    if signal_exists(
        symbol,
        direction
    ):
        return

    signals = load_signals()

    signals.append({
        "symbol": symbol,
        "direction": direction,
        "score": score,
        "day_change": day_change,
        "entry_price": entry_price,
        "timestamp": datetime.utcnow().timestamp(),

        "price_1h": None,
        "price_4h": None,

        "return_1h": None,
        "return_4h": None
    })

    save_signals(signals)

    print(
        f"SIGNAL SAVED: "
        f"{symbol} "
        f"{direction}"
    )


def update_signals(history):

    signals = load_signals()

    now = datetime.utcnow().timestamp()

    updated = False

    for signal in signals:

        symbol = signal["symbol"]

        if symbol not in history:
            continue

        if not history[symbol]:
            continue

        current_price = history[symbol][-1]["price"]

        elapsed_minutes = (
            now - signal["timestamp"]
        ) / 60

        # ====================
        # 1 HOUR
        # ====================

        if (
            signal["return_1h"] is None
            and elapsed_minutes >= 60
        ):

            signal["price_1h"] = current_price

            if signal["direction"] == "LONG":

                signal["return_1h"] = (
                    (
                        current_price
                        - signal["entry_price"]
                    )
                    / signal["entry_price"]
                ) * 100

            else:

                signal["return_1h"] = (
                    (
                        signal["entry_price"]
                        - current_price
                    )
                    / signal["entry_price"]
                ) * 100

            updated = True

        # ====================
        # 4 HOURS
        # ====================

        if (
            signal["return_4h"] is None
            and elapsed_minutes >= 240
        ):

            signal["price_4h"] = current_price

            if signal["direction"] == "LONG":

                signal["return_4h"] = (
                    (
                        current_price
                        - signal["entry_price"]
                    )
                    / signal["entry_price"]
                ) * 100

            else:

                signal["return_4h"] = (
                    (
                        signal["entry_price"]
                        - current_price
                    )
                    / signal["entry_price"]
                ) * 100

            updated = True

    if updated:

        save_signals(signals)
