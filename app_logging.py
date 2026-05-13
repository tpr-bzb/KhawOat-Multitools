import logging
import os
from functools import lru_cache
from logging.handlers import RotatingFileHandler


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
MAX_LOG_BYTES = 512 * 1024
BACKUP_COUNT = 5


def ensure_log_dir() -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    return LOG_DIR


@lru_cache(maxsize=None)
def get_logger(name: str, filename: str) -> logging.Logger:
    ensure_log_dir()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
