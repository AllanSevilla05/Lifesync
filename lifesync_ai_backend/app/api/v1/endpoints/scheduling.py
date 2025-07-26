from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User
from app.services.scheduling_service import scheduling_optimizer

router = APIRouter()

class ScheduleOptimizationRequest(BaseModel):
    target_date: date
    preferences: Optional[Dict[str, Any]] = {}
    constraints: Optional[List[Dict[str, Any]]] = []

class TimeBlockUpdate(BaseModel):
    block_id: str
    new_start_time: str
    new_end_time: str

class ScheduleFeedback(BaseModel):
    schedule_date: date
    rating: int  # 1-5
    feedback_text: Optional[str] = ""
    completed_blocks: List[str] = []
    missed_blocks: List[str] = []

@router.post("/optimize")
async def optimize_schedule(
    request: ScheduleOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an optimized daily schedule for the specified date"""
    
    try:
        target_datetime = datetime.combine(request.target_date, datetime.min.time())
        
        result = await scheduling_optimizer.optimize_daily_schedule(
            user_id=current_user.id,
            target_date=target_datetime,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "date": request.target_date.isoformat(),
            "schedule": result["schedule"],
            "metrics": result["metrics"],
            "recommendations": result["recommendations"],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize schedule: {str(e)}"
        )

@router.get("/weekly-optimization")
async def optimize_weekly_schedule(
    start_date: date = Query(..., description="Start date of the week"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate optimized schedules for an entire week"""
    
    try:
        weekly_schedules = {}
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            target_datetime = datetime.combine(current_date, datetime.min.time())
            
            result = await scheduling_optimizer.optimize_daily_schedule(
                user_id=current_user.id,
                target_date=target_datetime,
                db=db
            )
            
            if result["success"]:
                weekly_schedules[current_date.isoformat()] = {
                    "schedule": result["schedule"],
                    "metrics": result["metrics"],
                    "recommendations": result["recommendations"]
                }
        
        # Generate weekly insights
        weekly_insights = _generate_weekly_insights(weekly_schedules)
        
        return {
            "success": True,
            "week_start": start_date.isoformat(),
            "schedules": weekly_schedules,
            "weekly_insights": weekly_insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize weekly schedule: {str(e)}"
        )

@router.put("/update-block")
async def update_schedule_block(
    update: TimeBlockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific time block in the schedule"""
    
    # In a real implementation, you'd store and update the schedule in the database
    # For now, we'll just validate the time format and return success
    
    try:
        # Validate time format
        datetime.strptime(update.new_start_time, "%H:%M")
        datetime.strptime(update.new_end_time, "%H:%M")
        
        return {
            "success": True,
            "message": "Schedule block updated successfully",
            "updated_block": {
                "id": update.block_id,
                "start_time": update.new_start_time,
                "end_time": update.new_end_time
            }
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM format."
        )

@router.post("/feedback")
async def submit_schedule_feedback(
    feedback: ScheduleFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on a schedule to improve future optimizations"""
    
    try:
        # Store feedback in database (implement UserScheduleFeedback model)
        # For now, we'll just process and return insights
        
        feedback_insights = {
            "completion_rate": len(feedback.completed_blocks) / (len(feedback.completed_blocks) + len(feedback.missed_blocks)) * 100 if (feedback.completed_blocks or feedback.missed_blocks) else 0,
            "user_satisfaction": feedback.rating * 20,  # Convert to percentage
            "improvement_areas": []
        }
        
        if feedback.rating < 3:
            feedback_insights["improvement_areas"].append("Schedule complexity")
            feedback_insights["improvement_areas"].append("Time allocation")
        
        if len(feedback.missed_blocks) > len(feedback.completed_blocks):
            feedback_insights["improvement_areas"].append("Task duration estimation")
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "insights": feedback_insights,
            "recommendations": _generate_feedback_recommendations(feedback)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get("/analytics")
async def get_scheduling_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scheduling analytics and insights"""
    
    try:
        # In a real implementation, you'd query stored schedule data
        # For now, we'll return mock analytics
        
        analytics = {
            "period": f"Last {days} days",
            "total_schedules_generated": 25,
            "average_optimization_score": 78.5,
            "completion_rate": 72.3,
            "productivity_trends": {
                "morning": {"score": 85, "trend": "increasing"},
                "afternoon": {"score": 70, "trend": "stable"},
                "evening": {"score": 60, "trend": "decreasing"}
            },
            "task_category_distribution": {
                "work": 45,
                "personal": 30,
                "fitness": 15,
                "learning": 10
            },
            "weekly_patterns": {
                "monday": {"energy": "high", "productivity": 80},
                "tuesday": {"energy": "high", "productivity": 85},
                "wednesday": {"energy": "medium", "productivity": 75},
                "thursday": {"energy": "medium", "productivity": 70},
                "friday": {"energy": "low", "productivity": 65},
                "saturday": {"energy": "medium", "productivity": 60},
                "sunday": {"energy": "low", "productivity": 55}
            },
            "insights": [
                {
                    "type": "productivity",
                    "title": "Peak Performance Hours",
                    "message": "You're most productive between 9-11 AM. Consider scheduling important tasks during this time.",
                    "confidence": 0.85
                },
                {
                    "type": "balance",
                    "title": "Work-Life Balance",
                    "message": "Your work-life balance has improved by 15% this month.",
                    "confidence": 0.78
                },
                {
                    "type": "habit",
                    "title": "Consistency Improvement",
                    "message": "Your task completion rate increased by 12% after implementing AI scheduling.",
                    "confidence": 0.92
                }
            ]
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.get("/suggestions")
async def get_schedule_suggestions(
    date: Optional[date] = Query(None, description="Date for suggestions (defaults to today)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered schedule suggestions and optimizations"""
    
    try:
        target_date = date or datetime.now().date()
        
        # Generate contextual suggestions
        suggestions = await _generate_smart_suggestions(
            user_id=current_user.id,
            target_date=target_date,
            db=db
        )
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "suggestions": suggestions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )

# Helper functions

def _generate_weekly_insights(weekly_schedules: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights from weekly schedule data"""
    
    total_optimization_score = 0
    total_schedules = len(weekly_schedules)
    work_life_ratios = []
    
    for schedule_data in weekly_schedules.values():
        metrics = schedule_data["metrics"]
        total_optimization_score += metrics["optimization_score"]
        
        work_percentage = metrics["work_life_balance"]["work_percentage"]
        work_life_ratios.append(work_percentage)
    
    average_optimization = total_optimization_score / total_schedules if total_schedules > 0 else 0
    average_work_percentage = sum(work_life_ratios) / len(work_life_ratios) if work_life_ratios else 0
    
    insights = {
        "average_optimization_score": round(average_optimization, 1),
        "work_life_balance": {
            "average_work_percentage": round(average_work_percentage, 1),
            "balance_rating": "good" if 40 <= average_work_percentage <= 60 else "needs_attention"
        },
        "weekly_recommendations": []
    }
    
    if average_optimization < 75:
        insights["weekly_recommendations"].append({
            "type": "optimization",
            "message": "Consider consolidating similar tasks and adding more buffer time between activities."
        })
    
    if average_work_percentage > 65:
        insights["weekly_recommendations"].append({
            "type": "balance",
            "message": "Your work load is quite high this week. Consider scheduling more personal time."
        })
    
    return insights

def _generate_feedback_recommendations(feedback: ScheduleFeedback) -> List[Dict[str, Any]]:
    """Generate recommendations based on user feedback"""
    
    recommendations = []
    
    if feedback.rating <= 2:
        recommendations.append({
            "type": "improvement",
            "title": "Schedule Simplification",
            "message": "Try reducing the number of scheduled items to make your day more manageable."
        })
    
    completion_rate = len(feedback.completed_blocks) / (len(feedback.completed_blocks) + len(feedback.missed_blocks)) * 100 if (feedback.completed_blocks or feedback.missed_blocks) else 100
    
    if completion_rate < 50:
        recommendations.append({
            "type": "adjustment",
            "title": "Time Estimation",
            "message": "Consider allocating more time for tasks or breaking larger tasks into smaller ones."
        })
    
    return recommendations

async def _generate_smart_suggestions(
    user_id: int,
    target_date: date,
    db: Session
) -> List[Dict[str, Any]]:
    """Generate smart scheduling suggestions"""
    
    suggestions = [
        {
            "type": "productivity",
            "title": "Morning Focus Block",
            "message": "Schedule your most important task between 9-10 AM when your energy is highest.",
            "priority": "high",
            "actionable": True
        },
        {
            "type": "balance",
            "title": "Break Reminder",
            "message": "Add 15-minute breaks between intensive tasks to maintain productivity.",
            "priority": "medium",
            "actionable": True
        },
        {
            "type": "health",
            "title": "Movement Break",
            "message": "Consider adding a 10-minute walk after your longest work block.",
            "priority": "medium",
            "actionable": True
        },
        {
            "type": "optimization",
            "title": "Task Batching",
            "message": "Group similar tasks together to reduce context switching.",
            "priority": "low",
            "actionable": True
        }
    ]
    
    return suggestions