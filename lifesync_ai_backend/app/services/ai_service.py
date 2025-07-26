import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from app.core.config import settings

class AIService:
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.ollama_model = settings.ollama_model
    
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
        
        # Build a comprehensive prompt that includes conversation context
        context_info = ""
        if context and context.strip():
            context_info = f"""
CONVERSATION CONTEXT:
{context}

IMPORTANT: Analyze the current input in the context of the previous conversation. 
Consider how this input relates to or builds upon previous requests.
"""
        
        prompt = f"""You are a task extraction AI. Parse this voice input and extract actionable tasks, considering the full conversation context.

{context_info}
Current Voice Input: "{voice_text}"

IMPORTANT: Use the LOCAL TIME INFORMATION provided in the context for all date calculations. 
Do NOT use server time - use the user's local timezone and time.

TASK TITLE GUIDELINES:
- Create concise, actionable task titles (3-8 words max)
- Focus on the core action/objective, not the full voice input
- Use professional, clear language
- Remove filler words like "I need to", "don't forget", "also", etc.
- Make titles specific and actionable

Extract tasks and return in this exact JSON format:
{{
    "tasks": [
        {{
            "title": "concise task title",
            "description": "optional description with more details from voice input",
            "priority": 1-5,
            "estimated_duration": minutes_or_null,
            "due_date": "YYYY-MM-DD" or null,
            "tags": ["tag1", "tag2"]
        }}
    ],
    "confidence": 0.0-1.0,
    "parsing_notes": "any relevant notes about the parsing",
    "conversation_analysis": "brief analysis of how this input relates to previous conversation"
}}

Task Title Examples:
- "I need to buy groceries tomorrow" → "Buy groceries"
- "Don't forget about the dentist appointment on Friday" → "Dentist appointment"
- "Also, schedule a meeting with John next week" → "Schedule meeting with John"
- "I should exercise for 30 minutes tomorrow morning" → "30-minute workout"
- "Work on my business proposal" → "Business proposal"
- "Call mom and dad this weekend" → "Call parents"
- "Pick up dry cleaning after work" → "Pick up dry cleaning"
- "Finish the quarterly report by Friday" → "Complete quarterly report"

Context Analysis Guidelines:
1. If the input references previous tasks (e.g., "also", "don't forget", "and"), consider it as additional to previous requests
2. If the input modifies previous requests (e.g., "change the time", "update"), treat as modifications
3. If the input is completely new, treat as independent tasks
4. Consider temporal relationships (e.g., "before that", "after lunch")
5. Look for implicit connections to previous conversation

Time Calculation Rules:
1. ALWAYS use the LOCAL TIME INFORMATION from the context
2. "tomorrow" = local date + 1 day
3. "next week" = local date + 7 days
4. "next Monday" = next occurrence of Monday from local date
5. "July 30" = July 30th of current year (or next year if passed)
6. All date calculations must be based on the user's local timezone

Focus on:
1. Creating concise, actionable task titles
2. Extracting time/duration information
3. Inferring priority from urgency words
4. Identifying due dates and deadlines (using local time)
5. Understanding context from conversation history
6. Recognizing task modifications or additions

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
                            "max_tokens": 1000  # Increased for context analysis
                        }
                    },
                    timeout=20.0  # Increased timeout for context processing
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
                        # Fallback parsing with context
                        return self._fallback_voice_parsing_with_context(voice_text, context)
                else:
                    return self._fallback_voice_parsing_with_context(voice_text, context)
                    
        except Exception as e:
            print(f"Voice parsing error: {e}")
            return self._fallback_voice_parsing_with_context(voice_text, context)
    
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
                due_date = None
                
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
                
                # Date parsing
                due_date = self._extract_date_from_text(task_text)
                
                tasks.append({
                    "title": task_text,
                    "priority": priority,
                    "estimated_duration": duration,
                    "due_date": due_date,
                    "tags": []
                })
        
        return {
            "tasks": tasks,
            "confidence": 0.6,
            "parsing_notes": "Fallback parsing used"
        }
    
    def _fallback_voice_parsing_with_context(self, voice_text: str, context: str = None) -> Dict[str, Any]:
        """Enhanced fallback parsing that considers conversation context"""
        
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
        
        # Analyze context for additional context
        context_analysis = ""
        if context:
            context_analysis = "Analyzed with conversation context"
            # Look for context clues in the current input
            if any(word in voice_text.lower() for word in ['also', 'too', 'as well', 'don\'t forget', 'remember']):
                context_analysis += " - Appears to be additional to previous requests"
            if any(word in voice_text.lower() for word in ['change', 'update', 'modify', 'instead']):
                context_analysis += " - Appears to be modifying previous requests"
        
        for task_text in potential_tasks:
            task_text = task_text.strip()
            if task_text:
                priority = 3  # Default priority
                duration = None
                
                # Create a concise task title
                title = self._create_concise_title(task_text)
                
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
                
                # Date parsing
                due_date = self._extract_date_from_text(task_text, context)
                
                tasks.append({
                    "title": title,
                    "description": task_text,  # Keep original text as description
                    "priority": priority,
                    "estimated_duration": duration,
                    "due_date": due_date,
                    "tags": []
                })
        
        return {
            "tasks": tasks,
            "confidence": 0.6,
            "parsing_notes": "Fallback parsing used",
            "conversation_analysis": context_analysis or "No conversation context provided"
        }
    
    def _create_concise_title(self, task_text: str) -> str:
        """Create a concise, actionable task title from voice input"""
        import re
        
        # Remove common filler words and phrases
        text = task_text.lower()
        
        # Remove common prefixes
        prefixes_to_remove = [
            r'^i\s+(need\s+to|want\s+to|should|have\s+to|must|gotta|got\s+to)\s+',
            r'^don\'t\s+forget\s+(to\s+)?',
            r'^remember\s+(to\s+)?',
            r'^also\s+',
            r'^and\s+',
            r'^please\s+',
            r'^can\s+you\s+',
            r'^could\s+you\s+',
            r'^would\s+you\s+',
            r'^i\s+think\s+i\s+',
            r'^i\s+guess\s+i\s+',
            r'^maybe\s+i\s+',
        ]
        
        for pattern in prefixes_to_remove:
            text = re.sub(pattern, '', text)
        
        # Remove time-related phrases that don't add to the task
        time_phrases = [
            r'\s+(tomorrow|today|next\s+week|this\s+weekend|tonight|morning|afternoon|evening)\s*$',
            r'\s+by\s+(tomorrow|friday|monday|next\s+week)\s*$',
            r'\s+at\s+\d+(\:\d+)?\s*(am|pm)?\s*$',
        ]
        
        for pattern in time_phrases:
            text = re.sub(pattern, '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Capitalize first letter of each word
        words = text.split()
        if len(words) > 8:  # If still too long, take first 8 words
            words = words[:8]
        
        title = ' '.join(word.capitalize() for word in words)
        
        # Handle empty or very short titles
        if len(title) < 3:
            title = task_text[:50].strip()  # Fallback to first 50 chars
        
        return title
    
    def _extract_date_from_text(self, text: str, context: str = None) -> str:
        """Extract date from text using various patterns, using local time from context"""
        from datetime import datetime, timedelta
        import re

        # Parse local time information from context
        local_time = None
        timezone = None
        
        if context:
            # Extract timezone from context
            timezone_match = re.search(r'Timezone: ([^\n]+)', context)
            if timezone_match:
                timezone = timezone_match.group(1).strip()
            
            # Extract local time from context
            local_time_match = re.search(r'Local Date/Time: ([^\n]+)', context)
            if local_time_match:
                try:
                    local_time_str = local_time_match.group(1).strip()
                    # Parse the local time string (format: "January 15, 2024 at 02:30:45 PM")
                    local_time = datetime.strptime(local_time_str, "%B %d, %Y at %I:%M:%S %p")
                except ValueError:
                    pass
        
        # Use local time if available, otherwise fall back to server time
        if local_time:
            today = local_time
        else:
            today = datetime.now()

        text_lower = text.lower()

        # Pattern 1: Specific dates like "July 30", "30th of July", "July 30th"
        month_patterns = [
            r'(january|jan)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(february|feb)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(march|mar)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(april|apr)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(may)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(june|jun)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(july|jul)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(august|aug)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(september|sept|sep)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(october|oct)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(november|nov)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(december|dec)\s+(\d{1,2})(?:st|nd|rd|th)?',
        ]

        month_names = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sept': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }

        # Check for specific month + day patterns
        for pattern in month_patterns:
            match = re.search(pattern, text_lower)
            if match:
                month_name = match.group(1)
                day = int(match.group(2))
                month = month_names[month_name]

                # Determine year (assume current year or next year if date has passed)
                year = today.year
                try:
                    target_date = datetime(year, month, day)
                    if target_date < today:
                        # If date has passed this year, assume next year
                        target_date = datetime(year + 1, month, day)
                    return target_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        # Pattern 2: Relative dates like "tomorrow", "next week", "in 3 days"
        if 'tomorrow' in text_lower:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')

        if 'next week' in text_lower:
            next_week = today + timedelta(weeks=1)
            return next_week.strftime('%Y-%m-%d')

        if 'next month' in text_lower:
            # Simple next month calculation
            if today.month == 12:
                next_month = datetime(today.year + 1, 1, today.day)
            else:
                next_month = datetime(today.year, today.month + 1, today.day)
            return next_month.strftime('%Y-%m-%d')

        # Pattern 3: "in X days"
        days_match = re.search(r'in\s+(\d+)\s+days?', text_lower)
        if days_match:
            days = int(days_match.group(1))
            future_date = today + timedelta(days=days)
            return future_date.strftime('%Y-%m-%d')

        # Pattern 4: Day of week like "next Monday", "this Friday"
        day_patterns = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1, 'tues': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thurs': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }

        for day_name, day_num in day_patterns.items():
            if f'next {day_name}' in text_lower:
                # Find next occurrence of this day
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0:  # If it's today, get next week
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')

            if f'this {day_name}' in text_lower:
                # Find this week's occurrence of this day
                days_ahead = (day_num - today.weekday()) % 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')

        # Pattern 5: "by Friday", "due Monday" etc.
        for day_name, day_num in day_patterns.items():
            if f'by {day_name}' in text_lower or f'due {day_name}' in text_lower:
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0:  # If it's today, get next week
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')

        return None
    
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
