import logging
import os


def setup_logging() -> None:
    """Configure centralized logging for the entire application.

    Reads LOG_LEVEL from environment (default: INFO).
    Suppresses verbose output from noisy third-party libraries
    (httpx, httpcore, chromadb, sqlalchemy).
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=fmt,
        datefmt=datefmt,
    )

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
