"""Entidad Lista de Tareas del dominio."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskList(BaseModel):
    """Entidad Lista de Tareas."""
    
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    owner_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Métodos de negocio
    def update_title(self, new_title: str) -> None:
        """Actualiza el título de la lista."""
        if not new_title or len(new_title.strip()) == 0:
            raise ValueError("El título no puede estar vacío")
        self.title = new_title.strip()
        self.updated_at = datetime.now()
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Actualiza la descripción de la lista."""
        self.description = new_description
        self.updated_at = datetime.now()

    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    } 