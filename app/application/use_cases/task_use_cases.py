"""Casos de uso de tareas."""

from typing import List, Optional
from uuid import UUID

from app.application.dtos.task_dto import (
    TaskCreateRequest,
    TaskFilterParams,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
from app.application.exceptions.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from app.application.services.email_service import EmailService
from app.domain.entities.task import Task
from app.domain.repositories.task_list_repository import TaskListRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository


class TaskUseCases:
    """Casos de uso de tareas."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        task_list_repository: TaskListRepository,
        user_repository: UserRepository,
        email_service: EmailService,
    ):
        self.task_repository = task_repository
        self.task_list_repository = task_list_repository
        self.user_repository = user_repository
        self.email_service = email_service
    
    async def create_task(
        self, 
        task_list_id: UUID, 
        request: TaskCreateRequest, 
        user_id: UUID
    ) -> TaskResponse:
        """Crea una nueva tarea."""
        # Verificar que la lista de tareas existe y pertenece al usuario
        task_list = await self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("Lista de tareas", str(task_list_id))
        
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para crear tareas en esta lista")
        
        # Verificar que el usuario asignado existe (si se especifica)
        if request.assigned_to:
            assigned_user = await self.user_repository.get_by_id(request.assigned_to)
            if not assigned_user:
                raise NotFoundError("Usuario", str(request.assigned_to))
        
        # Crear la tarea
        task = Task(
            title=request.title,
            description=request.description,
            priority=request.priority,
            task_list_id=task_list_id,
            assigned_to=request.assigned_to,
            due_date=request.due_date
        )
        
        created_task = await self.task_repository.create(task)
        
        # Enviar notificación si la tarea fue asignada
        if request.assigned_to:
            await self._send_assignment_notification(
                created_task.id, 
                request.assigned_to, 
                task_list.title
            )
        
        return self._to_response(created_task)
    
    async def get_task(self, task_id: UUID, user_id: UUID) -> TaskResponse:
        """Obtiene una tarea por ID."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización
        await self._verify_task_access(task, user_id)
        
        return self._to_response(task)
    
    async def get_tasks_by_list(
        self, 
        task_list_id: UUID, 
        filters: TaskFilterParams, 
        user_id: UUID
    ) -> List[TaskResponse]:
        """Obtiene todas las tareas de una lista con filtros."""
        # Verificar que la lista existe y pertenece al usuario
        task_list = await self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("Lista de tareas", str(task_list_id))
        
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para ver las tareas de esta lista")
        
        # Obtener tareas con filtros
        tasks = await self.task_repository.get_by_task_list(
            task_list_id=task_list_id,
            status=filters.status,
            priority=filters.priority
        )
        
        return [self._to_response(task) for task in tasks]
    
    async def get_user_assigned_tasks(self, user_id: UUID) -> List[TaskResponse]:
        """Obtiene todas las tareas asignadas a un usuario."""
        tasks = await self.task_repository.get_by_assigned_user(user_id)
        return [self._to_response(task) for task in tasks]
    
    async def update_task(
        self, 
        task_id: UUID, 
        request: TaskUpdateRequest, 
        user_id: UUID
    ) -> TaskResponse:
        """Actualiza una tarea."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización
        await self._verify_task_access(task, user_id)
        
        # Verificar que el usuario asignado existe (si se especifica)
        old_assigned_to = task.assigned_to
        if request.assigned_to:
            assigned_user = await self.user_repository.get_by_id(request.assigned_to)
            if not assigned_user:
                raise NotFoundError("Usuario", str(request.assigned_to))
        
        # Actualizar campos si se proporcionan
        if request.title is not None:
            task.title = request.title
        
        if request.description is not None:
            task.description = request.description
        
        if request.priority is not None:
            task.update_priority(request.priority)
        
        if request.assigned_to is not None:
            if request.assigned_to != old_assigned_to:
                task.assign_to_user(request.assigned_to)
        
        if request.due_date is not None:
            task.due_date = request.due_date
        
        updated_task = await self.task_repository.update(task)
        
        # Enviar notificación si cambió la asignación
        if request.assigned_to and request.assigned_to != old_assigned_to:
            task_list = await self.task_list_repository.get_by_id(task.task_list_id)
            await self._send_assignment_notification(
                updated_task.id, 
                request.assigned_to, 
                task_list.title
            )
        
        return self._to_response(updated_task)
    
    async def update_task_status(
        self, 
        task_id: UUID, 
        request: TaskStatusUpdateRequest, 
        user_id: UUID
    ) -> TaskResponse:
        """Actualiza el estado de una tarea."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización (propietario o asignado)
        task_list = await self.task_list_repository.get_by_id(task.task_list_id)
        if task_list.owner_id != user_id and task.assigned_to != user_id:
            raise AuthorizationError("No tienes permisos para cambiar el estado de esta tarea")
        
        # Actualizar estado
        old_status = task.status
        task.update_status(request.status)
        
        updated_task = await self.task_repository.update(task)
        
        # Enviar notificación si la tarea fue completada
        if request.status.value == "completed" and old_status.value != "completed":
            if task_list.owner_id != user_id:  # Notificar al propietario si no es él quien la completó
                owner = await self.user_repository.get_by_id(task_list.owner_id)
                if owner:
                    await self.email_service.send_task_completion_notification(
                        owner.email, task.title
                    )
        
        return self._to_response(updated_task)
    
    async def assign_task(
        self, 
        task_id: UUID, 
        assigned_to: UUID, 
        user_id: UUID
    ) -> TaskResponse:
        """Asigna una tarea a un usuario."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización (solo el propietario puede asignar)
        await self._verify_task_access(task, user_id)
        
        # Verificar que el usuario asignado existe
        assigned_user = await self.user_repository.get_by_id(assigned_to)
        if not assigned_user:
            raise NotFoundError("Usuario", str(assigned_to))
        
        # Asignar tarea
        task.assign_to_user(assigned_to)
        updated_task = await self.task_repository.update(task)
        
        # Enviar notificación
        task_list = await self.task_list_repository.get_by_id(task.task_list_id)
        await self._send_assignment_notification(
            updated_task.id, 
            assigned_to, 
            task_list.title
        )
        
        return self._to_response(updated_task)
    
    async def unassign_task(self, task_id: UUID, user_id: UUID) -> TaskResponse:
        """Desasigna una tarea."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización
        await self._verify_task_access(task, user_id)
        
        # Desasignar tarea
        task.unassign()
        updated_task = await self.task_repository.update(task)
        
        return self._to_response(updated_task)
    
    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Elimina una tarea."""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Tarea", str(task_id))
        
        # Verificar autorización
        await self._verify_task_access(task, user_id)
        
        return await self.task_repository.delete(task_id)
    
    async def _verify_task_access(self, task: Task, user_id: UUID) -> None:
        """Verifica que el usuario tiene acceso a la tarea."""
        task_list = await self.task_list_repository.get_by_id(task.task_list_id)
        if task_list.owner_id != user_id:
            raise AuthorizationError("No tienes permisos para acceder a esta tarea")
    
    async def _send_assignment_notification(
        self, 
        task_id: UUID, 
        assigned_to: UUID, 
        task_list_title: str
    ) -> None:
        """Envía notificación de asignación de tarea."""
        try:
            task = await self.task_repository.get_by_id(task_id)
            assigned_user = await self.user_repository.get_by_id(assigned_to)
            
            if task and assigned_user:
                await self.email_service.send_task_assignment_notification(
                    assigned_user.email,
                    task.title,
                    task_list_title
                )
        except Exception as e:
            # Log error but don't fail the operation
            import logging
            logging.error(f"Error enviando notificación de asignación: {e}")
    
    def _to_response(self, task: Task) -> TaskResponse:
        """Convierte una entidad de tarea a respuesta DTO."""
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            task_list_id=task.task_list_id,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            is_overdue=task.is_overdue()
        ) 