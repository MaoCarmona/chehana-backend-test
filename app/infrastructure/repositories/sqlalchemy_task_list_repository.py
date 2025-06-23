"""Implementación del repositorio de listas de tareas con SQLAlchemy."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task_list import TaskList
from app.domain.repositories.task_list_repository import TaskListRepository
from app.infrastructure.database.models import TaskListModel


class SQLAlchemyTaskListRepository(TaskListRepository):
    """Implementación del repositorio de listas de tareas con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, task_list: TaskList) -> TaskList:
        """Crea una nueva lista de tareas."""
        db_task_list = TaskListModel(
            id=task_list.id,
            title=task_list.title,
            description=task_list.description,
            owner_id=task_list.owner_id,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at
        )
        self.session.add(db_task_list)
        await self.session.commit()
        await self.session.refresh(db_task_list)
        return self._to_entity(db_task_list)
    
    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        """Obtiene una lista de tareas por ID."""
        stmt = select(TaskListModel).where(TaskListModel.id == task_list_id)
        result = await self.session.execute(stmt)
        db_task_list = result.scalar_one_or_none()
        return self._to_entity(db_task_list) if db_task_list else None
    
    async def get_by_owner(self, owner_id: UUID) -> List[TaskList]:
        """Obtiene todas las listas de tareas de un propietario."""
        stmt = select(TaskListModel).where(TaskListModel.owner_id == owner_id)
        result = await self.session.execute(stmt)
        db_task_lists = result.scalars().all()
        return [self._to_entity(db_task_list) for db_task_list in db_task_lists]
    
    async def update(self, task_list: TaskList) -> TaskList:
        """Actualiza una lista de tareas."""
        stmt = select(TaskListModel).where(TaskListModel.id == task_list.id)
        result = await self.session.execute(stmt)
        db_task_list = result.scalar_one_or_none()
        
        if not db_task_list:
            raise ValueError(f"Lista de tareas con ID {task_list.id} no encontrada")
        
        db_task_list.title = task_list.title
        db_task_list.description = task_list.description
        db_task_list.updated_at = task_list.updated_at
        
        await self.session.commit()
        await self.session.refresh(db_task_list)
        return self._to_entity(db_task_list)
    
    async def delete(self, task_list_id: UUID) -> bool:
        """Elimina una lista de tareas."""
        stmt = select(TaskListModel).where(TaskListModel.id == task_list_id)
        result = await self.session.execute(stmt)
        db_task_list = result.scalar_one_or_none()
        
        if not db_task_list:
            return False
        
        await self.session.delete(db_task_list)
        await self.session.commit()
        return True
    
    async def list_all(self) -> List[TaskList]:
        """Lista todas las listas de tareas."""
        stmt = select(TaskListModel)
        result = await self.session.execute(stmt)
        db_task_lists = result.scalars().all()
        return [self._to_entity(db_task_list) for db_task_list in db_task_lists]
    
    def _to_entity(self, db_task_list: TaskListModel) -> TaskList:
        """Convierte un modelo de base de datos a entidad de dominio."""
        return TaskList(
            id=db_task_list.id,
            title=db_task_list.title,
            description=db_task_list.description,
            owner_id=db_task_list.owner_id,
            created_at=db_task_list.created_at,
            updated_at=db_task_list.updated_at
        ) 