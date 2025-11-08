from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles

from app.api.routes import analytics, auth, customers, products, qrcodes, scans
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import get_db

setup_logging()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request.headers.get("X-Request-ID", "auto"))
        return response


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, openapi_url=settings.openapi_url, docs_url=settings.docs_url)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def default_exception_handler(request: Request, exc: Exception):
        logging.exception("Unhandled", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(customers.router, prefix=f"{settings.api_prefix}/customers", tags=["customers"])
    app.include_router(products.router, prefix=f"{settings.api_prefix}/products", tags=["products"])
    app.include_router(qrcodes.router, prefix=f"{settings.api_prefix}/qrcodes", tags=["qrcodes"])
    app.include_router(scans.router, prefix="/api", tags=["scan"])
    app.include_router(analytics.router, prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])

    static_path = Path(settings.upload_dir)
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/healthz")
    async def healthcheck():
        for db in get_db():
            db.execute("SELECT 1")
            break
        return {"status": "ok"}

    return app


app = create_app()
