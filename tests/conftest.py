"""Configuración de pytest y fixtures globales."""

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.config import Base, get_async_session
from app.infrastructure.database.models import UserModel, TaskListModel, TaskModel
from app.main import app

# Base de datos en memoria para testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Motor de base de datos para testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Session maker para testing
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Fixture para el event loop de asyncio."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    """Fixture para sesión de base de datos de testing."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session):
    """Fixture para cliente de testing de FastAPI."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(db_session):
    """Fixture para usuario de ejemplo."""
    from app.application.services.auth_service import AuthService
    
    auth_service = AuthService()
    hashed_password = auth_service.get_password_hash("testpassword123")
    
    user = UserModel(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hashed_password,
        is_active=True,
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def sample_task_list(db_session, sample_user):
    """Fixture para lista de tareas de ejemplo."""
    task_list = TaskListModel(
        title="Test Task List",
        description="A test task list",
        owner_id=sample_user.id,
    )
    
    db_session.add(task_list)
    await db_session.commit()
    await db_session.refresh(task_list)
    
    return task_list


@pytest_asyncio.fixture
async def sample_task(db_session, sample_task_list):
    """Fixture para tarea de ejemplo."""
    task = TaskModel(
        title="Test Task",
        description="A test task",
        status="pending",
        priority="medium",
        task_list_id=sample_task_list.id,
    )
    
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    
    return task


@pytest.fixture
def auth_headers(client):
    """Fixture para headers de autenticación."""
    # Registrar usuario
    register_data = {
        "email": "auth@example.com",
        "username": "authuser",
        "full_name": "Auth User",
        "password": "password123",
    }
    
    client.post("/api/v1/auth/register", json=register_data)
    
    # Login
    login_data = {
        "username": "authuser",
        "password": "password123",
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"} 