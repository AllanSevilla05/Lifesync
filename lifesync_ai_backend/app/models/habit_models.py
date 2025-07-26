from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    frequency_type = Column(String, default="daily")  # daily, weekly, monthly
    frequency_value = Column(Integer, default=1)  # how many times per frequency_type
    target_duration = Column(Integer)  # in minutes
    category = Column(String)  # health, productivity, learning, etc.
    difficulty = Column(Integer, default=1)  # 1-5 scale
    streak_count = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    reminder_time = Column(String)  # HH:MM format
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")
    insights = relationship("HabitInsight", back_populates="habit", cascade="all, delete-orphan")

class HabitCompletion(Base):
    __tablename__ = "habit_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completion_date = Column(DateTime(timezone=True), server_default=func.now())
    duration_minutes = Column(Integer)  # actual time spent
    quality_rating = Column(Integer)  # 1-5 how well they did it
    notes = Column(Text)
    mood_before = Column(Integer)  # 1-10 scale
    mood_after = Column(Integer)  # 1-10 scale
    energy_before = Column(Integer)  # 1-10 scale
    energy_after = Column(Integer)  # 1-10 scale
    context = Column(JSON)  # location, weather, etc.
    
    # Relationships
    habit = relationship("Habit", back_populates="completions")

class HabitInsight(Base):
    __tablename__ = "habit_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    insight_type = Column(String)  # pattern, recommendation, achievement
    title = Column(String)
    description = Column(Text)
    data = Column(JSON)  # supporting data for the insight
    confidence_score = Column(Float, default=0.0)  # AI confidence in this insight
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    habit = relationship("Habit", back_populates="insights")

class UserBehaviorPattern(Base):
    __tablename__ = "user_behavior_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pattern_type = Column(String)  # productivity_peak, completion_time, difficulty_preference
    pattern_data = Column(JSON)  # the actual pattern data
    confidence_score = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class PersonalizationModel(Base):
    __tablename__ = "personalization_models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_type = Column(String)  # completion_predictor, difficulty_estimator, time_allocator
    model_data = Column(JSON)  # serialized model parameters
    accuracy_score = Column(Float, default=0.0)
    training_data_points = Column(Integer, default=0)
    last_trained = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")