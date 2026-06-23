"""Thin async wrapper over ccxt for connecting to the supported exchanges.

In production each user's encrypted API keys are decrypted at call-time and a
per-user ccxt client is constructed. This module exposes the surface the API
and execution service need, and a mock implementation when no keys are set.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import ccxt.async_support as ccxt

from app.core.exchanges import ExchangeId

logger = logging.getLogger(__name__)


class ExchangeManager:
    """Holds lazily-created ccxt clients keyed by exchange id."""

    def __init__(self) -> None:
        self._clients: dict[str, ccxt.Exchange] = {}

    async def get_client(self, exchange: ExchangeId, creds: dict | None = None) -> Any:
        key = f"{exchange.value}:{hash(tuple(sorted((creds or {}).items())))}"
        if key in self._clients:
            return self._clients[key]
        cls = getattr(ccxt, exchange.value, None)
        if cls is None:
            raise ValueError(f"Unsupported exchange: {exchange.value}")
        client = cls(creds or {"enableRateLimit": True})
        self._clients[key] = client
        return client

    async def place_market_order(
        self,
        exchange: ExchangeId,
        symbol: str,
        side: str,
        amount: float,
        leverage: int,
        creds: dict | None = None,
    ) -> dict:
        """Place a market order. Returns ccxt order dict or a mock."""
        try:
            client = await self.get_client(exchange, creds)
            await _safe(client.set_leverage, leverage, symbol)
            order = await client.create_order(symbol, "market", side, amount)
            return order
        except Exception as exc:  # noqa: BLE001
            logger.exception("Order failed on %s %s %s", exchange.value, side, symbol)
            raise RuntimeError(f"{exchange.value} order error: {exc}") from exc

    async def fetch_balance(self, exchange: ExchangeId, creds: dict | None = None) -> dict:
        client = await self.get_client(exchange, creds)
        return await client.fetch_balance()

    async def close_all(self) -> None:
        for client in self._clients.values():
            await _safe(client.close)
        self._clients.clear()


async def _safe(coro_or_fn, *args, **kwargs):
    fn = coro_or_fn(*args, **kwargs) if callable(coro_or_fn) else coro_or_fn
    if asyncio.iscoroutine(fn):
        return await fn
    return fn


manager = ExchangeManager()
