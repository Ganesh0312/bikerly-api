# Utils Folder Documentation

This folder contains utility modules for error handling, logging, and rate limiting. Below is a detailed explanation of each file, its classes, functions, and use cases.

---

## 📁 File Structure

```
app/utils/
├── __init__.py          # Package initialization and exports
├── logger.py            # Logging configuration
├── exceptions.py        # Custom exception classes
├── error_handler.py     # Exception handlers
└── rate_limit.py        # Rate limiting functionality
```

---

## 1. `logger.py` - Logging Configuration

### Purpose
Configures structured logging using Loguru library with multiple output handlers (console and files).

### Key Components

#### **Variables:**
- `LOG_LEVEL`: Logging level from environment (default: "INFO")
- `LOG_DIR`: Directory path for log files (`logs/`)
- `console_format`: Format string for console output (colored)
- `file_format`: Format string for file output (detailed)

#### **Logger Configuration:**
The logger is configured with three handlers:

1. **Console Handler** (lines 35-42)
   - Outputs to `sys.stdout`
   - Colored output for better readability
   - Format: `{time} | {level} | {name}:{function}:{line} | {message}`
   - Includes backtrace and diagnosis for debugging

2. **File Handler - All Logs** (lines 45-55)
   - File: `logs/app_YYYY-MM-DD.log`
   - Rotates daily at midnight
   - Retention: 30 days
   - Compressed old logs (ZIP)
   - Thread-safe (enqueue=True)

3. **File Handler - Errors Only** (lines 58-68)
   - File: `logs/errors_YYYY-MM-DD.log`
   - Only ERROR level and above
   - Retention: 90 days (longer for error tracking)
   - Compressed old logs

### Usage Example:
```python
from app.utils.logger import logger

# Log different levels
logger.debug("Debug information")
logger.info("User logged in: user@example.com")
logger.warning("Rate limit approaching")
logger.error("Database connection failed", exc_info=True)
logger.critical("System shutdown")
```

### Use Cases:
- Track application events
- Debug issues with detailed stack traces
- Monitor errors separately
- Audit user actions
- Performance monitoring

---

## 2. `exceptions.py` - Custom Exception Classes

### Purpose
Defines custom exception classes that extend the base `AppException` for consistent error handling across the application.

### Class Hierarchy:
```
AppException (Base)
├── ValidationError
├── AuthenticationError
├── AuthorizationError
├── NotFoundError
├── ConflictError
├── DatabaseError
└── RateLimitError
```

### Classes and Their Use Cases:

#### **1. `AppException` (Base Class)**
```python
class AppException(Exception)
```
- **Purpose**: Base class for all custom exceptions
- **Attributes**:
  - `message`: Human-readable error message
  - `status_code`: HTTP status code
  - `detail`: Detailed error description
  - `error_code`: Machine-readable error code
- **Use Case**: Extended by all other exception classes

#### **2. `ValidationError`**
```python
class ValidationError(AppException)
```
- **HTTP Status**: 400 Bad Request
- **Error Code**: `VALIDATION_ERROR`
- **Use Cases**:
  - Invalid input data
  - Missing required fields
  - Data format errors
  - Password too long/short
- **Example**:
```python
raise ValidationError(
    message="Password processing failed",
    detail="Password is too long. Maximum 72 bytes allowed."
)
```

#### **3. `AuthenticationError`**
```python
class AuthenticationError(AppException)
```
- **HTTP Status**: 401 Unauthorized
- **Error Code**: `AUTHENTICATION_ERROR`
- **Use Cases**:
  - Invalid login credentials
  - Expired tokens
  - Missing authentication
  - Invalid JWT token
- **Example**:
```python
raise AuthenticationError(
    message="Incorrect email or password",
    detail="Invalid credentials provided"
)
```

