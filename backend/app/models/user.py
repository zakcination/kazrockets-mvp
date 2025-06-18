from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    PARTICIPANT = "PARTICIPANT"
    ORGANIZER = "ORGANIZER"
    JUDGE = "JUDGE"


class AppUser(Base):
    __tablename__ = "app_users"
    
    user_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4, 
        index=True
    )
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    team_id = Column(
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
    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    captained_teams = relationship("Team", foreign_keys="Team.captain_id", back_populates="captain")
    evaluations = relationship("Evaluation", back_populates="judge")
    
    def __repr__(self):
        return f"<AppUser(user_id={self.user_id}, email={self.email}, role={self.role})>"
    
    @property
    def is_active(self):
        """Check if user is active (not soft deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self):
        """Soft delete the user."""
        self.deleted_at = func.now()