"""Interfaz del repositorio de tareas."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.task import Task, TaskPriority, TaskStatus


class TaskRepository(ABC):
    """Interfaz del repositorio de tareas."""
    
    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Crea una nueva tarea."""
        pass
    
    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Obtiene una tarea por ID."""
        pass
    
    @abstractmethod
    async def get_by_task_list(
        self, 
        task_list_id: UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """Obtiene todas las tareas de una lista con filtros opcionales."""
        pass
    
    @abstractmethod
    async def get_by_assigned_user(self, user_id: UUID) -> List[Task]:
        """Obtiene todas las tareas asignadas a un usuario."""
        pass
    
    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Actualiza una tarea."""
        pass
    
    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """Elimina una tarea."""
        pass
    
    @abstractmethod
    async def count_by_task_list_and_status(
        self, 
        task_list_id: UUID, 
        status: TaskStatus
    ) -> int:
        """Cuenta las tareas de una lista por estado."""
        pass 