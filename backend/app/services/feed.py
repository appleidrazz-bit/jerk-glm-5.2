"""Funding-rate feed. Generates the normalized ArbitrageRow stream.

Production: subscribe to each exchange's funding-rate + ticker websockets,
normalize, and emit snapshots. Development (mock_feed=True): deterministically
generate 520 rows and jitter them on an interval.
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import AsyncIterator, Dict

from app.core.config import settings
from app.core.exchanges import EXCHANGE_IDS, ExchangeId
from app.schemas import ArbitrageRow, FundingCell

logger = logging.getLogger(__name__)

_NAMES = [
    "Quant", "Hyper", "Nova", "Cyber", "Zen", "Prime", "Volt", "Orbit",
    "Alpha", "Beta", "Gamma", "Sigma", "Omega", "Flux", "Nex", "Aura",
    "Apex", "Edge", "Core", "Pulse", "Sync", "Node", "Link", "Mesh",
    "Grid", "Cube", "Byte", "Hex", "Iris", "Lux", "Vault", "Rune",
    "Echo", "Drift", "Swap", "Yield", "Stack", "Hedge", "Dex", "Amm",
]
_COLORS = ["#F7A600", "#22C55E", "#EF4444", "#3B82F6", "#A855F7", "#06B6D4"]

_BASE_COINS = [
    ("BTC", "Bitcoin", 68000, "#F7931A"),
    ("ETH", "Ethereum", 3500, "#627EEA"),
    ("SOL", "Solana", 145, "#14F195"),
    ("BNB", "BNB", 590, "#F0B90B"),
    ("XRP", "XRP", 0.52, "#00AAE4"),
    ("DOGE", "Dogecoin", 0.12, "#C2A633"),
]


def _gen_coins(count: int):
    """Generate *count* unique coins. Uses counter suffix to guarantee no infinite loop."""
    coins = list(_BASE_COINS)
    rng = random.Random(42)
    # Each base name + a numeric suffix = guaranteed unique symbol.
    # We need (count - 6) more names.
    idx = 0
    while len(coins) < count:
        name = _NAMES[idx % len(_NAMES)]
        suffix_num = idx // len(_NAMES)
        sym = f"{name}{suffix_num}" if suffix_num else name
        idx += 1
        base = 0.0001 + 10 ** (rng.random() * 5 - 1)
        coins.append((sym, f"{name} Protocol", base, rng.choice(_COLORS)))
    return coins[:count]


# Separate RNG so snapshot jitter doesn't affect generation determinism.
_rng = random.Random(1337)


def _rr():
    return _rng.random()


def _row_from_coin(coin, idx: int) -> ArbitrageRow:
    sym, name, base, color = coin
    mid = base * (0.9 + _rr() * 0.2)
    cells: Dict[ExchangeId, FundingCell] = {}
    for ex in EXCHANGE_IDS:
        spike = _rr() * 0.0015 if _rr() > 0.92 else 0
        sign = 1 if _rr() > 0.5 else -1
        rate = sign * (_rr() * 0.0003 + spike)
        cells[ExchangeId(ex)] = FundingCell(
            exchange=ExchangeId(ex),
            rate=rate,
            price=mid * (1 + (_rr() - 0.5) * 0.002),
            next_funding_ms=int(time.time() * 1000) + idx * 60_000,
        )

    rates = [(c.rate or 0) for c in cells.values()]
    best_long = min(cells, key=lambda e: cells[e].rate or 0)
    best_short = max(cells, key=lambda e: cells[e].rate or 0)
    spread = (max(rates) - min(rates)) * 3 * 365 * 100

    return ArbitrageRow(
        id=sym,
        symbol=f"{sym}USDT",
        name=name,
        icon_color=color,
        live_price=mid,
        change_24h_pct=(_rr() - 0.5) * 12,
        cells=cells,
        best_long=best_long,
        best_short=best_short,
        spread_pct=spread,
        est_profit_per_cycle=((max(rates) - min(rates)) * 1000) / 2,
    )


class FundingFeed:
    def __init__(self, count: int = 520) -> None:
        self.count = count
        self._coins = _gen_coins(count)

    def snapshot(self):
        return [_row_from_coin(c, i) for i, c in enumerate(self._coins)]

    async def stream(self, interval=None) -> AsyncIterator:
        interval = interval or settings.feed_interval_sec
        while True:
            yield self.snapshot()
            await asyncio.sleep(interval)


feed = FundingFeed()
