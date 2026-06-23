"""REST routes: funding snapshot, wallet, execution."""
from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import APIRouter

from app.exchanges.manager import manager
from app.schemas import (
    ExecutionRequest,
    ExecutionResult,
    WalletBalance,
)
from app.services.feed import feed
from app.services.wallet import get_balances, total_equity_usdt

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/funding", tags=["funding"])
async def get_funding():
    """One-shot snapshot of the arbitrage table."""
    return {"rows": [r.model_dump(mode="json") for r in feed.snapshot()]}


@router.get("/wallet", response_model=list[WalletBalance], tags=["wallet"])
async def get_wallet():
    return get_balances()


@router.get("/wallet/total", tags=["wallet"])
async def get_wallet_total():
    return {"total_usdt": total_equity_usdt()}


@router.post("/execute", response_model=ExecutionResult, tags=["execution"])
async def execute(req: ExecutionRequest):
    """Submit both legs of an arbitrage trade near-simultaneously.

    Production path places real market orders via ccxt. With no creds we run a
    safe simulation so the UI loop is fully exercisable.
    """
    amount_per_leg = req.amount_usdt / 2

    async def _leg(exchange, side):
        try:
            order = await manager.place_market_order(
                exchange=exchange,
                symbol=req.symbol,
                side=side,
                amount=amount_per_leg,
                leverage=req.leverage,
            )
            return order.get("id")
        except Exception as exc:  # noqa: BLE001
            logger.error("leg failed: %s", exc)
            return None

    long_id, short_id = await asyncio.gather(
        _leg(req.long_exchange, "buy"),
        _leg(req.short_exchange, "sell"),
    )

    ok = long_id is not None and short_id is not None
    # In simulation (no creds) ccxt raises -> ids are None; fake a success.
    if not settings_has_creds() and long_id is None and short_id is None:
        long_id = f"sim-{uuid.uuid4().hex[:8]}"
        short_id = f"sim-{uuid.uuid4().hex[:8]}"
        ok = True

    return ExecutionResult(
        ok=ok,
        long_order_id=long_id,
        short_order_id=short_id,
        detail="simulated" if not settings_has_creds() else None,
    )


def settings_has_creds() -> bool:
    from app.core.config import settings
    return bool(settings.vault_key)
