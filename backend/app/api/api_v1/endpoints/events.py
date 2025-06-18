from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_organizer
from app.schemas.event import Event, EventCreate, EventUpdate
from app.models.event import CompetitiveEvent
from app.models.user import AppUser

router = APIRouter()


@router.post("/", response_model=Event, status_code=201)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_organizer)
):
    """Create a new event (organizer only)."""
    event = CompetitiveEvent(
        title=event_data.title,
        start_date=event_data.start_date,
        end_date=event_data.end_date
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return Event.model_validate(event)


@router.get("/", response_model=List[Event])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get list of events."""
    stmt = select(CompetitiveEvent).where(
        CompetitiveEvent.deleted_at.is_(None)
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    return [Event.model_validate(event) for event in events]


@router.get("/{event_id}", response_model=Event)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get event by ID."""
    stmt = select(CompetitiveEvent).where(
        CompetitiveEvent.event_id == event_id,
        CompetitiveEvent.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    
    if not event:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return Event.model_validate(event)