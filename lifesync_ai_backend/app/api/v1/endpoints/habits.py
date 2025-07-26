from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.models.models import User
from app.models.habit_models import Habit, HabitCompletion, HabitInsight, UserBehaviorPattern
from app.schemas.habits import (
    HabitCreate, HabitUpdate, Habit as HabitSchema,
    HabitCompletionCreate, HabitCompletion as HabitCompletionSchema,
    HabitInsight as HabitInsightSchema
)
from app.api.v1.endpoints.auth import get_current_user
from app.services.habit_learning import habit_learning_engine

router = APIRouter()

@router.post("/", response_model=HabitSchema)
async def create_habit(
    habit: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit"""
    db_habit = Habit(**habit.model_dump(), user_id=current_user.id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@router.get("/", response_model=List[HabitSchema])
async def get_habits(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all habits for the current user"""
    query = db.query(Habit).filter(Habit.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Habit.is_active == True)
    
    habits = query.order_by(Habit.created_at.desc()).all()
    return habits

@router.get("/{habit_id}", response_model=HabitSchema)
async def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return habit

@router.put("/{habit_id}", response_model=HabitSchema)
async def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    update_data = habit_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}

@router.post("/{habit_id}/complete", response_model=HabitCompletionSchema)
async def complete_habit(
    habit_id: int,
    completion: HabitCompletionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a habit as completed"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Create completion record
    db_completion = HabitCompletion(**completion.model_dump(), habit_id=habit_id)
    db.add(db_completion)
    
    # Update habit statistics
    habit.total_completions += 1
    
    # Update streak
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check if there was a completion yesterday
    yesterday_completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completion_date >= datetime.combine(yesterday, datetime.min.time()),
        HabitCompletion.completion_date < datetime.combine(today, datetime.min.time())
    ).first()
    
    # Check if there's already a completion today
    today_completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completion_date >= datetime.combine(today, datetime.min.time())
    ).first()
    
    if not today_completion:  # First completion today
        if yesterday_completion or habit.streak_count == 0:
            habit.streak_count += 1
        else:
            habit.streak_count = 1  # Reset streak if gap found
        
        # Update longest streak
        if habit.streak_count > habit.longest_streak:
            habit.longest_streak = habit.streak_count
    
    db.commit()
    db.refresh(db_completion)
    
    # Schedule background learning analysis
    background_tasks.add_task(
        habit_learning_engine.analyze_user_patterns,
        current_user.id,
        db
    )
    
    return db_completion

@router.get("/{habit_id}/completions", response_model=List[HabitCompletionSchema])
async def get_habit_completions(
    habit_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get completion history for a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completion_date >= start_date
    ).order_by(HabitCompletion.completion_date.desc()).all()
    
    return completions

@router.get("/{habit_id}/insights", response_model=List[HabitInsightSchema])
async def get_habit_insights(
    habit_id: int,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated insights for a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    query = db.query(HabitInsight).filter(HabitInsight.habit_id == habit_id)
    
    if unread_only:
        query = query.filter(HabitInsight.is_read == False)
    
    insights = query.order_by(HabitInsight.created_at.desc()).all()
    return insights

@router.put("/insights/{insight_id}/read")
async def mark_insight_read(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an insight as read"""
    insight = db.query(HabitInsight).join(Habit).filter(
        HabitInsight.id == insight_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_read = True
    db.commit()
    
    return {"message": "Insight marked as read"}

@router.get("/analytics/overview")
async def get_habit_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall habit analytics for the user"""
    
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    if not habits:
        return {
            "total_habits": 0,
            "active_streaks": 0,
            "average_completion_rate": 0,
            "longest_streak": 0,
            "total_completions_this_week": 0
        }
    
    # Calculate overall statistics
    total_habits = len(habits)
    active_streaks = len([h for h in habits if h.streak_count > 0])
    longest_streak = max([h.longest_streak for h in habits])
    
    # Calculate completion rates
    completion_rates = []
    for habit in habits:
        days_since_creation = (datetime.utcnow() - habit.created_at).days + 1
        expected = days_since_creation * habit.frequency_value
        rate = min(habit.total_completions / expected, 1.0) if expected > 0 else 0
        completion_rates.append(rate)
    
    avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    # This week's completions
    week_start = datetime.utcnow() - timedelta(days=7)
    week_completions = db.query(HabitCompletion).join(Habit).filter(
        Habit.user_id == current_user.id,
        HabitCompletion.completion_date >= week_start
    ).count()
    
    return {
        "total_habits": total_habits,
        "active_streaks": active_streaks,
        "average_completion_rate": avg_completion_rate,
        "longest_streak": longest_streak,
        "total_completions_this_week": week_completions,
        "habits_by_category": _get_habits_by_category(habits),
        "completion_trend": _get_completion_trend(habits, db)
    }

@router.post("/analyze-patterns")
async def trigger_pattern_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger pattern analysis for all user habits"""
    
    background_tasks.add_task(
        habit_learning_engine.analyze_user_patterns,
        current_user.id,
        db
    )
    
    return {"message": "Pattern analysis started"}

@router.get("/behavior-patterns")
async def get_user_behavior_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's behavioral patterns identified by AI"""
    
    patterns = db.query(UserBehaviorPattern).filter(
        UserBehaviorPattern.user_id == current_user.id
    ).all()
    
    return [
        {
            "pattern_type": pattern.pattern_type,
            "data": pattern.pattern_data,
            "confidence_score": pattern.confidence_score,
            "last_updated": pattern.last_updated
        }
        for pattern in patterns
    ]

def _get_habits_by_category(habits: List[Habit]) -> dict:
    """Group habits by category"""
    categories = {}
    for habit in habits:
        category = habit.category or "Other"
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    return categories

def _get_completion_trend(habits: List[Habit], db: Session) -> dict:
    """Calculate completion trend over the last 30 days"""
    
    if not habits:
        return {"trend": "stable", "change_percentage": 0}
    
    now = datetime.utcnow()
    
    # Last 15 days vs previous 15 days
    mid_point = now - timedelta(days=15)
    start_point = now - timedelta(days=30)
    
    habit_ids = [h.id for h in habits]
    
    recent_completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id.in_(habit_ids),
        HabitCompletion.completion_date >= mid_point
    ).count()
    
    previous_completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id.in_(habit_ids),
        HabitCompletion.completion_date >= start_point,
        HabitCompletion.completion_date < mid_point
    ).count()
    
    if previous_completions == 0:
        return {"trend": "stable", "change_percentage": 0}
    
    change_percentage = ((recent_completions - previous_completions) / previous_completions) * 100
    
    if change_percentage > 10:
        trend = "improving"
    elif change_percentage < -10:
        trend = "declining"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change_percentage": change_percentage,
        "recent_completions": recent_completions,
        "previous_completions": previous_completions
    }