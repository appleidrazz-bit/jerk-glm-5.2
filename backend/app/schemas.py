"""Pydantic schemas for API request/response bodies."""
from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.core.exchanges import ExchangeId


class FundingCell(BaseModel):
    exchange: ExchangeId
    rate: Optional[float]
    price: Optional[float]
    next_funding_ms: int


class ArbitrageRow(BaseModel):
    id: str
    symbol: str
    name: str
    icon_color: str
    live_price: float
    change_24h_pct: float
    cells: Dict[ExchangeId, FundingCell]
    best_long: Optional[ExchangeId]
    best_short: Optional[ExchangeId]
    spread_pct: float
    est_profit_per_cycle: float


class WalletBalance(BaseModel):
    exchange: ExchangeId
    total_usdt: float
    available_usdt: float
    margin_used_usdt: float
    pnl_usdt: float


class ExecutionRequest(BaseModel):
    symbol: str
    long_exchange: ExchangeId
    short_exchange: ExchangeId
    leverage: int = Field(ge=1, le=100)
    amount_usdt: float = Field(gt=0)


class ExecutionResult(BaseModel):
    ok: bool
    long_order_id: Optional[str] = None
    short_order_id: Optional[str] = None
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
