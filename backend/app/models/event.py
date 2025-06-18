from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.core.database import Base


class CompetitiveEvent(Base):
    __tablename__ = "competitive_events"
    
    event_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4, 
        index=True
    )
    title = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    winner_team_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("teams.team_id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    winner_team = relationship("Team", back_populates="won_events")
    submissions = relationship("Submission", back_populates="event")
    
    def __repr__(self):
        return f"<CompetitiveEvent(event_id={self.event_id}, title={self.title})>"
    
    @property
    def is_active(self):
        """Check if event is active (not soft deleted)."""
        return self.deleted_at is None
    
    @property
    def is_ongoing(self):
        """Check if event is currently ongoing."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        return self.start_date <= now <= self.end_date
    
    @property
    def is_finished(self):
        """Check if event has finished."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        return now > self.end_date
    
    def soft_delete(self):
        """Soft delete the event."""
        self.deleted_at = func.now()