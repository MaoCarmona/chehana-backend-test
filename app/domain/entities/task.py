"""Entidad Tarea del dominio."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Estados posibles de una tarea."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Prioridades posibles de una tarea."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """Entidad Tarea."""
    
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    task_list_id: UUID
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Métodos de negocio
    def update_status(self, new_status: TaskStatus) -> None:
        """Actualiza el estado de la tarea."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
        elif new_status != TaskStatus.COMPLETED and old_status == TaskStatus.COMPLETED:
            self.completed_at = None
    
    def update_priority(self, new_priority: TaskPriority) -> None:
        """Actualiza la prioridad de la tarea."""
        self.priority = new_priority
        self.updated_at = datetime.now()
    
    def assign_to_user(self, user_id: UUID) -> None:
        """Asigna la tarea a un usuario."""
        self.assigned_to = user_id
        self.updated_at = datetime.now()
    
    def unassign(self) -> None:
        """Desasigna la tarea."""
        self.assigned_to = None
        self.updated_at = datetime.now()
    
    def is_completed(self) -> bool:
        """Verifica si la tarea está completada."""
        return self.status == TaskStatus.COMPLETED
    
    def is_overdue(self) -> bool:
        """Verifica si la tarea está vencida."""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date and not self.is_completed()

    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    } 