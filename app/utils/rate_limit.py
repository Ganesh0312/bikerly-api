"""
Rate limiting functionality using in-memory storage
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.utils.exceptions import RateLimitError
from app.utils.logger import logger


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, consider using Redis or similar
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._cleanup_interval = timedelta(minutes=5)
        self._last_cleanup = datetime.utcnow()
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks"""
        now = datetime.utcnow()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff = now - timedelta(hours=1)
        keys_to_remove = []
        
        for key, timestamps in self._requests.items():
            self._requests[key] = [ts for ts in timestamps if ts > cutoff]
            if not self._requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._requests[key]
        
        self._last_cleanup = now
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get a unique identifier for the client"""
        # Try to get real IP from proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP if multiple are present
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Include user agent for additional uniqueness if needed
        user_agent = request.headers.get("User-Agent", "")
        
        return f"{client_ip}:{user_agent[:50]}"
    
    def is_allowed(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed
        
        Args:
            identifier: Unique identifier for the client
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        self._cleanup_old_entries()
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Filter out old requests
        self._requests[identifier] = [
            ts for ts in self._requests[identifier] if ts > cutoff
        ]
        
        # Count current requests
        request_count = len(self._requests[identifier])
        
        if request_count >= max_requests:
            # Calculate retry after (time until oldest request expires)
            if self._requests[identifier]:
                oldest_request = min(self._requests[identifier])
                retry_after = int((oldest_request + timedelta(seconds=window_seconds) - now).total_seconds())
                retry_after = max(1, retry_after)
            else:
                retry_after = window_seconds
            
            return False, retry_after
        
        # Add current request
        self._requests[identifier].append(now)
        return True, 0


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests
    """
    
    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,
        exempt_paths: list = None,
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.exempt_paths = exempt_paths or ["/", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        identifier = rate_limiter._get_client_identifier(request)
        is_allowed, retry_after = rate_limiter.is_allowed(
            identifier=identifier,
            max_requests=self.calls,
            window_seconds=self.period,
        )
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "retry_after": retry_after,
                },
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": True,
                    "error_code": "RATE_LIMIT_ERROR",
                    "message": "Rate limit exceeded",
                    "detail": f"Too many requests. Please try again after {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )
        
        response = await call_next(request)
        return response


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance"""
    return rate_limiter


# Dependency function for rate limiting specific endpoints
def check_rate_limit(
    request: Request,
    max_requests: int = 10,
    window_seconds: int = 60,
) -> None:
    """
    FastAPI dependency to rate limit a specific endpoint
    
    Args:
        request: FastAPI Request object
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        
    Raises:
        RateLimitError: If rate limit is exceeded
    """
    identifier = rate_limiter._get_client_identifier(request)
    is_allowed, retry_after = rate_limiter.is_allowed(
        identifier=identifier,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )
    
    if not is_allowed:
        raise RateLimitError(
            message="Rate limit exceeded",
            retry_after=retry_after,
        )


# Helper function to create rate limit dependency
def create_rate_limit_dependency(max_requests: int = 10, window_seconds: int = 60):
    """
    Factory function to create a rate limit dependency
    
    Usage:
        @router.post("/endpoint")
        async def my_endpoint(
            request: Request,
            _: None = Depends(create_rate_limit_dependency(max_requests=5, window_seconds=60))
        ):
            ...
    """
    from functools import partial
    
    def rate_limit_dep(request: Request) -> None:
        return check_rate_limit(request, max_requests, window_seconds)
    
    return rate_limit_dep

