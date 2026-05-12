from __future__ import annotations
import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)
    # Silence noisy libs
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if settings.is_production else logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
