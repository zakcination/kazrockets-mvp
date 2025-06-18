from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.user import (
    User, UserCreate, Token, LoginRequest, RefreshTokenRequest,
    PasswordChangeRequest
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import AppUser

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    user, token = await AuthService.register_user(db, user_data)
    
    return {
        "message": "User registered successfully",
        "user": User.model_validate(user),
        "tokens": token
    }


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user."""
    user, token = await AuthService.login_user(db, login_data)
    
    return {
        "message": "Login successful",
        "user": User.model_validate(user),
        "tokens": token
    }


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    return await AuthService.refresh_access_token(db, refresh_data.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: AppUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user."""
    await AuthService.logout_user(db, current_user)
    return {"message": "Logout successful"}


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get current user profile."""
    return User.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: AppUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    success = await UserService.change_password(
        db,
        current_user.user_id,
        password_data.current_password,
        password_data.new_password
    )
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )