import os 
from datetime import timedelta

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bikerly_db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "9000"))

# Rate limiting configuration
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "90"))  # seconds

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_access_token_expires() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)