# main.py
from fastapi import FastAPI
from pymongo.errors import PyMongoError

from app.db import init_db
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.utils.logger import logger
from app.utils.error_handler import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from app.utils.rate_limit import RateLimitMiddleware
from app.utils.exceptions import AppException
from app.services.config import RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Initialize logger
logger.info("Starting Bikerly API application")

app = FastAPI(
    title="Bikerly API with Beanie Auth",
    description="API for Bikerly application with authentication and user management",
    version="1.0.0",
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    calls=RATE_LIMIT_CALLS,
    period=RATE_LIMIT_PERIOD,
    exempt_paths=["/", "/docs", "/openapi.json", "/redoc"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PyMongoError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup"""
    try:
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("Shutting down Bikerly API application")


@app.get("/")
def root():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {
        "message": "Hello from FastAPI in bikerly-api!",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "bikerly-api",
        "version": "1.0.0",
    }


# Include routers
app.include_router(auth_router)
app.include_router(users_router)

logger.info("Application setup complete")