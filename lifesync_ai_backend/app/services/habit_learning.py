import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.models import User, Task
from app.models.habit_models import Habit, HabitCompletion, HabitInsight, UserBehaviorPattern, PersonalizationModel

class HabitLearningEngine:
    """Advanced machine learning engine for habit tracking and behavioral analysis"""
    
    def __init__(self):
        self.min_data_points = 5  # Minimum completions needed for meaningful insights
        
    async def analyze_user_patterns(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analyze user behavior patterns and generate insights"""
        
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        all_patterns = {}
        
        for habit in habits:
            completions = db.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit.id
            ).order_by(HabitCompletion.completion_date).all()
            
            if len(completions) >= self.min_data_points:
                patterns = self._analyze_habit_patterns(habit, completions)
                all_patterns[habit.id] = patterns
                
                # Generate insights based on patterns
                insights = await self._generate_habit_insights(habit, patterns, db)
                
                # Store insights in database
                for insight in insights:
                    db_insight = HabitInsight(
                        habit_id=habit.id,
                        insight_type=insight['type'],
                        title=insight['title'],
                        description=insight['description'],
                        data=insight['data'],
                        confidence_score=insight['confidence']
                    )
                    db.add(db_insight)
        
        # Analyze cross-habit patterns
        cross_patterns = self._analyze_cross_habit_patterns(all_patterns)
        
        # Update user behavior patterns
        await self._update_user_behavior_patterns(user_id, cross_patterns, db)
        
        db.commit()
        return all_patterns
    
    def _analyze_habit_patterns(self, habit: Habit, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze patterns for a specific habit"""
        
        patterns = {
            'completion_rate': self._calculate_completion_rate(habit, completions),
            'time_patterns': self._analyze_time_patterns(completions),
            'quality_trends': self._analyze_quality_trends(completions),
            'mood_energy_correlation': self._analyze_mood_energy_correlation(completions),
            'streak_analysis': self._analyze_streak_patterns(completions),
            'contextual_patterns': self._analyze_contextual_patterns(completions),
            'difficulty_adaptation': self._analyze_difficulty_adaptation(habit, completions)
        }
        
        return patterns
    
    def _calculate_completion_rate(self, habit: Habit, completions: List[HabitCompletion]) -> Dict[str, float]:
        """Calculate various completion rates"""
        
        now = datetime.utcnow()
        
        # Overall completion rate
        days_since_creation = (now - habit.created_at).days + 1
        expected_completions = days_since_creation * habit.frequency_value
        actual_completions = len(completions)
        overall_rate = min(actual_completions / expected_completions, 1.0) if expected_completions > 0 else 0
        
        # Last 30 days
        thirty_days_ago = now - timedelta(days=30)
        recent_completions = [c for c in completions if c.completion_date >= thirty_days_ago]
        recent_rate = len(recent_completions) / min(30, days_since_creation) if days_since_creation > 0 else 0
        
        # Last 7 days
        seven_days_ago = now - timedelta(days=7)
        week_completions = [c for c in completions if c.completion_date >= seven_days_ago]
        week_rate = len(week_completions) / 7
        
        return {
            'overall': overall_rate,
            'last_30_days': recent_rate,
            'last_7_days': week_rate,
            'trend': 'improving' if recent_rate > overall_rate else 'declining' if recent_rate < overall_rate else 'stable'
        }
    
    def _analyze_time_patterns(self, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze when user completes habits"""
        
        if not completions:
            return {}
        
        # Group by hour of day
        hours = [c.completion_date.hour for c in completions]
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        # Find peak hours
        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            peak_percentage = hour_counts[peak_hour] / len(completions)
        else:
            peak_hour = None
            peak_percentage = 0
        
        # Group by day of week
        days = [c.completion_date.weekday() for c in completions]
        day_counts = defaultdict(int)
        for day in days:
            day_counts[day] += 1
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'peak_hour': peak_hour,
            'peak_hour_percentage': peak_percentage,
            'hourly_distribution': dict(hour_counts),
            'daily_distribution': {day_names[k]: v for k, v in day_counts.items()},
            'consistency_score': self._calculate_time_consistency(completions)
        }
    
    def _calculate_time_consistency(self, completions: List[HabitCompletion]) -> float:
        """Calculate how consistent user is with timing"""
        
        if len(completions) < 3:
            return 0.0
        
        hours = [c.completion_date.hour for c in completions]
        # Calculate standard deviation of hours
        mean_hour = np.mean(hours)
        std_dev = np.std(hours)
        
        # Convert to consistency score (lower std_dev = higher consistency)
        max_possible_std = 12  # Maximum possible standard deviation for hours
        consistency = max(0, 1 - (std_dev / max_possible_std))
        
        return consistency
    
    def _analyze_quality_trends(self, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze quality rating trends over time"""
        
        quality_ratings = [c.quality_rating for c in completions if c.quality_rating is not None]
        
        if len(quality_ratings) < 3:
            return {'insufficient_data': True}
        
        # Calculate trend
        x = np.arange(len(quality_ratings))
        slope = np.polyfit(x, quality_ratings, 1)[0]
        
        # Recent vs historical average
        recent_avg = np.mean(quality_ratings[-7:]) if len(quality_ratings) >= 7 else np.mean(quality_ratings)
        overall_avg = np.mean(quality_ratings)
        
        return {
            'overall_average': overall_avg,
            'recent_average': recent_avg,
            'trend_slope': slope,
            'trend': 'improving' if slope > 0.1 else 'declining' if slope < -0.1 else 'stable',
            'consistency': float(np.std(quality_ratings))
        }
    
    def _analyze_mood_energy_correlation(self, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze correlation between mood/energy and habit completion"""
        
        mood_before = [c.mood_before for c in completions if c.mood_before is not None]
        mood_after = [c.mood_after for c in completions if c.mood_after is not None]
        energy_before = [c.energy_before for c in completions if c.energy_before is not None]
        energy_after = [c.energy_after for c in completions if c.energy_after is not None]
        
        if len(mood_before) < 3:
            return {'insufficient_data': True}
        
        # Calculate mood/energy improvements
        mood_improvements = []
        energy_improvements = []
        
        for completion in completions:
            if completion.mood_before and completion.mood_after:
                mood_improvements.append(completion.mood_after - completion.mood_before)
            if completion.energy_before and completion.energy_after:
                energy_improvements.append(completion.energy_after - completion.energy_before)
        
        return {
            'avg_mood_improvement': np.mean(mood_improvements) if mood_improvements else 0,
            'avg_energy_improvement': np.mean(energy_improvements) if energy_improvements else 0,
            'avg_mood_before': np.mean(mood_before),
            'avg_mood_after': np.mean(mood_after) if mood_after else 0,
            'avg_energy_before': np.mean(energy_before),
            'avg_energy_after': np.mean(energy_after) if energy_after else 0,
            'positive_impact_percentage': len([x for x in mood_improvements if x > 0]) / len(mood_improvements) * 100 if mood_improvements else 0
        }
    
    def _analyze_streak_patterns(self, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze streak patterns and identify break points"""
        
        if not completions:
            return {}
        
        # Sort completions by date
        sorted_completions = sorted(completions, key=lambda x: x.completion_date)
        
        # Calculate streaks
        streaks = []
        current_streak = 1
        
        for i in range(1, len(sorted_completions)):
            prev_date = sorted_completions[i-1].completion_date.date()
            curr_date = sorted_completions[i].completion_date.date()
            
            if (curr_date - prev_date).days == 1:
                current_streak += 1
            else:
                if current_streak > 1:
                    streaks.append(current_streak)
                current_streak = 1
        
        if current_streak > 1:
            streaks.append(current_streak)
        
        # Analyze break patterns
        breaks = []
        for i in range(1, len(sorted_completions)):
            prev_date = sorted_completions[i-1].completion_date.date()
            curr_date = sorted_completions[i].completion_date.date()
            gap = (curr_date - prev_date).days - 1
            if gap > 0:
                breaks.append(gap)
        
        return {
            'total_streaks': len(streaks),
            'average_streak_length': np.mean(streaks) if streaks else 0,
            'longest_streak': max(streaks) if streaks else 0,
            'average_break_length': np.mean(breaks) if breaks else 0,
            'longest_break': max(breaks) if breaks else 0,
            'streak_consistency': len(streaks) / len(completions) if completions else 0
        }
    
    def _analyze_contextual_patterns(self, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze contextual factors that influence completion"""
        
        context_factors = defaultdict(list)
        
        for completion in completions:
            if completion.context:
                for key, value in completion.context.items():
                    context_factors[key].append(value)
        
        # Analyze each contextual factor
        patterns = {}
        for factor, values in context_factors.items():
            if len(values) >= 3:
                value_counts = defaultdict(int)
                for value in values:
                    value_counts[value] += 1
                
                most_common = max(value_counts, key=value_counts.get)
                patterns[factor] = {
                    'most_common': most_common,
                    'frequency': value_counts[most_common] / len(values),
                    'distribution': dict(value_counts)
                }
        
        return patterns
    
    def _analyze_difficulty_adaptation(self, habit: Habit, completions: List[HabitCompletion]) -> Dict[str, Any]:
        """Analyze how user adapts to habit difficulty over time"""
        
        if len(completions) < 5:
            return {'insufficient_data': True}
        
        # Analyze duration trends (proxy for difficulty adaptation)
        durations = [c.duration_minutes for c in completions if c.duration_minutes is not None]
        
        if len(durations) < 3:
            return {'insufficient_data': True}
        
        # Calculate trend in duration over time
        x = np.arange(len(durations))
        duration_slope = np.polyfit(x, durations, 1)[0]
        
        # Analyze quality vs duration correlation
        quality_duration_pairs = [(c.quality_rating, c.duration_minutes) 
                                 for c in completions 
                                 if c.quality_rating and c.duration_minutes]
        
        if len(quality_duration_pairs) >= 3:
            qualities, durations_for_quality = zip(*quality_duration_pairs)
            correlation = np.corrcoef(qualities, durations_for_quality)[0, 1]
        else:
            correlation = 0
        
        return {
            'duration_trend_slope': duration_slope,
            'duration_trend': 'increasing' if duration_slope > 0.5 else 'decreasing' if duration_slope < -0.5 else 'stable',
            'quality_duration_correlation': correlation,
            'adaptation_score': self._calculate_adaptation_score(completions),
            'recommended_difficulty_adjustment': self._recommend_difficulty_adjustment(habit, completions)
        }
    
    def _calculate_adaptation_score(self, completions: List[HabitCompletion]) -> float:
        """Calculate how well user is adapting to the habit"""
        
        if len(completions) < 5:
            return 0.5
        
        # Recent performance vs early performance
        early_completions = completions[:len(completions)//3]
        recent_completions = completions[-len(completions)//3:]
        
        early_quality = np.mean([c.quality_rating for c in early_completions if c.quality_rating])
        recent_quality = np.mean([c.quality_rating for c in recent_completions if c.quality_rating])
        
        if early_quality == 0:
            return 0.5
        
        improvement_ratio = recent_quality / early_quality
        
        # Score between 0 and 1
        adaptation_score = min(1.0, max(0.0, (improvement_ratio - 0.5) / 1.5 + 0.5))
        
        return adaptation_score
    
    def _recommend_difficulty_adjustment(self, habit: Habit, completions: List[HabitCompletion]) -> str:
        """Recommend difficulty adjustment based on performance"""
        
        if len(completions) < 7:
            return "maintain"
        
        recent_completions = completions[-7:]
        avg_quality = np.mean([c.quality_rating for c in recent_completions if c.quality_rating])
        completion_consistency = len(recent_completions) / 7  # Should be close to 1 for daily habits
        
        if avg_quality >= 4.5 and completion_consistency >= 0.9:
            return "increase"
        elif avg_quality <= 2.5 or completion_consistency <= 0.5:
            return "decrease"
        else:
            return "maintain"
    
    def _analyze_cross_habit_patterns(self, all_patterns: Dict[int, Dict]) -> Dict[str, Any]:
        """Analyze patterns across all user habits"""
        
        if not all_patterns:
            return {}
        
        # Find common peak times across habits
        all_peak_hours = []
        for habit_patterns in all_patterns.values():
            if 'time_patterns' in habit_patterns and 'peak_hour' in habit_patterns['time_patterns']:
                peak_hour = habit_patterns['time_patterns']['peak_hour']
                if peak_hour is not None:
                    all_peak_hours.append(peak_hour)
        
        # Calculate overall productivity patterns
        completion_rates = []
        for habit_patterns in all_patterns.values():
            if 'completion_rate' in habit_patterns:
                completion_rates.append(habit_patterns['completion_rate']['overall'])
        
        return {
            'overall_completion_rate': np.mean(completion_rates) if completion_rates else 0,
            'most_productive_hour': max(set(all_peak_hours), key=all_peak_hours.count) if all_peak_hours else None,
            'habit_synergy_score': self._calculate_habit_synergy(all_patterns),
            'consistency_across_habits': np.std(completion_rates) if len(completion_rates) > 1 else 0
        }
    
    def _calculate_habit_synergy(self, all_patterns: Dict[int, Dict]) -> float:
        """Calculate how well habits work together"""
        
        if len(all_patterns) < 2:
            return 0.5
        
        # Simple synergy calculation based on time consistency
        time_consistencies = []
        for habit_patterns in all_patterns.values():
            if 'time_patterns' in habit_patterns and 'consistency_score' in habit_patterns['time_patterns']:
                time_consistencies.append(habit_patterns['time_patterns']['consistency_score'])
        
        if not time_consistencies:
            return 0.5
        
        # Higher average consistency indicates better synergy
        return np.mean(time_consistencies)
    
    async def _update_user_behavior_patterns(self, user_id: int, patterns: Dict[str, Any], db: Session):
        """Update user behavior patterns in database"""
        
        for pattern_type, pattern_data in patterns.items():
            # Check if pattern already exists
            existing_pattern = db.query(UserBehaviorPattern).filter(
                and_(
                    UserBehaviorPattern.user_id == user_id,
                    UserBehaviorPattern.pattern_type == pattern_type
                )
            ).first()
            
            if existing_pattern:
                existing_pattern.pattern_data = pattern_data
                existing_pattern.last_updated = datetime.utcnow()
            else:
                new_pattern = UserBehaviorPattern(
                    user_id=user_id,
                    pattern_type=pattern_type,
                    pattern_data=pattern_data,
                    confidence_score=0.8  # Default confidence
                )
                db.add(new_pattern)
    
    async def _generate_habit_insights(self, habit: Habit, patterns: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate actionable insights from patterns"""
        
        insights = []
        
        # Completion rate insights
        if 'completion_rate' in patterns:
            completion_data = patterns['completion_rate']
            
            if completion_data['trend'] == 'declining':
                insights.append({
                    'type': 'warning',
                    'title': 'Completion Rate Declining',
                    'description': f"Your completion rate for '{habit.name}' has dropped to {completion_data['last_30_days']:.1%} in the last 30 days. Consider adjusting the difficulty or frequency.",
                    'data': completion_data,
                    'confidence': 0.8
                })
            elif completion_data['overall'] >= 0.8:
                insights.append({
                    'type': 'achievement',
                    'title': 'Great Consistency!',
                    'description': f"You're maintaining an excellent {completion_data['overall']:.1%} completion rate for '{habit.name}'. Keep up the great work!",
                    'data': completion_data,
                    'confidence': 0.9
                })
        
        # Time pattern insights
        if 'time_patterns' in patterns and patterns['time_patterns'].get('peak_hour') is not None:
            time_data = patterns['time_patterns']
            peak_hour = time_data['peak_hour']
            
            insights.append({
                'type': 'pattern',
                'title': 'Optimal Time Identified',
                'description': f"You're most successful with '{habit.name}' around {peak_hour}:00. {time_data['peak_hour_percentage']:.1%} of your completions happen at this time.",
                'data': time_data,
                'confidence': time_data['peak_hour_percentage']
            })
        
        # Quality trend insights
        if 'quality_trends' in patterns and not patterns['quality_trends'].get('insufficient_data'):
            quality_data = patterns['quality_trends']
            
            if quality_data['trend'] == 'improving':
                insights.append({
                    'type': 'achievement',
                    'title': 'Quality Improving',
                    'description': f"The quality of your '{habit.name}' sessions is improving over time. Your recent average is {quality_data['recent_average']:.1f}/5.",
                    'data': quality_data,
                    'confidence': 0.7
                })
        
        # Mood/Energy insights
        if 'mood_energy_correlation' in patterns and not patterns['mood_energy_correlation'].get('insufficient_data'):
            mood_data = patterns['mood_energy_correlation']
            
            if mood_data['avg_mood_improvement'] > 0.5:
                insights.append({
                    'type': 'benefit',
                    'title': 'Positive Mood Impact',
                    'description': f"'{habit.name}' consistently improves your mood by an average of {mood_data['avg_mood_improvement']:.1f} points. This habit is great for your wellbeing!",
                    'data': mood_data,
                    'confidence': 0.8
                })
        
        # Difficulty adjustment insights
        if 'difficulty_adaptation' in patterns and not patterns['difficulty_adaptation'].get('insufficient_data'):
            difficulty_data = patterns['difficulty_adaptation']
            adjustment = difficulty_data['recommended_difficulty_adjustment']
            
            if adjustment != 'maintain':
                action = 'increase' if adjustment == 'increase' else 'reduce'
                insights.append({
                    'type': 'recommendation',
                    'title': f'Consider {action.title()}ing Difficulty',
                    'description': f"Based on your performance, you might benefit from {action}ing the difficulty or duration of '{habit.name}'.",
                    'data': difficulty_data,
                    'confidence': 0.6
                })
        
        return insights

# Global habit learning engine instance
habit_learning_engine = HabitLearningEngine()