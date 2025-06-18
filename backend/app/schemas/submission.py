from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.models.submission import SubmissionStatus


class SubmissionBase(BaseModel):
    team_id: UUID
    event_id: UUID


class SubmissionCreate(SubmissionBase):
    pass  # File will be handled separately in the endpoint


class SubmissionUpdate(BaseModel):
    status: Optional[SubmissionStatus] = None


class SubmissionInDB(SubmissionBase):
    submission_id: UUID
    file_url: str
    status: SubmissionStatus
    submitted_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Submission(SubmissionInDB):
    """Submission response schema."""
    pass


class SubmissionWithDetails(Submission):
    """Submission response with additional details."""
    team_name: str
    event_title: str
    average_score: Optional[float] = None
    evaluation_count: int = 0


class SubmissionSummary(BaseModel):
    """Simplified submission information."""
    submission_id: UUID
    team_name: str
    event_title: str
    status: SubmissionStatus
    submitted_at: datetime
    average_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class SubmissionStats(BaseModel):
    """Submission statistics."""
    submission_id: UUID
    team_name: str
    event_title: str
    status: SubmissionStatus
    submitted_at: datetime
    evaluation_count: int = 0
    average_score: Optional[float] = None
    highest_score: Optional[int] = None
    lowest_score: Optional[int] = None


class FileUploadResponse(BaseModel):
    """File upload response."""
    file_url: str
    file_size: int
    content_type: str
    upload_timestamp: datetime


class SubmissionStatusUpdate(BaseModel):
    """Submission status update notification."""
    submission_id: UUID
    old_status: SubmissionStatus
    new_status: SubmissionStatus
    updated_by: UUID
    updated_at: datetime