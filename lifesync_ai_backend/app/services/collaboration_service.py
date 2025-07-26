import secrets
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.models import User, Task
from app.models.collaboration_models import (
    Team, TeamMember, SharedTask, SharedGoal, TaskComment, TeamActivityLog,
    CollaborationInvite, UserCollaborationSettings, SharePermission, ShareStatus
)

class CollaborationService:
    """Service for handling all collaboration features"""
    
    def __init__(self):
        self.invite_code_length = 8
        self.default_invite_expiry_hours = 72
    
    # Team Management
    async def create_team(self, name: str, description: str, owner_id: int, db: Session) -> Team:
        """Create a new team"""
        team_code = self._generate_unique_code(db, 'team')
        
        team = Team(
            name=name,
            description=description,
            owner_id=owner_id,
            team_code=team_code,
            settings={
                'allow_member_invites': True,
                'require_approval_for_joins': False,
                'default_member_permission': SharePermission.VIEW.value
            }
        )
        
        db.add(team)
        db.flush()  # Get the team ID
        
        # Add owner as admin member
        owner_member = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role=SharePermission.ADMIN,
            status=ShareStatus.ACCEPTED,
            joined_at=datetime.utcnow()
        )
        
        db.add(owner_member)
        
        # Log team creation
        await self._log_team_activity(
            team.id, owner_id, "team_created", "team", team.id,
            {"team_name": name}, db
        )
        
        db.commit()
        db.refresh(team)
        return team
    
    async def join_team_by_code(self, team_code: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Join a team using team code"""
        team = db.query(Team).filter(
            Team.team_code == team_code,
            Team.is_active == True
        ).first()
        
        if not team:
            return {"success": False, "error": "Invalid team code"}
        
        # Check if user is already a member
        existing_member = db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id
            )
        ).first()
        
        if existing_member:
            if existing_member.status == ShareStatus.ACCEPTED:
                return {"success": False, "error": "You are already a member of this team"}
            elif existing_member.status == ShareStatus.PENDING:
                return {"success": False, "error": "Your membership request is pending approval"}
        
        # Create membership
        member_status = ShareStatus.ACCEPTED
        if team.settings.get('require_approval_for_joins', False):
            member_status = ShareStatus.PENDING
        
        member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role=SharePermission(team.settings.get('default_member_permission', 'view')),
            status=member_status,
            joined_at=datetime.utcnow() if member_status == ShareStatus.ACCEPTED else None
        )
        
        db.add(member)
        
        # Log activity
        await self._log_team_activity(
            team.id, user_id, "user_joined", "team", team.id,
            {"status": member_status.value}, db
        )
        
        db.commit()
        
        return {
            "success": True,
            "team": team,
            "status": member_status.value,
            "message": "Successfully joined team" if member_status == ShareStatus.ACCEPTED else "Membership request sent for approval"
        }
    
    async def invite_user_to_team(self, team_id: int, inviter_id: int, email: str, 
                                  permission: SharePermission, message: str, db: Session) -> Dict[str, Any]:
        """Invite a user to join a team"""
        
        # Check if inviter has permission to invite
        inviter_member = db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == inviter_id,
                TeamMember.status == ShareStatus.ACCEPTED,
                TeamMember.role.in_([SharePermission.ADMIN, SharePermission.EDIT])
            )
        ).first()
        
        if not inviter_member:
            return {"success": False, "error": "You don't have permission to invite users to this team"}
        
        # Generate invite code
        invite_code = self._generate_unique_code(db, 'invite')
        expires_at = datetime.utcnow() + timedelta(hours=self.default_invite_expiry_hours)
        
        invite = CollaborationInvite(
            invite_code=invite_code,
            invited_by=inviter_id,
            invited_email=email,
            entity_type="team",
            entity_id=team_id,
            permission=permission,
            message=message,
            expires_at=expires_at
        )
        
        db.add(invite)
        
        # Log activity
        await self._log_team_activity(
            team_id, inviter_id, "user_invited", "team", team_id,
            {"invited_email": email, "permission": permission.value}, db
        )
        
        db.commit()
        
        return {
            "success": True,
            "invite_code": invite_code,
            "expires_at": expires_at,
            "message": "Invitation sent successfully"
        }
    
    # Task Sharing
    async def share_task(self, task_id: int, sharer_id: int, db: Session,
                        team_id: Optional[int] = None, user_id: Optional[int] = None,
                        permission: SharePermission = SharePermission.VIEW,
                        message: str = "", expires_hours: Optional[int] = None) -> Dict[str, Any]:
        """Share a task with a team or individual user"""
        
        # Verify task ownership
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == sharer_id)
        ).first()
        
        if not task:
            return {"success": False, "error": "Task not found or you don't have permission to share it"}
        
        if not team_id and not user_id:
            return {"success": False, "error": "Must specify either team_id or user_id"}
        
        # Check for existing share
        existing_share = db.query(SharedTask).filter(
            and_(
                SharedTask.task_id == task_id,
                SharedTask.team_id == team_id if team_id else None,
                SharedTask.shared_with_user_id == user_id if user_id else None,
                SharedTask.status != ShareStatus.REVOKED
            )
        ).first()
        
        if existing_share:
            return {"success": False, "error": "Task is already shared with this recipient"}
        
        expires_at = None
        if expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        shared_task = SharedTask(
            task_id=task_id,
            team_id=team_id,
            shared_with_user_id=user_id,
            shared_by=sharer_id,
            permission=permission,
            status=ShareStatus.ACCEPTED,  # Direct shares are automatically accepted
            message=message,
            expires_at=expires_at
        )
        
        db.add(shared_task)
        
        # Log activity
        if team_id:
            await self._log_team_activity(
                team_id, sharer_id, "task_shared", "task", task_id,
                {"task_title": task.title, "permission": permission.value}, db
            )
        
        db.commit()
        
        return {
            "success": True,
            "shared_task_id": shared_task.id,
            "message": "Task shared successfully"
        }
    
    async def add_task_comment(self, shared_task_id: int, user_id: int, 
                              content: str, db: Session) -> Dict[str, Any]:
        """Add a comment to a shared task"""
        
        # Verify user has access to the shared task
        shared_task = db.query(SharedTask).filter(
            SharedTask.id == shared_task_id
        ).first()
        
        if not shared_task:
            return {"success": False, "error": "Shared task not found"}
        
        # Check permissions
        has_access = False
        
        if shared_task.shared_with_user_id == user_id:
            has_access = True
        elif shared_task.team_id:
            member = db.query(TeamMember).filter(
                and_(
                    TeamMember.team_id == shared_task.team_id,
                    TeamMember.user_id == user_id,
                    TeamMember.status == ShareStatus.ACCEPTED
                )
            ).first()
            has_access = member is not None
        elif shared_task.shared_by == user_id:
            has_access = True
        
        if not has_access:
            return {"success": False, "error": "You don't have permission to comment on this task"}
        
        comment = TaskComment(
            shared_task_id=shared_task_id,
            user_id=user_id,
            content=content
        )
        
        db.add(comment)
        
        # Log activity if it's a team task
        if shared_task.team_id:
            await self._log_team_activity(
                shared_task.team_id, user_id, "comment_added", "task", shared_task.task_id,
                {"comment_preview": content[:50] + "..." if len(content) > 50 else content}, db
            )
        
        db.commit()
        db.refresh(comment)
        
        return {
            "success": True,
            "comment": comment,
            "message": "Comment added successfully"
        }
    
    # Access Control
    def check_task_access(self, task_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """Check if user has access to a task and what permission level"""
        
        # Check if user owns the task
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        
        if task:
            return {
                "has_access": True,
                "permission": SharePermission.ADMIN,
                "is_owner": True
            }
        
        # Check shared tasks
        shared_task = db.query(SharedTask).filter(
            and_(
                SharedTask.task_id == task_id,
                SharedTask.status == ShareStatus.ACCEPTED,
                or_(
                    SharedTask.shared_with_user_id == user_id,
                    SharedTask.team_id.in_(
                        db.query(TeamMember.team_id).filter(
                            and_(
                                TeamMember.user_id == user_id,
                                TeamMember.status == ShareStatus.ACCEPTED
                            )
                        )
                    )
                )
            )
        ).first()
        
        if shared_task:
            # Check if share has expired
            if shared_task.expires_at and shared_task.expires_at < datetime.utcnow():
                return {"has_access": False, "reason": "Share has expired"}
            
            return {
                "has_access": True,
                "permission": shared_task.permission,
                "is_owner": False,
                "shared_task_id": shared_task.id
            }
        
        return {"has_access": False, "reason": "No access found"}
    
    def get_user_teams(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get all teams a user is a member of"""
        
        teams_query = db.query(Team, TeamMember).join(
            TeamMember, Team.id == TeamMember.team_id
        ).filter(
            and_(
                TeamMember.user_id == user_id,
                TeamMember.status == ShareStatus.ACCEPTED,
                Team.is_active == True
            )
        ).all()
        
        teams = []
        for team, membership in teams_query:
            member_count = db.query(TeamMember).filter(
                and_(
                    TeamMember.team_id == team.id,
                    TeamMember.status == ShareStatus.ACCEPTED
                )
            ).count()
            
            teams.append({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "team_code": team.team_code,
                "member_count": member_count,
                "user_role": membership.role.value,
                "is_owner": team.owner_id == user_id,
                "created_at": team.created_at
            })
        
        return teams
    
    def get_shared_tasks(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get all tasks shared with a user"""
        
        shared_tasks_query = db.query(SharedTask, Task, User).join(
            Task, SharedTask.task_id == Task.id
        ).join(
            User, SharedTask.shared_by == User.id
        ).filter(
            and_(
                or_(
                    SharedTask.shared_with_user_id == user_id,
                    SharedTask.team_id.in_(
                        db.query(TeamMember.team_id).filter(
                            and_(
                                TeamMember.user_id == user_id,
                                TeamMember.status == ShareStatus.ACCEPTED
                            )
                        )
                    )
                ),
                SharedTask.status == ShareStatus.ACCEPTED,
                or_(
                    SharedTask.expires_at.is_(None),
                    SharedTask.expires_at > datetime.utcnow()
                )
            )
        ).all()
        
        shared_tasks = []
        for shared_task, task, sharer in shared_tasks_query:
            # Get comment count
            comment_count = db.query(TaskComment).filter(
                TaskComment.shared_task_id == shared_task.id
            ).count()
            
            shared_tasks.append({
                "shared_task_id": shared_task.id,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date,
                    "priority": task.priority,
                    "status": task.status
                },
                "shared_by": {
                    "id": sharer.id,
                    "full_name": sharer.full_name,
                    "email": sharer.email
                },
                "permission": shared_task.permission.value,
                "message": shared_task.message,
                "comment_count": comment_count,
                "shared_at": shared_task.created_at,
                "expires_at": shared_task.expires_at
            })
        
        return shared_tasks
    
    # Utility Methods
    def _generate_unique_code(self, db: Session, code_type: str) -> str:
        """Generate a unique code for teams or invites"""
        
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(self.invite_code_length))
            
            if code_type == 'team':
                existing = db.query(Team).filter(Team.team_code == code).first()
            else:  # invite
                existing = db.query(CollaborationInvite).filter(
                    CollaborationInvite.invite_code == code
                ).first()
            
            if not existing:
                return code
    
    async def _log_team_activity(self, team_id: int, user_id: int, action_type: str,
                                entity_type: str, entity_id: int, details: Dict[str, Any],
                                db: Session):
        """Log activity for team activity feed"""
        
        activity = TeamActivityLog(
            team_id=team_id,
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        
        db.add(activity)

# Global collaboration service instance
collaboration_service = CollaborationService()