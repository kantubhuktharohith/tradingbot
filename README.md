# 📈 Indian Stock Market Trading Bot

A Python-based automated trading signal bot for **Indian stocks (NSE)** that monitors your watchlist and sends real-time **BUY / SELL alerts via Telegram** using a multi-indicator technical analysis strategy.

> ⚠️ **Disclaimer:** This bot is for **educational and paper trading purposes only**. It does not execute real trades. Always do your own research before investing.

---

## 🚀 Features

- 📊 **Multi-Indicator Strategy** — Combines SMA, RSI, MACD, and Volume for high-confidence signals
- 📱 **Telegram Integration** — Receive instant BUY/SELL alerts with live chart links on your phone
- 🔍 **Nifty 50 Screener** — Scan all 50 Nifty stocks for top gainers, losers & high volume movers
- 📋 **Dynamic Watchlist** — Add/remove stocks on the fly via Telegram commands
- 📉 **Paper Trade Tracker** — Auto-records every signal and tracks P&L statistics
- ⏱️ **Flexible Timeframes** — Switch between 1m, 5m, 15m, 30m, 1h, and 1d intervals
- 🔕 **Snooze Mode** — Temporarily pause alerts without stopping the bot
- ☁️ **Deployable to Heroku** — Ships with a `Procfile` for cloud deployment

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `yfinance` | Fetch real-time & historical stock data from Yahoo Finance |
| `pandas` | Technical indicator calculations |
| `requests` | Telegram Bot API communication |
| Python 3.x | Core language |

---

## 📁 Project Structure

```
trading/
├── bot.py             # Main loop: market checks, Telegram command routing
├── strategy.py        # Technical analysis engine (SMA, RSI, MACD, Volume)
├── screener.py        # Nifty 50 scanner for gainers, losers & high volume
├── telegram_bot.py    # Telegram API helpers (send alerts, menu, polling)
├── trades.py          # Paper trade recording and P&L statistics
├── config.py          # Settings, watchlist loader, environment variables
├── watchlist.txt      # Your monitored stocks (one ticker per line)
├── nifty50.txt        # Nifty 50 ticker list for screener
├── trades.json        # Auto-generated paper trade history
├── requirements.txt   # Python dependencies
├── Procfile           # Heroku worker process definition
└── .env               # 🔒 Secret keys (NOT committed to Git)
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a Telegram Bot
1. Open Telegram and chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy your **Bot Token**
4. Get your **Chat ID** from [@userinfobot](https://t.me/userinfobot)

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 5. Set Up Your Watchlist
Edit `watchlist.txt` and add NSE stock tickers (one per line):
```
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
```

### 6. Run the Bot
```bash
python bot.py
```

---

## 📲 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` or `/menu` | Show the interactive button menu |
| `/add SYMBOL` | Add a stock to watchlist (e.g. `/add TCS.NS`) |
| `/remove SYMBOL` | Remove a stock from watchlist |
| `/list` | View current watchlist |
| `/check` | Force an immediate market check |
| `/stats` | View paper trading P&L statistics |
| `/scan` | Run Nifty 50 screener |
| `/timeframe 5m` | Change analysis timeframe (`1m` `5m` `15m` `30m` `1h` `1d`) |
| `/snooze 30` | Snooze alerts for N minutes |
| `/resume` | Resume alerts after snooze |
| `/help` | Show all available commands |

---

## 🧠 Trading Strategy

The bot uses a **score-based multi-indicator system**. Each indicator votes, and the final signal is determined by the total score:

| Indicator | BUY Condition | SELL Condition |
|-----------|--------------|----------------|
| **SMA 20/50** | SMA20 > SMA50 (bullish crossover) | SMA20 < SMA50 (bearish crossover) |
| **RSI (14)** | RSI < 70 (not overbought) | RSI > 30 (not oversold) |
| **MACD** | MACD Line > Signal Line | MACD Line < Signal Line |
| **Volume** | Volume ≥ 1.2× 20-day average | Volume ≥ 1.2× 20-day average |

**Signal Rules:**
- ✅ **STRONG BUY** → 3 or 4 buy conditions met
- 🟢 **BUY** → 2 buy conditions met + SMA bullish
- 🔴 **STRONG SELL** → 3 or 4 sell conditions met
- ❌ **SELL** → 2 sell conditions met + SMA bearish
- ⏸️ **HOLD** → No clear signal

---

## ☁️ Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set TELEGRAM_TOKEN=your_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id
git push heroku main
heroku ps:scale worker=1
```

The `Procfile` is already configured to run the bot as a background worker.

---

## 📊 Example Alert

```
📈 STRONG BUY - TCS.NS

Price: Rs.3842.50
RSI: 58.3
MACD Histogram: 0.0214
Volume: 1.8x avg
Time: 10:35:00

🔗 View Chart
```

---

## 🔒 Security Notes

- Never commit your `.env` file — it's already in `.gitignore`
- Rotate your Telegram bot token immediately if exposed
- This bot only **reads** market data; it cannot place real orders

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ for Indian stock market traders</p>
