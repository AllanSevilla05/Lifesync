from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User
from app.services.goals_service import goals_service

router = APIRouter()

class CreateGoalRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    goal_type: str = "personal"
    priority: str = "medium"
    target_value: Optional[float] = None
    unit: Optional[str] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    time_frame: str = "monthly"
    tags: Optional[List[str]] = []
    reminder_settings: Optional[Dict[str, Any]] = {}
    milestones: Optional[List[Dict[str, Any]]] = []

class UpdateProgressRequest(BaseModel):
    progress_value: float
    notes: Optional[str] = ""
    source: str = "manual"

class CreateReflectionRequest(BaseModel):
    reflection_text: str
    mood_rating: Optional[int] = None
    energy_rating: Optional[int] = None
    motivation_rating: Optional[int] = None
    challenges: Optional[List[str]] = []
    wins: Optional[List[str]] = []
    lessons_learned: Optional[str] = ""
    next_actions: Optional[List[str]] = []

@router.post("/")
async def create_goal(
    request: CreateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new SMART goal with AI assistance"""
    
    try:
        goal_data = request.model_dump()
        result = await goals_service.create_smart_goal(goal_data, current_user.id, db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "goal": result["goal"],
            "smart_score": result["smart_score"],
            "ai_suggestions": result["suggestions"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create goal: {str(e)}"
        )

@router.get("/")
async def get_goals(
    status: Optional[str] = Query(None, description="Filter by status"),
    goal_type: Optional[str] = Query(None, description="Filter by goal type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's goals with optional filtering"""
    
    try:
        goals = goals_service.get_user_goals(
            user_id=current_user.id,
            status_filter=status,
            goal_type_filter=goal_type,
            db=db
        )
        
        return {
            "success": True,
            "goals": goals,
            "total_count": len(goals)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goals: {str(e)}"
        )

@router.get("/{goal_id}")
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal with detailed information"""
    
    try:
        from app.models.goal_models import Goal, GoalProgress, GoalMilestone, GoalReflection
        from sqlalchemy import and_
        
        goal = db.query(Goal).filter(
            and_(Goal.id == goal_id, Goal.user_id == current_user.id)
        ).first()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        # Get progress history
        progress_history = db.query(GoalProgress).filter(
            GoalProgress.goal_id == goal_id
        ).order_by(GoalProgress.logged_at.desc()).limit(20).all()
        
        # Get milestones
        milestones = db.query(GoalMilestone).filter(
            GoalMilestone.goal_id == goal_id
        ).order_by(GoalMilestone.order_index).all()
        
        # Get recent reflections
        reflections = db.query(GoalReflection).filter(
            GoalReflection.goal_id == goal_id
        ).order_by(GoalReflection.created_at.desc()).limit(5).all()
        
        goal_data = goals_service._format_goal_response(goal)
        goal_data.update({
            "progress_history": [
                {
                    "id": p.id,
                    "progress_value": p.progress_value,
                    "progress_percentage": p.progress_percentage,
                    "notes": p.notes,
                    "logged_at": p.logged_at.isoformat(),
                    "source": p.source
                }
                for p in progress_history
            ],
            "milestones": [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.description,
                    "target_value": m.target_value,
                    "target_date": m.target_date.isoformat() if m.target_date else None,
                    "is_completed": m.is_completed,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                    "order_index": m.order_index
                }
                for m in milestones
            ],
            "recent_reflections": [
                {
                    "id": r.id,
                    "reflection_text": r.reflection_text,
                    "mood_rating": r.mood_rating,
                    "energy_rating": r.energy_rating,
                    "motivation_rating": r.motivation_rating,
                    "created_at": r.created_at.isoformat()
                }
                for r in reflections
            ]
        })
        
        return {"success": True, "goal": goal_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal: {str(e)}"
        )

@router.post("/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    request: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a specific goal"""
    
    try:
        progress_data = request.model_dump()
        result = await goals_service.update_goal_progress(
            goal_id, progress_data, current_user.id, db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "progress": result["progress"],
            "message": "Progress updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )

@router.post("/{goal_id}/reflections")
async def create_goal_reflection(
    goal_id: int,
    request: CreateReflectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a reflection entry for a goal"""
    
    try:
        reflection_data = request.model_dump()
        result = await goals_service.create_goal_reflection(
            goal_id, reflection_data, current_user.id, db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "reflection_id": result["reflection_id"],
            "message": "Reflection created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reflection: {str(e)}"
        )

@router.put("/{goal_id}/status")
async def update_goal_status(
    goal_id: int,
    status_update: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal status (active, paused, completed, cancelled)"""
    
    try:
        from app.models.goal_models import Goal, GoalStatus
        from sqlalchemy import and_
        
        goal = db.query(Goal).filter(
            and_(Goal.id == goal_id, Goal.user_id == current_user.id)
        ).first()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        new_status = status_update.get("status")
        if new_status not in [s.value for s in GoalStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        goal.status = GoalStatus(new_status)
        
        # Set completion percentage to 100% if completed
        if new_status == "completed":
            goal.completion_percentage = 100.0
            goal.current_value = goal.target_value or goal.current_value
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Goal status updated to {new_status}",
            "goal": goals_service._format_goal_response(goal)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update goal status: {str(e)}"
        )

@router.get("/recommendations/personalized")
async def get_goal_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized goal recommendations based on user patterns"""
    
    try:
        recommendations = await goals_service.generate_goal_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/analytics/overview")
async def get_goals_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive goals analytics"""
    
    try:
        from app.models.goal_models import Goal, GoalProgress, GoalStatus, GoalType
        from sqlalchemy import func
        from datetime import timedelta
        
        # Basic statistics
        total_goals = db.query(Goal).filter(Goal.user_id == current_user.id).count()
        active_goals = db.query(Goal).filter(
            and_(Goal.user_id == current_user.id, Goal.status == GoalStatus.ACTIVE)
        ).count()
        completed_goals = db.query(Goal).filter(
            and_(Goal.user_id == current_user.id, Goal.status == GoalStatus.COMPLETED)
        ).count()
        
        # Completion rate by type
        goal_type_stats = db.query(
            Goal.goal_type,
            func.count(Goal.id).label('total'),
            func.sum(func.case([(Goal.status == GoalStatus.COMPLETED, 1)], else_=0)).label('completed')
        ).filter(Goal.user_id == current_user.id).group_by(Goal.goal_type).all()
        
        type_completion_rates = {}
        for stat in goal_type_stats:
            total = stat.total
            completed = stat.completed or 0
            type_completion_rates[stat.goal_type.value] = {
                "total": total,
                "completed": completed,
                "completion_rate": (completed / total * 100) if total > 0 else 0
            }
        
        # Recent progress trend
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_progress = db.query(GoalProgress).join(Goal).filter(
            and_(
                Goal.user_id == current_user.id,
                GoalProgress.logged_at >= cutoff_date
            )
        ).order_by(GoalProgress.logged_at).all()
        
        progress_trend = []
        for progress in recent_progress[-20:]:  # Last 20 entries
            progress_trend.append({
                "date": progress.logged_at.isoformat(),
                "value": progress.progress_value,
                "percentage": progress.progress_percentage
            })
        
        # Average SMART scores
        goals_with_smart = db.query(Goal).filter(
            and_(
                Goal.user_id == current_user.id,
                Goal.smart_analysis.isnot(None)
            )
        ).all()
        
        avg_smart_score = 0
        if goals_with_smart:
            smart_scores = [
                g.smart_analysis.get("overall_score", 0) 
                for g in goals_with_smart 
                if g.smart_analysis
            ]
            avg_smart_score = sum(smart_scores) / len(smart_scores) if smart_scores else 0
        
        analytics = {
            "overview": {
                "total_goals": total_goals,
                "active_goals": active_goals,
                "completed_goals": completed_goals,
                "completion_rate": (completed_goals / total_goals * 100) if total_goals > 0 else 0,
                "average_smart_score": round(avg_smart_score, 1)
            },
            "goal_types": type_completion_rates,
            "progress_trend": progress_trend,
            "insights": [
                {
                    "type": "performance",
                    "title": "Goal Completion Rate",
                    "value": f"{(completed_goals / total_goals * 100) if total_goals > 0 else 0:.1f}%",
                    "trend": "positive" if completed_goals > 0 else "neutral"
                },
                {
                    "type": "focus",
                    "title": "Active Goals",
                    "value": str(active_goals),
                    "trend": "neutral" if active_goals <= 3 else "warning"
                }
            ]
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.post("/{goal_id}/milestones/{milestone_id}/complete")
async def complete_milestone(
    goal_id: int,
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a milestone as completed"""
    
    try:
        from app.models.goal_models import Goal, GoalMilestone
        from sqlalchemy import and_
        
        # Verify goal ownership
        goal = db.query(Goal).filter(
            and_(Goal.id == goal_id, Goal.user_id == current_user.id)
        ).first()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        milestone = db.query(GoalMilestone).filter(
            and_(
                GoalMilestone.id == milestone_id,
                GoalMilestone.goal_id == goal_id
            )
        ).first()
        
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
        
        milestone.is_completed = True
        milestone.completed_at = datetime.utcnow()
        
        # Update goal progress if milestone has target value
        if milestone.target_value and goal.target_value:
            progress_increase = (milestone.target_value / goal.target_value) * 100
            goal.completion_percentage = min(100, goal.completion_percentage + progress_increase)
            goal.current_value = min(goal.target_value, goal.current_value + milestone.target_value)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Milestone completed successfully",
            "milestone": {
                "id": milestone.id,
                "title": milestone.title,
                "completed_at": milestone.completed_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete milestone: {str(e)}"
        )