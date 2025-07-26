from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MoodEntryCreate(BaseModel):
    mood_level: int  # 1-10
    energy_level: int  # 1-10
    stress_level: Optional[int] = None  # 1-10
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class MoodEntry(MoodEntryCreate):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WellnessSuggestion(BaseModel):
    action: str
    duration: str
    reasoning: str
    urgency: str  # low, medium, high

class WellnessInsights(BaseModel):
    suggestions: List[WellnessSuggestion]
    overall_assessment: str
    focus_area: str  # energy, mood, stress, balance
