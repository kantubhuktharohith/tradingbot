# Indian Stock Market Trading Signal Bot

An automated trading signal bot for Indian stock markets (NSE) that monitors selected stocks, analyzes technical indicators in real time, and delivers BUY and SELL alerts directly to Telegram.

The system is designed for educational purposes, strategy testing, and paper trading. It does not place live trades or interact with brokerage accounts.

## Key Features

### Real-Time Market Monitoring

Continuously tracks NSE-listed stocks from a configurable watchlist and evaluates market conditions using multiple technical indicators.

### Multi-Indicator Trading Strategy

Generates trading signals by combining:

* Simple Moving Averages (SMA 20 / SMA 50)
* Relative Strength Index (RSI)
* Moving Average Convergence Divergence (MACD)
* Volume Analysis

### Telegram Notifications

Receive instant alerts with:

* Signal type (BUY / SELL)
* Current market price
* Indicator values
* Volume confirmation
* Direct chart links

### Nifty 50 Market Scanner

Analyze Nifty 50 constituents to identify:

* Top gainers
* Top losers
* High-volume movers
* Potential trading opportunities

### Dynamic Watchlist Management

Manage monitored stocks directly through Telegram commands without restarting the application.

### Paper Trading Analytics

Track generated signals and maintain performance statistics, including:

* Trade history
* Win/Loss ratio
* Profit & Loss estimates
* Strategy performance metrics

### Flexible Timeframes

Support for multiple analysis intervals:

* 1 Minute
* 5 Minutes
* 15 Minutes
* 30 Minutes
* 1 Hour
* 1 Day

### Alert Control

Pause and resume notifications using Snooze Mode while keeping the bot operational.

### Cloud Deployment Ready

Includes deployment configuration for Heroku and can be adapted for other cloud platforms.

---

## Technology Stack

| Technology       | Purpose                                  |
| ---------------- | ---------------------------------------- |
| Python 3.x       | Core Application                         |
| pandas           | Data Processing & Indicator Calculations |
| yfinance         | Market Data Retrieval                    |
| requests         | Telegram API Integration                 |
| Telegram Bot API | Alert Delivery                           |

---

## Project Architecture

```text
trading/
├── bot.py             # Application entry point
├── strategy.py        # Signal generation engine
├── screener.py        # Nifty 50 market scanner
├── telegram_bot.py    # Telegram integration layer
├── trades.py          # Paper trading and analytics
├── config.py          # Configuration management
├── watchlist.txt      # User watchlist
├── nifty50.txt        # Nifty 50 symbols
├── trades.json        # Trade history storage
├── requirements.txt   # Python dependencies
├── Procfile           # Deployment configuration
└── .env               # Environment variables
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading-bot
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Telegram Bot

1. Create a bot using @BotFather.
2. Obtain the bot token.
3. Retrieve your Telegram Chat ID.
4. Create a `.env` file:

```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Configure Watchlist

Add NSE symbols to `watchlist.txt`:

```text
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
```

### Start the Bot

```bash
python bot.py
```

---

## Telegram Commands

| Command          | Function                         |
| ---------------- | -------------------------------- |
| `/start`         | Initialize bot interface         |
| `/menu`          | Display command menu             |
| `/add SYMBOL`    | Add stock to watchlist           |
| `/remove SYMBOL` | Remove stock from watchlist      |
| `/list`          | Show active watchlist            |
| `/check`         | Trigger immediate market scan    |
| `/scan`          | Run Nifty 50 screener            |
| `/stats`         | Display paper trading statistics |
| `/timeframe`     | Change analysis timeframe        |
| `/snooze`        | Pause notifications              |
| `/resume`        | Resume notifications             |
| `/help`          | Show help information            |

---

## Trading Logic

The strategy uses a weighted confirmation model where multiple indicators contribute to the final signal.

| Indicator | Bullish Signal            | Bearish Signal          |
| --------- | ------------------------- | ----------------------- |
| SMA 20/50 | SMA20 > SMA50             | SMA20 < SMA50           |
| RSI (14)  | RSI below overbought zone | RSI above oversold zone |
| MACD      | MACD above signal line    | MACD below signal line  |
| Volume    | Above average volume      | Above average volume    |

### Signal Classification

| Signal      | Conditions                                          |
| ----------- | --------------------------------------------------- |
| STRONG BUY  | 3–4 bullish confirmations                           |
| BUY         | Minimum 2 confirmations including SMA trend         |
| HOLD        | No clear directional bias                           |
| SELL        | Minimum 2 bearish confirmations including SMA trend |
| STRONG SELL | 3–4 bearish confirmations                           |

---

## Example Alert

```text
📈 STRONG BUY | TCS.NS

Price: ₹3842.50
RSI: 58.3
MACD Histogram: 0.0214
Volume: 1.8x Average

Time: 10:35 AM
```

---

## Deployment

### Heroku

```bash
heroku create your-app-name

heroku config:set TELEGRAM_TOKEN=your_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id

git push heroku main

heroku ps:scale worker=1
```

The included Procfile runs the application as a background worker process.

---

## Security Best Practices

* Never commit `.env` files.
* Store credentials using environment variables.
* Rotate Telegram tokens immediately if compromised.
* Restrict repository access when testing proprietary strategies.

---

## Disclaimer

This project is intended solely for educational, research, and paper-trading purposes.

The software does not provide financial advice and should not be considered a recommendation to buy or sell securities. Trading and investing involve significant financial risk. Users are responsible for conducting their own research and making independent investment decisions.

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to your fork
5. Open a Pull Request

Please open an issue before submitting major feature requests or architectural changes.

---

## License

Distributed under the MIT License. See the LICENSE file for details.

---

<p align="center">
Built for algorithmic trading enthusiasts and developers exploring Indian equity markets.
</p>
