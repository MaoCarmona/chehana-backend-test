# Decision Log - Chehana Backend Test

Este documento explica las decisiones técnicas tomadas durante el desarrollo del sistema de gestión de tareas.

## 📋 Índice

1. [Arquitectura General](#arquitectura-general)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Estructura de Base de Datos](#estructura-de-base-de-datos)
4. [Autenticación y Autorización](#autenticación-y-autorización)
5. [Patrones de Diseño](#patrones-de-diseño)
6. [Testing](#testing)
7. [DevOps y Deployment](#devops-y-deployment)
8. [Decisiones de Rendimiento](#decisiones-de-rendimiento)

## 🏗️ Arquitectura General

### Clean Architecture

**Decisión**: Implementar Clean Architecture con separación clara de capas.

**Razones**:
- ✅ **Mantenibilidad**: Separación clara de responsabilidades
- ✅ **Testabilidad**: Fácil testeo unitario de cada capa
- ✅ **Escalabilidad**: Permite agregar nuevas funcionalidades sin afectar el core
- ✅ **Independencia**: El dominio no depende de frameworks o bases de datos

**Estructura Implementada**:
```
Domain (Entidades + Repositorios abstractos)
    ↓
Application (Casos de uso + DTOs + Servicios)
    ↓
Infrastructure (Implementaciones + API + DB)
```

**Alternativas Consideradas**:
- MVR tradicional: Descartado por acoplamiento
- Arquitectura por capas simple: Descartado por mezcla de responsabilidades

## 🛠️ Stack Tecnológico

### FastAPI como Framework Principal

**Decisión**: Usar FastAPI como framework web principal.

**Razones**:
- ✅ **Performance**: Uno de los frameworks más rápidos para Python
- ✅ **Tipado**: Soporte nativo para type hints
- ✅ **Documentación automática**: Swagger/OpenAPI integrado
- ✅ **Validación**: Pydantic integrado para validación de datos
- ✅ **Async/Await**: Soporte nativo para programación asíncrona

**Alternativas Consideradas**:
- Django REST Framework: Más pesado, no async nativo
- Flask: Requiere más configuración manual

### PostgreSQL como Base de Datos

**Decisión**: Usar PostgreSQL como base de datos principal.

**Razones**:
- ✅ **ACID**: Garantías de transacciones
- ✅ **Relaciones**: Soporte completo para relaciones complejas
- ✅ **UUID**: Soporte nativo para UUIDs
- ✅ **JSON**: Soporte para datos semi-estructurados
- ✅ **Escalabilidad**: Probado en producción a gran escala

**Alternativas Consideradas**:
- MongoDB: Descartado por necesidad de relaciones estrictas
- SQLite: Descartado por limitaciones de concurrencia

### SQLAlchemy con Async

**Decisión**: Usar SQLAlchemy 2.0 con soporte asíncrono.

**Razones**:
- ✅ **ORM Maduro**: Ampliamente probado y documentado
- ✅ **Async Support**: Soporte nativo para operaciones asíncronas
- ✅ **Type Safety**: Excelente integración con type hints
- ✅ **Migration**: Alembic integrado para migraciones

**Implementación**:
```python
# Configuración async
async_engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(bind=async_engine)
```

## 🗃️ Estructura de Base de Datos

### Uso de UUIDs como Primary Keys

**Decisión**: Usar UUIDs en lugar de IDs incrementales.

**Razones**:
- ✅ **Seguridad**: No expone información sobre volumen de datos
- ✅ **Distribución**: Permite sharding sin conflictos
- ✅ **APIs**: URLs más seguras
- ✅ **Integración**: Facilita integraciones con sistemas externos

**Implementación**:
```python
id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), 
    primary_key=True, 
    default=uuid.uuid4
)
```

### Relaciones y Constraints

**Decisión**: Usar foreign keys con cascades específicos.

**Razones**:
- ✅ **Integridad**: Garantiza consistencia de datos
- ✅ **Performance**: Índices automáticos en FKs
- ✅ **Mantenimiento**: Cascades automáticos apropiados

**Implementación**:
```python
# Cascade DELETE para tareas cuando se elimina lista
tasks: Mapped[List["TaskModel"]] = relationship(
    "TaskModel", 
    back_populates="task_list", 
    cascade="all, delete-orphan"
)

# SET NULL para asignaciones cuando se elimina usuario
assigned_to: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), 
    ForeignKey("users.id", ondelete="SET NULL"), 
    nullable=True
)
```

## 🔐 Autenticación y Autorización

### JWT para Autenticación

**Decisión**: Implementar autenticación basada en JWT.

**Razones**:
- ✅ **Stateless**: No requiere almacenamiento de sesión
- ✅ **Escalabilidad**: Fácil escalamiento horizontal
- ✅ **Performance**: No consultas de sesión en cada request
- ✅ **Estándar**: RFC 7519, ampliamente soportado

**Configuración**:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
```

**Alternativas Consideradas**:
- Sessions: Descartado por limitaciones de escalabilidad
- OAuth2: Innecesario para este scope

### bcrypt para Hashing de Passwords

**Decisión**: Usar bcrypt para hashear contraseñas.

**Razones**:
- ✅ **Seguridad**: Resistente a ataques de fuerza bruta
- ✅ **Salt automático**: Salt único por password
- ✅ **Configurable**: Work factor ajustable
- ✅ **Estándar**: Ampliamente usado y auditado

### Autorización Basada en Ownership

**Decisión**: Implementar autorización basada en propietario de recursos.

**Razones**:
- ✅ **Simplicidad**: Modelo simple y comprensible
- ✅ **Seguridad**: Cada usuario solo ve sus recursos
- ✅ **Performance**: Filtros eficientes por owner_id

**Implementación**:
```python
# Solo el propietario puede ver/modificar sus listas
if task_list.owner_id != user_id:
    raise AuthorizationError("No autorizado")
```

## 🎯 Patrones de Diseño

### Repository Pattern

**Decisión**: Implementar Repository Pattern para abstracción de datos.

**Razones**:
- ✅ **Testabilidad**: Fácil mocking para tests
- ✅ **Flexibilidad**: Cambio de implementación sin afectar lógica
- ✅ **Separación**: Dominio independiente de infraestructura

**Implementación**:
```python
# Contrato abstracto
class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

# Implementación concreta
class SQLAlchemyUserRepository(UserRepository):
    async def create(self, user: User) -> User:
        # Implementación específica
```

### Dependency Injection

**Decisión**: Usar el sistema de DI nativo de FastAPI.

**Razones**:
- ✅ **Integración**: Nativo en FastAPI
- ✅ **Performance**: Resolución eficiente
- ✅ **Simplicidad**: Sintaxis clara y concisa

**Implementación**:
```python
def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)
```

### Use Case Pattern

**Decisión**: Encapsular lógica de negocio en casos de uso.

**Razones**:
- ✅ **Single Responsibility**: Cada caso de uso tiene una responsabilidad
- ✅ **Testabilidad**: Fácil testeo de lógica de negocio
- ✅ **Reutilización**: Casos de uso reutilizables

## 🧪 Testing

### pytest como Framework de Testing

**Decisión**: Usar pytest para testing.

**Razones**:
- ✅ **Fixtures**: Sistema de fixtures flexible
- ✅ **Parametrización**: Tests parametrizados fáciles
- ✅ **Plugins**: Amplio ecosistema de plugins
- ✅ **Async**: Soporte para testing asíncrono

### Cobertura de 75%

**Decisión**: Establecer objetivo mínimo de 75% de cobertura.

**Razones**:
- ✅ **Calidad**: Balance entre calidad y tiempo de desarrollo
- ✅ **Pragmático**: No 100% que puede ser contraproducente
- ✅ **Enfoque**: Concentrarse en lógica crítica

**Configuración**:
```ini
[tool:pytest]
addopts = --cov=app --cov-fail-under=75
```

### Testing por Capas

**Decisión**: Separar tests por tipo (unit/integration).

**Razones**:
- ✅ **Velocidad**: Tests unitarios rápidos
- ✅ **Aislamiento**: Tests unitarios aislados
- ✅ **Confiabilidad**: Tests de integración para flujos completos

**Estructura**:
```
tests/
├── unit/          # Tests rápidos, sin dependencias
└── integration/   # Tests con BD, más lentos
```

## 🚀 DevOps y Deployment

### Docker Multistage

**Decisión**: Usar Dockerfile multistage para optimización.

**Razones**:
- ✅ **Tamaño**: Imágenes más pequeñas
- ✅ **Seguridad**: Sin herramientas de build en producción
- ✅ **Performance**: Mejores tiempos de build

**Implementación**:
```dockerfile
# Etapa 1: Dependencias
FROM python:3.11-slim as dependencies
RUN pip install -r requirements.txt

# Etapa 2: Aplicación
FROM python:3.11-slim as application
COPY --from=dependencies /usr/local/lib/python3.11/site-packages
```

### Docker Compose para Desarrollo

**Decisión**: Incluir docker-compose.yml completo.

**Razones**:
- ✅ **Simplicidad**: Un comando para levantar todo
- ✅ **Consistencia**: Mismo entorno en todos lados
- ✅ **Servicios**: BD, email server incluidos

**Servicios incluidos**:
- App (FastAPI)
- PostgreSQL
- PgAdmin (administración)
- MailHog (testing de emails)

### Alembic para Migraciones

**Decisión**: Usar Alembic para migraciones de BD.

**Razones**:
- ✅ **Versionado**: Control de versiones de esquema
- ✅ **Rollback**: Capacidad de revertir cambios
- ✅ **Automatización**: Generación automática de migraciones

## ⚡ Decisiones de Rendimiento

### Async/Await en Toda la Stack

**Decisión**: Usar programación asíncrona en toda la aplicación.

**Razones**:
- ✅ **Concurrencia**: Mejor manejo de múltiples requests
- ✅ **Escalabilidad**: Menos recursos por connection
- ✅ **Performance**: Mejor utilización de CPU

**Implementación**:
```python
# Repository async
async def create(self, user: User) -> User:
    # Operación asíncrona
    
# Use case async
async def register_user(self, request: UserRegisterRequest):
    # Lógica asíncrona
    
# Endpoint async
async def register_user(request: UserRegisterRequest):
    # Handler asíncrono
```

### Lazy Loading de Relaciones

**Decisión**: Usar lazy loading por defecto, eager cuando sea necesario.

**Razones**:
- ✅ **Performance**: Evita N+1 queries
- ✅ **Memoria**: Carga solo datos necesarios
- ✅ **Flexibilidad**: Eager loading donde se requiera

### Connection Pooling

**Decisión**: Configurar pool de conexiones para BD.

**Razones**:
- ✅ **Performance**: Reutilización de conexiones
- ✅ **Recursos**: Límite de conexiones concurrentes
- ✅ **Estabilidad**: Previene agotamiento de conexiones

## 🔧 Herramientas de Desarrollo

### Black + isort para Formateo

**Decisión**: Usar Black como formateador principal con isort.

**Razones**:
- ✅ **Consistencia**: Formato consistente sin discusiones
- ✅ **Automatización**: Formateo automático
- ✅ **Adopción**: Estándar de facto en Python

### flake8 + ruff para Linting

**Decisión**: Combinar flake8 con ruff para linting.

**Razones**:
- ✅ **Calidad**: Detección de problemas potenciales
- ✅ **Estándares**: Adherencia a PEP 8
- ✅ **Performance**: ruff es extremadamente rápido

### Pre-commit Hooks (Recomendado)

**Decisión**: Recomendar pre-commit hooks.

**Razones**:
- ✅ **Prevención**: Detecta problemas antes del commit
- ✅ **Automatización**: Ejecuta herramientas automáticamente
- ✅ **Calidad**: Mantiene estándares de código

## 📊 Métricas y Monitoreo

### Health Checks

**Decisión**: Implementar endpoints de health check.

**Razones**:
- ✅ **Monitoring**: Facilita monitoreo automatizado
- ✅ **Deployment**: Validación de deployments
- ✅ **Debugging**: Información de estado del sistema

### Logging Estructurado

**Decisión**: Usar logging estructurado.

**Razones**:
- ✅ **Debugging**: Facilita debugging en producción
- ✅ **Monitoring**: Integración con sistemas de monitoreo
- ✅ **Trazabilidad**: Seguimiento de requests

## 🔮 Decisiones Futuras

### Cosas a Considerar para Producción

1. **Rate Limiting**: Implementar limitación de requests
2. **Caching**: Redis para caching de queries frecuentes
3. **Observability**: OpenTelemetry para tracing
4. **Security**: Implementar security headers
5. **Performance**: Profiling y optimización de queries
6. **Backup**: Estrategia de backup de BD
7. **CI/CD**: Pipeline automatizado
8. **Documentation**: Documentación de arquitectura

### Posibles Mejoras

1. **Microservicios**: Separar en servicios más pequeños
2. **Event Sourcing**: Para auditoria completa
3. **CQRS**: Separar commands de queries
4. **GraphQL**: API más flexible para frontend
5. **WebSockets**: Notificaciones en tiempo real

---

Este documento será actualizado conforme evolucione el proyecto y se tomen nuevas decisiones técnicas. 