import time
from datetime import datetime, timedelta

import config
from telegram_bot import send_telegram_alert, send_menu, flush_old_updates, poll_telegram
from strategy import get_data, analyze
from trades import record_trade_entry, close_trade, get_stats
from screener import run_screener


# ===============================================================
#                    MARKET CHECK
# ===============================================================

def run_market_check(force=False):
    """Run analysis on all watchlisted stocks."""
    is_snoozed = config.snooze_until and datetime.now() < config.snooze_until

    if force:
        print("Manual check triggered...")

    print(f"--- Checking Market at {datetime.now().strftime('%H:%M:%S')} ---")

    summary_lines = []

    for stock in list(config.STOCKS):
        data = get_data(stock)
        signal, price, indicators = analyze(data)

        if price is not None:
            rsi_str = f"{indicators.get('rsi', 0):.1f}" if indicators.get('rsi') else "N/A"
            vol_str = f"{indicators.get('volume_ratio', 0):.1f}x" if indicators.get('volume_ratio') else "N/A"
            print(f"[{stock}] Rs.{price:.2f} | {signal} | RSI:{rsi_str} | Vol:{vol_str}")

            if force:
                icon = ""
                if "BUY" in signal:
                    icon = "^ "
                elif "SELL" in signal:
                    icon = "v "
                else:
                    icon = "- "
                summary_lines.append(
                    f"{icon}{stock.replace('.NS', '')}: Rs.{price:.2f} | {signal} | RSI:{rsi_str}"
                )

            if signal in ["BUY", "SELL", "STRONG BUY", "STRONG SELL"]:
                if config.current_signals.get(stock) != signal:
                    old_signal = config.current_signals.get(stock)
                    if old_signal and old_signal.replace("STRONG ", "") != signal.replace("STRONG ", ""):
                        closed = close_trade(stock, price)
                        if closed:
                            pnl_str = f"+Rs.{closed['pnl']:.2f}" if closed['pnl'] >= 0 else f"Rs.{closed['pnl']:.2f}"
                            pnl_msg = f"\nClosed {closed['signal']} trade: {pnl_str} ({closed['pnl_pct']}%)"
                        else:
                            pnl_msg = ""
                    else:
                        pnl_msg = ""

                    record_trade_entry(stock, signal.replace("STRONG ", ""), price)

                    if not is_snoozed and not force:
                        strength = "STRONG " if "STRONG" in signal else ""
                        action = signal.replace("STRONG ", "")
                        chart_link = f"https://finance.yahoo.com/quote/{stock}"
                        rsi_val = indicators.get('rsi')
                        macd_val = indicators.get('macd_hist')

                        alert_msg = (
                            f"<b>{strength}{action} - {stock}</b>\n\n"
                            f"Price: Rs.{price:.2f}\n"
                            f"RSI: {rsi_val:.1f}\n"
                            f"MACD Histogram: {macd_val:.4f}\n"
                            f"Volume: {indicators.get('volume_ratio', 0):.1f}x avg\n"
                            f"Time: {datetime.now().strftime('%H:%M:%S')}"
                            f"{pnl_msg}\n\n"
                            f"<a href='{chart_link}'>View Chart</a>"
                        )
                        send_telegram_alert(alert_msg)

                    config.current_signals[stock] = signal
        else:
            print(f"[{stock}] {signal}")
            if force:
                summary_lines.append(f"- {stock.replace('.NS', '')}: {signal}")

    if force and summary_lines:
        summary = "\n".join(summary_lines)
        send_telegram_alert(
            f"<b>Market Check</b>\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')} | TF: {config.INTERVAL}\n\n"
            f"{summary}"
        )

    if is_snoozed:
        remaining = (config.snooze_until - datetime.now()).seconds // 60
        print(f"(Alerts snoozed - {remaining} min remaining)")

    print(f"Next check in {config.CHECK_INTERVAL_SECONDS // 60} minutes...\n")


# ===============================================================
#                    COMMAND HANDLERS
# ===============================================================

