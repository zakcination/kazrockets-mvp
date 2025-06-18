from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
import enum
from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Submission(Base):
    __tablename__ = "submissions"
    
    submission_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4, 
        index=True
    )
    team_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("teams.team_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    event_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("competitive_events.event_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    file_url = Column(String, nullable=False)  # URL to cloud-stored PDF
    status = Column(
        Enum(SubmissionStatus), 
        nullable=False, 
        default=SubmissionStatus.PENDING
    )
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    team = relationship("Team", back_populates="submissions")
    event = relationship("CompetitiveEvent", back_populates="submissions")
    evaluations = relationship("Evaluation", back_populates="submission")
    
    def __repr__(self):
        return f"<Submission(submission_id={self.submission_id}, status={self.status})>"
    
    @property
    def is_active(self):
        """Check if submission is active (not soft deleted)."""
        return self.deleted_at is None
    
    @property
    def average_score(self):
        """Calculate average score from all evaluations."""
        if not self.evaluations:
            return None
        
        active_evaluations = [e for e in self.evaluations if e.is_active]
        if not active_evaluations:
            return None
            
        return sum(e.score for e in active_evaluations) / len(active_evaluations)
    
    def soft_delete(self):
        """Soft delete the submission."""
        self.deleted_at = func.now()