from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import AppUser, UserRole
from app.models.team import Team
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> AppUser:
        """Create a new user."""
        # Check if email already exists
        stmt = select(AppUser).where(
            AppUser.email == user_data.email,
            AppUser.deleted_at.is_(None)
        )
        existing_user = await db.execute(stmt)
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = AppUser(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            role=user_data.role
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[AppUser]:
        """Authenticate user with email and password."""
        stmt = select(AppUser).where(
            AppUser.email == email,
            AppUser.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[AppUser]:
        """Get user by ID."""
        stmt = select(AppUser).options(
            selectinload(AppUser.team)
        ).where(
            AppUser.user_id == user_id,
            AppUser.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[AppUser]:
        """Get user by email."""
        stmt = select(AppUser).where(
            AppUser.email == email,
            AppUser.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None
    ) -> List[AppUser]:
        """Get list of users with optional filtering."""
        stmt = select(AppUser).where(AppUser.deleted_at.is_(None))
        
        if role:
            stmt = stmt.where(AppUser.role == role)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_data: UserUpdate,
        current_user: AppUser
    ) -> AppUser:
        """Update user information."""
        # Get user
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions (users can only update themselves, unless organizer)
        if current_user.user_id != user_id and current_user.role != UserRole.ORGANIZER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update fields
        if user_data.name is not None:
            user.name = user_data.name
        
        if user_data.email is not None:
            # Check if new email already exists
            if user_data.email != user.email:
                stmt = select(AppUser).where(
                    AppUser.email == user_data.email,
                    AppUser.deleted_at.is_(None),
                    AppUser.user_id != user_id
                )
                existing_user = await db.execute(stmt)
                if existing_user.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
            user.email = user_data.email
        
        if user_data.team_id is not None:
            # Validate team exists if team_id is provided
            if user_data.team_id:
                stmt = select(Team).where(
                    Team.team_id == user_data.team_id,
                    Team.deleted_at.is_(None)
                )
                team_result = await db.execute(stmt)
                if not team_result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Team not found"
                    )
            user.team_id = user_data.team_id
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """Soft delete user."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.soft_delete()
        await db.commit()
        
        return True
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        await db.commit()
        
        return True