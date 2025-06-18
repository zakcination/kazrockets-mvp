from typing import List
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_participant
from app.schemas.submission import Submission, SubmissionCreate
from app.models.submission import Submission as SubmissionModel
from app.models.user import AppUser, UserRole

router = APIRouter()


@router.post("/", response_model=dict, status_code=201)
async def create_submission(
    team_id: UUID = Form(...),
    event_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_participant)
):
    """Create a new submission (participant only)."""
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate user is in the team
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit for your own team"
        )
    
    # For MVP, we'll simulate file upload
    file_url = f"submissions/{event_id}/{team_id}/{file.filename}"
    
    submission = SubmissionModel(
        team_id=team_id,
        event_id=event_id,
        file_url=file_url
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return {
        "message": "Submission created successfully",
        "submission_id": submission.submission_id,
        "status": submission.status.value
    }


@router.get("/", response_model=List[Submission])
async def get_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    event_id: UUID = Query(None),
    team_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get list of submissions."""
    stmt = select(SubmissionModel).where(
        SubmissionModel.deleted_at.is_(None)
    )
    
    # Filter by event if provided
    if event_id:
        stmt = stmt.where(SubmissionModel.event_id == event_id)
    
    # Filter by team if provided
    if team_id:
        stmt = stmt.where(SubmissionModel.team_id == team_id)
    
    # Participants can only see their own team's submissions
    if current_user.role == UserRole.PARTICIPANT and current_user.team_id:
        stmt = stmt.where(SubmissionModel.team_id == current_user.team_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    submissions = result.scalars().all()
    
    return [Submission.model_validate(submission) for submission in submissions]