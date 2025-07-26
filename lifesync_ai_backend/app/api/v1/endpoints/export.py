from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import json
import csv
import io
from datetime import datetime
from typing import Literal

from app.core.database import get_db
from app.models.models import User, Task, MoodEntry, Document
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/data")
async def export_user_data(
    format: Literal["json", "csv"] = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data in JSON or CSV format"""
    
    # Get all user data
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    mood_entries = db.query(MoodEntry).filter(MoodEntry.user_id == current_user.id).all()
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    if format == "json":
        return _export_json(current_user, tasks, mood_entries, documents)
    else:
        return _export_csv(current_user, tasks, mood_entries, documents)

@router.get("/tasks")
async def export_tasks(
    format: Literal["json", "csv"] = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export only tasks data"""
    
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    if format == "json":
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "status": task.status,
                "estimated_duration": task.estimated_duration,
                "actual_duration": task.actual_duration,
                "completion_percentage": task.completion_percentage,
                "tags": task.tags,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
        
        return Response(
            content=json.dumps(tasks_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=lifesync_tasks_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
    
    else:  # CSV format
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "ID", "Title", "Description", "Due Date", "Priority", "Status",
            "Estimated Duration", "Actual Duration", "Completion %", "Tags",
            "Created At", "Updated At", "Completed At"
        ])
        
        # Write data
        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description or "",
                task.due_date.isoformat() if task.due_date else "",
                task.priority,
                task.status,
                task.estimated_duration or "",
                task.actual_duration or "",
                task.completion_percentage or 0,
                json.dumps(task.tags) if task.tags else "",
                task.created_at.isoformat(),
                task.updated_at.isoformat() if task.updated_at else "",
                task.completed_at.isoformat() if task.completed_at else ""
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=lifesync_tasks_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

@router.get("/wellness")
async def export_wellness_data(
    format: Literal["json", "csv"] = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export wellness and mood data"""
    
    mood_entries = db.query(MoodEntry).filter(MoodEntry.user_id == current_user.id).all()
    
    if format == "json":
        wellness_data = []
        for entry in mood_entries:
            wellness_data.append({
                "id": entry.id,
                "mood_level": entry.mood_level,
                "energy_level": entry.energy_level,
                "stress_level": entry.stress_level,
                "notes": entry.notes,
                "tags": entry.tags,
                "created_at": entry.created_at.isoformat()
            })
        
        return Response(
            content=json.dumps(wellness_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=lifesync_wellness_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
    
    else:  # CSV format
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "ID", "Mood Level", "Energy Level", "Stress Level", 
            "Notes", "Tags", "Date"
        ])
        
        # Write data
        for entry in mood_entries:
            writer.writerow([
                entry.id,
                entry.mood_level,
                entry.energy_level,
                entry.stress_level or "",
                entry.notes or "",
                json.dumps(entry.tags) if entry.tags else "",
                entry.created_at.isoformat()
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=lifesync_wellness_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

def _export_json(user: User, tasks, mood_entries, documents):
    """Export all data as JSON"""
    
    export_data = {
        "export_info": {
            "export_date": datetime.utcnow().isoformat(),
            "user_email": user.email,
            "user_name": user.full_name,
            "lifesync_version": "1.0.0"
        },
        "user_profile": {
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
            "preferences": user.preferences,
            "onboarding_completed": user.onboarding_completed
        },
        "tasks": [],
        "wellness_data": [],
        "documents": []
    }
    
    # Export tasks
    for task in tasks:
        export_data["tasks"].append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "status": task.status,
            "estimated_duration": task.estimated_duration,
            "actual_duration": task.actual_duration,
            "completion_percentage": task.completion_percentage,
            "tags": task.tags,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        })
    
    # Export wellness data
    for entry in mood_entries:
        export_data["wellness_data"].append({
            "id": entry.id,
            "mood_level": entry.mood_level,
            "energy_level": entry.energy_level,
            "stress_level": entry.stress_level,
            "notes": entry.notes,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat()
        })
    
    # Export document metadata (not the actual files for security)
    for doc in documents:
        export_data["documents"].append({
            "id": doc.id,
            "filename": doc.filename,
            "document_type": doc.document_type,
            "file_size": doc.file_size,
            "processed": doc.processed,
            "processing_status": doc.processing_status,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
            "extracted_tasks_count": len(doc.extracted_tasks.get("tasks", [])) if doc.extracted_tasks else 0
        })
    
    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=lifesync_export_{datetime.now().strftime('%Y%m%d')}.json"
        }
    )

def _export_csv(user: User, tasks, mood_entries, documents):
    """Export all data as ZIP file containing multiple CSV files"""
    import zipfile
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Export tasks CSV
        tasks_csv = io.StringIO()
        tasks_writer = csv.writer(tasks_csv)
        tasks_writer.writerow([
            "ID", "Title", "Description", "Due Date", "Priority", "Status",
            "Estimated Duration", "Actual Duration", "Completion %", "Tags",
            "Created At", "Updated At", "Completed At"
        ])
        
        for task in tasks:
            tasks_writer.writerow([
                task.id, task.title, task.description or "", 
                task.due_date.isoformat() if task.due_date else "",
                task.priority, task.status,
                task.estimated_duration or "", task.actual_duration or "",
                task.completion_percentage or 0,
                json.dumps(task.tags) if task.tags else "",
                task.created_at.isoformat(),
                task.updated_at.isoformat() if task.updated_at else "",
                task.completed_at.isoformat() if task.completed_at else ""
            ])
        
        zip_file.writestr("tasks.csv", tasks_csv.getvalue())
        
        # Export wellness CSV
        wellness_csv = io.StringIO()
        wellness_writer = csv.writer(wellness_csv)
        wellness_writer.writerow([
            "ID", "Mood Level", "Energy Level", "Stress Level", 
            "Notes", "Tags", "Date"
        ])
        
        for entry in mood_entries:
            wellness_writer.writerow([
                entry.id, entry.mood_level, entry.energy_level,
                entry.stress_level or "", entry.notes or "",
                json.dumps(entry.tags) if entry.tags else "",
                entry.created_at.isoformat()
            ])
        
        zip_file.writestr("wellness.csv", wellness_csv.getvalue())
        
        # Export documents CSV
        docs_csv = io.StringIO()
        docs_writer = csv.writer(docs_csv)
        docs_writer.writerow([
            "ID", "Filename", "Document Type", "File Size", "Processed",
            "Processing Status", "Uploaded At", "Processed At", "Extracted Tasks Count"
        ])
        
        for doc in documents:
            docs_writer.writerow([
                doc.id, doc.filename, doc.document_type, doc.file_size,
                doc.processed, doc.processing_status,
                doc.uploaded_at.isoformat(),
                doc.processed_at.isoformat() if doc.processed_at else "",
                len(doc.extracted_tasks.get("tasks", [])) if doc.extracted_tasks else 0
            ])
        
        zip_file.writestr("documents.csv", docs_csv.getvalue())
        
        # Add export info
        info_csv = io.StringIO()
        info_writer = csv.writer(info_csv)
        info_writer.writerow(["Export Date", "User Email", "User Name", "Total Tasks", "Total Wellness Entries", "Total Documents"])
        info_writer.writerow([
            datetime.utcnow().isoformat(),
            user.email,
            user.full_name,
            len(tasks),
            len(mood_entries),
            len(documents)
        ])
        
        zip_file.writestr("export_info.csv", info_csv.getvalue())
    
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=lifesync_export_{datetime.now().strftime('%Y%m%d')}.zip"
        }
    )

@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    
    # This is a destructive operation - in a real app you'd want additional confirmations
    # Delete all associated data
    db.query(Task).filter(Task.user_id == current_user.id).delete()
    db.query(MoodEntry).filter(MoodEntry.user_id == current_user.id).delete()
    db.query(Document).filter(Document.user_id == current_user.id).delete()
    
    # Delete user
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account and all data successfully deleted"}