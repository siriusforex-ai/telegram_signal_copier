# 🤖 Telegram Signal Copier Bot — AI-Powered, Free & Open Source

> Monitors any Telegram signal channel, uses Claude AI to parse signals in any format, and automatically places trades on MetaTrader 5 with stop loss and take profit in under 3 seconds.

[![YouTube Tutorial](https://img.shields.io/badge/YouTube-Tutorial-red?style=for-the-badge&logo=youtube)](https://youtu.be/76wGAj3WBo8)
[![Telegram](https://img.shields.io/badge/Telegram-Community-blue?style=for-the-badge&logo=telegram)](https://t.me/codepipss)
[![Python](https://img.shields.io/badge/Python-3.12-green?style=for-the-badge&logo=python)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📺 Full Video Tutorial

Watch the complete build + live demo on YouTube:

▶️ **[I Built a Free AI Telegram Signal Copier Bot with Python & MetaTrader 5](https://youtu.be/76wGAj3WBo8)**

---

## ❓ What Is This?

A free, open-source bot that:

1. **Monitors** any Telegram signal channel you're subscribed to in real time
2. **Sends** each message to **Claude AI** which reads and understands the signal — no matter how it's formatted
3. **Places** the trade on **MetaTrader 5** automatically with the correct stop loss and take profit
4. **Displays** everything in a live Rich terminal dashboard

**The paid tools that do this charge $50–$200.** This one is completely free.

---

## 🧠 Why Claude AI Instead of Regex?

Most signal copiers use hardcoded regex patterns to parse signals. The moment a signal provider changes their format — even slightly — the copier breaks.

This bot uses **Claude AI (Anthropic)** to read signals the way a human would. It doesn't care about formatting. All of these work:

```
GOLD BUY NOW
Entry: 4718
SL: 4700
TP1: 4730
TP2: 4750
```

```
XAUUSD SELL NOW @ 4735
TP : 4720
TP : 4710
SL : 4750
```

```
Buy gold at market, stop loss 4690, take profit 4725 and 4740
```

```
Close all gold trades
```

And if the channel posts commentary, news, or trade updates like "+120 pips running! Set breakeven" — Claude knows it's not a signal and skips it.

---

## ⚡ Features

- **AI-powered signal parsing** — works with any signal format from any provider
- **All 6 order types** — market buy/sell, buy/sell limit, buy/sell stop
- **Multiple take profits** — splits lot across TP1, TP2, TP3 automatically
- **Close signals** — detects "close all" instructions and closes positions
- **Live Rich dashboard** — connection status, signals, positions with P&L, trade history
- **JSON trade logging** — every trade saved for review
- **Real-time monitoring** — catches signals instantly via Telethon (not polling)
- **Any channel** — works with any Telegram channel you're subscribed to (public, private, VIP)

---

## 📁 Project Structure

```
telegram_signal_copier/
├── config.py              # All settings and environment variables
├── signal_listener.py     # Telethon client — monitors Telegram channel
├── signal_parser.py       # Claude AI signal parser — the brain
├── mt5_executor.py        # MetaTrader 5 trade execution
├── dashboard.py           # Rich terminal dashboard
├── trade_logger.py        # JSON trade logging
├── main.py                # Entry point — ties everything together
├── .env                   # Your API keys and credentials (create this)
└── requirements.txt       # Python packages
```

---

## 🔧 Requirements

- **Python 3.12** (not 3.13 or 3.14 — MT5 library doesn't support them yet)
- **MetaTrader 5** installed and logged into your broker account
- **Telegram account** subscribed to the signal channel you want to monitor
- **Telegram API credentials** (free — from https://my.telegram.org)
- **Anthropic API key** (from https://console.anthropic.com — $5 minimum credits)

---

## 🚀 Setup

### 1. Clone the repo

```bash
git clone https://github.com/siriusforex-ai/telegram_signal_copier.git
cd telegram_signal_copier
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your API keys

| Key | Where to get it | Cost |
|-----|-----------------|------|
| Telegram API ID & Hash | https://my.telegram.org | Free |
| Telegram Phone Number | Your registered number | — |
| MetaTrader 5 Credentials | Your broker | Free (demo account) |
| Anthropic API Key | https://console.anthropic.com | $5 minimum |

### 4. Create your `.env` file

Create a file called `.env` in the project folder:

```env
# Telegram (get from https://my.telegram.org)
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=+your_phone_number

# Signal channel to monitor (username without @ or channel ID)
SIGNAL_CHANNEL=Forex

# MetaTrader 5
MT5_ACCOUNT=your_mt5_account_number
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_broker_server

# Claude AI (get from https://console.anthropic.com)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 5. Run the bot

Make sure MetaTrader 5 is open and logged in, then:

```bash
python main.py
```

On the first run, Telethon will ask for your phone number and a verification code from Telegram. After that it saves a session file and connects automatically.

---

## 📊 Dashboard Preview

```
╭──────────────────────────────────────────────────────────────╮
│   CodePips  —  Telegram Signal Copier  |  2026-04-24 20:59  │
╰──────────────────────────────────────────────────────────────╯

╭─────────── Status ───────────╮ ╭──────── GOLD ────────╮
│   MetaTrader 5:  Connected   │ │   Balance: $9,370    │
│   Telegram:      Active      │ │   Bid/Ask: 4725/4726 │
│   Channel:       Forex VIP   │ │   Spread:  46 pts    │
╰──────────────────────────────╯ ╰──────────────────────╯

╭──────────────────── Signals ─────────────────────╮
│   1 received  |  1 executed  |  0 skipped        │
│   Last signal: BUY MARKET SL: 4700 TP: 4730     │
╰──────────────────────────────────────────────────╯

╭──────────────────── Positions (3) ───────────────╮
│   745853324  LONG  0.01  Entry: 4717.50  $-0.76  │
│   745853328  LONG  0.01  Entry: 4717.34  $-0.60  │
│   745853337  LONG  0.01  Entry: 4717.34  $-0.60  │
╰──────────────────────────────────────────────────╯
```

---

## 🔄 How It Works

```
Signal posted in Telegram channel
        │
        ▼
Telethon catches it instantly (real-time, not polling)
        │
        ▼
Message sent to Claude AI for parsing
        │
        ▼
Claude returns: direction, entry, SL, TP[], order type
        │
        ▼
Is it a real signal? ──No──▶ Skip, keep listening
        │
       Yes
        │
        ▼
MetaTrader 5 places the trade (splits lot across TPs)
        │
        ▼
Dashboard updates, trade logged to JSON
```

---

## ⚠️ Important Notes

- **Always test with a small lot size first** (0.01) before scaling up
- **Not all signal providers are profitable** — the bot executes faster, it doesn't make bad signals good
- **Protect your session file** — the `.session` file gives access to your Telegram account. Never share it or upload it to GitHub
- **Anthropic API costs** — each signal costs less than $0.01 to parse. $5 in credits will last months
- **Python 3.12 only** — the MetaTrader 5 library does not work with Python 3.13 or 3.14

---

## 🔗 Links

- 📺 **YouTube Tutorial:** https://youtu.be/76wGAj3WBo8
- 📢 **Telegram Channel:** https://t.me/codepipss
- 💬 **Telegram Community:** https://t.me/+qH90fZfIYeNmYzM1
- 🐦 **Twitter/X:** https://x.com/codepips_

---

## 📄 Setup Links

- 🔹 Telegram API credentials: https://my.telegram.org
- 🔹 Anthropic (Claude AI) console: https://console.anthropic.com
- 🔹 Python 3.12 download: https://www.python.org/downloads/release/python-3129/
- 🔹 MetaTrader 5 download: https://www.metatrader5.com/en/download

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. I am not a financial advisor. Nothing in this repository constitutes financial advice. Always use a demo account for testing. Trade at your own risk.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

**Built with ❤️ by [CodePips](https://youtube.com/@CodePips)**
