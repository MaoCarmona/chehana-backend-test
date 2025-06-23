"""Router de tareas."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dtos.auth_dto import UserResponse
from app.application.dtos.task_dto import (
    TaskCreateRequest,
    TaskFilterParams,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
from app.application.exceptions.exceptions import (
    ApplicationException,
    AuthorizationError,
    NotFoundError,
)
from app.application.use_cases.task_use_cases import TaskUseCases
from app.domain.entities.task import TaskPriority, TaskStatus
from app.infrastructure.api.dependencies import get_current_user, get_task_use_cases

router = APIRouter(prefix="/tasks", tags=["Tareas"])


@router.post(
    "/lists/{task_list_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarea",
    description="Crea una nueva tarea en una lista específica",
)
async def create_task(
    task_list_id: UUID,
    request: TaskCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Crea una nueva tarea."""
    try:
        return await task_use_cases.create_task(task_list_id, request, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/lists/{task_list_id}/tasks",
    response_model=List[TaskResponse],
    summary="Obtener tareas de una lista",
    description="Obtiene todas las tareas de una lista con filtros opcionales",
)
async def get_tasks_by_list(
    task_list_id: UUID,
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Obtiene tareas de una lista con filtros."""
    try:
        filters = TaskFilterParams(
            status=status_filter,
            priority=priority_filter
        )
        return await task_use_cases.get_tasks_by_list(
            task_list_id, filters, current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/assigned-to-me",
    response_model=List[TaskResponse],
    summary="Obtener tareas asignadas",
    description="Obtiene todas las tareas asignadas al usuario autenticado",
)
async def get_assigned_tasks(
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Obtiene las tareas asignadas al usuario."""
    try:
        return await task_use_cases.get_user_assigned_tasks(current_user.id)
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Obtener tarea",
    description="Obtiene una tarea específica por ID",
)
async def get_task(
    task_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Obtiene una tarea por ID."""
    try:
        return await task_use_cases.get_task(task_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Actualizar tarea",
    description="Actualiza una tarea específica",
)
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Actualiza una tarea."""
    try:
        return await task_use_cases.update_task(task_id, request, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Actualizar estado de tarea",
    description="Actualiza el estado de una tarea específica",
)
async def update_task_status(
    task_id: UUID,
    request: TaskStatusUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Actualiza el estado de una tarea."""
    try:
        return await task_use_cases.update_task_status(task_id, request, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{task_id}/assign/{user_id}",
    response_model=TaskResponse,
    summary="Asignar tarea",
    description="Asigna una tarea a un usuario específico",
)
async def assign_task(
    task_id: UUID,
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Asigna una tarea a un usuario."""
    try:
        return await task_use_cases.assign_task(task_id, user_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{task_id}/unassign",
    response_model=TaskResponse,
    summary="Desasignar tarea",
    description="Desasigna una tarea (quita el usuario asignado)",
)
async def unassign_task(
    task_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Desasigna una tarea."""
    try:
        return await task_use_cases.unassign_task(task_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarea",
    description="Elimina una tarea específica",
)
async def delete_task(
    task_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
):
    """Elimina una tarea."""
    try:
        result = await task_use_cases.delete_task(task_id, current_user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) 