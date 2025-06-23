"""Casos de uso de listas de tareas."""

from typing import List
from uuid import UUID

from app.application.dtos.task_list_dto import (
    TaskListCreateRequest,
    TaskListResponse,
    TaskListUpdateRequest,
)
from app.application.exceptions.exceptions import AuthorizationError, NotFoundError
from app.domain.entities.task import TaskStatus
from app.domain.entities.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository


class TaskListUseCases:
    """Casos de uso de listas de tareas."""
    
    def __init__(
        self, 
        task_list_repository: TaskListRepository,
        task_repository: TaskRepository
    ):
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository
    
    async def create_task_list(
        self, 
        request: TaskListCreateRequest, 
        owner_id: UUID
    ) -> TaskListResponse:
        """Crea una nueva lista de tareas."""
        task_list = TaskList(
            title=request.title,
            description=request.description,
            owner_id=owner_id
        )
        
        created_task_list = await self.task_list_repository.create(task_list)
        
        return TaskListResponse(
            id=created_task_list.id,
            title=created_task_list.title,
            description=created_task_list.description,
            owner_id=created_task_list.owner_id,
            created_at=created_task_list.created_at,
            updated_at=created_task_list.updated_at,
            completion_percentage=0.0
        )
    
    async def get_task_list(self, task_list_id: UUID, user_id: UUID) -> TaskListResponse:
        """Obtiene una lista de tareas por ID."""
        task_list = await self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("Lista de tareas", str(task_list_id))
        
        # Verificar autorización (solo el propietario puede ver la lista)
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para ver esta lista de tareas")
        
        # Calcular porcentaje de completitud
        completion_percentage = await self._calculate_completion_percentage(task_list_id)
        
        return TaskListResponse(
            id=task_list.id,
            title=task_list.title,
            description=task_list.description,
            owner_id=task_list.owner_id,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
            completion_percentage=completion_percentage
        )
    
    async def get_user_task_lists(self, user_id: UUID) -> List[TaskListResponse]:
        """Obtiene todas las listas de tareas de un usuario."""
        task_lists = await self.task_list_repository.get_by_owner(user_id)
        
        result = []
        for task_list in task_lists:
            completion_percentage = await self._calculate_completion_percentage(task_list.id)
            result.append(TaskListResponse(
                id=task_list.id,
                title=task_list.title,
                description=task_list.description,
                owner_id=task_list.owner_id,
                created_at=task_list.created_at,
                updated_at=task_list.updated_at,
                completion_percentage=completion_percentage
            ))
        
        return result
    
    async def update_task_list(
        self, 
        task_list_id: UUID, 
        request: TaskListUpdateRequest, 
        user_id: UUID
    ) -> TaskListResponse:
        """Actualiza una lista de tareas."""
        task_list = await self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("Lista de tareas", str(task_list_id))
        
        # Verificar autorización
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para modificar esta lista de tareas")
        
        # Actualizar campos si se proporcionan
        if request.title is not None:
            task_list.update_title(request.title)
        
        if request.description is not None:
            task_list.update_description(request.description)
        
        updated_task_list = await self.task_list_repository.update(task_list)
        
        # Calcular porcentaje de completitud
        completion_percentage = await self._calculate_completion_percentage(task_list_id)
        
        return TaskListResponse(
            id=updated_task_list.id,
            title=updated_task_list.title,
            description=updated_task_list.description,
            owner_id=updated_task_list.owner_id,
            created_at=updated_task_list.created_at,
            updated_at=updated_task_list.updated_at,
            completion_percentage=completion_percentage
        )
    
    async def delete_task_list(self, task_list_id: UUID, user_id: UUID) -> bool:
        """Elimina una lista de tareas."""
        task_list = await self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("Lista de tareas", str(task_list_id))
        
        # Verificar autorización
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para eliminar esta lista de tareas")
        
        return await self.task_list_repository.delete(task_list_id)
    
    async def _calculate_completion_percentage(self, task_list_id: UUID) -> float:
        """Calcula el porcentaje de completitud de una lista de tareas."""
        total_tasks = await self.task_repository.get_by_task_list(task_list_id)
        if not total_tasks:
            return 0.0
        
        completed_tasks = await self.task_repository.count_by_task_list_and_status(
            task_list_id, TaskStatus.COMPLETED
        )
        
        return round((completed_tasks / len(total_tasks)) * 100, 2) 