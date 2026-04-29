"""
dashboard.py — Rich formatted terminal dashboard
showing connection status, signals, positions, and trade history.
"""

import MetaTrader5 as mt5
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.columns import Columns
from datetime import datetime
import time

import config
from mt5_executor import get_account_info, get_open_positions, get_tick, get_symbol_info, is_connected
from signal_listener import listener_state
from trade_logger import get_recent_trades


console = Console()


def build_header():
    """Build the header panel."""
    header = Text()
    header.append("  CodePips", style="bold cyan")
    header.append("  —  ", style="dim")
    header.append("Telegram Signal Copier", style="bold white")
    header.append("  |  ", style="dim")
    header.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), style="dim")
    return Panel(header, style="cyan", height=3)


def build_status_table():
    """Build connection status display."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(width=20)
    table.add_column()

    # MT5 status
    if is_connected():
        mt5_status = Text("Connected", style="bold green")
    else:
        mt5_status = Text("Disconnected", style="bold red")
    table.add_row(Text("MetaTrader 5:", style="dim"), mt5_status)

    # Telegram status
    if listener_state["connected"]:
        tg_status = Text("Active", style="bold green")
    else:
        tg_status = Text("Waiting...", style="bold yellow")
    table.add_row(Text("Telegram:", style="dim"), tg_status)

    # Channel
    table.add_row(
        Text("Channel:", style="dim"),
        Text(str(listener_state["channel_name"]), style="bold white"),
    )

    return Panel(table, title="Status", border_style="dim")


def build_account_panel():
    """Build account info panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(width=16)
    table.add_column()

    acc = get_account_info()
    tick = get_tick()
    sym = get_symbol_info()

    if acc:
        table.add_row(Text("Balance:", style="dim"), Text(f"${acc.balance:,.2f}", style="bold white"))
        table.add_row(Text("Equity:", style="dim"), Text(f"${acc.equity:,.2f}", style="bold white"))

    if tick and sym:
        spread = (tick.ask - tick.bid) / sym.point
        table.add_row(Text("Bid / Ask:", style="dim"), Text(f"{tick.bid:.2f} / {tick.ask:.2f}", style="white"))
        table.add_row(Text("Spread:", style="dim"), Text(f"{spread:.0f} pts", style="white"))

    return Panel(table, title=f"{config.SYMBOL}", border_style="dim")


def build_signal_panel():
    """Build last signal display."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(width=16)
    table.add_column()

    # Stats
    table.add_row(
        Text("Signals:", style="dim"),
        Text(f"{listener_state['signals_received']} received  |  {listener_state['signals_executed']} executed  |  {listener_state['signals_skipped']} skipped", style="white"),
    )

    # Last message
    last_msg = listener_state.get("last_message", "")
    if last_msg:
        msg_time = listener_state.get("last_message_time")
        time_str = msg_time.strftime("%H:%M:%S") if msg_time else ""
        table.add_row(
            Text("Last msg:", style="dim"),
            Text(f"[{time_str}] {last_msg[:80]}", style="white"),
        )
    else:
        table.add_row(Text("Last msg:", style="dim"), Text("Waiting for messages...", style="dim italic"))

    # Last parsed signal
    signal = listener_state.get("last_signal")
    if signal and signal.get("is_signal"):
        direction = signal.get("direction", "")
        order_type = signal.get("order_type", "")
        entry = signal.get("entry", 0)
        sl = signal.get("sl", 0)
        tp_list = signal.get("tp", [])

        dir_style = "bold green" if direction == "BUY" else "bold red" if direction == "SELL" else "bold yellow"
        signal_text = Text()
        signal_text.append(f"{direction} ", style=dir_style)
        signal_text.append(f"{order_type} ", style="dim")
        if entry:
            signal_text.append(f"@ {entry:.2f} ", style="white")
        if sl:
            signal_text.append(f"SL: {sl:.2f} ", style="red")
        if tp_list:
            tp_str = " / ".join(f"{tp:.2f}" for tp in tp_list if tp)
            signal_text.append(f"TP: {tp_str}", style="green")

        table.add_row(Text("Last signal:", style="dim"), signal_text)

    return Panel(table, title="Signals", border_style="dim")


def build_positions_table():
    """Build open positions table."""
    table = Table(box=None, padding=(0, 1))
    table.add_column("Ticket", style="dim", width=12)
    table.add_column("Dir", width=6)
    table.add_column("Lot", width=6)
    table.add_column("Entry", width=10)
    table.add_column("SL", width=10)
    table.add_column("TP", width=10)
    table.add_column("P&L", width=12)

    positions = get_open_positions()

    if not positions:
        return Panel(Text("No open positions", style="dim italic"), title="Positions", border_style="dim")

    for pos in positions:
        direction = "LONG" if pos.type == mt5.ORDER_TYPE_BUY else "SHORT"
        dir_style = "green" if direction == "LONG" else "red"
        pnl = pos.profit
        pnl_style = "bold green" if pnl >= 0 else "bold red"

        table.add_row(
            str(pos.ticket),
            Text(direction, style=dir_style),
            f"{pos.volume}",
            f"{pos.price_open:.2f}",
            f"{pos.sl:.2f}" if pos.sl else "-",
            f"{pos.tp:.2f}" if pos.tp else "-",
            Text(f"${pnl:+.2f}", style=pnl_style),
        )

    return Panel(table, title=f"Positions ({len(positions)})", border_style="dim")


def build_trade_log():
    """Build recent trade history."""
    table = Table(box=None, padding=(0, 1))
    table.add_column("Time", style="dim", width=10)
    table.add_column("Dir", width=6)
    table.add_column("Entry", width=10)
    table.add_column("SL", width=10)
    table.add_column("TP", width=10)
    table.add_column("Lot", width=6)
    table.add_column("Status", width=10)

    recent = get_recent_trades(8)

    if not recent:
        return Panel(Text("No trades yet", style="dim italic"), title="Trade History", border_style="dim")

    for trade in recent:
        ts = trade.get("timestamp", "")
        time_str = ts[11:19] if len(ts) > 19 else ts

        signal = trade.get("parsed_signal", {})
        execs = trade.get("executions", [])
        action = trade.get("action", "")

        if action == "CLOSE_ALL":
            table.add_row(
                time_str, Text("CLOSE", style="yellow"), "-", "-", "-", "-",
                Text("Closed", style="yellow"),
            )
        elif signal and execs:
            direction = signal.get("direction", "")
            dir_style = "green" if direction == "BUY" else "red"

            for ex in execs:
                table.add_row(
                    time_str,
                    Text(direction, style=dir_style),
                    f"{ex.get('entry', 0):.2f}",
                    f"{ex.get('sl', 0):.2f}" if ex.get('sl') else "-",
                    f"{ex.get('tp', 0):.2f}" if ex.get('tp') else "-",
                    f"{ex.get('lot', 0)}",
                    Text("Filled", style="green"),
                )

    return Panel(table, title="Trade History", border_style="dim")


def build_dashboard():
    """Build the full dashboard layout."""
    console.clear()

    console.print(build_header())
    console.print()

    # Status and account side by side
    console.print(Columns([build_status_table(), build_account_panel()], equal=True))
    console.print()

    # Signals
    console.print(build_signal_panel())
    console.print()

    # Positions
    console.print(build_positions_table())
    console.print()

    # Trade log
    console.print(build_trade_log())


def run_dashboard_loop():
    """Continuously refresh the dashboard."""
    while True:
        try:
            build_dashboard()
        except Exception as e:
            console.print(f"[red][ERROR] Dashboard: {e}[/red]")
        time.sleep(config.REFRESH_INTERVAL)
