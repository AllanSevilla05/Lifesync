from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class GoalType(str, enum.Enum):
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    HEALTH = "health"
    FINANCIAL = "financial"
    LEARNING = "learning"
    RELATIONSHIP = "relationship"
    CREATIVE = "creative"

class GoalStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class GoalPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TimeFrame(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    goal_type = Column(Enum(GoalType), default=GoalType.PERSONAL)
    status = Column(Enum(GoalStatus), default=GoalStatus.DRAFT)
    priority = Column(Enum(GoalPriority), default=GoalPriority.MEDIUM)
    
    # SMART goal criteria
    target_value = Column(Float)  # Measurable target
    current_value = Column(Float, default=0.0)  # Current progress
    unit = Column(String)  # Unit of measurement (hours, pages, pounds, etc.)
    
    # Time-bound criteria
    start_date = Column(DateTime(timezone=True))
    target_date = Column(DateTime(timezone=True))
    time_frame = Column(Enum(TimeFrame), default=TimeFrame.MONTHLY)
    
    # AI-enhanced features
    ai_suggestions = Column(JSON)  # AI-generated suggestions for achieving the goal
    smart_analysis = Column(JSON)  # SMART criteria analysis
    predicted_completion = Column(DateTime(timezone=True))  # AI prediction
    difficulty_score = Column(Float)  # 1-10 difficulty rating
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata
    tags = Column(JSON)  # Array of tags
    reminder_settings = Column(JSON)  # Reminder preferences
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")
    progress_logs = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")
    reflections = relationship("GoalReflection", back_populates="goal", cascade="all, delete-orphan")

class GoalMilestone(Base):
    __tablename__ = "goal_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    target_value = Column(Float)
    target_date = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    goal = relationship("Goal", back_populates="milestones")

class GoalProgress(Base):
    __tablename__ = "goal_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    progress_value = Column(Float, nullable=False)
    progress_percentage = Column(Float)
    notes = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Progress metadata
    source = Column(String)  # manual, automatic, integration
    data_source = Column(JSON)  # Source-specific data
    
    # Relationships
    goal = relationship("Goal", back_populates="progress_logs")

class GoalReflection(Base):
    __tablename__ = "goal_reflections"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    reflection_text = Column(Text, nullable=False)
    mood_rating = Column(Integer)  # 1-10 scale
    energy_rating = Column(Integer)  # 1-10 scale
    motivation_rating = Column(Integer)  # 1-10 scale
    challenges = Column(JSON)  # Array of challenges faced
    wins = Column(JSON)  # Array of wins/achievements
    lessons_learned = Column(Text)
    next_actions = Column(JSON)  # Array of next actions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    goal = relationship("Goal", back_populates="reflections")

class GoalTemplate(Base):
    __tablename__ = "goal_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    goal_type = Column(Enum(GoalType))
    template_data = Column(JSON)  # Template structure
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User")

class GoalInsight(Base):
    __tablename__ = "goal_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"))
    insight_type = Column(String, nullable=False)  # pattern, prediction, recommendation
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0-1 confidence level
    data_points = Column(JSON)  # Supporting data
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    goal = relationship("Goal")

# Add to User model relationship (in models.py)
# goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")