"""Tests unitarios para entidades del dominio."""

from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.entities.task import Task, TaskPriority, TaskStatus
from app.domain.entities.task_list import TaskList
from app.domain.entities.user import User


class TestUser:
    """Tests para la entidad User."""
    
    def test_user_creation(self):
        """Test creación de usuario."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password",
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.hashed_password == "hashed_password"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)


class TestTaskList:
    """Tests para la entidad TaskList."""
    
    def test_task_list_creation(self):
        """Test creación de lista de tareas."""
        owner_id = uuid4()
        task_list = TaskList(
            title="Test List",
            description="Test Description",
            owner_id=owner_id,
        )
        
        assert task_list.title == "Test List"
        assert task_list.description == "Test Description"
        assert task_list.owner_id == owner_id
        assert isinstance(task_list.created_at, datetime)
    
    def test_update_title(self):
        """Test actualización de título."""
        task_list = TaskList(
            title="Original Title",
            owner_id=uuid4(),
        )
        
        original_updated_at = task_list.updated_at
        task_list.update_title("New Title")
        
        assert task_list.title == "New Title"
        assert task_list.updated_at != original_updated_at
    
    def test_update_title_validation(self):
        """Test validación de título vacío."""
        task_list = TaskList(
            title="Original Title",
            owner_id=uuid4(),
        )
        
        with pytest.raises(ValueError, match="El título no puede estar vacío"):
            task_list.update_title("")
    
    def test_update_description(self):
        """Test actualización de descripción."""
        task_list = TaskList(
            title="Test Title",
            owner_id=uuid4(),
        )
        
        task_list.update_description("New Description")
        
        assert task_list.description == "New Description"
        assert task_list.updated_at is not None


class TestTask:
    """Tests para la entidad Task."""
    
    def test_task_creation(self):
        """Test creación de tarea."""
        task_list_id = uuid4()
        task = Task(
            title="Test Task",
            description="Test Description",
            task_list_id=task_list_id,
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_list_id == task_list_id
        assert task.assigned_to is None
        assert isinstance(task.created_at, datetime)
    
    def test_update_status_to_completed(self):
        """Test actualización de estado a completado."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        task.update_status(TaskStatus.COMPLETED)
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.updated_at is not None
    
    def test_update_status_from_completed(self):
        """Test actualización de estado desde completado."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        # Completar tarea
        task.update_status(TaskStatus.COMPLETED)
        assert task.completed_at is not None
        
        # Cambiar a en progreso
        task.update_status(TaskStatus.IN_PROGRESS)
        
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.completed_at is None
    
    def test_update_priority(self):
        """Test actualización de prioridad."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        task.update_priority(TaskPriority.HIGH)
        
        assert task.priority == TaskPriority.HIGH
        assert task.updated_at is not None
    
    def test_assign_to_user(self):
        """Test asignación de tarea a usuario."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        user_id = uuid4()
        task.assign_to_user(user_id)
        
        assert task.assigned_to == user_id
        assert task.updated_at is not None
    
    def test_unassign(self):
        """Test desasignación de tarea."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
            assigned_to=uuid4(),
        )
        
        task.unassign()
        
        assert task.assigned_to is None
        assert task.updated_at is not None
    
    def test_is_completed(self):
        """Test verificación de tarea completada."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        assert not task.is_completed()
        
        task.update_status(TaskStatus.COMPLETED)
        assert task.is_completed()
    
    def test_is_overdue_without_due_date(self):
        """Test verificación de vencimiento sin fecha límite."""
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
        )
        
        assert not task.is_overdue()
    
    def test_is_overdue_with_future_date(self):
        """Test verificación de vencimiento con fecha futura."""
        from datetime import datetime, timedelta
        
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
            due_date=datetime.now() + timedelta(days=1),
        )
        
        assert not task.is_overdue()
    
    def test_is_overdue_with_past_date(self):
        """Test verificación de vencimiento con fecha pasada."""
        from datetime import datetime, timedelta
        
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
            due_date=datetime.now() - timedelta(days=1),
        )
        
        assert task.is_overdue()
    
    def test_is_overdue_completed_task(self):
        """Test que tarea completada no está vencida."""
        from datetime import datetime, timedelta
        
        task = Task(
            title="Test Task",
            task_list_id=uuid4(),
            due_date=datetime.now() - timedelta(days=1),
        )
        
        task.update_status(TaskStatus.COMPLETED)
        
        assert not task.is_overdue() 