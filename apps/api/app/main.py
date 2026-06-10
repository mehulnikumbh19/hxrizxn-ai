from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.db.session import init_db
from app.services.security import RateLimitMiddleware, SecureHeadersMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Hxrizxn AI API",
        description="HORIZON-X multi-agent decision simulator with Foundry IQ-ready grounding.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecureHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.include_router(router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    return app


app = create_app()

