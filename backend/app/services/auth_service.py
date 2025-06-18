from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.user import AppUser
from app.schemas.user import Token, LoginRequest, UserCreate
from app.services.user_service import UserService
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_token,
    get_password_hash
)
from app.core.config import settings


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> Tuple[AppUser, Token]:
        """Register a new user and return user with tokens."""
        # Create user
        user = await UserService.create_user(db, user_data)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.user_id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.user_id)}
        )
        
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
        return user, token
    
    @staticmethod
    async def login_user(db: AsyncSession, login_data: LoginRequest) -> Tuple[AppUser, Token]:
        """Login user and return user with tokens."""
        # Authenticate user
        user = await UserService.authenticate_user(
            db, login_data.email, login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.user_id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.user_id)}
        )
        
        token = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
        return user, token
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        from uuid import UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await UserService.get_user_by_id(db, user_uuid)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.user_id), "role": user.role.value}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.user_id)}
        )
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def logout_user(db: AsyncSession, user: AppUser) -> bool:
        """Logout user (in a real app, this would invalidate tokens)."""
        # In a production app, you might want to:
        # 1. Add tokens to a blacklist
        # 2. Store active sessions in Redis
        # 3. Clear refresh tokens from database
        
        # For MVP, we'll just return True as the client will discard tokens
        return True
    
    @staticmethod
    def validate_token(token: str, token_type: str = "access") -> Optional[dict]:
        """Validate and decode JWT token."""
        return verify_token(token, token_type)