from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.models import User, Document, Task
from app.schemas.task import TaskCreate
from app.api.v1.endpoints.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.core.config import settings

router = APIRouter()
document_processor = DocumentProcessor()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "general",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document to extract tasks and deadlines"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create database record
        db_document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            document_type=document_type,
            processing_status="pending"
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Process document asynchronously (in a real app, you'd use Celery or similar)
        try:
            # Extract content and tasks
            extracted_content = await document_processor.extract_content(file_path, file_ext)
            extracted_tasks = await document_processor.extract_tasks(extracted_content)
            
            # Update document record
            db_document.extracted_content = extracted_content
            db_document.extracted_tasks = extracted_tasks
            db_document.processed = True
            db_document.processing_status = "completed"
            db_document.processed_at = datetime.utcnow()
            
            # Create tasks from extracted data
            created_tasks = []
            for task_data in extracted_tasks.get("tasks", []):
                db_task = Task(
                    user_id=current_user.id,
                    title=task_data.get("title"),
                    description=task_data.get("description", ""),
                    due_date=task_data.get("due_date"),
                    priority=task_data.get("priority", 2),
                    estimated_duration=task_data.get("estimated_duration")
                )
                db.add(db_task)
                created_tasks.append(db_task)
            
            db.commit()
            
            return {
                "document_id": db_document.id,
                "filename": file.filename,
                "processing_status": "completed",
                "extracted_tasks_count": len(created_tasks),
                "extracted_tasks": extracted_tasks
            }
            
        except Exception as processing_error:
            # Update status to failed
            db_document.processing_status = "failed"
            db.commit()
            
            return {
                "document_id": db_document.id,
                "filename": file.filename,
                "processing_status": "failed",
                "error": str(processing_error)
            }
    
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/")
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.uploaded_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "document_type": doc.document_type,
            "file_size": doc.file_size,
            "processed": doc.processed,
            "processing_status": doc.processing_status,
            "uploaded_at": doc.uploaded_at,
            "processed_at": doc.processed_at,
            "extracted_tasks_count": len(doc.extracted_tasks.get("tasks", [])) if doc.extracted_tasks else 0
        }
        for doc in documents
    ]

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "file_size": document.file_size,
        "processed": document.processed,
        "processing_status": document.processing_status,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "extracted_content": document.extracted_content,
        "extracted_tasks": document.extracted_tasks
    }

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its associated file"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}