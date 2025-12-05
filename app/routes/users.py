from fastapi import APIRouter, Depends, Request

from app.models.user import UserPublic
from app.services.authSecurity import get_current_user, require_role
from app.utils.logger import logger
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: UserPublic = Depends(get_current_user), request: Request = None):
    """
    Get current user's profile information
    """
    try:
        logger.info(f"User profile accessed: {current_user.email}")
        return current_user
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}", exc_info=True)
        raise


@router.get("/admin-only")
async def admin_only(current_user: UserPublic = Depends(require_role("admin")), request: Request = None):
    """
    Admin-only endpoint
    
    Requires admin role
    """
    try:
        logger.info(f"Admin endpoint accessed by: {current_user.email}")
        return {"message": f"Hello admin {current_user.email}"}
    except Exception as e:
        logger.error(f"Error in admin endpoint: {str(e)}", exc_info=True)
        raise
