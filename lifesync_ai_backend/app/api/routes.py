# app/api/routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.llama_service import LlamaService
from app.schemas.task_schemas import (
    TaskInput, ParsedTasksResponse, ScheduleRequest, ScheduleResponse,
    DocumentUpload, DocumentProcessResponse, WellnessRequest, WellnessResponse,
    UserBehaviorData, BehaviorAnalysisResponse
)
import json

router = APIRouter()
llama_service = LlamaService()

@router.post("/parse-task", response_model=ParsedTasksResponse)
async def parse_task_command(task_input: TaskInput):
    """
    Parse user's voice or text input to extract tasks
    """
    try:
        result = await llama_service.parse_task_command(task_input.user_input)
        
        if result and "tasks" in result:
            return ParsedTasksResponse(
                success=True,
                tasks=result["tasks"],
                message="Tasks parsed successfully"
            )
        else:
            return ParsedTasksResponse(
                success=False,
                tasks=[],
                message="No tasks could be extracted from input"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing tasks: {str(e)}")

@router.post("/suggest-schedule", response_model=ScheduleResponse)
async def suggest_schedule(schedule_request: ScheduleRequest):
    """
    Generate AI-optimized schedule based on tasks and user preferences
    """
    try:
        # Convert Pydantic models to dicts for Llama service
        tasks_dict = [task.dict() for task in schedule_request.tasks]
        preferences_dict = schedule_request.user_preferences.dict()
        
        result = await llama_service.suggest_schedule(
            tasks_dict, 
            preferences_dict, 
            schedule_request.user_history
        )
        
        if result and "schedule" in result:
            return ScheduleResponse(
                success=True,
                schedule=result["schedule"],
                message="Schedule generated successfully"
            )
        else:
            return ScheduleResponse(
                success=False,
                schedule=[],
                message="Could not generate schedule"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating schedule: {str(e)}")

@router.post("/process-document", response_model=DocumentProcessResponse)
async def process_document(document: DocumentUpload):
    """
    Process uploaded document (like syllabus) to extract tasks and deadlines
    """
    try:
        result = await llama_service.process_document(
            document.document_text, 
            document.document_type
        )
        
        if result and "extracted_items" in result:
            return DocumentProcessResponse(
                success=True,
                extracted_items=result["extracted_items"],
                message="Document processed successfully"
            )
        else:
            return DocumentProcessResponse(
                success=False,
                extracted_items=[],
                message="Could not extract items from document"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle file upload and extract text for processing
    """
    try:
        content = await file.read()
        
        # Handle different file types
        if file.content_type == "text/plain":
            text_content = content.decode("utf-8")
        elif file.content_type == "application/pdf":
            # You'll need to add PDF processing library like PyPDF2
            text_content = "PDF processing not implemented yet"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Process the extracted text
        result = await llama_service.process_document(text_content, "uploaded_file")
        
        return {
            "success": True,
            "filename": file.filename,
            "extracted_items": result.get("extracted_items", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/wellness-suggestions", response_model=WellnessResponse)
async def get_wellness_suggestions(wellness_request: WellnessRequest):
    """
    Get AI-powered wellness suggestions based on mood and schedule
    """
    try:
        mood_dict = wellness_request.mood_data.dict()
        schedule_dict = wellness_request.schedule_data
        
        result = await llama_service.suggest_wellness_actions(mood_dict, schedule_dict)
        
        if result and "wellness_suggestions" in result:
            return WellnessResponse(
                success=True,
                wellness_suggestions=result["wellness_suggestions"],
                message="Wellness suggestions generated"
            )
        else:
            return WellnessResponse(
                success=False,
                wellness_suggestions=[],
                message="Could not generate wellness suggestions"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating wellness suggestions: {str(e)}")

@router.post("/analyze-behavior", response_model=BehaviorAnalysisResponse)
async def analyze_user_behavior(behavior_data: UserBehaviorData):
    """
    Analyze user behavior patterns to improve future AI suggestions
    """
    try:
        completion_data = behavior_data.task_completions
        
        result = await llama_service.analyze_user_behavior(completion_data)
        
        if result and "insights" in result:
            return BehaviorAnalysisResponse(
                success=True,
                insights=result["insights"],
                message="Behavior analysis completed"
            )
        else:
            return BehaviorAnalysisResponse(
                success=False,
                insights={},
                message="Could not analyze behavior patterns"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing behavior: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "service": "LifeSync AI Backend"}

@router.get("/models")
async def list_available_models():
    """
    List available Llama models
    """
    try:
        # This would connect to Ollama to list models
        return {"models": ["llama2", "llama3.1", "codellama"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")