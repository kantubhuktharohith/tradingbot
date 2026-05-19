import json
import os
from datetime import datetime
import config


def load_trades():
    if os.path.exists(config.TRADES_FILE):
        with open(config.TRADES_FILE, "r") as f:
            return json.load(f)
    return {"open_trades": {}, "closed_trades": []}


def save_trades(trades):
    with open(config.TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)


def record_trade_entry(stock, signal, price):
    """Record a paper trade entry."""
    trades = load_trades()
    trades["open_trades"][stock] = {
        "signal": signal,
        "entry_price": price,
        "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_trades(trades)


def close_trade(stock, exit_price):
    """Close an open paper trade and calculate PnL."""
    trades = load_trades()
    if stock not in trades["open_trades"]:
        return None

    entry = trades["open_trades"].pop(stock)
    entry_price = entry["entry_price"]
    signal = entry["signal"]

    if signal == "BUY":
        pnl = exit_price - entry_price
    else:
        pnl = entry_price - exit_price

    pnl_pct = (pnl / entry_price) * 100

    closed = {
        "stock": stock,
        "signal": signal,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "entry_time": entry["entry_time"],
        "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    trades["closed_trades"].append(closed)
    save_trades(trades)
    return closed


def get_stats():
    """Calculate overall paper trading statistics."""
    trades = load_trades()
    closed = trades["closed_trades"]

    if not closed:
        return "No closed trades yet. The bot will track trades automatically when signals change."

    total = len(closed)
    wins = sum(1 for t in closed if t["pnl"] > 0)
    losses = sum(1 for t in closed if t["pnl"] <= 0)
    total_pnl = sum(t["pnl"] for t in closed)
    win_rate = (wins / total) * 100 if total > 0 else 0

    best = max(closed, key=lambda t: t["pnl"])
    worst = min(closed, key=lambda t: t["pnl"])

    open_trades = trades["open_trades"]
    open_info = f"\nOpen Positions: {len(open_trades)}" if open_trades else ""

    return (
        f"<b>Paper Trading Stats</b>\n"
        f"{'='*25}\n"
        f"Total Trades: {total}\n"
        f"Wins: {wins} | Losses: {losses}\n"
        f"Win Rate: {win_rate:.1f}%\n"
        f"Total PnL: Rs.{total_pnl:.2f}\n\n"
        f"Best Trade: {best['stock']} (+Rs.{best['pnl']:.2f})\n"
        f"Worst Trade: {worst['stock']} (Rs.{worst['pnl']:.2f})"
        f"{open_info}"
    )
