# app/core/logging.py

import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request

from app.core.config import settings
from app.utils.helpers import mask_ip

# Detect environment
ENV = settings.ENV

logger = logging.getLogger("petcare")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Remove existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
)
logger.addHandler(console_handler)

# File handler (only in dev)
if ENV != "production":
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "petcare.log", maxBytes=5_000_000, backupCount=3
    )
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)


async def log_requests(request: Request, call_next):
    ip = request.client.host  # type: ignore
    masked_ip = mask_ip(ip)
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} from {masked_ip} "
        f"completed_in={process_time:.2f}ms, status_code={response.status_code}"
    )
    return response


def log_rate_limit_exceeded(request: Request, ip: str):
    """
    Log when a user exceeds the rate limit.

    Args:
        ip (str): The raw client IP address.
        request (Request): FastAPI request object for extracting path/method.
    """
    masked_ip = mask_ip(ip)
    endpoint = request.url.path
    method = request.method

    logger.warning(
        "Rate limit exceeded from %s at %s with method=%s",
        masked_ip,
        endpoint,
        method,
    )
