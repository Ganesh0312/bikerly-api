"""
Logger configuration using loguru
"""
import sys
from pathlib import Path
from loguru import logger
import os
import logging
# Remove default logger
logger.remove()

# Get log level from environment or default to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Console logging format
console_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# File logging format (more detailed)
file_format = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message} | "
    "{extra}"
)

# Add console handler (minimal backtrace for console)
logger.add(
    sys.stdout,
    format=console_format,
    level=LOG_LEVEL,
    colorize=True,
    backtrace=False,  # Disable backtrace in console
    diagnose=False,  # Disable diagnose in console
)

# Add file handler for all logs (detailed for debugging)
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    format=file_format,
    level=LOG_LEVEL,
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    backtrace=True,  # Keep backtrace in file for debugging
    diagnose=True,  # Keep diagnose in file for debugging
    enqueue=True,  # Thread-safe logging
)

# Add file handler for errors only (full details for errors)
logger.add(
    LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
    format=file_format,
    level="ERROR",
    rotation="00:00",
    retention="90 days",  # Keep error logs longer
    compression="zip",
    backtrace=True,  # Full backtrace for errors
    diagnose=True,  # Full diagnose for errors
    enqueue=True,
)

# # Configure logger for uvicorn access logs
# logger.configure(
#     handlers=[
#         {
#             "sink": sys.stdout,
#             "format": console_format,
#             "level": LOG_LEVEL,
#         }
#     ]
# )

# Export logger instance
__all__ = ["logger"]

