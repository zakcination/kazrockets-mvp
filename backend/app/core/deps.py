from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import AppUser, UserRole
from app.schemas.user import TokenData
from uuid import UUID

security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AppUser:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    payload = verify_token(credentials.credentials, "access")
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    stmt = select(AppUser).where(
        AppUser.user_id == user_uuid,
        AppUser.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: AppUser = Depends(get_current_user)
) -> AppUser:
    """Get current active user (not soft deleted)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """Dependency factory to require specific user roles."""
    async def role_checker(
        current_user: AppUser = Depends(get_current_active_user)
    ) -> AppUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user
    
    return role_checker


# Specific role dependencies
async def require_participant(
    current_user: AppUser = Depends(require_role(UserRole.PARTICIPANT))
) -> AppUser:
    """Require PARTICIPANT role."""
    return current_user


async def require_organizer(
    current_user: AppUser = Depends(require_role(UserRole.ORGANIZER))
) -> AppUser:
    """Require ORGANIZER role."""
    return current_user


async def require_judge(
    current_user: AppUser = Depends(require_role(UserRole.JUDGE))
) -> AppUser:
    """Require JUDGE role."""
    return current_user


async def require_organizer_or_judge(
    current_user: AppUser = Depends(require_role(UserRole.ORGANIZER, UserRole.JUDGE))
) -> AppUser:
    """Require ORGANIZER or JUDGE role."""
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AppUser]:
    """Get current user if token is provided, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(db, credentials)
    except HTTPException:
        return None