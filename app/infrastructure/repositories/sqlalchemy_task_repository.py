"""Implementación del repositorio de tareas con SQLAlchemy."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task, TaskPriority, TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.models import TaskModel


class SQLAlchemyTaskRepository(TaskRepository):
    """Implementación del repositorio de tareas con SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, task: Task) -> Task:
        """Crea una nueva tarea."""
        db_task = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            task_list_id=task.task_list_id,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return self._to_entity(db_task)
    
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Obtiene una tarea por ID."""
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(stmt)
        db_task = result.scalar_one_or_none()
        return self._to_entity(db_task) if db_task else None
    
    async def get_by_task_list(
        self, 
        task_list_id: UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """Obtiene todas las tareas de una lista con filtros opcionales."""
        stmt = select(TaskModel).where(TaskModel.task_list_id == task_list_id)
        
        if status:
            stmt = stmt.where(TaskModel.status == status.value)
        
        if priority:
            stmt = stmt.where(TaskModel.priority == priority.value)
        
        result = await self.session.execute(stmt)
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    async def get_by_assigned_user(self, user_id: UUID) -> List[Task]:
        """Obtiene todas las tareas asignadas a un usuario."""
        stmt = select(TaskModel).where(TaskModel.assigned_to == user_id)
        result = await self.session.execute(stmt)
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    async def update(self, task: Task) -> Task:
        """Actualiza una tarea."""
        stmt = select(TaskModel).where(TaskModel.id == task.id)
        result = await self.session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            raise ValueError(f"Tarea con ID {task.id} no encontrada")
        
        db_task.title = task.title
        db_task.description = task.description
        db_task.status = task.status.value
        db_task.priority = task.priority.value
        db_task.assigned_to = task.assigned_to
        db_task.due_date = task.due_date
        db_task.updated_at = task.updated_at
        db_task.completed_at = task.completed_at
        
        await self.session.commit()
        await self.session.refresh(db_task)
        return self._to_entity(db_task)
    
    async def delete(self, task_id: UUID) -> bool:
        """Elimina una tarea."""
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            return False
        
        await self.session.delete(db_task)
        await self.session.commit()
        return True
    
    async def count_by_task_list_and_status(
        self, 
        task_list_id: UUID, 
        status: TaskStatus
    ) -> int:
        """Cuenta las tareas de una lista por estado."""
        stmt = select(func.count(TaskModel.id)).where(
            TaskModel.task_list_id == task_list_id,
            TaskModel.status == status.value
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    def _to_entity(self, db_task: TaskModel) -> Task:
        """Convierte un modelo de base de datos a entidad de dominio."""
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=TaskStatus(db_task.status),
            priority=TaskPriority(db_task.priority),
            task_list_id=db_task.task_list_id,
            assigned_to=db_task.assigned_to,
            due_date=db_task.due_date,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            completed_at=db_task.completed_at
        ) 