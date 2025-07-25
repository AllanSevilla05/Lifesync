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
