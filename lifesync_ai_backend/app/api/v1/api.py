from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks  # import your endpoint modules

api_router = APIRouter()

# Include all versioned endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])