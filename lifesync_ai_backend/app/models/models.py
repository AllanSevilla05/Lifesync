from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    onboarding_completed = Column(Boolean, default=False)
    preferences = Column(JSON)  # User preferences and settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="owner")
    mood_entries = relationship("MoodEntry", back_populates="user")
    documents = relationship("Document", back_populates="user")
    habits = relationship("Habit", back_populates="owner")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime(timezone=True))
    priority = Column(Integer, default=1)  # 1-5 scale
    status = Column(String, default="pending")  # pending, in_progress, completed
    estimated_duration = Column(Integer)  # in minutes
    actual_duration = Column(Integer)
    ai_suggested_time = Column(DateTime(timezone=True))
    completion_percentage = Column(Float, default=0.0)
    tags = Column(JSON)  # Array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="tasks")
    check_ins = relationship("TaskCheckIn", back_populates="task")

class TaskCheckIn(Base):
    __tablename__ = "task_check_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_response = Column(String)  # started, completed, delayed, etc.
    notes = Column(Text)
    mood_at_checkin = Column(Integer)  # 1-10
    energy_at_checkin = Column(Integer)  # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="check_ins")

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_level = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer, nullable=False)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    notes = Column(Text)
    tags = Column(JSON)  # Array of mood/activity tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mood_entries")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    document_type = Column(String)  # syllabus, schedule, notes, etc.
    processed = Column(Boolean, default=False)
    extracted_content = Column(Text)
    extracted_tasks = Column(JSON)  # Array of extracted tasks
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="documents")

class AIInteraction(Base):
    __tablename__ = "ai_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String)  # task_suggestion, schedule_optimization, voice_command
    input_data = Column(JSON)
    ai_response = Column(JSON)
    feedback_score = Column(Integer)  # User feedback on AI suggestion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
