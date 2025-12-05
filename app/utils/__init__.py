"""
Utility modules for the application
"""
from app.utils.logger import logger
from app.utils.exceptions import (
    AppException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    RateLimitError,
)
from app.utils.rate_limit import (
    RateLimiter,
    RateLimitMiddleware,
    rate_limiter,
    check_rate_limit,
    create_rate_limit_dependency,
)

__all__ = [
    "logger",
    "AppException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseError",
    "RateLimitError",
    "RateLimiter",
    "RateLimitMiddleware",
    "rate_limiter",
    "check_rate_limit",
    "create_rate_limit_dependency",
]

