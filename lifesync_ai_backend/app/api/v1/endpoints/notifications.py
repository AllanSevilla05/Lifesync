from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import User
from app.api.v1.endpoints.auth import get_current_user
from app.services.notification_service import notification_service

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_notifications(
    current_user: User = Depends(get_current_user)
):
    """Get all pending notifications for the current user"""
    notifications = notification_service.get_user_notifications(current_user.id)
    return notifications

@router.post("/mark-read")
async def mark_notification_read(
    notification_index: int,
    current_user: User = Depends(get_current_user)
):
    """Mark a specific notification as read"""
    notification_service.mark_notification_read(current_user.id, notification_index)
    return {"message": "Notification marked as read"}

@router.post("/clear-all")
async def clear_all_notifications(
    current_user: User = Depends(get_current_user)
):
    """Clear all notifications for the current user"""
    notification_service.clear_user_notifications(current_user.id)
    return {"message": "All notifications cleared"}

@router.post("/daily-summary")
async def generate_daily_summary(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and send daily summary notification"""
    background_tasks.add_task(
        notification_service.generate_daily_summary,
        current_user.id,
        db
    )
    return {"message": "Daily summary generation started"}

@router.post("/check-overdue")
async def check_overdue_tasks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Check for overdue tasks across all users"""
    background_tasks.add_task(
        notification_service.check_overdue_tasks,
        db
    )
    return {"message": "Overdue tasks check started"}

@router.post("/break-reminder")
async def suggest_break(
    last_activity_minutes_ago: int = 120,  # 2 hours default
    current_user: User = Depends(get_current_user)
):
    """Suggest a break based on activity time"""
    last_activity_time = datetime.utcnow() - timedelta(minutes=last_activity_minutes_ago)
    await notification_service.suggest_break_reminder(current_user.id, last_activity_time)
    return {"message": "Break reminder evaluated"}