"""
Custom exceptions for the application
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class AppException(Exception):
    """Base exception for application errors"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when validation fails"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class AuthenticationError(AppException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Invalid credentials",
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(AppException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Authorization failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or "Insufficient permissions",
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundError(AppException):
    """Raised when a resource is not found"""
    def __init__(self, resource: str = "Resource", detail: Optional[str] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or f"{resource} not found",
            error_code="NOT_FOUND",
        )


class ConflictError(AppException):
    """Raised when a resource conflict occurs"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT_ERROR",
        )


class DatabaseError(AppException):
    """Raised when a database operation fails"""
    def __init__(self, message: str = "Database operation failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        detail = message
        if retry_after:
            detail = f"{message}. Retry after {retry_after} seconds"
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
        )

