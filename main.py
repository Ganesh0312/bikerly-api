from fastapi import FastAPI
from contextlib import asynccontextmanager
from pymongo.errors import PyMongoError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import init_db, close_db
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.utils.logger import logger
from app.utils.rate_limit import RateLimitMiddleware
from app.utils.exceptions import AppException
from app.utils.error_handler import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from app.services.config import RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Bikerly API")
    await init_db()

    yield

    logger.info("🛑 Shutting down Bikerly API")
    await close_db()


app = FastAPI(
    title="Bikerly API",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    RateLimitMiddleware,
    calls=RATE_LIMIT_CALLS,
    period=RATE_LIMIT_PERIOD,
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PyMongoError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Health
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "UP", "service": "bikerly-api"}

# Routers
app.include_router(auth_router)
app.include_router(users_router)
