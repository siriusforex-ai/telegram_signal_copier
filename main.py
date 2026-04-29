"""
main.py — CodePips Telegram Signal Copier
Ties together the signal listener, MT5 executor, and dashboard.

Usage: python main.py
"""

import asyncio
import threading
import sys

import config
from mt5_executor import connect as mt5_connect, disconnect as mt5_disconnect, get_account_info
from signal_listener import listener_state
from dashboard import run_dashboard_loop


def print_banner():
    """Print the startup banner."""
    print()
    print("=" * 60)
    print("  CodePips — Telegram Signal Copier")
    print("=" * 60)

    acc = get_account_info()
    if acc:
        print(f"  Account:    {acc.login}")
        print(f"  Balance:    ${acc.balance:,.2f}")
        print(f"  Server:     {config.MT5_SERVER}")

    print(f"  Symbol:     {config.SYMBOL}")
    print(f"  Channel:    {config.SIGNAL_CHANNEL}")
    print(f"  Lot Size:   {config.DEFAULT_LOT_SIZE}")
    print(f"  AI Parser:  Claude ({config.CLAUDE_MODEL})")
    print("=" * 60)
    print()


def validate_config():
    """Check that all required settings are filled in."""
    errors = []

    if config.TELEGRAM_API_ID == 0:
        errors.append("TELEGRAM_API_ID is not set in .env")
    if not config.TELEGRAM_API_HASH:
        errors.append("TELEGRAM_API_HASH is not set in .env")
    if not config.TELEGRAM_PHONE:
        errors.append("TELEGRAM_PHONE is not set in .env")
    if not config.ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is not set in .env")
    if config.MT5_PASSWORD == "your_password":
        errors.append("MT5_PASSWORD is still the placeholder in .env")

    if errors:
        print("[ERROR] Missing configuration:")
        for e in errors:
            print(f"  - {e}")
        print()
        print("Create a .env file with the required values. See .env")
        return False

    return True


def main():
    if not validate_config():
        sys.exit(1)

    print("[INFO] Connecting to MetaTrader 5...")
    if not mt5_connect():
        print("[ERROR] Could not connect to MT5. Make sure MetaTrader 5 is open and logged in.")
        sys.exit(1)

    print_banner()

    print("[INFO] Starting Telegram signal listener...")
    print("[INFO] On first run you'll be asked for your phone number and a verification code.")
    print("[INFO] Press Ctrl+C to stop.")
    print()

    try:
        asyncio.run(start_with_dashboard())
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        mt5_disconnect()
        print("[OK] Signal Copier stopped.")


async def start_with_dashboard():
    """Connect to Telegram first, then start dashboard."""
    from telethon import TelegramClient, events

    client = TelegramClient(
        config.SESSION_FILE,
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH,
    )
    await client.start(phone=config.TELEGRAM_PHONE)
    print("[OK] Telegram connected!")
    listener_state["connected"] = True

    # Resolve channel
    try:
        channel = await client.get_entity(config.SIGNAL_CHANNEL)
        channel_id = int(f"-100{channel.id}")
        listener_state["channel_name"] = getattr(channel, "title", config.SIGNAL_CHANNEL)
        print(f"[OK] Channel resolved: {listener_state['channel_name']} (ID: {channel_id})")
    except Exception as e:
        print(f"[ERROR] Could not resolve channel '{config.SIGNAL_CHANNEL}': {e}")
        return

    # Start dashboard in background
    dashboard_thread = threading.Thread(target=run_dashboard_loop, daemon=True)
    dashboard_thread.start()

    # Listen to ALL messages, filter by channel ID manually
    @client.on(events.NewMessage)
    async def handler(event):
        print(
            f"[DEBUG] Message from chat_id: {event.chat_id} — {event.message.text[:50] if event.message.text else 'no text'}")

        if event.chat_id != channel_id:
            return

        message_text = event.message.text
        if not message_text:
            return

        from datetime import datetime
        from signal_parser import parse_signal
        from mt5_executor import execute_signal, close_all_positions
        from trade_logger import log_trade, log_close

        timestamp = datetime.now()
        listener_state["last_message"] = message_text[:200]
        listener_state["last_message_time"] = timestamp

        signal = await asyncio.to_thread(parse_signal, message_text)

        if signal is None or not signal.get("is_signal", False):
            listener_state["signals_skipped"] += 1
            return

        listener_state["signals_received"] += 1
        listener_state["last_signal"] = signal

        direction = signal.get("direction", "")

        if direction == "CLOSE":
            results = await asyncio.to_thread(close_all_positions)
            listener_state["last_trade_results"] = results
            listener_state["signals_executed"] += 1
            log_close(results, message_text)
        else:
            results = await asyncio.to_thread(execute_signal, signal)
            listener_state["last_trade_results"] = results
            if results:
                listener_state["signals_executed"] += 1
                log_trade(signal, results, message_text)

    print(f"[OK] Listening to channel: {listener_state['channel_name']}")
    await client.run_until_disconnected()


if __name__ == "__main__":
    main()