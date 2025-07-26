from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User, Task
from app.services.tasks_service import tasks_service

router = APIRouter()

class SyncOperation(BaseModel):
    action: str  # CREATE, UPDATE, DELETE
    entity_type: str  # task, habit, goal
    entity_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime
    client_id: Optional[str] = None

class SyncRequest(BaseModel):
    operations: List[SyncOperation]
    last_sync_timestamp: Optional[datetime] = None
    device_id: str

class SyncConflict(BaseModel):
    operation_index: int
    conflict_type: str  # version_conflict, not_found, permission_denied
    server_data: Optional[Dict[str, Any]] = None
    message: str

class SyncResponse(BaseModel):
    success: bool
    processed_operations: int
    conflicts: List[SyncConflict] = []
    server_changes: List[Dict[str, Any]] = []
    new_sync_timestamp: datetime

@router.post("/sync", response_model=SyncResponse)
async def sync_data(
    sync_request: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform bidirectional sync between client and server.
    Handles conflict resolution and returns server changes.
    """
    
    conflicts = []
    processed_operations = 0
    server_changes = []
    
    try:
        # Process client operations
        for i, operation in enumerate(sync_request.operations):
            try:
                await process_sync_operation(operation, current_user, db, i, conflicts)
                processed_operations += 1
            except Exception as e:
                conflicts.append(SyncConflict(
                    operation_index=i,
                    conflict_type="processing_error",
                    message=str(e)
                ))
        
        # Get server changes since last sync
        if sync_request.last_sync_timestamp:
            server_changes = await get_server_changes(
                current_user.id, 
                sync_request.last_sync_timestamp,
                sync_request.device_id,
                db
            )
        
        # Commit all changes
        db.commit()
        
        return SyncResponse(
            success=True,
            processed_operations=processed_operations,
            conflicts=conflicts,
            server_changes=server_changes,
            new_sync_timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )

async def process_sync_operation(
    operation: SyncOperation,
    user: User,
    db: Session,
    operation_index: int,
    conflicts: List[SyncConflict]
):
    """Process a single sync operation"""
    
    if operation.entity_type == "task":
        await process_task_operation(operation, user, db, operation_index, conflicts)
    else:
        conflicts.append(SyncConflict(
            operation_index=operation_index,
            conflict_type="unsupported_entity",
            message=f"Entity type '{operation.entity_type}' not supported"
        ))

async def process_task_operation(
    operation: SyncOperation,
    user: User,
    db: Session,
    operation_index: int,
    conflicts: List[SyncConflict]
):
    """Process task-specific sync operations"""
    
    if operation.action == "CREATE":
        # Create new task
        task_data = {
            "title": operation.data.get("title"),
            "description": operation.data.get("description", ""),
            "due_date": operation.data.get("due_date"),
            "priority": operation.data.get("priority", 1),
            "status": operation.data.get("status", "pending"),
            "user_id": user.id
        }
        
        # Remove None values
        task_data = {k: v for k, v in task_data.items() if v is not None}
        
        try:
            result = await tasks_service.create_task(task_data, user.id, db)
            if not result["success"]:
                conflicts.append(SyncConflict(
                    operation_index=operation_index,
                    conflict_type="creation_failed",
                    message=result["error"]
                ))
        except Exception as e:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="creation_error",
                message=str(e)
            ))
    
    elif operation.action == "UPDATE":
        if not operation.entity_id:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="missing_id",
                message="Entity ID required for update operation"
            ))
            return
        
        # Check if task exists and user has permission
        existing_task = db.query(Task).filter(
            Task.id == operation.entity_id,
            Task.user_id == user.id
        ).first()
        
        if not existing_task:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="not_found",
                message="Task not found or access denied"
            ))
            return
        
        # Check for version conflicts
        if (hasattr(existing_task, 'updated_at') and 
            existing_task.updated_at > operation.timestamp):
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="version_conflict",
                server_data={
                    "id": existing_task.id,
                    "title": existing_task.title,
                    "description": existing_task.description,
                    "due_date": existing_task.due_date.isoformat() if existing_task.due_date else None,
                    "priority": existing_task.priority,
                    "status": existing_task.status,
                    "updated_at": existing_task.updated_at.isoformat()
                },
                message="Server version is newer than client version"
            ))
            return
        
        # Update task
        update_data = {}
        for field in ["title", "description", "due_date", "priority", "status"]:
            if field in operation.data:
                update_data[field] = operation.data[field]
        
        try:
            result = await tasks_service.update_task(
                operation.entity_id, 
                update_data, 
                user.id, 
                db
            )
            if not result["success"]:
                conflicts.append(SyncConflict(
                    operation_index=operation_index,
                    conflict_type="update_failed",
                    message=result["error"]
                ))
        except Exception as e:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="update_error",
                message=str(e)
            ))
    
    elif operation.action == "DELETE":
        if not operation.entity_id:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="missing_id",
                message="Entity ID required for delete operation"
            ))
            return
        
        try:
            result = await tasks_service.delete_task(operation.entity_id, user.id, db)
            if not result["success"]:
                conflicts.append(SyncConflict(
                    operation_index=operation_index,
                    conflict_type="delete_failed",
                    message=result["error"]
                ))
        except Exception as e:
            conflicts.append(SyncConflict(
                operation_index=operation_index,
                conflict_type="delete_error",
                message=str(e)
            ))

async def get_server_changes(
    user_id: int,
    last_sync_timestamp: datetime,
    device_id: str,
    db: Session
) -> List[Dict[str, Any]]:
    """Get all server changes since last sync timestamp"""
    
    changes = []
    
    # Get task changes
    task_changes = db.query(Task).filter(
        Task.user_id == user_id,
        Task.updated_at > last_sync_timestamp
    ).all()
    
    for task in task_changes:
        changes.append({
            "entity_type": "task",
            "action": "UPDATE",  # We'll treat all as updates for simplicity
            "entity_id": str(task.id),
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            },
            "timestamp": task.updated_at.isoformat()
        })
    
    return changes

@router.get("/sync/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sync status information"""
    
    # Get count of user's data
    task_count = db.query(Task).filter(Task.user_id == current_user.id).count()
    
    # Get last modified timestamps
    latest_task = db.query(Task).filter(
        Task.user_id == current_user.id
    ).order_by(Task.updated_at.desc()).first()
    
    return {
        "user_id": current_user.id,
        "data_counts": {
            "tasks": task_count
        },
        "last_modified": {
            "tasks": latest_task.updated_at.isoformat() if latest_task else None
        },
        "server_timestamp": datetime.utcnow().isoformat()
    }

@router.post("/sync/resolve-conflict")
async def resolve_sync_conflict(
    conflict_resolution: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve a sync conflict by accepting either client or server version,
    or providing a merged version.
    """
    
    entity_type = conflict_resolution.get("entity_type")
    entity_id = conflict_resolution.get("entity_id")
    resolution = conflict_resolution.get("resolution")  # "client", "server", "merge"
    merged_data = conflict_resolution.get("merged_data")
    
    if entity_type == "task" and entity_id:
        if resolution == "client":
            # Accept client version
            update_data = conflict_resolution.get("client_data", {})
        elif resolution == "server":
            # Keep server version (no action needed)
            return {"success": True, "message": "Server version kept"}
        elif resolution == "merge" and merged_data:
            # Apply merged version
            update_data = merged_data
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conflict resolution"
            )
        
        try:
            result = await tasks_service.update_task(entity_id, update_data, current_user.id, db)
            if result["success"]:
                db.commit()
                return {"success": True, "data": result["task"]}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported entity type or missing data"
    )