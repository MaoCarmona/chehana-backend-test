"""Interfaz del repositorio de listas de tareas."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.task_list import TaskList


class TaskListRepository(ABC):
    """Interfaz del repositorio de listas de tareas."""
    
    @abstractmethod
    async def create(self, task_list: TaskList) -> TaskList:
        """Crea una nueva lista de tareas."""
        pass
    
    @abstractmethod
    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Obtiene una lista de tareas por ID."""
        pass
    
    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[TaskList]:
        """Obtiene todas las listas de tareas de un propietario."""
        pass
    
    @abstractmethod
    async def update(self, task_list: TaskList) -> TaskList:
        """Actualiza una lista de tareas."""
        pass
    
    @abstractmethod
    async def delete(self, task_list_id: UUID) -> bool:
        """Elimina una lista de tareas."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[TaskList]:
        """Lista todas las listas de tareas."""
        pass 