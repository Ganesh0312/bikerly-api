import os
from datetime import timedelta
from dotenv import load_dotenv

# LOAD .env FILE FIRST (this is the missing piece)
load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# ---------- Database ----------
MONGO_URL = require_env("MONGO_URL")
MONGO_DB_NAME = require_env("MONGO_DB_NAME")

# ---------- JWT ----------
JWT_SECRET_KEY = require_env("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ---------- Rate Limiting ----------
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

# ---------- Logging ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_access_token_expires() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
