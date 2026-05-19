import requests
import json
import config


def send_telegram_alert(message, reply_markup=None):
    """Send a text message to Telegram, optionally with inline keyboard buttons."""
    print(f"Sending: {message[:80].replace(chr(10), ' ')}...")
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": config.CHAT_ID, "text": message, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram alert sent successfully.")
        else:
            print(f"Failed to send Telegram alert. Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")


def send_menu():
    """Send the main interactive menu with inline keyboard buttons."""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "+ Add Stock", "callback_data": "cmd_add"},
                {"text": "- Remove Stock", "callback_data": "cmd_remove"},
            ],
            [
                {"text": "Watchlist", "callback_data": "cmd_list"},
                {"text": "Check Now", "callback_data": "cmd_check"},
            ],
            [
                {"text": "Stats", "callback_data": "cmd_stats"},
                {"text": "Scan Nifty 50", "callback_data": "cmd_scan"},
            ],
            [
                {"text": "Timeframe", "callback_data": "cmd_timeframe"},
                {"text": "Snooze 30m", "callback_data": "cmd_snooze_30"},
            ],
        ]
    }
    send_telegram_alert(
        "<b>Trading Bot Menu</b>\n\nChoose an option below or type a command:",
        reply_markup=keyboard
    )


def answer_callback(callback_query_id):
    """Answer a callback query (removes the loading indicator on the button)."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass


def flush_old_updates():
    """Skip all pending Telegram messages so old button clicks don't trigger on restart."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url, params={"offset": -1, "timeout": 0}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])
            if results:
                config.last_update_id = results[-1]["update_id"]
                requests.get(url, params={"offset": config.last_update_id + 1, "timeout": 0}, timeout=5)
                print(f"Flushed old Telegram messages (update {config.last_update_id})")
            else:
                print("No pending Telegram messages.")
    except Exception:
        pass


def poll_telegram(handle_text_command, handle_callback):
    """Poll Telegram for new messages and callback queries."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url, params={"offset": config.last_update_id + 1, "timeout": 1}, timeout=10)
        if response.status_code != 200:
            return
        data = response.json()
        results = data.get("result", [])
        if not results:
            return

        # STEP 1: Update offset to the LATEST update ID first
        max_id = max(r["update_id"] for r in results)
        config.last_update_id = max_id

        # STEP 2: Confirm with Telegram BEFORE processing (prevents re-delivery)
        requests.get(url, params={"offset": config.last_update_id + 1, "timeout": 0}, timeout=5)

        # STEP 3: Now safely process each update
        for result in results:
            uid = result["update_id"]
            if uid in config.processed_updates:
                continue
            config.processed_updates.add(uid)

            # Handle text messages
            if "message" in result:
                msg = result["message"]
                sid = msg.get("chat", {}).get("id")
                if str(sid) != str(config.CHAT_ID):
                    continue
                text = msg.get("text", "").strip()
                if text:
                    handle_text_command(text)

            # Handle button presses (callback queries)
            elif "callback_query" in result:
                cq = result["callback_query"]
                sid = cq.get("from", {}).get("id")
                if str(sid) != str(config.CHAT_ID):
                    continue
                cb_data = cq.get("data", "")
                cb_id = cq.get("id")
                answer_callback(cb_id)
                if cb_data:
                    handle_callback(cb_data, cb_id)

        # Keep set small
        if len(config.processed_updates) > 200:
            config.processed_updates.clear()

    except Exception:
        pass
