"""Dependencias de FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.auth_dto import UserResponse
from app.application.exceptions.exceptions import AuthenticationError
from app.application.services.auth_service import AuthService
from app.application.services.email_service import EmailService
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.application.use_cases.task_list_use_cases import TaskListUseCases
from app.application.use_cases.task_use_cases import TaskUseCases
from app.infrastructure.database.config import get_async_session
from app.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from app.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

security = HTTPBearer()


async def get_database_session() -> AsyncSession:
    """Obtiene una sesión de base de datos."""
    async for session in get_async_session():
        yield session


def get_auth_service() -> AuthService:
    """Obtiene el servicio de autenticación."""
    return AuthService()


def get_email_service() -> EmailService:
    """Obtiene el servicio de email."""
    return EmailService()


def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyUserRepository:
    """Obtiene el repositorio de usuarios."""
    return SQLAlchemyUserRepository(session)


def get_task_list_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyTaskListRepository:
    """Obtiene el repositorio de listas de tareas."""
    return SQLAlchemyTaskListRepository(session)


def get_task_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyTaskRepository:
    """Obtiene el repositorio de tareas."""
    return SQLAlchemyTaskRepository(session)


def get_auth_use_cases(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthUseCases:
    """Obtiene los casos de uso de autenticación."""
    return AuthUseCases(user_repository, auth_service)


def get_task_list_use_cases(
    task_list_repository: SQLAlchemyTaskListRepository = Depends(get_task_list_repository),
    task_repository: SQLAlchemyTaskRepository = Depends(get_task_repository),
) -> TaskListUseCases:
    """Obtiene los casos de uso de listas de tareas."""
    return TaskListUseCases(task_list_repository, task_repository)


def get_task_use_cases(
    task_repository: SQLAlchemyTaskRepository = Depends(get_task_repository),
    task_list_repository: SQLAlchemyTaskListRepository = Depends(get_task_list_repository),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> TaskUseCases:
    """Obtiene los casos de uso de tareas."""
    return TaskUseCases(task_repository, task_list_repository, user_repository, email_service)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> UserResponse:
    """Obtiene el usuario actual autenticado."""
    try:
        user = await auth_use_cases.get_current_user(credentials.credentials)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 