from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    captain_id: Optional[UUID] = None


class TeamMember(BaseModel):
    user_id: UUID
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


class TeamInDB(TeamBase):
    team_id: UUID
    captain_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Team(TeamInDB):
    """Team response schema."""
    pass


class TeamWithMembers(Team):
    """Team response with member information."""
    captain_name: str
    members: List[TeamMember] = []
    member_count: int = 0


class TeamSummary(BaseModel):
    """Simplified team information."""
    team_id: UUID
    name: str
    captain_name: str
    member_count: int
    
    class Config:
        from_attributes = True


class JoinTeamRequest(BaseModel):
    team_id: UUID


class LeaveTeamRequest(BaseModel):
    pass  # No fields needed, user identified by JWT