#### **4. `AuthorizationError`**
```python
class AuthorizationError(AppException)
```
- **HTTP Status**: 403 Forbidden
- **Error Code**: `AUTHORIZATION_ERROR`
- **Use Cases**:
  - Insufficient permissions
  - Role-based access denied
  - Resource access denied
- **Example**:
```python
raise AuthorizationError(
    message="Not enough permissions",
    detail="This endpoint requires admin role"
)
```

#### **5. `NotFoundError`**
```python
class NotFoundError(AppException)
```
- **HTTP Status**: 404 Not Found
- **Error Code**: `NOT_FOUND`
- **Use Cases**:
  - User not found
  - Resource doesn't exist
  - Invalid ID provided
- **Example**:
```python
raise NotFoundError(
    resource="User",
    detail="User with ID 123 not found"
)
```

#### **6. `ConflictError`**
```python
class ConflictError(AppException)
```
- **HTTP Status**: 409 Conflict
- **Error Code**: `CONFLICT_ERROR`
- **Use Cases**:
  - Duplicate email registration
  - Resource already exists
  - Concurrent modification conflicts
- **Example**:
```python
raise ConflictError(
    message="User with this email already exists",
    detail="A user with this email address is already registered"
)
```

#### **7. `DatabaseError`**
```python
class DatabaseError(AppException)
```
- **HTTP Status**: 500 Internal Server Error
- **Error Code**: `DATABASE_ERROR`
- **Use Cases**:
  - Database connection failures
  - Query execution errors
  - Transaction failures
- **Example**:
```python
raise DatabaseError(
    message="Failed to create user",
    detail="An error occurred while creating your account"
)
```

#### **8. `RateLimitError`**
```python
class RateLimitError(AppException)
```
- **HTTP Status**: 429 Too Many Requests
- **Error Code**: `RATE_LIMIT_ERROR`
- **Attributes**: Includes `retry_after` (seconds)
- **Use Cases**:
  - Too many requests from same client
  - API rate limit exceeded
  - Brute force protection
- **Example**:
```python
raise RateLimitError(
    message="Rate limit exceeded",
    retry_after=60
)
```

---

## 3. `error_handler.py` - Exception Handlers

### Purpose
Contains async exception handler functions that catch and format exceptions into consistent JSON responses.

### Functions:

#### **1. `app_exception_handler()`**
```python
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse
```
- **Purpose**: Handles all custom `AppException` instances
- **What it does**:
  - Logs the error with context (error_code, status_code, path, method)
  - Returns JSON response with error details
- **Response Format**:
```json
{
    "error": true,
    "error_code": "ERROR_CODE",
    "message": "Error message",
    "detail": "Detailed description",
    "path": "/api/endpoint"
}
```

#### **2. `http_exception_handler()`**
```python
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse
```
- **Purpose**: Handles FastAPI/Starlette HTTP exceptions
- **What it does**:
  - Logs as warning (less severe than custom exceptions)
  - Formats standard HTTP exceptions consistently
- **Use Case**: Catches exceptions raised by FastAPI itself

#### **3. `validation_exception_handler()`**
```python
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse
```
- **Purpose**: Handles Pydantic validation errors
- **What it does**:
  - Logs validation errors with full error details
  - Returns 422 status with list of validation errors
- **Response Format**:
```json
{
    "error": true,
    "error_code": "VALIDATION_ERROR",
    "message": "Validation error",
    "detail": "Invalid request data",
    "errors": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ],
    "path": "/api/endpoint"
}
```

