# =====================================
# config.py
# Crypto Pro Premium Bot V2
# =====================================

# Scan interval
SCAN_INTERVAL_MINUTES = 5

# Top opportunities
TOP_LONGS = 3
TOP_SHORTS = 2

# Cooldown
ALERT_COOLDOWN_HOURS = 12

# Filters

MIN_VOLUME_24H = 5_000_000      # $5M
MIN_OPEN_INTEREST = 1_000_000   # $1M

# Scores

LONG_ALERT_SCORE = 80
SHORT_ALERT_SCORE = 80

# History

MAX_HISTORY_PER_SYMBOL = 100

# Bybit

BYBIT_CATEGORY = "linear"

# Discord

EMBED_COLOR_LONG = 0x00FF00
EMBED_COLOR_SHORT = 0xFF0000