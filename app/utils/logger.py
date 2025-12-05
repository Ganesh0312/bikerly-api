"""
Logger configuration using loguru
"""
import sys
from pathlib import Path
from loguru import logger
import os

# Remove default logger
logger.remove()

# Get log level from environment or default to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

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

# Add console handler
logger.add(
    sys.stdout,
    format=console_format,
    level=LOG_LEVEL,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Add file handler for all logs
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    format=file_format,
    level=LOG_LEVEL,
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    backtrace=True,
    diagnose=True,
    enqueue=True,  # Thread-safe logging
)

# Add file handler for errors only
logger.add(
    LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
    format=file_format,
    level="ERROR",
    rotation="00:00",
    retention="90 days",  # Keep error logs longer
    compression="zip",
    backtrace=True,
    diagnose=True,
    enqueue=True,
)

# Configure logger for uvicorn access logs
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": console_format,
            "level": LOG_LEVEL,
        }
    ]
)

# Export logger instance
__all__ = ["logger"]

