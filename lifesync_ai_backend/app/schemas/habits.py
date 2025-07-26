from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    frequency_type: str = Field(default="daily", pattern="^(daily|weekly|monthly)$")
    frequency_value: int = Field(default=1, ge=1, le=30)
    target_duration: Optional[int] = Field(None, ge=1)  # in minutes
    category: Optional[str] = None
    difficulty: int = Field(default=1, ge=1, le=5)
    reminder_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")  # HH:MM format
    tags: Optional[List[str]] = None

class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    frequency_type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    frequency_value: Optional[int] = Field(None, ge=1, le=30)
    target_duration: Optional[int] = Field(None, ge=1)
    category: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None
    reminder_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    tags: Optional[List[str]] = None

class Habit(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    frequency_type: str
    frequency_value: int
    target_duration: Optional[int]
    category: Optional[str]
    difficulty: int
    streak_count: int
    longest_streak: int
    total_completions: int
    is_active: bool
    reminder_time: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class HabitCompletionCreate(BaseModel):
    duration_minutes: Optional[int] = Field(None, ge=1)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    mood_before: Optional[int] = Field(None, ge=1, le=10)
    mood_after: Optional[int] = Field(None, ge=1, le=10)
    energy_before: Optional[int] = Field(None, ge=1, le=10)
    energy_after: Optional[int] = Field(None, ge=1, le=10)
    context: Optional[Dict[str, Any]] = None

class HabitCompletion(BaseModel):
    id: int
    habit_id: int
    completion_date: datetime
    duration_minutes: Optional[int]
    quality_rating: Optional[int]
    notes: Optional[str]
    mood_before: Optional[int]
    mood_after: Optional[int]
    energy_before: Optional[int]
    energy_after: Optional[int]
    context: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class HabitInsight(BaseModel):
    id: int
    habit_id: int
    insight_type: str
    title: str
    description: str
    data: Optional[Dict[str, Any]]
    confidence_score: float
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class HabitAnalytics(BaseModel):
    completion_rate: Dict[str, float]
    time_patterns: Dict[str, Any]
    quality_trends: Dict[str, Any]
    mood_energy_correlation: Dict[str, Any]
    streak_analysis: Dict[str, Any]
    contextual_patterns: Dict[str, Any]
    difficulty_adaptation: Dict[str, Any]