def handle_text_command(text):
    """Handle text-based commands from the user."""
    text = text.strip()

    if text in ["/start", "/menu"]:
        send_menu()

    elif text.startswith("/add "):
        stock = text.split(" ", 1)[1].strip().upper()
        if stock not in config.STOCKS:
            config.STOCKS.append(stock)
            config.current_signals[stock] = None
            config.save_watchlist()
            send_telegram_alert(f"Added {stock} to watchlist.")
        else:
            send_telegram_alert(f"{stock} is already in the watchlist.")

    elif text.startswith("/remove "):
        stock = text.split(" ", 1)[1].strip().upper()
        if stock in config.STOCKS:
            config.STOCKS.remove(stock)
            config.current_signals.pop(stock, None)
            config.save_watchlist()
            send_telegram_alert(f"Removed {stock} from watchlist.")
        else:
            send_telegram_alert(f"{stock} not found in watchlist.")

    elif text == "/list":
        if config.STOCKS:
            stocks_list = "\n".join([
                f"  {i+1}. <a href='https://finance.yahoo.com/quote/{s}'>{s}</a>"
                for i, s in enumerate(config.STOCKS)
            ])
            send_telegram_alert(f"<b>Watchlist ({len(config.STOCKS)} stocks)</b>\n{stocks_list}")
        else:
            send_telegram_alert("Watchlist is empty. Use /add SYMBOL to add stocks.")

    elif text == "/stats":
        send_telegram_alert(get_stats())

    elif text == "/scan":
        run_screener()

    elif text == "/check":
        run_market_check(force=True)

    elif text.startswith("/timeframe "):
        tf = text.split(" ", 1)[1].strip().lower()
        valid_tf = {"1m": "1d", "5m": "5d", "15m": "5d", "30m": "1mo", "1h": "1mo", "1d": "6mo"}
        if tf in valid_tf:
            config.INTERVAL = tf
            config.PERIOD = valid_tf[tf]
            send_telegram_alert(f"Timeframe changed to <b>{tf}</b>.\nData period: {config.PERIOD}")
        else:
            send_telegram_alert(f"Invalid timeframe. Valid options:\n{', '.join(valid_tf.keys())}")

    elif text.startswith("/snooze"):
        parts = text.split()
        minutes = 30
        if len(parts) > 1:
            try:
                minutes = int(parts[1])
            except ValueError:
                minutes = 30
        config.snooze_until = datetime.now() + timedelta(minutes=minutes)
        send_telegram_alert(
            f"Alerts snoozed for {minutes} minutes.\n"
            f"Resume at: {config.snooze_until.strftime('%H:%M:%S')}\n\n"
            f"Type /resume to resume early."
        )

    elif text == "/resume":
        config.snooze_until = None
        send_telegram_alert("Alerts resumed! You will receive signals again.")

    elif text == "/help":
        help_msg = (
            "<b>Bot Commands</b>\n\n"
            "/menu - Show button menu\n"
            "/add SYMBOL - Add stock (e.g. /add TCS.NS)\n"
            "/remove SYMBOL - Remove stock\n"
            "/list - View watchlist\n"
            "/check - Force market check now\n"
            "/stats - Paper trading stats\n"
            "/scan - Nifty 50 screener\n"
            "/timeframe 5m - Change timeframe\n"
            "/snooze 30 - Snooze alerts (minutes)\n"
            "/resume - Resume alerts\n"
            "/help - Show this help"
        )
        send_telegram_alert(help_msg)


def handle_callback(callback_data, callback_query_id):
    """Handle inline keyboard button presses."""
    if callback_data == "cmd_add":
        send_telegram_alert("Type: /add SYMBOL\n\nExample: /add TATAMOTORS.NS")
    elif callback_data == "cmd_remove":
        if config.STOCKS:
            stocks_list = "\n".join([f"  {s}" for s in config.STOCKS])
            send_telegram_alert(f"Type: /remove SYMBOL\n\nCurrent watchlist:\n{stocks_list}")
        else:
            send_telegram_alert("Watchlist is empty.")
    elif callback_data == "cmd_list":
        handle_text_command("/list")
    elif callback_data == "cmd_check":
        run_market_check(force=True)
    elif callback_data == "cmd_stats":
        send_telegram_alert(get_stats())
    elif callback_data == "cmd_scan":
        run_screener()
    elif callback_data == "cmd_timeframe":
        send_telegram_alert(
            f"Current timeframe: <b>{config.INTERVAL}</b>\n\n"
            "Type: /timeframe [value]\n"
            "Options: 1m, 5m, 15m, 30m, 1h, 1d"
        )
    elif callback_data == "cmd_snooze_30":
        config.snooze_until = datetime.now() + timedelta(minutes=30)
        send_telegram_alert(f"Alerts snoozed for 30 minutes.\nResume at: {config.snooze_until.strftime('%H:%M:%S')}")


# ===============================================================
#                    MAIN LOOP
# ===============================================================

def run_bot():
    print(f"Trading Bot Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(config.STOCKS)} stocks | Timeframe: {config.INTERVAL}")
    print("Press Ctrl+C to stop.\n")

    flush_old_updates()
    send_menu()

    last_market_check = time.time()

    try:
        while True:
            poll_telegram(handle_text_command, handle_callback)

            now = time.time()
            if now - last_market_check >= config.CHECK_INTERVAL_SECONDS:
                run_market_check()
                last_market_check = time.time()

            time.sleep(3)

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        send_telegram_alert("Trading Bot Stopped.")


if __name__ == "__main__":
    run_bot()
