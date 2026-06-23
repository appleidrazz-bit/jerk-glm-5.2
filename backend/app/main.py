"""FastAPI application factory."""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.feed import feed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", docs_url="/api/docs")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    @app.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}

    @app.websocket("/ws/funding")
    async def ws_funding(ws: WebSocket) -> None:
        await ws.accept()
        try:
            async for snapshot in feed.stream():
                payload = json.dumps(
                    {"rows": [r.model_dump(mode="json") for r in snapshot]},
                    default=str,
                )
                await ws.send_text(payload)
        except WebSocketDisconnect:
            return
        except Exception:  # noqa: BLE001
            logging.exception("funding ws error")
            await ws.close()

    return app


app = create_app()
