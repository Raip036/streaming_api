import logging

from fastapi import FastAPI

from app.api import health, payments, users
from app.config import get_settings
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app = FastAPI(title="Reply Streaming API", version="1.0.0")
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(payments.router)
    return app


app = create_app()
