from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.core.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    evaluation_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4, 
        index=True
    )
    submission_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("submissions.submission_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    judge_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("app_users.user_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    score = Column(Integer, nullable=False)  # Range: 0-100
    comments = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Constraints
    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 100', name='check_score_range'),
    )
    
    # Relationships
    submission = relationship("Submission", back_populates="evaluations")
    judge = relationship("AppUser", back_populates="evaluations")
    
    def __repr__(self):
        return f"<Evaluation(evaluation_id={self.evaluation_id}, score={self.score})>"
    
    @property
    def is_active(self):
        """Check if evaluation is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self):
        """Soft delete the evaluation."""
        self.deleted_at = func.now()