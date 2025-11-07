from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from .config import settings
from .deps import get_db
from .auth.router import router as auth_router
from .customers.router import router as customers_router
from .products.router import router as products_router
from .qr.router import router as qr_router
from .events.router import public_router, router as events_router
from .services.analytics import router as analytics_router
from .utils.logging import setup_logging, with_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = with_request_id(request)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="QR Lifecycle Platform", version="1.0.0")
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def default_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logging.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(customers_router, prefix="/api/customers", tags=["customers"])
    app.include_router(products_router, prefix="/api/products", tags=["products"])
    app.include_router(qr_router, prefix="/api/qrcodes", tags=["qr"])
    app.include_router(events_router, prefix="/api/events", tags=["events"])
    app.include_router(public_router, tags=["scan"])
    app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

    @app.get("/healthz")
    async def health(db=Depends(get_db)) -> dict[str, Any]:
        db.execute("SELECT 1")
        return {"status": "ok"}

    return app


app = create_app()
