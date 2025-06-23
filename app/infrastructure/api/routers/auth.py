"""Router de autenticación."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dtos.auth_dto import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.application.exceptions.exceptions import (
    ApplicationException,
    ConflictError,
)
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.infrastructure.api.dependencies import get_auth_use_cases, get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Registra un nuevo usuario en el sistema",
)
async def register_user(
    request: UserRegisterRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """Registra un nuevo usuario."""
    try:
        return await auth_use_cases.register_user(request)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token de acceso",
)
async def login_user(
    request: UserLoginRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """Autentica un usuario."""
    try:
        return await auth_use_cases.login_user(request)
    except ApplicationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario actual",
    description="Obtiene la información del usuario autenticado",
)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
):
    """Obtiene la información del usuario actual."""
    return current_user 