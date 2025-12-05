"""
Error handling middleware and exception handlers
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import PyMongoError

from app.utils.exceptions import AppException
from app.utils.logger import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    errors = exc.errors()
    logger.warning(
        f"Validation error: {errors}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Validation error",
            "detail": "Invalid request data",
            "errors": errors,
            "path": request.url.path,
        },
    )


async def database_exception_handler(request: Request, exc: PyMongoError) -> JSONResponse:
    """Handle database errors"""
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "DATABASE_ERROR",
            "message": "Database operation failed",
            "detail": "An error occurred while processing your request",
            "path": request.url.path,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions"""
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error",
            "detail": "An unexpected error occurred",
            "path": request.url.path,
        },
    )

