"""
signal_listener.py — Monitors a Telegram channel for new messages
using Telethon (user client, not bot API).
Passes each message to Claude for parsing, then executes on MT5.
"""

import asyncio
from telethon import TelegramClient, events
from datetime import datetime

import config
from signal_parser import parse_signal
from mt5_executor import execute_signal, close_all_positions
from trade_logger import log_trade, log_close


# Shared state for the dashboard to read
listener_state = {
    "connected": False,
    "channel_name": config.SIGNAL_CHANNEL,
    "last_message": "",
    "last_message_time": None,
    "last_signal": None,
    "last_trade_results": [],
    "signals_received": 0,
    "signals_executed": 0,
    "signals_skipped": 0,
}


async def start_listener(dashboard_callback=None):
    """
    Start the Telethon client and listen for new messages
    from the configured signal channel.
    """
    client = TelegramClient(
        config.SESSION_FILE,
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH,
    )

    await client.start(phone=config.TELEGRAM_PHONE)
    listener_state["connected"] = True

    # Resolve the channel
    try:
        channel = await client.get_entity(config.SIGNAL_CHANNEL)
        listener_state["channel_name"] = getattr(channel, "title", config.SIGNAL_CHANNEL)
    except Exception as e:
        print(f"[ERROR] Could not resolve channel '{config.SIGNAL_CHANNEL}': {e}")
        print("[INFO] Make sure you are subscribed to this channel on your Telegram account")
        return

    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        message_text = event.message.text
        if not message_text:
            return

        timestamp = datetime.now()

        # Update state
        listener_state["last_message"] = message_text[:200]
        listener_state["last_message_time"] = timestamp

        # Send to Claude for parsing
        signal = await asyncio.to_thread(parse_signal, message_text)

        if signal is None:
            listener_state["signals_skipped"] += 1
            return

        if not signal.get("is_signal", False):
            listener_state["signals_skipped"] += 1
            return

        listener_state["signals_received"] += 1
        listener_state["last_signal"] = signal

        # Execute the signal on MT5
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

        # Trigger dashboard refresh if callback provided
        if dashboard_callback:
            dashboard_callback()

    print(f"[OK] Listening to channel: {listener_state['channel_name']}")
    await client.run_until_disconnected()
