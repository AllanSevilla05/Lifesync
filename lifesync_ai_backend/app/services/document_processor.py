import os
import re
from typing import Dict, List, Any
from datetime import datetime, timedelta
import httpx
import json

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

from app.core.config import settings

class DocumentProcessor:
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.ollama_model = settings.ollama_model
    
    async def extract_content(self, file_path: str, file_ext: str) -> str:
        """Extract text content from various document types"""
        
        if file_ext == '.txt':
            return self._extract_from_txt(file_path)
        elif file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract content from text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract content from PDF file"""
        if not PyPDF2:
            raise ValueError("PyPDF2 not installed. Cannot process PDF files.")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract content from DOCX file"""
        if not DocxDocument:
            raise ValueError("python-docx not installed. Cannot process DOCX files.")
        
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    async def extract_tasks(self, content: str) -> Dict[str, Any]:
        """Use AI to extract tasks, assignments, and deadlines from document content"""
        
        prompt = f"""You are a task extraction AI specialized in processing academic and professional documents. 
        
Analyze this document content and extract all tasks, assignments, deadlines, and important dates.

Document Content:
{content}

Extract information and return in this exact JSON format:
{{
    "tasks": [
        {{
            "title": "clear, concise task title",
            "description": "detailed description if available",
            "due_date": "YYYY-MM-DD" or null,
            "priority": 1-5 (based on urgency/importance),
            "estimated_duration": minutes_or_null,
            "category": "assignment/exam/project/meeting/other",
            "source_text": "original text from document"
        }}
    ],
    "important_dates": [
        {{
            "date": "YYYY-MM-DD",
            "event": "description of event",
            "type": "deadline/exam/meeting/other"
        }}
    ],
    "course_info": {{
        "course_name": "extracted course name or null",
        "instructor": "instructor name or null",
        "semester": "semester info or null"
    }},
    "confidence": 0.0-1.0,
    "extraction_notes": "any relevant notes about the extraction"
}}

Guidelines:
1. Look for keywords like: assignment, homework, project, exam, quiz, due, deadline, submit
2. Extract dates in various formats (MM/DD/YYYY, Month DD, etc.)
3. Infer priority from words like "final", "major", "important", "urgent"
4. Estimate duration based on task complexity (reading: 30-60min, assignments: 2-4hrs, projects: 6-20hrs)
5. For syllabi: extract all assignments and their due dates
6. For schedules: extract meetings, classes, and events
7. Be conservative with confidence scores

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
                            "temperature": 0.3,  # Lower temperature for more consistent extraction
                            "max_tokens": 2000
                        }
                    },
                    timeout=30.0
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
                        # Fallback to rule-based extraction
                        return self._fallback_task_extraction(content)
                else:
                    return self._fallback_task_extraction(content)
                    
        except Exception as e:
            print(f"Task extraction error: {e}")
            return self._fallback_task_extraction(content)
    
    def _fallback_task_extraction(self, content: str) -> Dict[str, Any]:
        """Simple rule-based task extraction when AI is unavailable"""
        
        tasks = []
        important_dates = []
        
        # Common task keywords
        task_keywords = ['assignment', 'homework', 'project', 'essay', 'report', 'quiz', 'exam', 'test', 'paper']
        
        # Date patterns
        date_patterns = [
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{1,2}/\d{1,2}/\d{2})\b',   # MM/DD/YY
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for task-related lines
            line_lower = line.lower()
            
            # Check if line contains task keywords
            for keyword in task_keywords:
                if keyword in line_lower:
                    # Extract dates from the same line
                    due_date = None
                    for pattern in date_patterns:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        if matches:
                            # Simple date parsing (you'd want to improve this)
                            due_date = matches[0]
                            break
                    
                    # Determine priority
                    priority = 3  # Default
                    if any(word in line_lower for word in ['final', 'major', 'important']):
                        priority = 5
                    elif any(word in line_lower for word in ['quiz', 'minor']):
                        priority = 2
                    
                    # Estimate duration based on task type
                    duration = None
                    if 'quiz' in line_lower:
                        duration = 30
                    elif any(word in line_lower for word in ['essay', 'paper', 'report']):
                        duration = 240  # 4 hours
                    elif 'project' in line_lower:
                        duration = 600  # 10 hours
                    elif any(word in line_lower for word in ['assignment', 'homework']):
                        duration = 120  # 2 hours
                    
                    tasks.append({
                        "title": line[:100],  # Truncate long titles
                        "description": "",
                        "due_date": due_date,
                        "priority": priority,
                        "estimated_duration": duration,
                        "category": self._categorize_task(line_lower),
                        "source_text": line
                    })
                    break
        
        return {
            "tasks": tasks[:20],  # Limit to prevent overwhelming
            "important_dates": important_dates,
            "course_info": {
                "course_name": None,
                "instructor": None,
                "semester": None
            },
            "confidence": 0.6,
            "extraction_notes": "Fallback rule-based extraction used"
        }
    
    def _categorize_task(self, text: str) -> str:
        """Simple categorization of tasks"""
        if any(word in text for word in ['exam', 'test', 'quiz']):
            return 'exam'
        elif any(word in text for word in ['project', 'presentation']):
            return 'project'
        elif any(word in text for word in ['assignment', 'homework']):
            return 'assignment'
        elif any(word in text for word in ['meeting', 'class', 'lecture']):
            return 'meeting'
        else:
            return 'other'