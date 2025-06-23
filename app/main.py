"""Aplicación principal de FastAPI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.api.routers import auth, task_lists, tasks
from app.infrastructure.database.config import async_engine
from app.infrastructure.database.models import Base

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    # Startup
    logger.info("Iniciando aplicación...")
    
    # Crear tablas si no existen
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Aplicación iniciada correctamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    await async_engine.dispose()
    logger.info("Aplicación cerrada correctamente")


# Crear instancia de FastAPI
app = FastAPI(
    title="Chehana Backend Test - Sistema de Gestión de Tareas",
    description="""
    ## Sistema de Gestión de Tareas con FastAPI

    Este sistema permite:

    ### Funcionalidades Principales
    * **Autenticación JWT**: Registro y login de usuarios
    * **Gestión de Listas**: CRUD completo de listas de tareas
    * **Gestión de Tareas**: CRUD completo de tareas con estados y prioridades
    * **Filtros Avanzados**: Filtrado por estado, prioridad y porcentaje de completitud
    
    ### Funcionalidades Avanzadas (Bonus)
    * **Asignación de Tareas**: Asignar tareas a usuarios específicos
    * **Notificaciones**: Simulación de envío de emails de notificación
    * **Autorización**: Control de acceso basado en roles y propietarios
    
    ### Arquitectura
    * **Clean Architecture**: Separación clara por capas (Domain, Application, Infrastructure)
    * **Dependency Injection**: Inyección de dependencias con FastAPI
    * **Repository Pattern**: Abstracción de acceso a datos
    * **Use Cases**: Lógica de negocio encapsulada
    """,
    version="1.0.0",
    contact={
        "name": "Kevin Mauricio Carmona Loaiza",
        "email": "kevin.carmona@utp.edu.co",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(task_lists.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
async def root():
    """Endpoint de health check."""
    return {
        "message": "¡Bienvenido al Sistema de Gestión de Tareas de Chehana!",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint de verificación de salud."""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "auth": "active",
            "tasks": "active",
            "notifications": "active",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 