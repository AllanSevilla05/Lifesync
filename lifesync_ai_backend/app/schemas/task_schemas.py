# app/schemas/task_schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    ACADEMIC = "academic"

class TaskInput(BaseModel):
    user_input: str = Field(..., description="User's voice or text input")

class Task(BaseModel):
    name: str
    priority: Priority
    category: Category
    estimated_duration: int = Field(..., description="Duration in minutes")
    due_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ParsedTasksResponse(BaseModel):
    success: bool
    tasks: List[Task]
    message: Optional[str] = None

class UserPreferences(BaseModel):
    productive_hours: List[str] = Field(default=["09:00", "14:00"])
    break_frequency: int = Field(default=90, description="Minutes between breaks")
    work_day_start: str = Field(default="09:00")
    work_day_end: str = Field(default="17:00")
    preferred_task_duration: int = Field(default=45, description="Preferred task duration in minutes")

class ScheduleItem(BaseModel):
    time: str
    duration: int
    task: str
    type: str = Field(..., description="work/break/meal")
    priority: Optional[Priority] = None

class ScheduleRequest(BaseModel):
    tasks: List[Task]
    user_preferences: UserPreferences
    user_history: Optional[Dict[str, Any]] = None

class ScheduleResponse(BaseModel):
    success: bool
    schedule: List[ScheduleItem]
    message: Optional[str] = None

class DocumentUpload(BaseModel):
    document_text: str
    document_type: str = Field(default="syllabus")

class ExtractedItem(BaseModel):
    name: str
    type: str = Field(..., description="assignment/exam/project/deadline")
    due_date: Optional[date] = None
    description: Optional[str] = None

class DocumentProcessResponse(BaseModel):
    success: bool
    extracted_items: List[ExtractedItem]
    message: Optional[str] = None

class MoodData(BaseModel):
    energy_level: int = Field(..., ge=1, le=10, description="Energy level 1-10")
    mood_rating: int = Field(..., ge=1, le=10, description="Mood rating 1-10")
    stress_level: int = Field(..., ge=1, le=10, description="Stress level 1-10")
    timestamp: datetime = Field(default_factory=datetime.now)

class WellnessAction(BaseModel):
    type: str = Field(..., description="break/hydration/exercise/meal/rest")
    time: str
    action: str
    reason: str

class WellnessRequest(BaseModel):
    mood_data: MoodData
    schedule_data: Dict[str, Any]

class WellnessResponse(BaseModel):
    success: bool
    wellness_suggestions: List[WellnessAction]
    message: Optional[str] = None

class UserBehaviorData(BaseModel):
    task_completions: List[Dict[str, Any]]
    completion_times: Dict[str, float]  # task_type -> avg_completion_time
    success_rates: Dict[str, float]     # time_slot -> success_rate

class BehaviorAnalysisResponse(BaseModel):
    success: bool
    insights: Dict[str, Any]
    recommendations: List[str] = []
    message: Optional[str] = None