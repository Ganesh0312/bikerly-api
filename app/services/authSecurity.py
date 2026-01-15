from datetime import datetime
from typing import Optional, Callable
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
import bcrypt

from app.services.config import JWT_SECRET_KEY, JWT_ALGORITHM, get_access_token_expires
from app.models.user import User, UserPublic
from app.utils.exceptions import AuthenticationError, AuthorizationError
from app.utils.logger import logger

# Initialize CryptContext with explicit bcrypt backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=12)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Raises:
        ValueError: If password is too long (>72 bytes) or hashing fails
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    try:
        # Encode password to bytes to check length
        raw_bytes = password.encode("utf-8")
        byte_length = len(raw_bytes)

        # Bcrypt has a 72-byte limit, truncate if necessary
        if byte_length > 72:
            logger.warning(f"Password exceeds bcrypt 72-byte limit ({byte_length} bytes), truncating")
            password = raw_bytes[:72].decode("utf-8", errors="ignore")
        
        # Use bcrypt directly to avoid passlib issues
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        return hashed.decode("utf-8")
        
    except ValueError as e:
        # Re-raise ValueError as-is (expected errors)
        raise
    except Exception as e:
        # Log unexpected errors without full stack trace
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Password hashing failed. Please try again.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Use bcrypt directly for verification
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.warning(f"Error verifying password: {str(e)}")
        return False


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing token payload
        
    Returns:
        Encoded JWT token string
    """
    try:
        to_decode = data.copy()
        expire = datetime.utcnow() + get_access_token_expires()
        to_decode.update({"exp": expire})
        token = jwt.encode(to_decode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        logger.debug(f"Access token created for: {data.get('sub')}")
        return token
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise


async def get_current_user(token: str = Depends(oauth_scheme)) -> UserPublic:
    """
    Get the current authenticated user from JWT token
    
    Args:
        token: JWT access token
        
    Returns:
        UserPublic object for the authenticated user
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise AuthenticationError(
                message="Could not validate credentials",
                detail="Invalid token format",
            )
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        raise AuthenticationError(
            message="Could not validate credentials",
            detail="Invalid or expired token",
        )
    
    user = await User.find_one(User.email == email)
    if user is None:
        logger.warning(f"User not found for token email: {email}")
        raise AuthenticationError(
            message="Could not validate credentials",
            detail="User not found",
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {email}")
        raise AuthenticationError(
            message="Account is inactive",
            detail="Your account has been deactivated",
        )

    return UserPublic(
        id=str(user.id),
        uuid=user.uuid,
        email=user.email,
        user_name=user.user_name,
        phone_number=user.phone_number,
        country_code=user.country_code,
        name=user.name,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        profile_picture_url=user.profile_picture_url,
        bio=user.bio,
        website=user.website,
        location=user.location,
        social_links=user.social_links,
        created_at=user.created_at,
        updated_at=user.updated_at,
        created_by=user.created_by,
        updated_by=user.updated_by,
    )


def require_role(required_role: str) -> Callable:
    """
    Dependency factory to require a specific role
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_dep(current_user: UserPublic = Depends(get_current_user)):
        if current_user.role != required_role:
            logger.warning(
                f"Authorization failed: User {current_user.email} "
                f"(role: {current_user.role}) attempted to access {required_role}-only endpoint"
            )
            raise AuthorizationError(
                message="Not enough permissions",
                detail=f"This endpoint requires {required_role} role",
            )
        return current_user
    return role_dep