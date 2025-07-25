from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1
    estimated_duration: Optional[int] = None
    tags: Optional[List[str]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    completion_percentage: Optional[float] = None
    tags: Optional[List[str]] = None

class Task(TaskBase):
    id: int
    user_id: int
    status: str
    completion_percentage: float
    ai_suggested_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskCheckInCreate(BaseModel):
    user_response: str
    notes: Optional[str] = None
    mood_at_checkin: Optional[int] = None
    energy_at_checkin: Optional[int] = None

class VoiceTaskInput(BaseModel):
    voice_text: str
    context: Optional[str] = None  # Additional context for better parsing
