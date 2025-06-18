from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class EvaluationBase(BaseModel):
    submission_id: UUID
    score: int = Field(..., ge=0, le=100, description="Score must be between 0 and 100")
    comments: Optional[str] = Field(None, max_length=1000)


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationUpdate(BaseModel):
    score: Optional[int] = Field(None, ge=0, le=100, description="Score must be between 0 and 100")
    comments: Optional[str] = Field(None, max_length=1000)


class EvaluationInDB(EvaluationBase):
    evaluation_id: UUID
    judge_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Evaluation(EvaluationInDB):
    """Evaluation response schema."""
    pass


class EvaluationWithDetails(Evaluation):
    """Evaluation response with additional details."""
    judge_name: str
    submission_team_name: str
    submission_event_title: str


class EvaluationSummary(BaseModel):
    """Simplified evaluation information."""
    evaluation_id: UUID
    judge_name: str
    score: int
    created_at: datetime
    has_comments: bool
    
    class Config:
        from_attributes = True


class SubmissionEvaluations(BaseModel):
    """All evaluations for a submission."""
    submission_id: UUID
    team_name: str
    event_title: str
    evaluations: list[EvaluationWithDetails] = []
    average_score: Optional[float] = None
    evaluation_count: int = 0


class JudgeEvaluationStats(BaseModel):
    """Judge evaluation statistics."""
    judge_id: UUID
    judge_name: str
    total_evaluations: int = 0
    average_score_given: Optional[float] = None
    highest_score_given: Optional[int] = None
    lowest_score_given: Optional[int] = None


class EvaluationRanking(BaseModel):
    """Submission ranking based on evaluations."""
    rank: int
    submission_id: UUID
    team_name: str
    average_score: float
    evaluation_count: int