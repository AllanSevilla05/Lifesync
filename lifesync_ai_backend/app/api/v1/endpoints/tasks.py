from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.models import User, Task, TaskCheckIn
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema, TaskCheckInCreate, VoiceTaskInput
from app.api.v1.endpoints.auth import get_current_user
from app.services.ai_service import AIService


router = APIRouter()
ai_service = AIService()

@router.post("/", response_model=TaskSchema)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Set completion time if task is being marked as completed
    if update_data.get("status") == "completed" and task.status != "completed":
        update_data["completed_at"] = datetime.utcnow()
        update_data["completion_percentage"] = 100.0
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.post("/voice", response_model=List[TaskSchema])
async def create_tasks_from_voice(
    voice_input: VoiceTaskInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create tasks from voice/natural language input"""
    
    # Parse voice input using AI
    parsed_data = await ai_service.parse_voice_input(
        voice_input.voice_text, 
        voice_input.context
    )
    
    created_tasks = []
    
    for task_data in parsed_data.get("tasks", []):
        db_task = Task(
            user_id=current_user.id,
            title=task_data.get("title"),
            description=task_data.get("description"),
            priority=task_data.get("priority", 1),
            estimated_duration=task_data.get("estimated_duration"),
            due_date=task_data.get("due_date")
        )
        db.add(db_task)
        created_tasks.append(db_task)
    
    db.commit()
    
    for task in created_tasks:
        db.refresh(task)
    
    return created_tasks

@router.post("/{task_id}/check-in")
async def task_check_in(
    task_id: int,
    check_in: TaskCheckInCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a check-in for a specific task"""
    
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_check_in = TaskCheckIn(
        task_id=task_id,
        **check_in.model_dump()
    )
    db.add(db_check_in)
    
    # Update task status based on check-in response
    if check_in.user_response == "started":
        task.status = "in_progress"
    elif check_in.user_response == "completed":
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.completion_percentage = 100.0
    
    db.commit()
    db.refresh(db_check_in)
    
    return {"message": "Check-in recorded successfully", "check_in": db_check_in}

@router.get("/optimize/schedule")
async def optimize_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-optimized schedule for the user's tasks"""
    
    # Get pending tasks
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_(["pending", "in_progress"])
    ).all()
    
    # Convert to dict format for AI processing
    task_data = [
        {
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date,
            "estimated_duration": task.estimated_duration
        }
        for task in tasks
    ]
    
    # Get user preferences
    user_preferences = get_current_user.preferences or {}
    
    # Get recent mood data (you'd implement this)
    mood_data = {"mood": 7, "energy": 6}  # Placeholder
    
    # Get AI optimization
    optimized_schedule = await ai_service.optimize_daily_schedule(
        task_data,
        user_preferences,
        mood_data,
        datetime.now()
    )
    
    return optimized_schedule