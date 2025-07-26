from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import User, Task
from datetime import datetime

class TasksService:
    """Service for managing tasks and task-related operations"""
    
    def get_user_tasks(self, user_id: int, db: Session) -> List[Task]:
        """Get all tasks for a user"""
        return db.query(Task).filter(Task.user_id == user_id).all()
    
    def create_task(self, task_data: Dict[str, Any], user_id: int, db: Session) -> Task:
        """Create a new task"""
        task = Task(**task_data, user_id=user_id)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    def update_task(self, task_id: int, task_data: Dict[str, Any], user_id: int, db: Session) -> Optional[Task]:
        """Update an existing task"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            return None
        
        for field, value in task_data.items():
            if hasattr(task, field):
                setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    
    def delete_task(self, task_id: int, user_id: int, db: Session) -> bool:
        """Delete a task"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True

# Create a global instance
tasks_service = TasksService()