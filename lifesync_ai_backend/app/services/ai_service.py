import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from app.core.config import settings

class AIService:
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.ollama_model = settings.ollama_model
    
    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """Generic method to generate AI responses"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }
                    },
                    timeout=20.0
                )
                
                if response.status_code == 200:
                    ollama_response = response.json()
                    ai_output = ollama_response.get("response", "")
                    
                    # Try to parse JSON response
                    try:
                        json_start = ai_output.find('{')
                        json_end = ai_output.rfind('}') + 1
                        if json_start != -1 and json_end != 0:
                            clean_json = ai_output[json_start:json_end]
                            return json.loads(clean_json)
                        else:
                            return {"response": ai_output, "raw": True}
                    except json.JSONDecodeError:
                        return {"response": ai_output, "raw": True}
                else:
                    return {"error": f"API error: {response.status_code}", "response": ""}
                    
        except Exception as e:
            return {"error": str(e), "response": ""}
    
    async def optimize_daily_schedule(
        self, 
        tasks: List[Dict], 
        user_preferences: Dict,
        mood_data: Dict,
        current_time: datetime
    ) -> Dict[str, Any]:
        """
        Use Ollama AI to optimize the user's daily schedule based on:
        - Tasks and their priorities
        - User's productivity patterns
        - Current mood and energy
        - Historical completion data
        """
        
        prompt = f"""You are LifeSync AI, an expert productivity assistant. Analyze and optimize this user's daily schedule.

Current Time: {current_time}

Tasks to schedule:
{json.dumps(tasks, indent=2, default=str)}

User Preferences:
{json.dumps(user_preferences, indent=2)}

Current Mood/Energy Data:
{json.dumps(mood_data, indent=2)}

Please provide an optimized schedule with the following JSON format:
{{
    "optimized_schedule": [
        {{
            "task_id": 1,
            "suggested_time": "2024-01-15T09:00:00",
            "duration_minutes": 60,
            "reasoning": "High energy task scheduled during peak productivity"
        }}
    ],
    "break_suggestions": [
        {{
            "time": "2024-01-15T10:30:00",
            "duration_minutes": 15,
            "type": "short_break"
        }}
    ],
    "wellness_recommendations": [
        "Take a 5-minute breathing exercise at 2 PM",
        "Hydrate every hour"
    ],
    "schedule_insights": "Your energy levels suggest focusing on creative tasks in the morning",
    "ai_confidence": 0.85
}}

Focus on:
1. Matching high-energy tasks with user's peak productivity times
2. Balancing work intensity throughout the day
3. Including appropriate breaks
4. Considering task priorities and deadlines
5. Factoring in current mood and energy levels

Respond only with valid JSON."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 1500
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    ollama_response = response.json()
                    ai_output = ollama_response.get("response", "")
                    
                    # Try to parse JSON from the response
                    try:
                        # Clean the response - sometimes models include extra text
                        json_start = ai_output.find('{')
                        json_end = ai_output.rfind('}') + 1
                        if json_start != -1 and json_end != 0:
                            clean_json = ai_output[json_start:json_end]
                            return json.loads(clean_json)
                        else:
                            raise ValueError("No JSON found in response")
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"JSON parsing error: {e}")
                        return self._fallback_scheduling(tasks, user_preferences)
                else:
                    print(f"Ollama API error: {response.status_code}")
                    return self._fallback_scheduling(tasks, user_preferences)
                    
        except Exception as e:
            print(f"AI service error: {e}")
            return self._fallback_scheduling(tasks, user_preferences)
    
    async def parse_voice_input(self, voice_text: str, context: str = None) -> Dict[str, Any]:
        """Parse natural language input using Ollama to extract tasks and intentions"""
        
        prompt = f"""You are a task extraction AI. Parse this voice input and extract actionable tasks.

Voice Input: "{voice_text}"
Context: {context or "None"}

Extract tasks and return in this exact JSON format:
{{
    "tasks": [
        {{
            "title": "extracted task title",
            "description": "optional description",
            "priority": 1-5,
            "estimated_duration": minutes_or_null,
            "due_date": "YYYY-MM-DD" or null,
            "tags": ["tag1", "tag2"]
        }}
    ],
    "confidence": 0.0-1.0,
    "parsing_notes": "any relevant notes about the parsing"
}}

Examples:
- "I need to shop, exercise, and work on my business proposal" → 3 separate tasks
- "Finish the report by Friday" → 1 task with due date
- "30 minute workout tomorrow morning" → 1 task with duration and timing

Focus on:
1. Splitting compound requests into individual tasks
2. Extracting time/duration information
3. Inferring priority from urgency words
4. Identifying due dates and deadlines

Respond only with valid JSON."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more consistent parsing
                            "max_tokens": 800
                        }
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    ollama_response = response.json()
                    ai_output = ollama_response.get("response", "")
                    
                    try:
                        # Extract JSON from response
                        json_start = ai_output.find('{')
                        json_end = ai_output.rfind('}') + 1
                        if json_start != -1 and json_end != 0:
                            clean_json = ai_output[json_start:json_end]
                            return json.loads(clean_json)
                        else:
                            raise ValueError("No JSON found")
                    except (json.JSONDecodeError, ValueError):
                        # Fallback parsing
                        return self._fallback_voice_parsing(voice_text)
                else:
                    return self._fallback_voice_parsing(voice_text)
                    
        except Exception as e:
            print(f"Voice parsing error: {e}")
            return self._fallback_voice_parsing(voice_text)
    
    async def suggest_wellness_actions(
        self, 
        mood_level: int, 
        energy_level: int, 
        stress_level: int,
        recent_activities: List[Dict]
    ) -> Dict[str, Any]:
        """Use Ollama to suggest personalized wellness actions based on current state"""
        
        prompt = f"""You are a wellness AI assistant. Based on the user's current state, suggest 3-5 specific, actionable wellness recommendations.

