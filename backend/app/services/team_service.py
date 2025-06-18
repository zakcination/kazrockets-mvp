from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from uuid import UUID

from app.models.team import Team
from app.models.user import AppUser, UserRole
from app.schemas.team import TeamCreate, TeamUpdate


class TeamService:
    """Service class for team operations."""
    
    @staticmethod
    async def create_team(db: AsyncSession, team_data: TeamCreate, captain: AppUser) -> Team:
        """Create a new team."""
        # Validate captain is a participant
        if captain.role != UserRole.PARTICIPANT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only participants can be team captains"
            )
        
        # Check if captain is already in a team
        if captain.team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Captain is already in a team"
            )
        
        # Create team
        team = Team(
            name=team_data.name,
            captain_id=captain.user_id
        )
        
        db.add(team)
        await db.flush()  # Get team_id without committing
        
        # Add captain to team
        captain.team_id = team.team_id
        
        await db.commit()
        await db.refresh(team)
        
        return team
    
    @staticmethod
    async def get_team_by_id(db: AsyncSession, team_id: UUID) -> Optional[Team]:
        """Get team by ID with members."""
        stmt = select(Team).options(
            selectinload(Team.captain),
            selectinload(Team.members)
        ).where(
            Team.team_id == team_id,
            Team.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_teams(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Team]:
        """Get list of teams."""
        stmt = select(Team).options(
            selectinload(Team.captain),
            selectinload(Team.members)
        ).where(
            Team.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_team(
        db: AsyncSession,
        team_id: UUID,
        team_data: TeamUpdate,
        current_user: AppUser
    ) -> Team:
        """Update team information."""
        # Get team
        team = await TeamService.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check permissions (only captain or organizer can update)
        if (current_user.user_id != team.captain_id and 
            current_user.role != UserRole.ORGANIZER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update fields
        if team_data.name is not None:
            team.name = team_data.name
        
        if team_data.captain_id is not None:
            # Validate new captain
            stmt = select(AppUser).where(
                AppUser.user_id == team_data.captain_id,
                AppUser.deleted_at.is_(None),
                AppUser.role == UserRole.PARTICIPANT,
                AppUser.team_id == team_id  # Must be current team member
            )
            new_captain = await db.execute(stmt)
            if not new_captain.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New captain must be a participant and current team member"
                )
            team.captain_id = team_data.captain_id
        
        await db.commit()
        await db.refresh(team)
        
        return team
    
    @staticmethod
    async def join_team(db: AsyncSession, team_id: UUID, user: AppUser) -> Team:
        """Add user to team."""
        # Validate user is a participant
        if user.role != UserRole.PARTICIPANT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only participants can join teams"
            )
        
        # Check if user is already in a team
        if user.team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in a team"
            )
        
        # Get team
        team = await TeamService.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Add user to team
        user.team_id = team_id
        await db.commit()
        
        # Refresh team with updated members
        await db.refresh(team)
        return team
    
    @staticmethod
    async def leave_team(db: AsyncSession, user: AppUser) -> bool:
        """Remove user from team."""
        if not user.team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not in a team"
            )
        
        # Get team
        team = await TeamService.get_team_by_id(db, user.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check if user is captain
        if user.user_id == team.captain_id:
            # Count other team members
            stmt = select(func.count(AppUser.user_id)).where(
                AppUser.team_id == team.team_id,
                AppUser.user_id != user.user_id,
                AppUser.deleted_at.is_(None)
            )
            member_count = await db.execute(stmt)
            count = member_count.scalar()
            
            if count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Captain cannot leave team with other members. Transfer captaincy first."
                )
            else:
                # Delete team if captain is the only member
                team.soft_delete()
        
        # Remove user from team
        user.team_id = None
        await db.commit()
        
        return True
    
    @staticmethod
    async def delete_team(db: AsyncSession, team_id: UUID) -> bool:
        """Soft delete team."""
        team = await TeamService.get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Remove all members from team
        stmt = select(AppUser).where(
            AppUser.team_id == team_id,
            AppUser.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        members = result.scalars().all()
        
        for member in members:
            member.team_id = None
        
        # Soft delete team
        team.soft_delete()
        await db.commit()
        
        return True