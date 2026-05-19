import yfinance as yf
import pandas as pd
import config


def get_data(stock, interval=None, period=None):
    """Fetch stock data from Yahoo Finance."""
    try:
        iv = interval or config.INTERVAL
        pd_val = period or config.PERIOD
        data = yf.download(stock, period=pd_val, interval=iv, progress=False, multi_level_index=False)
        data = data.dropna()
        return data
    except Exception as e:
        print(f"Error fetching data for {stock}: {e}")
        return None


def calculate_rsi(series, period=14):
    """Calculate RSI indicator."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series, fast=12, slow=26, signal=9):
    """Calculate MACD, Signal line, and Histogram."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def analyze(data):
    """Advanced multi-indicator analysis: SMA + RSI + MACD + Volume."""
    if data is None or len(data) < 50:
        return "NOT ENOUGH DATA", None, {}

    close = data['Close'].squeeze()
    volume = data['Volume'].squeeze()

    # SMA
    sma_20 = close.rolling(window=20).mean()
    sma_50 = close.rolling(window=50).mean()

    # RSI
    rsi = calculate_rsi(close, 14)

    # MACD
    macd_line, signal_line, macd_hist = calculate_macd(close)

    # Volume filter
    avg_volume = volume.rolling(window=20).mean()

    current_price = float(close.iloc[-1])

    latest_sma20 = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None
    latest_sma50 = float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None
    latest_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
    latest_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None
    latest_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None
    latest_hist = float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else None
    latest_vol = float(volume.iloc[-1]) if not pd.isna(volume.iloc[-1]) else 0
    latest_avg_vol = float(avg_volume.iloc[-1]) if not pd.isna(avg_volume.iloc[-1]) else 1
    vol_ratio = latest_vol / latest_avg_vol if latest_avg_vol > 0 else 0

    indicators = {
        "sma20": latest_sma20,
        "sma50": latest_sma50,
        "rsi": latest_rsi,
        "macd": latest_macd,
        "macd_signal": latest_signal,
        "macd_hist": latest_hist,
        "volume_ratio": round(vol_ratio, 2)
    }

    if latest_sma20 is None or latest_sma50 is None or latest_rsi is None:
        return "WAITING FOR DATA", current_price, indicators

    # Strategy Logic
    sma_bullish = latest_sma20 > latest_sma50
    sma_bearish = latest_sma20 < latest_sma50
    rsi_ok_buy = latest_rsi < 70 if latest_rsi else False
    rsi_ok_sell = latest_rsi > 30 if latest_rsi else False
    macd_bullish = latest_macd > latest_signal if (latest_macd is not None and latest_signal is not None) else False
    macd_bearish = latest_macd < latest_signal if (latest_macd is not None and latest_signal is not None) else False
    high_volume = vol_ratio >= 1.2

    buy_score = sum([sma_bullish, rsi_ok_buy, macd_bullish, high_volume])
    sell_score = sum([sma_bearish, rsi_ok_sell, macd_bearish, high_volume])

    if buy_score >= 3:
        return "STRONG BUY", current_price, indicators
    elif buy_score >= 2 and sma_bullish:
        return "BUY", current_price, indicators
    elif sell_score >= 3:
        return "STRONG SELL", current_price, indicators
    elif sell_score >= 2 and sma_bearish:
        return "SELL", current_price, indicators
    else:
        return "HOLD", current_price, indicators
