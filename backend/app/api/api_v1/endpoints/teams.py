from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_participant, require_organizer
from app.schemas.team import (
    Team, TeamCreate, TeamUpdate, TeamWithMembers, TeamSummary,
    JoinTeamRequest, LeaveTeamRequest
)
from app.services.team_service import TeamService
from app.models.user import AppUser

router = APIRouter()


@router.post("/", response_model=TeamWithMembers, status_code=201)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_participant)
):
    """Create a new team (participant only)."""
    team = await TeamService.create_team(db, team_data, current_user)
    
    # Create response with member details
    team_dict = Team.model_validate(team).model_dump()
    team_dict["captain_name"] = team.captain.name
    team_dict["members"] = [
        {
            "user_id": member.user_id,
            "name": member.name,
            "email": member.email,
            "role": member.role.value
        }
        for member in team.members
    ]
    team_dict["member_count"] = len(team.members)
    
    return TeamWithMembers(**team_dict)


@router.get("/", response_model=List[TeamSummary])
async def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get list of teams."""
    teams = await TeamService.get_teams(db, skip=skip, limit=limit)
    
    return [
        TeamSummary(
            team_id=team.team_id,
            name=team.name,
            captain_name=team.captain.name,
            member_count=len(team.members)
        )
        for team in teams
    ]


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get team by ID."""
    team = await TeamService.get_team_by_id(db, team_id)
    if not team:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Create response with member details
    team_dict = Team.model_validate(team).model_dump()
    team_dict["captain_name"] = team.captain.name
    team_dict["members"] = [
        {
            "user_id": member.user_id,
            "name": member.name,
            "email": member.email,
            "role": member.role.value
        }
        for member in team.members
    ]
    team_dict["member_count"] = len(team.members)
    
    return TeamWithMembers(**team_dict)


@router.put("/{team_id}", response_model=TeamWithMembers)
async def update_team(
    team_id: UUID,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Update team (captain or organizer only)."""
    team = await TeamService.update_team(db, team_id, team_data, current_user)
    
    # Create response with member details
    team_dict = Team.model_validate(team).model_dump()
    team_dict["captain_name"] = team.captain.name
    team_dict["members"] = [
        {
            "user_id": member.user_id,
            "name": member.name,
            "email": member.email,
            "role": member.role.value
        }
        for member in team.members
    ]
    team_dict["member_count"] = len(team.members)
    
    return TeamWithMembers(**team_dict)


@router.post("/join", response_model=dict)
async def join_team(
    join_data: JoinTeamRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_participant)
):
    """Join a team (participant only)."""
    team = await TeamService.join_team(db, join_data.team_id, current_user)
    return {
        "message": "Successfully joined team",
        "team_id": team.team_id,
        "team_name": team.name
    }


@router.post("/leave", response_model=dict)
async def leave_team(
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_participant)
):
    """Leave current team (participant only)."""
    success = await TeamService.leave_team(db, current_user)
    return {"message": "Successfully left team"}


@router.delete("/{team_id}")
async def delete_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_organizer)
):
    """Delete team (organizer only)."""
    success = await TeamService.delete_team(db, team_id)
    return {"message": "Team deleted successfully"}