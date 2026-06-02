import json
import os
from datetime import datetime

SIGNALS_FILE = "signals.json"


def load_signals():
    if not os.path.exists(SIGNALS_FILE):
        return []

    with open(SIGNALS_FILE, "r") as f:
        return json.load(f)


def save_signals(signals):
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals, f, indent=2)


def save_signal(symbol, direction, score, day_change, entry_price):
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
        "return_4h": None,

        "status_1h": None,
        "status_4h": None
    })

    save_signals(signals)
