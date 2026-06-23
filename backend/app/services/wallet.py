"""Wallet aggregation service. Mock balances when no exchange creds are set."""
from __future__ import annotations

from app.core.exchanges import ExchangeId
from app.schemas import WalletBalance

_MOCK: dict[ExchangeId, WalletBalance] = {
    ExchangeId.bybit: WalletBalance(exchange=ExchangeId.bybit, total_usdt=52480.12, available_usdt=41200.0, margin_used_usdt=8200.5, pnl_usdt=3079.62),
    ExchangeId.binance: WalletBalance(exchange=ExchangeId.binance, total_usdt=41250.4, available_usdt=38000.0, margin_used_usdt=1200.4, pnl_usdt=2050.0),
    ExchangeId.bitget: WalletBalance(exchange=ExchangeId.bitget, total_usdt=28900.66, available_usdt=24000.0, margin_used_usdt=3000.66, pnl_usdt=1900.0),
    ExchangeId.bingx: WalletBalance(exchange=ExchangeId.bingx, total_usdt=21500.0, available_usdt=19000.0, margin_used_usdt=1500.0, pnl_usdt=1000.0),
    ExchangeId.delta: WalletBalance(exchange=ExchangeId.delta, total_usdt=18400.55, available_usdt=16000.0, margin_used_usdt=1400.55, pnl_usdt=1400.0),
    ExchangeId.kucoin: WalletBalance(exchange=ExchangeId.kucoin, total_usdt=21720.03, available_usdt=20000.0, margin_used_usdt=920.03, pnl_usdt=1720.03),
}


def get_balances() -> list[WalletBalance]:
    return list(_MOCK.values())


def total_equity_usdt() -> float:
    return sum(b.total_usdt for b in _MOCK.values())
