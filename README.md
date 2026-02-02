# Crypto Trading Tools 🚀

Automated cryptocurrency trading toolkit for Binance and Polymarket.

## Features

- 📊 **Funding Rate Scanner** - Find high APR funding arbitrage opportunities
- 💱 **Cross-Venue Arbitrage** - Polymarket + Binance hedging
- 📈 **Market Monitor** - Real-time volatility and momentum detection
- ⚖️ **Risk Management** - Position sizing, Kelly criterion, Sharpe ratio

## Quick Start

```bash
git clone https://github.com/vvonha/crypto-trading-tools
cd crypto-trading-tools
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python tools/funding.py scan
```

## Tools

| Tool | Description |
|------|-------------|
| `bankr.py` | Binance API wrapper |
| `funding.py` | Funding rate scanner |
| `monitor.py` | Market monitoring |
| `risk.py` | Risk calculations |

## Disclaimer

This software is for educational purposes only. Trade at your own risk.

## Support

⭐ Star this repo if you find it useful!

[![GitHub Sponsors](https://img.shields.io/github/sponsors/vvonha?style=social)](https://github.com/sponsors/vvonha)
