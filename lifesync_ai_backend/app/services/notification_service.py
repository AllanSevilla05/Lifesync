import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json

from app.core.database import get_db
from app.models.models import User, Task, MoodEntry
from app.services.ai_service import AIService

class NotificationService:
    def __init__(self):
        self.ai_service = AIService()
        self.active_notifications = {}
    
    async def schedule_task_reminder(self, task_id: int, reminder_time: datetime, db: Session):
        """Schedule a reminder for a specific task"""
        
        # Calculate delay until reminder time
        now = datetime.utcnow()
        delay = (reminder_time - now).total_seconds()
        
        if delay > 0:
            # Schedule the reminder
            await asyncio.sleep(delay)
            await self._send_task_reminder(task_id, db)
    
    async def _send_task_reminder(self, task_id: int, db: Session):
        """Send a task reminder notification"""
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task or task.status == "completed":
            return
        
        notification = {
            "type": "task_reminder",
            "task_id": task.id,
            "title": f"Reminder: {task.title}",
            "message": f"It's time to work on: {task.title}",
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store notification for the user
        user_id = task.user_id
        if user_id not in self.active_notifications:
            self.active_notifications[user_id] = []
        
        self.active_notifications[user_id].append(notification)
        
        # In a real app, you'd send this via WebSocket, push notification, etc.
        print(f"📱 Notification sent to user {user_id}: {notification['title']}")
    
    async def check_overdue_tasks(self, db: Session):
        """Check for overdue tasks and send notifications"""
        now = datetime.utcnow()
        
        overdue_tasks = db.query(Task).filter(
            and_(
                Task.due_date < now,
                Task.status.in_(["pending", "in_progress"]),
                Task.due_date.isnot(None)
            )
        ).all()
        
        for task in overdue_tasks:
            notification = {
                "type": "overdue_task",
                "task_id": task.id,
                "title": f"Overdue: {task.title}",
                "message": f"Task '{task.title}' is overdue. Would you like to reschedule?",
                "due_date": task.due_date.isoformat(),
                "priority": 5,  # High priority for overdue
                "timestamp": now.isoformat()
            }
            
            user_id = task.user_id
            if user_id not in self.active_notifications:
                self.active_notifications[user_id] = []
            
            self.active_notifications[user_id].append(notification)
    
    async def generate_daily_summary(self, user_id: int, db: Session):
        """Generate a daily summary notification with AI insights"""
        
        # Get today's tasks
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        tasks_today = db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date >= today_start,
                Task.due_date <= today_end
            )
        ).all()
        
        completed_tasks = [t for t in tasks_today if t.status == "completed"]
        pending_tasks = [t for t in tasks_today if t.status in ["pending", "in_progress"]]
        
        # Get recent mood data
        recent_mood = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).first()
        
        # Generate AI summary
        summary_data = {
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "total_tasks": len(tasks_today),
            "recent_mood": recent_mood.mood_level if recent_mood else None,
            "recent_energy": recent_mood.energy_level if recent_mood else None
        }
        
        # Create summary message
        if summary_data["total_tasks"] == 0:
            message = "No tasks scheduled for today. Great time to plan ahead or focus on self-care!"
        else:
            completion_rate = (summary_data["completed_tasks"] / summary_data["total_tasks"]) * 100
            if completion_rate >= 80:
                message = f"🎉 Excellent work! You've completed {summary_data['completed_tasks']}/{summary_data['total_tasks']} tasks today."
            elif completion_rate >= 50:
                message = f"👍 Good progress! {summary_data['completed_tasks']}/{summary_data['total_tasks']} tasks done. Keep it up!"
            else:
                message = f"📝 {summary_data['pending_tasks']} tasks still pending. You've got this!"
        
        notification = {
            "type": "daily_summary",
            "title": "Daily Summary",
            "message": message,
            "data": summary_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if user_id not in self.active_notifications:
            self.active_notifications[user_id] = []
        
        self.active_notifications[user_id].append(notification)
    
    async def suggest_break_reminder(self, user_id: int, last_activity_time: datetime):
        """Suggest a break if user has been working for too long"""
        now = datetime.utcnow()
        work_duration = (now - last_activity_time).total_seconds() / 3600  # hours
        
        if work_duration >= 2:  # Working for 2+ hours
            notification = {
                "type": "break_reminder",
                "title": "Time for a Break! 🧘‍♀️",
                "message": f"You've been focused for {work_duration:.1f} hours. Take a 10-minute break to recharge!",
                "suggestions": [
                    "Take a short walk",
                    "Do some stretching",
                    "Practice deep breathing",
                    "Hydrate with water"
                ],
                "timestamp": now.isoformat()
            }
            
            if user_id not in self.active_notifications:
                self.active_notifications[user_id] = []
            
            self.active_notifications[user_id].append(notification)
    
    def get_user_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all pending notifications for a user"""
        return self.active_notifications.get(user_id, [])
    
    def mark_notification_read(self, user_id: int, notification_index: int):
        """Mark a notification as read/remove it"""
        if user_id in self.active_notifications:
            notifications = self.active_notifications[user_id]
            if 0 <= notification_index < len(notifications):
                notifications.pop(notification_index)
    
    def clear_user_notifications(self, user_id: int):
        """Clear all notifications for a user"""
        if user_id in self.active_notifications:
            self.active_notifications[user_id] = []

# Global notification service instance
notification_service = NotificationService()