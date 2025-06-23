"""Interfaz del repositorio de usuarios."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(ABC):
    """Interfaz del repositorio de usuarios."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        """Lista todos los usuarios."""
        pass 