"""
trade_logger.py — Logs every trade to a JSON file for review.
"""

import json
import os
from datetime import datetime
import config


def log_trade(signal: dict, trade_results: list, raw_message: str):
    """
    Log a trade event to the JSON file.

    Args:
        signal: The parsed signal from Claude
        trade_results: List of execution results from MT5
        raw_message: The original Telegram message text
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "raw_message": raw_message[:500],  # trim long messages
        "parsed_signal": signal,
        "executions": trade_results,
    }

    logs = _load_logs()
    logs.append(entry)
    _save_logs(logs)


def log_close(close_results: list, raw_message: str):
    """Log a close event."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "raw_message": raw_message[:500],
        "action": "CLOSE_ALL",
        "results": close_results,
    }

    logs = _load_logs()
    logs.append(entry)
    _save_logs(logs)


def get_recent_trades(count: int = 10) -> list:
    """Return the last N trade entries."""
    logs = _load_logs()
    return logs[-count:] if logs else []


def get_trade_count() -> int:
    """Return total number of logged trades."""
    return len(_load_logs())


def _load_logs() -> list:
    """Load existing logs from file."""
    if not os.path.exists(config.TRADE_LOG_FILE):
        return []
    try:
        with open(config.TRADE_LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _save_logs(logs: list):
    """Save logs to file with atomic write."""
    tmp = config.TRADE_LOG_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        os.replace(tmp, config.TRADE_LOG_FILE)
    except IOError as e:
        print(f"[ERROR] Could not write trade log: {e}")
