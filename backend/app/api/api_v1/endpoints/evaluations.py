from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_judge
from app.schemas.evaluation import Evaluation, EvaluationCreate
from app.models.evaluation import Evaluation as EvaluationModel
from app.models.user import AppUser

router = APIRouter()


@router.post("/", response_model=Evaluation, status_code=201)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(require_judge)
):
    """Create a new evaluation (judge only)."""
    evaluation = EvaluationModel(
        submission_id=evaluation_data.submission_id,
        judge_id=current_user.user_id,
        score=evaluation_data.score,
        comments=evaluation_data.comments
    )
    
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    
    return Evaluation.model_validate(evaluation)


@router.get("/", response_model=List[Evaluation])
async def get_evaluations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    submission_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_active_user)
):
    """Get list of evaluations."""
    stmt = select(EvaluationModel).where(
        EvaluationModel.deleted_at.is_(None)
    )
    
    if submission_id:
        stmt = stmt.where(EvaluationModel.submission_id == submission_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    evaluations = result.scalars().all()
    
    return [Evaluation.model_validate(evaluation) for evaluation in evaluations]