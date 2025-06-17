# app/services/llama_service.py
import ollama
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class LlamaService:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.client = ollama.Client()
    
    async def parse_task_command(self, user_input: str) -> Dict:
        """
        Parse user input to extract tasks and their details
        """
        prompt = f"""
        You are a task extraction AI for LifeSync app. Extract tasks from the user input and return ONLY valid JSON.
        
        User input: "{user_input}"
        
        Extract tasks with these properties:
        - name: task description
        - priority: high/medium/low
        - category: work/personal/health/academic
        - estimated_duration: in minutes (number only)
        - due_date: if mentioned, return as YYYY-MM-DD, otherwise null
        
        Return format:
        {{"tasks": [{{"name": "task name", "priority": "medium", "category": "personal", "estimated_duration": 30, "due_date": null}}]}}
        
        JSON only, no explanation:
        """
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            return self._parse_json_response(response['response'])
        except Exception as e:
            print(f"Error in parse_task_command: {e}")
            return {"tasks": []}
    
    async def suggest_schedule(self, tasks: List[Dict], user_preferences: Dict, user_history: Dict = None) -> Dict:
        """
        Generate optimized schedule based on tasks and user patterns
        """
        prompt = f"""
        You are a scheduling AI for LifeSync. Create an optimal daily schedule.
        
        Tasks to schedule: {json.dumps(tasks)}
        User preferences: {json.dumps(user_preferences)}
        User history patterns: {json.dumps(user_history or {})}
        
        Consider:
        - User's productive hours
        - Task priorities and deadlines
        - Energy levels throughout the day
        - Break times and meals
        
        Return schedule as JSON with time slots:
        {{"schedule": [{{"time": "09:00", "duration": 60, "task": "task name", "type": "work/break/meal"}}]}}
        
        JSON only:
        """
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.4}
            )
            
            return self._parse_json_response(response['response'])
        except Exception as e:
            print(f"Error in suggest_schedule: {e}")
            return {"schedule": []}
    
    async def process_document(self, document_text: str, document_type: str = "syllabus") -> Dict:
        """
        Process uploaded documents to extract tasks and deadlines
        """
        prompt = f"""
        Extract tasks and deadlines from this {document_type}:
        
        {document_text}
        
        Find:
        - Assignment names
        - Due dates
        - Exam dates
        - Project milestones
        
        Return as JSON:
        {{"extracted_items": [{{"name": "Assignment 1", "type": "assignment", "due_date": "2025-07-15", "description": "Math homework"}}]}}
        
        JSON only:
        """
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.2}
            )
            
            return self._parse_json_response(response['response'])
        except Exception as e:
            print(f"Error in process_document: {e}")
            return {"extracted_items": []}
    
    async def analyze_user_behavior(self, completion_data: List[Dict]) -> Dict:
        """
        Analyze user's task completion patterns to improve future suggestions
        """
        prompt = f"""
        Analyze this user's task completion patterns:
        
        {json.dumps(completion_data)}
        
        Find patterns in:
        - Best times for different task types
        - Average completion times
        - Success rates by time of day
        - Preferred task ordering
        
        Return insights as JSON:
        {{"insights": {{"best_work_hours": ["09:00", "14:00"], "avg_task_duration": {{"work": 45, "personal": 30}}, "success_patterns": "description"}}}}
        
        JSON only:
        """
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            return self._parse_json_response(response['response'])
        except Exception as e:
            print(f"Error in analyze_user_behavior: {e}")
            return {"insights": {}}
    
    async def suggest_wellness_actions(self, mood_data: Dict, schedule_data: Dict) -> Dict:
        """
        Suggest wellness actions based on mood and current schedule
        """
        prompt = f"""
        Based on user's current mood and schedule, suggest wellness actions:
        
        Mood data: {json.dumps(mood_data)}
        Current schedule: {json.dumps(schedule_data)}
        
        Suggest appropriate:
        - Break times
        - Hydration reminders
        - Movement/exercise
        - Meal suggestions
        - Rest periods
        
        Return as JSON:
        {{"wellness_suggestions": [{{"type": "break", "time": "10:30", "action": "5-minute walk", "reason": "mental refresh"}}]}}
        
        JSON only:
        """
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={"temperature": 0.4}
            )
            
            return self._parse_json_response(response['response'])
        except Exception as e:
            print(f"Error in suggest_wellness_actions: {e}")
            return {"wellness_suggestions": []}
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        Extract and parse JSON from Llama's response
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                print(f"No JSON found in response: {response}")
                return {}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response was: {response}")
            return {}
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            return {}