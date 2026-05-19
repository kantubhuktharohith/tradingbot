import yfinance as yf
import time
import config
from telegram_bot import send_telegram_alert


def run_screener():
    """Scan Nifty 50 for top gainers, losers, and high volume stocks."""
    print("Running Nifty 50 screener...")

    results = []
    for stock in config.NIFTY50:
        try:
            data = yf.download(stock, period="2d", interval="1d", progress=False, multi_level_index=False)
            if data is None or len(data) < 2:
                continue
            close = data['Close'].squeeze()
            volume = data['Volume'].squeeze()
            prev_close = float(close.iloc[-2])
            curr_close = float(close.iloc[-1])
            curr_vol = float(volume.iloc[-1])
            avg_vol = float(volume.mean())
            change_pct = ((curr_close - prev_close) / prev_close) * 100
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0

            results.append({
                "stock": stock,
                "price": curr_close,
                "change_pct": round(change_pct, 2),
                "vol_ratio": round(vol_ratio, 2)
            })
        except Exception:
            continue
        time.sleep(0.3)

    if not results:
        send_telegram_alert("Screener failed. Could not fetch data.")
        return

    gainers = sorted(results, key=lambda x: x["change_pct"], reverse=True)[:5]
    losers = sorted(results, key=lambda x: x["change_pct"])[:5]
    high_vol = sorted(results, key=lambda x: x["vol_ratio"], reverse=True)[:5]

    msg = "<b>Nifty 50 Screener</b>\n\n"

    msg += "<b>Top 5 Gainers</b>\n"
    for s in gainers:
        name = s['stock'].replace('.NS', '')
        link = f"https://finance.yahoo.com/quote/{s['stock']}"
        msg += f"  <a href='{link}'>{name}</a> Rs.{s['price']:.0f} (+{s['change_pct']}%)\n"

    msg += "\n<b>Top 5 Losers</b>\n"
    for s in losers:
        name = s['stock'].replace('.NS', '')
        link = f"https://finance.yahoo.com/quote/{s['stock']}"
        msg += f"  <a href='{link}'>{name}</a> Rs.{s['price']:.0f} ({s['change_pct']}%)\n"

    msg += "\n<b>Highest Volume (vs Avg)</b>\n"
    for s in high_vol:
        name = s['stock'].replace('.NS', '')
        link = f"https://finance.yahoo.com/quote/{s['stock']}"
        msg += f"  <a href='{link}'>{name}</a> {s['vol_ratio']}x avg volume\n"

    send_telegram_alert(msg)
    print("Screener complete.")
