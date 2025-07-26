from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User
from app.models.collaboration_models import SharePermission, ShareStatus
from app.services.collaboration_service import collaboration_service

router = APIRouter()

# Request Models
class CreateTeamRequest(BaseModel):
    name: str
    description: str = ""

class JoinTeamRequest(BaseModel):
    team_code: str

class InviteUserRequest(BaseModel):
    email: EmailStr
    permission: SharePermission = SharePermission.VIEW
    message: str = ""

class ShareTaskRequest(BaseModel):
    task_id: int
    team_id: Optional[int] = None
    user_id: Optional[int] = None
    permission: SharePermission = SharePermission.VIEW
    message: str = ""
    expires_hours: Optional[int] = None

class AddCommentRequest(BaseModel):
    content: str

# Team Management Endpoints
@router.post("/teams")
async def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    try:
        team = await collaboration_service.create_team(
            name=request.name,
            description=request.description,
            owner_id=current_user.id,
            db=db
        )
        return {
            "success": True,
            "team": {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "team_code": team.team_code,
                "created_at": team.created_at
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/teams/join")
async def join_team(
    request: JoinTeamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a team using team code"""
    try:
        result = await collaboration_service.join_team_by_code(
            team_code=request.team_code,
            user_id=current_user.id,
            db=db
        )
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/teams")
async def get_user_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all teams the current user is a member of"""
    try:
        teams = collaboration_service.get_user_teams(current_user.id, db)
        return {"success": True, "teams": teams}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/teams/{team_id}/invite")
async def invite_user_to_team(
    team_id: int,
    request: InviteUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a user to join a team"""
    try:
        result = await collaboration_service.invite_user_to_team(
            team_id=team_id,
            inviter_id=current_user.id,
            email=request.email,
            permission=request.permission,
            message=request.message,
            db=db
        )
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Task Sharing Endpoints
@router.post("/share-task")
async def share_task(
    request: ShareTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a task with a team or individual user"""
    try:
        result = await collaboration_service.share_task(
            task_id=request.task_id,
            sharer_id=current_user.id,
            db=db,
            team_id=request.team_id,
            user_id=request.user_id,
            permission=request.permission,
            message=request.message,
            expires_hours=request.expires_hours
        )
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/shared-tasks")
async def get_shared_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks shared with the current user"""
    try:
        shared_tasks = collaboration_service.get_shared_tasks(current_user.id, db)
        return {"success": True, "shared_tasks": shared_tasks}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/tasks/{task_id}/access")
async def check_task_access(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check user's access permissions for a specific task"""
    try:
        access_info = collaboration_service.check_task_access(task_id, current_user.id, db)
        return {"success": True, "access": access_info}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Comment System Endpoints
@router.post("/shared-tasks/{shared_task_id}/comments")
async def add_task_comment(
    shared_task_id: int,
    request: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a shared task"""
    try:
        result = await collaboration_service.add_task_comment(
            shared_task_id=shared_task_id,
            user_id=current_user.id,
            content=request.content,
            db=db
        )
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/shared-tasks/{shared_task_id}/comments")
async def get_task_comments(
    shared_task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a shared task"""
    try:
        # First check if user has access to this shared task
        from app.models.collaboration_models import SharedTask, TeamMember
        from sqlalchemy import and_, or_
        
        shared_task = db.query(SharedTask).filter(
            SharedTask.id == shared_task_id
        ).first()
        
        if not shared_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared task not found"
            )
        
        # Check access permissions
        has_access = False
        if shared_task.shared_with_user_id == current_user.id:
            has_access = True
        elif shared_task.team_id:
            member = db.query(TeamMember).filter(
                and_(
                    TeamMember.team_id == shared_task.team_id,
                    TeamMember.user_id == current_user.id,
                    TeamMember.status == ShareStatus.ACCEPTED
                )
            ).first()
            has_access = member is not None
        elif shared_task.shared_by == current_user.id:
            has_access = True
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view comments on this task"
            )
        
        # Get comments with author information
        from app.models.collaboration_models import TaskComment
        comments_query = db.query(TaskComment, User).join(
            User, TaskComment.user_id == User.id
        ).filter(
            TaskComment.shared_task_id == shared_task_id
        ).order_by(TaskComment.created_at.asc()).all()
        
        comments = []
        for comment, author in comments_query:
            comments.append({
                "id": comment.id,
                "content": comment.content,
                "is_edited": comment.is_edited,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "author": {
                    "id": author.id,
                    "full_name": author.full_name,
                    "email": author.email
                }
            })
        
        return {"success": True, "comments": comments}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )