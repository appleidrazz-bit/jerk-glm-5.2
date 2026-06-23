"""Canonical exchange list shared by API, services and tests."""
from enum import Enum


class ExchangeId(str, Enum):
    bybit = "bybit"
    binance = "binance"
    bitget = "bitget"
    bingx = "bingx"
    delta = "delta"
    kucoin = "kucoin"


EXCHANGE_IDS = [e.value for e in ExchangeId]

EXCHANGE_META = {
    "bybit": {"name": "Bybit", "short": "BYB", "color": "#F7A600"},
    "binance": {"name": "Binance", "short": "BIN", "color": "#F0B90B"},
    "bitget": {"name": "Bitget", "short": "BTG", "color": "#00F0FF"},
    "bingx": {"name": "BingX", "short": "BGX", "color": "#14F195"},
    "delta": {"name": "Delta Exchange", "short": "DLT", "color": "#7B3FE4"},
    "kucoin": {"name": "KuCoin", "short": "KUC", "color": "#23AF91"},
}
