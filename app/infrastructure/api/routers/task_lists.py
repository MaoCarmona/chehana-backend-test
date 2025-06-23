"""Router de listas de tareas."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.auth_dto import UserResponse
from app.application.dtos.task_list_dto import (
    TaskListCreateRequest,
    TaskListResponse,
    TaskListUpdateRequest,
)
from app.application.exceptions.exceptions import (
    ApplicationException,
    AuthorizationError,
    NotFoundError,
)
from app.application.use_cases.task_list_use_cases import TaskListUseCases
from app.infrastructure.api.dependencies import get_current_user, get_task_list_use_cases

router = APIRouter(prefix="/task-lists", tags=["Listas de Tareas"])


@router.post(
    "/",
    response_model=TaskListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear lista de tareas",
    description="Crea una nueva lista de tareas",
)
async def create_task_list(
    request: TaskListCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
):
    """Crea una nueva lista de tareas."""
    try:
        return await task_list_use_cases.create_task_list(request, current_user.id)
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=List[TaskListResponse],
    summary="Obtener listas de tareas del usuario",
    description="Obtiene todas las listas de tareas del usuario autenticado",
)
async def get_user_task_lists(
    current_user: UserResponse = Depends(get_current_user),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
):
    """Obtiene todas las listas de tareas del usuario."""
    try:
        return await task_list_use_cases.get_user_task_lists(current_user.id)
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{task_list_id}",
    response_model=TaskListResponse,
    summary="Obtener lista de tareas",
    description="Obtiene una lista de tareas específica por ID",
)
async def get_task_list(
    task_list_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
):
    """Obtiene una lista de tareas por ID."""
    try:
        return await task_list_use_cases.get_task_list(task_list_id, current_user.id)
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
    "/{task_list_id}",
    response_model=TaskListResponse,
    summary="Actualizar lista de tareas",
    description="Actualiza una lista de tareas específica",
)
async def update_task_list(
    task_list_id: UUID,
    request: TaskListUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
):
    """Actualiza una lista de tareas."""
    try:
        return await task_list_use_cases.update_task_list(
            task_list_id, request, current_user.id
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


@router.delete(
    "/{task_list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lista de tareas",
    description="Elimina una lista de tareas específica",
)
async def delete_task_list(
    task_list_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
):
    """Elimina una lista de tareas."""
    try:
        result = await task_list_use_cases.delete_task_list(task_list_id, current_user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lista de tareas no encontrada",
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