#### **4. `database_exception_handler()`**
```python
async def database_exception_handler(request: Request, exc: PyMongoError) -> JSONResponse
```
- **Purpose**: Handles MongoDB/PyMongo errors
- **What it does**:
  - Logs database errors with full stack trace
  - Returns generic error message (doesn't expose DB details)
- **Use Case**: Connection failures, query errors, etc.

#### **5. `beanie_exception_handler()`**
```python
async def beanie_exception_handler(request: Request, exc: BeanieException) -> JSONResponse
```
- **Purpose**: Handles Beanie ORM specific errors
- **What it does**:
  - Logs Beanie errors with context
  - Returns generic database error response
- **Use Case**: Document validation, query errors, etc.

#### **6. `general_exception_handler()`**
```python
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse
```
- **Purpose**: Catches all unhandled exceptions (catch-all)
- **What it does**:
  - Logs full exception with stack trace
  - Returns generic 500 error
  - Prevents exposing internal errors to clients
- **Use Case**: Unexpected errors, programming errors, etc.

### Registration in main.py:
```python
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PyMongoError, database_exception_handler)
app.add_exception_handler(BeanieException, beanie_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

---

## 4. `rate_limit.py` - Rate Limiting

### Purpose
Implements rate limiting to prevent API abuse, brute force attacks, and ensure fair resource usage.

### Classes:

#### **1. `RateLimiter`**
```python
class RateLimiter
```
- **Purpose**: Core rate limiting logic with in-memory storage
- **Attributes**:
  - `_requests`: Dictionary storing request timestamps per client
  - `_cleanup_interval`: How often to clean old entries (5 minutes)
  - `_last_cleanup`: Last cleanup timestamp

##### **Methods:**

**`_cleanup_old_entries()`**
- **Purpose**: Prevents memory leaks by removing old entries
- **What it does**:
  - Runs every 5 minutes
  - Removes entries older than 1 hour
  - Deletes empty client entries
- **Why needed**: Without cleanup, memory usage grows indefinitely

**`_get_client_identifier(request: Request) -> str`**
- **Purpose**: Creates unique identifier for each client
- **What it does**:
  - Extracts IP from `X-Forwarded-For` header (if behind proxy)
  - Falls back to `request.client.host`
  - Includes User-Agent (first 50 chars) for uniqueness
- **Returns**: `"{ip}:{user_agent}"`
- **Example**: `"192.168.1.1:Mozilla/5.0..."`

**`is_allowed(identifier, max_requests, window_seconds) -> Tuple[bool, int]`**
- **Purpose**: Checks if a request should be allowed
- **Parameters**:
  - `identifier`: Client identifier
  - `max_requests`: Maximum requests allowed (default: 100)
  - `window_seconds`: Time window in seconds (default: 60)
- **Returns**: `(is_allowed: bool, retry_after: int)`
- **Logic**:
  1. Cleans old entries
  2. Filters requests within time window
  3. Counts current requests
  4. If limit exceeded, calculates retry_after time
  5. If allowed, adds current request timestamp
- **Example**:
```python
is_allowed, retry_after = rate_limiter.is_allowed(
    identifier="192.168.1.1:...",
    max_requests=10,
    window_seconds=60
)
```

#### **2. `RateLimitMiddleware`**
```python
class RateLimitMiddleware(BaseHTTPMiddleware)
```
- **Purpose**: FastAPI middleware to apply rate limiting globally
- **Inherits**: `BaseHTTPMiddleware` from Starlette
- **Attributes**:
  - `calls`: Max requests per window
  - `period`: Time window in seconds
  - `exempt_paths`: Paths to skip rate limiting

##### **Methods:**

**`__init__(app, calls, period, exempt_paths)`**
- **Purpose**: Initialize middleware with configuration
- **Exempt paths**: `["/", "/docs", "/openapi.json", "/redoc"]`

**`dispatch(request, call_next)`**
- **Purpose**: Intercepts all requests
- **What it does**:
  1. Checks if path is exempt
  2. Gets client identifier
  3. Checks rate limit
  4. If exceeded, returns 429 response
  5. If allowed, continues to next middleware/route
- **Response on limit exceeded**:
```json
{
    "error": true,
    "error_code": "RATE_LIMIT_ERROR",
    "message": "Rate limit exceeded",
    "detail": "Too many requests. Please try again after 45 seconds.",
    "retry_after": 45
}
```
- **Headers**: `Retry-After: 45`

### Functions:

#### **1. `get_rate_limiter() -> RateLimiter`**
- **Purpose**: Get the global rate limiter instance
- **Returns**: Singleton `RateLimiter` instance
- **Use Case**: Access rate limiter from anywhere in the app

#### **2. `check_rate_limit(request, max_requests, window_seconds) -> None`**
- **Purpose**: FastAPI dependency function for endpoint-specific rate limiting
- **Parameters**:
  - `request`: FastAPI Request object
  - `max_requests`: Max requests allowed
  - `window_seconds`: Time window
- **Raises**: `RateLimitError` if limit exceeded
- **Use Case**: Apply stricter limits to specific endpoints

#### **3. `create_rate_limit_dependency(max_requests, window_seconds)`**
- **Purpose**: Factory function to create rate limit dependencies
- **Returns**: Dependency function for FastAPI
- **Usage Example**:
```python
@router.post("/register")
async def register(
    user_in: UserCreate,
    request: Request,
    _: None = Depends(create_rate_limit_dependency(max_requests=5, window_seconds=60))
):
    # Only 5 registrations per minute per client
    ...
```

### Global Instance:
```python
rate_limiter = RateLimiter()  # Singleton instance
```

### Use Cases:
1. **Global Rate Limiting**: Applied via middleware to all routes
2. **Endpoint-Specific**: Stricter limits for sensitive endpoints (login, register)
3. **Brute Force Protection**: Prevent password guessing attacks
4. **API Fairness**: Ensure fair resource distribution
5. **DoS Protection**: Prevent denial of service attacks

### Configuration:
Set via environment variables:
```env
RATE_LIMIT_CALLS=100      # Max requests
RATE_LIMIT_PERIOD=60      # Time window in seconds
```

---

## 5. `__init__.py` - Package Exports

### Purpose
Makes all utilities easily importable from a single location.

### Exports:
- **Logger**: `logger`
- **Exceptions**: All exception classes
- **Rate Limiting**: Classes and functions

### Usage:
```python
# Instead of:
from app.utils.logger import logger
from app.utils.exceptions import ValidationError
from app.utils.rate_limit import create_rate_limit_dependency

# You can do:
from app.utils import logger, ValidationError, create_rate_limit_dependency
```

---

## 🔄 How They Work Together

### Request Flow with Error Handling:

1. **Request arrives** → `RateLimitMiddleware` checks rate limit
2. **If rate limited** → Returns 429 response immediately
3. **If allowed** → Request proceeds to route handler
4. **Route handler** → May raise custom exception (e.g., `AuthenticationError`)
5. **Exception handler** → Catches exception, logs it, returns JSON response
6. **Logger** → Records all events throughout the process

### Example Flow:
```
User Request → Rate Limit Check → Route Handler → Exception Raised
                                                      ↓
                                            Exception Handler
                                                      ↓
                                            Logger Records Error
                                                      ↓
                                            JSON Response Sent
```

---

## 📝 Best Practices

1. **Use Custom Exceptions**: Always use custom exceptions instead of generic `HTTPException`
2. **Log Appropriately**: Use correct log levels (DEBUG, INFO, WARNING, ERROR)
3. **Rate Limit Sensitive Endpoints**: Apply stricter limits to login/register
4. **Monitor Logs**: Regularly check error logs for issues
5. **Clean Up**: Rate limiter automatically cleans up, but monitor memory usage

---

## 🚀 Production Considerations

1. **Use Redis for Rate Limiting**: In-memory storage doesn't work across multiple servers
2. **Log Aggregation**: Use services like ELK, CloudWatch, or Datadog
3. **Error Tracking**: Integrate with Sentry or similar services
4. **Monitoring**: Set up alerts for high error rates or rate limit violations
5. **Log Retention**: Adjust retention policies based on compliance requirements

