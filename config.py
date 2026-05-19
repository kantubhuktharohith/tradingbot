import os

# Load .env variables manually
def load_env():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()

# ===== SETTINGS =====
INTERVAL = "5m"
PERIOD = "5d"
CHECK_INTERVAL_SECONDS = 300  # 5 minutes between market checks

# Load stocks from watchlist.txt
STOCKS = []
if os.path.exists("watchlist.txt"):
    with open("watchlist.txt", "r") as f:
        STOCKS = [line.strip() for line in f if line.strip()]
if not STOCKS:
    STOCKS = ["RELIANCE.NS"]

# Load Nifty 50 for screener
NIFTY50 = []
if os.path.exists("nifty50.txt"):
    with open("nifty50.txt", "r") as f:
        NIFTY50 = [line.strip() for line in f if line.strip()]

# Telegram Settings
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "your_telegram_token_here")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Bot State
current_signals = {}
last_update_id = 0
snooze_until = None
TRADES_FILE = "trades.json"
processed_updates = set()


def save_watchlist():
    with open("watchlist.txt", "w") as f:
        for stock in STOCKS:
            f.write(f"{stock}\n")
