from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    start_date: datetime
    end_date: datetime
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    winner_team_id: Optional[UUID] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class EventInDB(EventBase):
    event_id: UUID
    winner_team_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Event(EventInDB):
    """Event response schema."""
    pass


class EventWithWinner(Event):
    """Event response with winner information."""
    winner_team_name: Optional[str] = None


class EventSummary(BaseModel):
    """Simplified event information."""
    event_id: UUID
    title: str
    start_date: datetime
    end_date: datetime
    is_ongoing: bool
    is_finished: bool
    submission_count: int = 0
    
    class Config:
        from_attributes = True


class EventStats(BaseModel):
    """Event statistics."""
    event_id: UUID
    title: str
    total_submissions: int = 0
    pending_submissions: int = 0
    approved_submissions: int = 0
    rejected_submissions: int = 0
    total_evaluations: int = 0
    average_score: Optional[float] = None


class DeclareWinnerRequest(BaseModel):
    winner_team_id: UUID