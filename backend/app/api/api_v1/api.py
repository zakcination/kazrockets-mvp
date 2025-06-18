from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, teams, events, submissions, evaluations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Evaluations"])