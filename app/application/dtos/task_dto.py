"""DTOs para tareas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.task import TaskPriority, TaskStatus


class TaskCreateRequest(BaseModel):
    """DTO para crear una tarea."""
    
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdateRequest(BaseModel):
    """DTO para actualizar una tarea."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskStatusUpdateRequest(BaseModel):
    """DTO para actualizar el estado de una tarea."""
    
    status: TaskStatus


class TaskResponse(BaseModel):
    """DTO para respuesta de tarea."""
    
    id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    task_list_id: UUID
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_overdue: bool = False

    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    }


class TaskFilterParams(BaseModel):
    """DTO para parámetros de filtro de tareas."""
    
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None 