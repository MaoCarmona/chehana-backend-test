"""DTOs para listas de tareas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaskListCreateRequest(BaseModel):
    """DTO para crear una lista de tareas."""
    
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskListUpdateRequest(BaseModel):
    """DTO para actualizar una lista de tareas."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskListResponse(BaseModel):
    """DTO para respuesta de lista de tareas."""
    
    id: UUID
    title: str
    description: Optional[str] = None
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    completion_percentage: float = 0.0

    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    } 