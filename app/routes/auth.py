from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User, UserCreate, Token
from app.services.authSecurity import hash_password, get_current_user, verify_password, create_access_token
from app.utils.exceptions import ConflictError, AuthenticationError, DatabaseError, ValidationError
from app.utils.logger import logger
from app.utils.rate_limit import create_rate_limit_dependency
from uuid import uuid4


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    _: None = Depends(create_rate_limit_dependency(max_requests=5, window_seconds=60))
):
    """
    Register a new user
    
    Rate limited to 5 requests per minute to prevent abuse
    """
    try:
        logger.info(f"Registration attempt for email: {user_in.email}")
        
        # Check if user already exists
        existing = await User.find_one(User.email == user_in.email)
        if existing:
            logger.warning(f"Registration failed: Email already exists - {user_in.email}")
            raise ConflictError(
                message="User with this email already exists",
                detail="A user with this email address is already registered",
            )

        # Hash password and create user
        try:
            hashed_password_value = hash_password(user_in.password)
        except ValueError as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise ValidationError(
                message="Password processing failed",
                detail="Password is too long. Maximum 72 bytes allowed.",
            )

        user = User(
            email=user_in.email,
            user_name=user_in.user_name,
            phone_number=user_in.phone_number,
            country_code=user_in.country_code,
            name=user_in.name,
            display_name=user_in.display_name,
            hashed_password=hashed_password_value,
        )

        await user.insert()
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")

        return {
            "id": str(user.id),
            "uuid": user.uuid,
            "email": user.email,
            "user_name": user.user_name,
            "display_name": user.display_name,
            "role": user.role,
        }
    
    except ConflictError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="Failed to create user",
            detail="An error occurred while creating your account. Please try again later.",
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    _: None = Depends(create_rate_limit_dependency(max_requests=10, window_seconds=60))
):
    """
    Login endpoint
    
    Rate limited to 10 requests per minute to prevent brute force attacks
    """
    try:
        # OAuth2PasswordRequestForm: form_data.username, form_data.password
        email = form_data.username
        password = form_data.password
        
        logger.info(f"Login attempt for email: {email}")

        # Find user
        user = await User.find_one(User.email == email)
        if not user:
            logger.warning(f"Login failed: User not found - {email}")
            raise AuthenticationError(
                message="Incorrect email or password",
                detail="Invalid credentials provided",
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password for email - {email}")
            raise AuthenticationError(
                message="Incorrect email or password",
                detail="Invalid credentials provided",
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: Inactive user - {email}")
            raise AuthenticationError(
                message="Account is inactive",
                detail="Your account has been deactivated. Please contact support.",
            )

        # Create access token
        token = create_access_token(
            data={"sub": user.email, "role": user.role, "uuid": user.uuid}
        )

        logger.info(f"User logged in successfully: {user.email}")
        return Token(access_token=token, token_type="bearer")
    
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise AuthenticationError(
            message="Login failed",
            detail="An error occurred during login. Please try again later.",
        )