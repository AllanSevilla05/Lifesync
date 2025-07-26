from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import User, MoodEntry
from app.schemas.wellness import MoodEntryCreate, MoodEntry as MoodEntrySchema, WellnessInsights
from app.api.v1.endpoints.auth import get_current_user
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.post("/mood", response_model=MoodEntrySchema)
async def log_mood(
    mood_entry: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a new mood entry"""
    db_mood = MoodEntry(**mood_entry.model_dump(), user_id=current_user.id)
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

@router.get("/mood", response_model=List[MoodEntrySchema])
async def get_mood_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood history for the specified number of days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= start_date
    ).order_by(MoodEntry.created_at.desc()).all()
    
    return mood_entries

@router.get("/suggestions", response_model=WellnessInsights)
async def get_wellness_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized wellness suggestions based on recent mood and activity"""
    
    # Get latest mood entry
    latest_mood = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).order_by(MoodEntry.created_at.desc()).first()
    
    if not latest_mood:
        # Provide default suggestions if no mood data
        return WellnessInsights(
            suggestions=[
                {
                    "action": "Log your current mood to get personalized suggestions",
                    "duration": "2 minutes",
                    "reasoning": "Understanding your current state helps provide better recommendations",
                    "urgency": "low"
                }
            ],
            overall_assessment="No mood data available yet",
            focus_area="awareness"
        )
    
    # Get recent activities (you might want to expand this)
    recent_activities = []
    
    # Get AI-generated wellness suggestions
    suggestions = await ai_service.suggest_wellness_actions(
        mood_level=latest_mood.mood_level,
        energy_level=latest_mood.energy_level,
        stress_level=latest_mood.stress_level or 5,
        recent_activities=recent_activities
    )
    
    return suggestions

@router.get("/insights")
async def get_wellness_insights(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wellness insights and trends over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.created_at >= start_date
    ).order_by(MoodEntry.created_at.asc()).all()
    
    if not mood_entries:
        return {
            "message": "No mood data available for the specified period",
            "trends": {},
            "recommendations": ["Start logging your mood daily to track trends"]
        }
    
    # Calculate averages and trends
    total_entries = len(mood_entries)
    avg_mood = sum(entry.mood_level for entry in mood_entries) / total_entries
    avg_energy = sum(entry.energy_level for entry in mood_entries) / total_entries
    avg_stress = sum(entry.stress_level or 5 for entry in mood_entries) / total_entries
    
    # Calculate recent vs older averages for trends
    recent_entries = mood_entries[-7:] if len(mood_entries) >= 7 else mood_entries
    recent_avg_mood = sum(entry.mood_level for entry in recent_entries) / len(recent_entries)
    
    mood_trend = "improving" if recent_avg_mood > avg_mood else "declining" if recent_avg_mood < avg_mood else "stable"
    
    return {
        "period_days": days,
        "total_entries": total_entries,
        "averages": {
            "mood": round(avg_mood, 1),
            "energy": round(avg_energy, 1),
            "stress": round(avg_stress, 1)
        },
        "trends": {
            "mood_trend": mood_trend,
            "recent_avg_mood": round(recent_avg_mood, 1)
        },
        "recommendations": [
            f"Your average mood is {avg_mood:.1f}/10 - {'Keep up the good work!' if avg_mood >= 7 else 'Consider focusing on mood-boosting activities'}",
            f"Your energy levels average {avg_energy:.1f}/10 - {'Great energy levels!' if avg_energy >= 7 else 'Try incorporating more energizing activities'}",
            f"Your stress levels average {avg_stress:.1f}/10 - {'Good stress management!' if avg_stress <= 4 else 'Consider stress reduction techniques'}"
        ]
    }