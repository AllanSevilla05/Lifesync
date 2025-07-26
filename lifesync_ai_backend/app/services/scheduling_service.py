from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.models import User, Task
from app.models.goal_models import Goal
from app.models.habit_models import Habit, HabitCompletion
from app.services.ai_service import AIService
import json

# Create AI service instance
ai_service = AIService()

class SchedulingOptimizer:
    """AI-powered scheduling optimization service"""
    
    def __init__(self):
        self.time_blocks = [
            {"name": "Early Morning", "start": 6, "end": 9, "energy": "high"},
            {"name": "Morning", "start": 9, "end": 12, "energy": "high"},
            {"name": "Midday", "start": 12, "end": 14, "energy": "medium"},
            {"name": "Afternoon", "start": 14, "end": 17, "energy": "medium"},
            {"name": "Evening", "start": 17, "end": 20, "energy": "low"},
            {"name": "Night", "start": 20, "end": 23, "energy": "low"}
        ]
    
    async def optimize_daily_schedule(
        self, 
        user_id: int, 
        target_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Generate an optimized daily schedule for the user"""
        
        # Get user data
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Analyze user patterns
        user_patterns = await self._analyze_user_patterns(user_id, db)
        
        # Get tasks to schedule
        tasks_to_schedule = await self._get_schedulable_tasks(user_id, target_date, db)
        
        # Get existing commitments
        existing_commitments = await self._get_existing_commitments(user_id, target_date, db)
        
        # Generate optimized schedule
        optimized_schedule = await self._generate_schedule(
            tasks_to_schedule,
            existing_commitments,
            user_patterns,
            target_date
        )
        
        # Calculate schedule metrics
        metrics = self._calculate_schedule_metrics(optimized_schedule, user_patterns)
        
        return {
            "success": True,
            "schedule": optimized_schedule,
            "metrics": metrics,
            "recommendations": await self._generate_recommendations(
                optimized_schedule, 
                user_patterns,
                user_id,
                db
            )
        }
    
    async def _analyze_user_patterns(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analyze user productivity patterns and preferences"""
        
        # Get habit completion patterns
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        habit_patterns = {}
        
        for habit in habits:
            completions = db.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit.id
            ).order_by(HabitCompletion.completed_at.desc()).limit(30).all()
            
            if completions:
                # Analyze completion times
                completion_hours = [c.completed_at.hour for c in completions]
                most_common_hour = max(set(completion_hours), key=completion_hours.count)
                
                habit_patterns[habit.name] = {
                    "preferred_time": most_common_hour,
                    "completion_rate": len(completions) / 30,
                    "category": habit.category
                }
        
        # Get task completion patterns
        completed_tasks = db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status == "completed",
                Task.updated_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).all()
        
        task_patterns = {}
        if completed_tasks:
            completion_hours = [t.updated_at.hour for t in completed_tasks]
            productivity_by_hour = {}
            
            for hour in range(24):
                hour_completions = completion_hours.count(hour)
                productivity_by_hour[hour] = hour_completions
            
            # Find peak productivity hours
            peak_hours = sorted(productivity_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
            task_patterns["peak_hours"] = [hour for hour, count in peak_hours if count > 0]
        
        # Analyze work-life balance preferences
        work_tasks = [t for t in completed_tasks if 'work' in t.title.lower() or 'job' in t.title.lower()]
        personal_tasks = [t for t in completed_tasks if t not in work_tasks]
        
        balance_patterns = {
            "work_ratio": len(work_tasks) / len(completed_tasks) if completed_tasks else 0.5,
            "personal_ratio": len(personal_tasks) / len(completed_tasks) if completed_tasks else 0.5
        }
        
        return {
            "habits": habit_patterns,
            "tasks": task_patterns,
            "balance": balance_patterns,
            "energy_levels": self._estimate_energy_levels(habit_patterns, task_patterns)
        }
    
    def _estimate_energy_levels(self, habit_patterns: Dict, task_patterns: Dict) -> Dict[str, str]:
        """Estimate user's energy levels throughout the day"""
        
        energy_levels = {}
        
        # Default energy pattern
        for block in self.time_blocks:
            energy_levels[block["name"]] = block["energy"]
        
        # Adjust based on user patterns
        if task_patterns.get("peak_hours"):
            for hour in task_patterns["peak_hours"]:
                for block in self.time_blocks:
                    if block["start"] <= hour < block["end"]:
                        energy_levels[block["name"]] = "high"
                        break
        
        return energy_levels
    
    async def _get_schedulable_tasks(
        self, 
        user_id: int, 
        target_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get tasks that need to be scheduled for the target date"""
        
        # Get tasks due on or before target date
        tasks = db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status.in_(["pending", "in_progress"]),
                or_(
                    Task.due_date <= target_date + timedelta(days=1),
                    Task.due_date.is_(None)
                )
            )
        ).all()
        
        schedulable_tasks = []
        for task in tasks:
            # Estimate task duration and complexity
            duration = self._estimate_task_duration(task)
            complexity = self._estimate_task_complexity(task)
            
            schedulable_tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date,
                "estimated_duration": duration,
                "complexity": complexity,
                "category": self._categorize_task(task)
            })
        
        return schedulable_tasks
    
    def _estimate_task_duration(self, task: Task) -> int:
        """Estimate task duration in minutes"""
        
        # Simple heuristic based on title length and description
        base_duration = 30  # 30 minutes base
        
        # Adjust based on priority
        priority_multiplier = {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.5}
        duration = base_duration * priority_multiplier.get(task.priority, 1.0)
        
        # Adjust based on description length
        if task.description:
            description_factor = min(len(task.description) / 100, 2.0)
            duration *= (1 + description_factor * 0.5)
        
        # Look for time keywords in title/description
        text = f"{task.title} {task.description or ''}".lower()
        if any(word in text for word in ["quick", "brief", "short"]):
            duration *= 0.5
        elif any(word in text for word in ["long", "detailed", "comprehensive"]):
            duration *= 1.5
        elif any(word in text for word in ["meeting", "call"]):
            duration = 60  # Default meeting time
        
        return int(max(15, min(duration, 240)))  # 15 min to 4 hours
    
    def _estimate_task_complexity(self, task: Task) -> str:
        """Estimate task complexity: low, medium, high"""
        
        # Simple heuristic based on priority and content
        if task.priority >= 4:
            return "high"
        elif task.priority >= 2:
            return "medium"
        else:
            return "low"
    
    def _categorize_task(self, task: Task) -> str:
        """Categorize task based on content"""
        
        text = f"{task.title} {task.description or ''}".lower()
        
        if any(word in text for word in ["work", "job", "project", "meeting", "email"]):
            return "work"
        elif any(word in text for word in ["exercise", "gym", "workout", "run"]):
            return "fitness"
        elif any(word in text for word in ["family", "friend", "personal", "home"]):
            return "personal"
        elif any(word in text for word in ["learn", "study", "read", "course"]):
            return "learning"
        else:
            return "general"
    
    async def _get_existing_commitments(
        self, 
        user_id: int, 
        target_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get existing commitments for the day"""
        
        # Get scheduled tasks (if we had a calendar integration)
        # For now, return basic commitments like habits
        
        habits = db.query(Habit).filter(
            and_(
                Habit.user_id == user_id,
                Habit.is_active == True
            )
        ).all()
        
        commitments = []
        for habit in habits:
            if habit.frequency == "daily":
                # Estimate preferred time based on category
                preferred_time = self._get_habit_preferred_time(habit)
                commitments.append({
                    "type": "habit",
                    "title": habit.name,
                    "duration": 30,  # Default habit duration
                    "preferred_time": preferred_time,
                    "flexibility": "medium"
                })
        
        return commitments
    
    def _get_habit_preferred_time(self, habit: Habit) -> int:
        """Get preferred time for habit based on category"""
        
        category_times = {
            "exercise": 7,      # Early morning
            "meditation": 8,    # Morning
            "work": 9,          # Work hours
            "learning": 14,     # Afternoon
            "social": 18,       # Evening
            "relaxation": 20    # Night
        }
        
        return category_times.get(habit.category, 12)  # Default to midday
    
    async def _generate_schedule(
        self,
        tasks: List[Dict[str, Any]],
        commitments: List[Dict[str, Any]],
        user_patterns: Dict[str, Any],
        target_date: datetime
    ) -> Dict[str, Any]:
        """Generate optimized schedule using AI"""
        
        # Create schedule prompt for AI
        prompt = self._create_scheduling_prompt(tasks, commitments, user_patterns, target_date)
        
        try:
            # Use AI to generate schedule
            ai_response = await ai_service.generate_response(prompt)
            schedule_data = json.loads(ai_response)
            
            # Validate and adjust schedule
            validated_schedule = self._validate_schedule(schedule_data, tasks, commitments)
            
            return validated_schedule
            
        except Exception as e:
            # Fallback to rule-based scheduling if AI fails
            return self._fallback_schedule(tasks, commitments, user_patterns)
    
    def _create_scheduling_prompt(
        self,
        tasks: List[Dict[str, Any]],
        commitments: List[Dict[str, Any]],
        user_patterns: Dict[str, Any],
        target_date: datetime
    ) -> str:
        """Create a prompt for AI scheduling"""
        
        return f"""
        As an AI scheduling assistant, create an optimized daily schedule for {target_date.strftime('%Y-%m-%d')}.

        User Patterns:
        - Peak productivity hours: {user_patterns.get('tasks', {}).get('peak_hours', [])}
        - Energy levels: {user_patterns.get('energy_levels', {})}
        - Work-life balance ratio: {user_patterns.get('balance', {})}

        Tasks to Schedule:
        {json.dumps(tasks, indent=2)}

        Existing Commitments:
        {json.dumps(commitments, indent=2)}

        Guidelines:
        1. Schedule high-complexity tasks during peak energy hours
        2. Batch similar tasks together
        3. Leave buffer time between tasks
        4. Respect existing commitments
        5. Balance work and personal tasks
        6. Include breaks

        Return a JSON schedule with this structure:
        {{
            "schedule_blocks": [
                {{
                    "start_time": "09:00",
                    "end_time": "10:30",
                    "task_id": "task_123",
                    "title": "Task Title",
                    "type": "work|personal|break|habit",
                    "energy_match": "high|medium|low"
                }}
            ],
            "unscheduled_tasks": [],
            "optimization_score": 85
        }}
        """
    
    def _validate_schedule(
        self,
        schedule_data: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        commitments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate and adjust the AI-generated schedule"""
        
        if not isinstance(schedule_data, dict) or "schedule_blocks" not in schedule_data:
            return self._fallback_schedule(tasks, commitments, {})
        
        # Validate time blocks don't overlap
        schedule_blocks = schedule_data["schedule_blocks"]
        validated_blocks = []
        
        for block in schedule_blocks:
            if self._is_valid_time_block(block, validated_blocks):
                validated_blocks.append(block)
        
        schedule_data["schedule_blocks"] = validated_blocks
        return schedule_data
    
    def _is_valid_time_block(self, block: Dict[str, Any], existing_blocks: List[Dict[str, Any]]) -> bool:
        """Check if a time block is valid and doesn't overlap"""
        
        try:
            start_time = datetime.strptime(block["start_time"], "%H:%M").time()
            end_time = datetime.strptime(block["end_time"], "%H:%M").time()
            
            # Check for overlaps with existing blocks
            for existing in existing_blocks:
                existing_start = datetime.strptime(existing["start_time"], "%H:%M").time()
                existing_end = datetime.strptime(existing["end_time"], "%H:%M").time()
                
                if (start_time < existing_end and end_time > existing_start):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _fallback_schedule(
        self,
        tasks: List[Dict[str, Any]],
        commitments: List[Dict[str, Any]],
        user_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a basic rule-based schedule as fallback"""
        
        schedule_blocks = []
        current_time = 9  # Start at 9 AM
        
        # Add commitments first
        for commitment in commitments:
            schedule_blocks.append({
                "start_time": f"{commitment['preferred_time']:02d}:00",
                "end_time": f"{commitment['preferred_time']:02d}:{commitment['duration']:02d}",
                "title": commitment["title"],
                "type": commitment["type"],
                "energy_match": "medium"
            })
        
        # Sort tasks by priority and complexity
        sorted_tasks = sorted(tasks, key=lambda x: (x["priority"], x["complexity"]), reverse=True)
        
        # Schedule tasks
        for task in sorted_tasks[:8]:  # Limit to 8 tasks per day
            duration_hours = task["estimated_duration"] / 60
            
            schedule_blocks.append({
                "start_time": f"{current_time:02d}:00",
                "end_time": f"{current_time + int(duration_hours):02d}:{int((duration_hours % 1) * 60):02d}",
                "task_id": task["id"],
                "title": task["title"],
                "type": task["category"],
                "energy_match": "medium"
            })
            
            current_time += max(1, int(duration_hours))
            if current_time >= 18:  # Don't schedule past 6 PM
                break
        
        return {
            "schedule_blocks": schedule_blocks,
            "unscheduled_tasks": sorted_tasks[8:],
            "optimization_score": 70
        }
    
    def _calculate_schedule_metrics(
        self, 
        schedule: Dict[str, Any], 
        user_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate metrics for the generated schedule"""
        
        total_blocks = len(schedule["schedule_blocks"])
        work_blocks = len([b for b in schedule["schedule_blocks"] if b.get("type") == "work"])
        personal_blocks = len([b for b in schedule["schedule_blocks"] if b.get("type") == "personal"])
        
        return {
            "total_scheduled_items": total_blocks,
            "work_life_balance": {
                "work_percentage": (work_blocks / total_blocks * 100) if total_blocks > 0 else 0,
                "personal_percentage": (personal_blocks / total_blocks * 100) if total_blocks > 0 else 0
            },
            "optimization_score": schedule.get("optimization_score", 70),
            "unscheduled_count": len(schedule.get("unscheduled_tasks", []))
        }
    
    async def _generate_recommendations(
        self,
        schedule: Dict[str, Any],
        user_patterns: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Check for optimization opportunities
        if schedule.get("optimization_score", 0) < 80:
            recommendations.append({
                "type": "optimization",
                "title": "Schedule Optimization",
                "message": "Your schedule could be better optimized. Consider rearranging tasks based on your energy levels.",
                "priority": "medium"
            })
        
        # Check work-life balance
        metrics = self._calculate_schedule_metrics(schedule, user_patterns)
        work_percentage = metrics["work_life_balance"]["work_percentage"]
        
        if work_percentage > 70:
            recommendations.append({
                "type": "balance",
                "title": "Work-Life Balance",
                "message": "Consider adding more personal time to your schedule for better balance.",
                "priority": "high"
            })
        elif work_percentage < 30:
            recommendations.append({
                "type": "balance",
                "title": "Productivity Focus",
                "message": "You might want to allocate more time for work-related tasks.",
                "priority": "medium"
            })
        
        # Check for unscheduled tasks
        if len(schedule.get("unscheduled_tasks", [])) > 0:
            recommendations.append({
                "type": "tasks",
                "title": "Unscheduled Tasks",
                "message": f"You have {len(schedule['unscheduled_tasks'])} tasks that couldn't be scheduled today. Consider rescheduling or breaking them down.",
                "priority": "medium"
            })
        
        return recommendations

# Global instance
scheduling_optimizer = SchedulingOptimizer()