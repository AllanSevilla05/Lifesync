from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: int
    is_active: bool
    onboarding_completed: bool
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class OnboardingData(BaseModel):
    wake_time: str
    sleep_time: str
    work_hours_start: str
    work_hours_end: str
    productivity_peak: str  # morning, afternoon, evening, night
    preferred_break_duration: int  # minutes
    fitness_goals: Optional[str] = None
    work_style: str  # focused, flexible, structured
    notification_preferences: Dict[str, bool]
