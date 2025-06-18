from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_organizer
from app.schemas.user import User, UserUpdate, UserWithTeam
from app.services.user_service import UserService
from app.models.user import AppUser, UserRole

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[UserRole] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_organizer)
):
    """Get list of users (organizer only)."""
    users = await UserService.get_users(db, skip=skip, limit=limit, role=role)
    return [User.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserWithTeam)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get user by ID."""
    # Users can view their own profile, organizers can view any profile
    if current_user.user_id != user_id and current_user.role != UserRole.ORGANIZER:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create response with team information
    user_data = User.model_validate(user).model_dump()
    user_data["team_name"] = user.team.name if user.team else None
    
    return UserWithTeam(**user_data)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Update user."""
    updated_user = await UserService.update_user(db, user_id, user_data, current_user)
    return User.model_validate(updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_organizer)
):
    """Delete user (organizer only)."""
    success = await UserService.delete_user(db, user_id)
    return {"message": "User deleted successfully"}