from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class SharePermission(str, enum.Enum):
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"

class ShareStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_code = Column(String, unique=True, index=True)  # For easy team joining
    is_active = Column(Boolean, default=True)
    settings = Column(JSON)  # Team-specific settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    shared_tasks = relationship("SharedTask", back_populates="team", cascade="all, delete-orphan")
    shared_goals = relationship("SharedGoal", back_populates="team", cascade="all, delete-orphan")
    activity_logs = relationship("TeamActivityLog", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(SharePermission), default=SharePermission.VIEW)
    status = Column(Enum(ShareStatus), default=ShareStatus.PENDING)
    invited_by = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime(timezone=True))
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

class SharedTask(Base):
    __tablename__ = "shared_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    shared_with_user_id = Column(Integer, ForeignKey("users.id"))  # For direct user sharing
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(Enum(SharePermission), default=SharePermission.VIEW)
    status = Column(Enum(ShareStatus), default=ShareStatus.PENDING)
    message = Column(Text)  # Optional message from sharer
    expires_at = Column(DateTime(timezone=True))  # Optional expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task")
    team = relationship("Team", back_populates="shared_tasks")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id])
    sharer = relationship("User", foreign_keys=[shared_by])
    comments = relationship("TaskComment", back_populates="shared_task", cascade="all, delete-orphan")

class SharedGoal(Base):
    __tablename__ = "shared_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    shared_with_user_id = Column(Integer, ForeignKey("users.id"))
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(Enum(SharePermission), default=SharePermission.VIEW)
    status = Column(Enum(ShareStatus), default=ShareStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="shared_goals")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id])
    sharer = relationship("User", foreign_keys=[shared_by])

class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    shared_task_id = Column(Integer, ForeignKey("shared_tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    shared_task = relationship("SharedTask", back_populates="comments")
    author = relationship("User")

class TeamActivityLog(Base):
    __tablename__ = "team_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # joined, left, shared_task, completed_task, etc.
    entity_type = Column(String)  # task, goal, team
    entity_id = Column(Integer)
    details = Column(JSON)  # Additional context about the action
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="activity_logs")
    user = relationship("User")

class CollaborationInvite(Base):
    __tablename__ = "collaboration_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    invite_code = Column(String, unique=True, index=True)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_email = Column(String)
    entity_type = Column(String)  # team, task, goal
    entity_id = Column(Integer)
    permission = Column(Enum(SharePermission), default=SharePermission.VIEW)
    message = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    used_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inviter = relationship("User", foreign_keys=[invited_by])
    recipient = relationship("User", foreign_keys=[used_by])

class UserCollaborationSettings(Base):
    __tablename__ = "user_collaboration_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    allow_task_sharing = Column(Boolean, default=True)
    allow_team_invites = Column(Boolean, default=True)
    default_share_permission = Column(Enum(SharePermission), default=SharePermission.VIEW)
    notification_preferences = Column(JSON)  # What collaboration events to get notified about
    privacy_settings = Column(JSON)  # What info to share with collaborators
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")