"""Centralized logging setup. Every module just does
`logger = logging.getLogger(__name__)` and inherits whatever is
configured here on the root logger.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(_BACKEND_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "threatview.log")


def configure_logging(app) -> None:
    """Attach a rotating file handler and a console handler to the root
    logger, sized/leveled from app config.

    Safe to call more than once (e.g. under the reloader) since it
    replaces the handler list rather than appending to it.
    """
    level = getattr(logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    handlers = [console_handler]
    
    # Try to set up file logging. This will fail gracefully in read-only
    # serverless environments like Vercel.
    is_vercel = os.environ.get("VERCEL") == "1"
    
    if not is_vercel:
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except OSError:
            # Fallback to stdout only if read-only filesystem
            pass

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = handlers

    app.logger.setLevel(level)
