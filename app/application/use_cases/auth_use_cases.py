"""Casos de uso de autenticación."""

from app.application.dtos.auth_dto import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.application.exceptions.exceptions import (
    AuthenticationError,
    ConflictError,
    ValidationError,
)
from app.application.services.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class AuthUseCases:
    """Casos de uso de autenticación."""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        """Registra un nuevo usuario."""
        # Verificar si ya existe un usuario con el email
        existing_user = await self.user_repository.get_by_email(request.email)
        if existing_user:
            raise ConflictError("Ya existe un usuario con este email")
        
        # Verificar si ya existe un usuario con el username
        existing_user = await self.user_repository.get_by_username(request.username)
        if existing_user:
            raise ConflictError("Ya existe un usuario con este nombre de usuario")
        
        # Crear el usuario
        hashed_password = self.auth_service.get_password_hash(request.password)
        user = User(
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            hashed_password=hashed_password
        )
        
        created_user = await self.user_repository.create(user)
        
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            username=created_user.username,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
    
    async def login_user(self, request: UserLoginRequest) -> TokenResponse:
        """Autentica un usuario y retorna un token."""
        # Buscar usuario por username
        user = await self.user_repository.get_by_username(request.username)
        if not user:
            raise AuthenticationError("Credenciales inválidas")
        
        # Verificar contraseña
        if not self.auth_service.verify_password(request.password, user.hashed_password):
            raise AuthenticationError("Credenciales inválidas")
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")
        
        # Crear token
        access_token = self.auth_service.create_access_token(
            user_id=user.id,
            username=user.username
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.auth_service.get_token_expire_minutes() * 60
        )
    
    async def get_current_user(self, token: str) -> UserResponse:
        """Obtiene el usuario actual basado en el token."""
        # Verificar token
        payload = self.auth_service.verify_token(token)
        user_id = payload["user_id"]
        
        # Buscar usuario
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationError("Usuario no encontrado")
        
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        ) 