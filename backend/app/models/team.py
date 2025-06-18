from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4, 
        index=True
    )
    name = Column(String, nullable=False)
    captain_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("app_users.user_id", ondelete="CASCADE"), 
        nullable=False,
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
    captain = relationship("AppUser", foreign_keys=[captain_id], back_populates="captained_teams")
    members = relationship("AppUser", foreign_keys="AppUser.team_id", back_populates="team")
    submissions = relationship("Submission", back_populates="team")
    won_events = relationship("CompetitiveEvent", back_populates="winner_team")
    
    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name={self.name})>"
    
    @property
    def is_active(self):
        """Check if team is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self):
        """Soft delete the team."""
        self.deleted_at = func.now()