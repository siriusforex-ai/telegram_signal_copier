"""
config.py — All settings for the Signal Copier Bot
Fill in your credentials and adjust settings as needed.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════
#  TELEGRAM (Telethon)
# ═══════════════════════════════════════════════
# Get these from https://my.telegram.org
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

# The signal channel to monitor
# Use the @username (without @) or the channel ID (negative number)
SIGNAL_CHANNEL = os.getenv("SIGNAL_CHANNEL", "Forex")

# ═══════════════════════════════════════════════
#  METATRADER 5
# ═══════════════════════════════════════════════
MT5_ACCOUNT = int(os.getenv("MT5_ACCOUNT", "1301110952"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "your_password")
MT5_SERVER = os.getenv("MT5_SERVER", "XMGlobal-MT5 6")

# Symbol mapping — signal channels say "Gold" or "XAUUSD"
# but your broker might call it "GOLD" or "XAUUSD" or "GOLD.s"
SYMBOL = "GOLD"

# ═══════════════════════════════════════════════
#  CLAUDE AI (Signal Parsing)
# ═══════════════════════════════════════════════
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ═══════════════════════════════════════════════
#  TRADE SETTINGS
# ═══════════════════════════════════════════════
DEFAULT_LOT_SIZE = 0.03         # total lot — splits across TPs
MIN_LOT = 0.01                  # broker minimum
MAGIC_NUMBER = 400401           # unique ID for this bot's trades
DEVIATION = 20                  # max slippage in points

# If entry price is within this many points of current price,
# use market order. Otherwise use pending (limit/stop).
MARKET_ORDER_THRESHOLD = 50     # points

# ═══════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════
REFRESH_INTERVAL = 2            # seconds between dashboard refreshes

# ═══════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════
TRADE_LOG_FILE = "trade_log.json"

# ═══════════════════════════════════════════════
#  SESSION FILE
# ═══════════════════════════════════════════════
# Telethon saves your login session here
# After first login you won't need to verify again
SESSION_FILE = "signal_copier_session"