Current State:
- Mood Level: {mood_level}/10
- Energy Level: {energy_level}/10  
- Stress Level: {stress_level}/10

Recent Activities:
{json.dumps(recent_activities, indent=2)}

Provide personalized suggestions in this JSON format:
{{
    "suggestions": [
        {{
            "action": "specific action to take",
            "duration": "time needed",
            "reasoning": "why this helps",
            "urgency": "low/medium/high"
        }}
    ],
    "overall_assessment": "brief assessment of current state",
    "focus_area": "primary area to address (energy/mood/stress/balance)"
}}

Guidelines:
- Low energy (1-3): Suggest energizing activities, nutrition, movement
- Low mood (1-4): Suggest mood-boosting activities, social connection, creativity  
- High stress (7-10): Suggest stress relief, breathing, breaks
- Consider time of day and recent activities
- Make suggestions specific and actionable
- Prioritize immediate, practical actions

Respond only with valid JSON."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.6,
                            "max_tokens": 600
                        }
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    ollama_response = response.json()
                    ai_output = ollama_response.get("response", "")
                    
                    try:
                        json_start = ai_output.find('{')
                        json_end = ai_output.rfind('}') + 1
                        if json_start != -1 and json_end != 0:
                            clean_json = ai_output[json_start:json_end]
                            return json.loads(clean_json)
                        else:
                            raise ValueError("No JSON found")
                    except (json.JSONDecodeError, ValueError):
                        return self._fallback_wellness_suggestions(mood_level, energy_level, stress_level)
                else:
                    return self._fallback_wellness_suggestions(mood_level, energy_level, stress_level)
                    
        except Exception as e:
            print(f"Wellness suggestion error: {e}")
            return self._fallback_wellness_suggestions(mood_level, energy_level, stress_level)
    
    def _fallback_voice_parsing(self, voice_text: str) -> Dict[str, Any]:
        """Simple fallback for voice input parsing when AI is unavailable"""
        
        # Basic keyword detection
        tasks = []
        
        # Split on common separators
        potential_tasks = []
        for separator in [' and ', ', ', ' then ', ' also ']:
            if separator in voice_text.lower():
                potential_tasks = voice_text.split(separator)
                break
        
        if not potential_tasks:
            potential_tasks = [voice_text]
        
        for task_text in potential_tasks:
            task_text = task_text.strip()
            if task_text:
                priority = 3  # Default priority
                duration = None
                
                # Simple priority detection
                if any(word in task_text.lower() for word in ['urgent', 'asap', 'immediately']):
                    priority = 5
                elif any(word in task_text.lower() for word in ['important', 'must', 'need to']):
                    priority = 4
                
                # Simple duration detection
                import re
                duration_match = re.search(r'(\d+)\s*(minute|hour|min|hr)', task_text.lower())
                if duration_match:
                    num = int(duration_match.group(1))
                    unit = duration_match.group(2)
                    if unit in ['hour', 'hr']:
                        duration = num * 60
                    else:
                        duration = num
                
                tasks.append({
                    "title": task_text,
                    "priority": priority,
                    "estimated_duration": duration,
                    "due_date": None,
                    "tags": []
                })
        
        return {
            "tasks": tasks,
            "confidence": 0.6,
            "parsing_notes": "Fallback parsing used"
        }
    
    def _fallback_wellness_suggestions(self, mood_level: int, energy_level: int, stress_level: int) -> Dict[str, Any]:
        """Simple fallback wellness suggestions when AI is unavailable"""
        
        suggestions = []
        focus_area = "balance"
        
        if energy_level <= 3:
            suggestions.extend([
                {
                    "action": "Take a 10-minute walk outside",
                    "duration": "10 minutes",
                    "reasoning": "Fresh air and movement boost energy",
                    "urgency": "medium"
                },
                {
                    "action": "Have a healthy snack with protein",
                    "duration": "5 minutes",
                    "reasoning": "Stabilize blood sugar for sustained energy",
                    "urgency": "high"
                }
            ])
            focus_area = "energy"
        
        if stress_level >= 7:
            suggestions.extend([
                {
                    "action": "Try 4-7-8 breathing exercise",
                    "duration": "3 minutes",
                    "reasoning": "Activates parasympathetic nervous system",
                    "urgency": "high"
                },
                {
                    "action": "Take a 15-minute break from work",
                    "duration": "15 minutes",
                    "reasoning": "Prevent burnout and reset focus",
                    "urgency": "medium"
                }
            ])
            focus_area = "stress"
        
        if mood_level <= 4:
            suggestions.extend([
                {
                    "action": "Listen to uplifting music",
                    "duration": "10 minutes",
                    "reasoning": "Music triggers mood-boosting chemicals",
                    "urgency": "low"
                },
                {
                    "action": "Write down 3 things you're grateful for",
                    "duration": "5 minutes",
                    "reasoning": "Gratitude practice improves mood",
                    "urgency": "low"
                }
            ])
            if focus_area == "balance":
                focus_area = "mood"
        
        return {
            "suggestions": suggestions[:4],  # Limit to top 4
            "overall_assessment": f"Current state shows focus needed on {focus_area}",
            "focus_area": focus_area
        }
    
    def _fallback_scheduling(self, tasks: List[Dict], preferences: Dict) -> Dict[str, Any]:
        """Simple fallback scheduling when Ollama is unavailable"""
        
        # Sort by priority and due date
        sorted_tasks = sorted(
            tasks, 
            key=lambda x: (-x.get('priority', 1), x.get('due_date', '9999-12-31'))
        )
        
        schedule = []
        current_time = datetime.now()
        
        # Get user's peak productivity time
        peak_time = preferences.get('productivity_peak', 'morning')
        
        for i, task in enumerate(sorted_tasks):
            # Calculate suggested time based on user preferences
            if peak_time == 'morning':
                suggested_hour = 9 + i  # Start at 9 AM
            elif peak_time == 'afternoon':
                suggested_hour = 13 + i  # Start at 1 PM
            else:  # evening
                suggested_hour = 18 + i  # Start at 6 PM
            
            suggested_time = current_time.replace(
                hour=min(suggested_hour, 22),  # Don't go past 10 PM
                minute=0,
                second=0,
                microsecond=0
            )
            
            schedule.append({
                "task_id": task.get('id'),
                "suggested_time": suggested_time.isoformat(),
                "duration_minutes": task.get('estimated_duration', 60),
                "reasoning": f"Scheduled during {peak_time} productivity window"
            })
        
        return {
            "optimized_schedule": schedule,
            "break_suggestions": [
                {
                    "time": (current_time + timedelta(hours=2)).isoformat(),
                    "duration_minutes": 15,
                    "type": "short_break"
                }
            ],
            "wellness_recommendations": [
                "Stay hydrated throughout the day",
                "Take breaks every 2 hours"
            ],
            "schedule_insights": f"Tasks scheduled for {peak_time} based on your preferences",
            "ai_confidence": 0.7
        }
