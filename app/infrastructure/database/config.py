"""Configuración de la base de datos."""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class DatabaseSettings(BaseSettings):
    """Configuración de la base de datos."""
    
    database_url: str = "postgresql://user:password@localhost:5432/chehana_db"
    database_url_test: Optional[str] = None
    echo: bool = False
    
    class Config:
        env_file = ".env"


class Base(DeclarativeBase):
    """Clase base para los modelos de SQLAlchemy."""
    pass


# Configuración global
settings = DatabaseSettings()

# Motor de base de datos asíncrono
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.echo,
    future=True
)

# Motor de base de datos síncrono (para migraciones)
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql"),
    echo=settings.echo,
    future=True
)

# Sesión asíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sesión síncrona
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)


async def get_async_session() -> AsyncSession:
    """Obtiene una sesión asíncrona de base de datos."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session():
    """Obtiene una sesión síncrona de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 