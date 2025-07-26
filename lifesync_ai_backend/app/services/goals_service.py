from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.goal_models import (
    Goal, GoalMilestone, GoalProgress, GoalReflection, GoalTemplate, GoalInsight,
    GoalType, GoalStatus, GoalPriority, TimeFrame
)
from app.models.models import User
from app.services.ai_service import AIService
import json

# Create AI service instance
ai_service = AIService()

class GoalsService:
    """Smart goal setting and tracking service with AI assistance"""
    
    def __init__(self):
        self.smart_criteria = ["Specific", "Measurable", "Achievable", "Relevant", "Time-bound"]
    
    async def create_smart_goal(
        self, 
        goal_data: Dict[str, Any], 
        user_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Create a SMART goal with AI assistance"""
        
        try:
            # Analyze goal with SMART criteria
            smart_analysis = await self._analyze_smart_criteria(goal_data)
            
            # Generate AI suggestions
            ai_suggestions = await self._generate_goal_suggestions(goal_data, user_id, db)
            
            # Predict completion and difficulty
            predictions = await self._predict_goal_metrics(goal_data, user_id, db)
            
            # Create the goal
            goal = Goal(
                user_id=user_id,
                title=goal_data["title"],
                description=goal_data.get("description", ""),
                goal_type=GoalType(goal_data.get("goal_type", "personal")),
                priority=GoalPriority(goal_data.get("priority", "medium")),
                target_value=goal_data.get("target_value"),
                unit=goal_data.get("unit"),
                start_date=goal_data.get("start_date"),
                target_date=goal_data.get("target_date"),
                time_frame=TimeFrame(goal_data.get("time_frame", "monthly")),
                smart_analysis=smart_analysis,
                ai_suggestions=ai_suggestions,
                predicted_completion=predictions.get("predicted_completion"),
                difficulty_score=predictions.get("difficulty_score"),
                tags=goal_data.get("tags", []),
                reminder_settings=goal_data.get("reminder_settings", {}),
                status=GoalStatus.ACTIVE
            )
            
            db.add(goal)
            db.flush()
            
            # Create milestones if provided
            if goal_data.get("milestones"):
                await self._create_milestones(goal.id, goal_data["milestones"], db)
            
            db.commit()
            db.refresh(goal)
            
            return {
                "success": True,
                "goal": self._format_goal_response(goal),
                "smart_score": smart_analysis.get("overall_score", 0),
                "suggestions": ai_suggestions
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    async def _analyze_smart_criteria(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze goal against SMART criteria using AI"""
        
        prompt = f"""
        Analyze the following goal against SMART criteria and provide a detailed assessment:
        
        Goal: {goal_data.get('title', '')}
        Description: {goal_data.get('description', '')}
        Target: {goal_data.get('target_value', 'Not specified')} {goal_data.get('unit', '')}
        Deadline: {goal_data.get('target_date', 'Not specified')}
        
        Evaluate each SMART criterion (1-10 scale):
        - Specific: How clear and well-defined is the goal?
        - Measurable: Can progress be quantified?
        - Achievable: Is the goal realistic?
        - Relevant: Does it align with broader objectives?
        - Time-bound: Is there a clear deadline?
        
        Return JSON format:
        {{
            "specific": {{"score": 8, "feedback": "Goal is well-defined but could be more specific about..."}},
            "measurable": {{"score": 9, "feedback": "Clear metrics provided"}},
            "achievable": {{"score": 7, "feedback": "Challenging but realistic"}},
            "relevant": {{"score": 8, "feedback": "Aligns well with personal development"}},
            "time_bound": {{"score": 9, "feedback": "Clear deadline specified"}},
            "overall_score": 8.2,
            "recommendations": ["Add more specific milestones", "Consider breaking into smaller goals"]
        }}
        """
        
        try:
            response = await ai_service.generate_response(prompt)
            return json.loads(response)
        except Exception:
            return {
                "specific": {"score": 5, "feedback": "Unable to analyze"},
                "measurable": {"score": 5, "feedback": "Unable to analyze"},
                "achievable": {"score": 5, "feedback": "Unable to analyze"},
                "relevant": {"score": 5, "feedback": "Unable to analyze"},
                "time_bound": {"score": 5, "feedback": "Unable to analyze"},
                "overall_score": 5.0,
                "recommendations": []
            }
    
    async def _generate_goal_suggestions(
        self, 
        goal_data: Dict[str, Any], 
        user_id: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered suggestions for achieving the goal"""
        
        # Get user's past goals for context
        past_goals = db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.COMPLETED
            )
        ).limit(5).all()
        
        past_context = [{"title": g.title, "type": g.goal_type.value} for g in past_goals]
        
        prompt = f"""
        Generate actionable suggestions for achieving this goal:
        
        Goal: {goal_data.get('title', '')}
        Type: {goal_data.get('goal_type', '')}
        Target: {goal_data.get('target_value', '')} {goal_data.get('unit', '')}
        Deadline: {goal_data.get('target_date', '')}
        
        User's past successful goals: {past_context}
        
        Provide 5-7 specific, actionable suggestions in JSON format:
        [
            {{
                "type": "milestone",
                "title": "Break into weekly targets",
                "description": "Divide your goal into weekly milestones for better tracking",
                "priority": "high"
            }},
            {{
                "type": "habit",
                "title": "Daily practice routine",
                "description": "Establish a consistent daily routine",
                "priority": "medium"
            }}
        ]
        """
        
        try:
            response = await ai_service.generate_response(prompt)
            suggestions = json.loads(response)
            return suggestions if isinstance(suggestions, list) else []
        except Exception:
            return [
                {
                    "type": "planning",
                    "title": "Create a detailed plan",
                    "description": "Break down your goal into smaller, manageable steps",
                    "priority": "high"
                },
                {
                    "type": "tracking",
                    "title": "Set up regular check-ins",
                    "description": "Schedule weekly reviews of your progress",
                    "priority": "medium"
                }
            ]
    
    async def _predict_goal_metrics(
        self, 
        goal_data: Dict[str, Any], 
        user_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Predict completion date and difficulty score"""
        
        # Simple heuristic-based predictions (in a real system, use ML models)
        target_date = goal_data.get("target_date")
        if target_date:
            if isinstance(target_date, str):
                target_date = datetime.fromisoformat(target_date)
            
            # Calculate difficulty based on timeframe and complexity
            days_available = (target_date - datetime.utcnow()).days
            
            difficulty_factors = {
                "short_timeline": 1 if days_available < 30 else 0,
                "high_target": 1 if goal_data.get("target_value", 0) > 100 else 0,
                "complex_type": 1 if goal_data.get("goal_type") in ["professional", "learning"] else 0
            }
            
            difficulty_score = 5 + sum(difficulty_factors.values()) * 1.5
            
            # Predict completion (add buffer based on difficulty)
            buffer_days = int(difficulty_score * 2)
            predicted_completion = target_date + timedelta(days=buffer_days)
            
            return {
                "difficulty_score": min(difficulty_score, 10),
                "predicted_completion": predicted_completion
            }
        
        return {"difficulty_score": 5.0, "predicted_completion": None}
    
    async def _create_milestones(
        self, 
        goal_id: int, 
        milestones_data: List[Dict[str, Any]], 
        db: Session
    ):
        """Create milestones for a goal"""
        
        for i, milestone_data in enumerate(milestones_data):
            milestone = GoalMilestone(
                goal_id=goal_id,
                title=milestone_data["title"],
                description=milestone_data.get("description", ""),
                target_value=milestone_data.get("target_value"),
                target_date=milestone_data.get("target_date"),
                order_index=i
            )
            db.add(milestone)
    
    async def update_goal_progress(
        self, 
        goal_id: int, 
        progress_data: Dict[str, Any], 
        user_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Update goal progress and generate insights"""
        
        try:
            goal = db.query(Goal).filter(
                and_(Goal.id == goal_id, Goal.user_id == user_id)
            ).first()
            
            if not goal:
                return {"success": False, "error": "Goal not found"}
            
            # Create progress log
            progress = GoalProgress(
                goal_id=goal_id,
                progress_value=progress_data["progress_value"],
                notes=progress_data.get("notes", ""),
                source=progress_data.get("source", "manual")
            )
            
            # Calculate percentage
            if goal.target_value:
                progress.progress_percentage = (progress_data["progress_value"] / goal.target_value) * 100
                goal.completion_percentage = progress.progress_percentage
            
            # Update current value
            goal.current_value = progress_data["progress_value"]
            goal.last_updated = datetime.utcnow()
            
            db.add(progress)
            
            # Generate insights if significant progress
            if progress.progress_percentage and progress.progress_percentage % 25 == 0:
                await self._generate_progress_insights(goal, db)
            
            db.commit()
            
            return {
                "success": True,
                "progress": {
                    "current_value": goal.current_value,
                    "completion_percentage": goal.completion_percentage,
                    "target_value": goal.target_value
                }
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    async def _generate_progress_insights(self, goal: Goal, db: Session):
        """Generate AI insights based on progress patterns"""
        
        recent_progress = db.query(GoalProgress).filter(
            GoalProgress.goal_id == goal.id
        ).order_by(GoalProgress.logged_at.desc()).limit(10).all()
        
        if len(recent_progress) < 3:
            return
        
        # Analyze progress trend
        progress_values = [p.progress_value for p in recent_progress]
        is_improving = progress_values[0] > progress_values[-1]
        
        insight_content = ""
        insight_type = "pattern"
        
        if is_improving:
            insight_content = f"Great progress on '{goal.title}'! You've maintained a positive trend. Keep up the momentum!"
            if goal.completion_percentage >= 75:
                insight_content += " You're in the final stretch - consider planning your next goal."
        else:
            insight_content = f"Progress on '{goal.title}' has slowed. Consider reviewing your approach or breaking down remaining tasks."
            insight_type = "recommendation"
        
        insight = GoalInsight(
            user_id=goal.user_id,
            goal_id=goal.id,
            insight_type=insight_type,
            title="Progress Update",
            content=insight_content,
            confidence_score=0.8
        )
        
        db.add(insight)
    
    async def create_goal_reflection(
        self, 
        goal_id: int, 
        reflection_data: Dict[str, Any], 
        user_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Create a goal reflection entry"""
        
        try:
            goal = db.query(Goal).filter(
                and_(Goal.id == goal_id, Goal.user_id == user_id)
            ).first()
            
            if not goal:
                return {"success": False, "error": "Goal not found"}
            
            reflection = GoalReflection(
                goal_id=goal_id,
                reflection_text=reflection_data["reflection_text"],
                mood_rating=reflection_data.get("mood_rating"),
                energy_rating=reflection_data.get("energy_rating"),
                motivation_rating=reflection_data.get("motivation_rating"),
                challenges=reflection_data.get("challenges", []),
                wins=reflection_data.get("wins", []),
                lessons_learned=reflection_data.get("lessons_learned", ""),
                next_actions=reflection_data.get("next_actions", [])
            )
            
            db.add(reflection)
            db.commit()
            
            return {"success": True, "reflection_id": reflection.id}
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_user_goals(
        self, 
        user_id: int, 
        status_filter: Optional[str] = None,
        goal_type_filter: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get user's goals with optional filtering"""
        
        query = db.query(Goal).filter(Goal.user_id == user_id)
        
        if status_filter:
            query = query.filter(Goal.status == status_filter)
        
        if goal_type_filter:
            query = query.filter(Goal.goal_type == goal_type_filter)
        
        goals = query.order_by(Goal.created_at.desc()).all()
        
        return [self._format_goal_response(goal) for goal in goals]
    
    def _format_goal_response(self, goal: Goal) -> Dict[str, Any]:
        """Format goal for API response"""
        
        return {
            "id": goal.id,
            "title": goal.title,
            "description": goal.description,
            "goal_type": goal.goal_type.value,
            "status": goal.status.value,
            "priority": goal.priority.value,
            "target_value": goal.target_value,
            "current_value": goal.current_value,
            "unit": goal.unit,
            "completion_percentage": goal.completion_percentage,
            "start_date": goal.start_date.isoformat() if goal.start_date else None,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "time_frame": goal.time_frame.value,
            "difficulty_score": goal.difficulty_score,
            "smart_analysis": goal.smart_analysis,
            "ai_suggestions": goal.ai_suggestions,
            "tags": goal.tags,
            "created_at": goal.created_at.isoformat(),
            "updated_at": goal.updated_at.isoformat() if goal.updated_at else None
        }
    
    async def generate_goal_recommendations(
        self, 
        user_id: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate personalized goal recommendations"""
        
        # Analyze user's goal patterns
        user_goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        
        goal_types = [g.goal_type.value for g in user_goals]
        completed_goals = [g for g in user_goals if g.status == GoalStatus.COMPLETED]
        
        recommendations = []
        
        # Recommend based on successful patterns
        if len(completed_goals) > 0:
            successful_types = [g.goal_type.value for g in completed_goals]
            most_successful_type = max(set(successful_types), key=successful_types.count)
            
            recommendations.append({
                "type": "pattern_based",
                "title": f"Continue Your Success in {most_successful_type.title()}",
                "description": f"You've had great success with {most_successful_type} goals. Consider setting another challenging goal in this area.",
                "suggested_goal_type": most_successful_type,
                "confidence": 0.8
            })
        
        # Recommend balance
        if len(set(goal_types)) < 3:
            missing_types = set(["health", "learning", "personal"]) - set(goal_types)
            if missing_types:
                missing_type = list(missing_types)[0]
                recommendations.append({
                    "type": "balance",
                    "title": f"Explore {missing_type.title()} Goals",
                    "description": f"Consider adding a {missing_type} goal for better life balance.",
                    "suggested_goal_type": missing_type,
                    "confidence": 0.6
                })
        
        return recommendations

# Global instance
goals_service = GoalsService()