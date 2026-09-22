from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from seo_score import __version__
from seo_score.core.config import settings
from seo_score.db.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="SEO Score API",
    version=__version__,
    description="Automated SEO audit API. Stage 1: health and persistence.",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> JSONResponse:
    postgres = await _check_postgres()
    redis = await _check_redis()
    ok = postgres == "ok" and redis == "ok"
    payload: dict[str, Any] = {
        "status": "ok" if ok else "degraded",
        "version": __version__,
        "postgres": postgres,
        "redis": redis,
    }
    return JSONResponse(payload, status_code=200 if ok else 503)


async def _check_postgres() -> str:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001 — health must never raise
        return f"error: {type(exc).__name__}"


async def _check_redis() -> str:
    client = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
    try:
        pong = await client.ping()
        return "ok" if pong else "error: no pong"
    except Exception as exc:  # noqa: BLE001
        return f"error: {type(exc).__name__}"
    finally:
        await client.aclose()
