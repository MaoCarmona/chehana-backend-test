"""Implementación del repositorio de usuarios con SQLAlchemy."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """Implementación del repositorio de usuarios con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        db_user = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None
    
    async def update(self, user: User) -> User:
        """Actualiza un usuario."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"Usuario con ID {user.id} no encontrado")
        
        db_user.email = user.email
        db_user.username = user.username
        db_user.full_name = user.full_name
        db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        db_user.updated_at = user.updated_at
        
        await self.session.commit()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)
    
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.commit()
        return True
    
    async def list_all(self) -> List[User]:
        """Lista todos los usuarios."""
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        return [self._to_entity(db_user) for db_user in db_users]
    
    def _to_entity(self, db_user: UserModel) -> User:
        """Convierte un modelo de base de datos a entidad de dominio."""
        return User(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        ) 