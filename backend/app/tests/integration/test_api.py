"""Integration tests for the REST API surface using FastAPI TestClient."""
from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_funding_snapshot_shape():
    r = client.get("/api/funding")
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert isinstance(rows, list) and len(rows) > 0
    first = rows[0]
    for key in ("symbol", "live_price", "cells", "spread_pct", "best_long", "best_short"):
        assert key in first, f"missing {key}"


def test_wallet_endpoint():
    r = client.get("/api/wallet")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list) and len(body) == 6
    assert all("total_usdt" in b for b in body)


def test_wallet_total():
    r = client.get("/api/wallet/total")
    assert r.status_code == 200
    assert r.json()["total_usdt"] > 0


def test_execute_simulated_success():
    payload = {
        "symbol": "BTCUSDT",
        "long_exchange": "bybit",
        "short_exchange": "binance",
        "leverage": 5,
        "amount_usdt": 1000,
    }
    r = client.post("/api/execute", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["long_order_id"] and body["short_order_id"]


def test_execute_rejects_bad_leverage():
    payload = {
        "symbol": "BTCUSDT",
        "long_exchange": "bybit",
        "short_exchange": "binance",
        "leverage": 500,
        "amount_usdt": 1000,
    }
    r = client.post("/api/execute", json=payload)
    assert r.status_code == 422
