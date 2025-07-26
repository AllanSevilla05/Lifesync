from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks, wellness, documents, notifications, export, habits, collaboration, sync, scheduling, goals  # import your endpoint modules

api_router = APIRouter()

# Include all versioned endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(wellness.router, prefix="/wellness", tags=["wellness"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["scheduling"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])