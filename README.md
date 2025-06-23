# Chehana Backend Test - Sistema de Gestión de Tareas

¡Bienvenido al sistema de gestión de tareas desarrollado con FastAPI! 🚀

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de gestión de tareas utilizando FastAPI, siguiendo principios de Clean Architecture y mejores prácticas de desarrollo. El sistema incluye autenticación JWT, CRUD completo de listas y tareas, filtros avanzados, asignación de usuarios y notificaciones simuladas.

## 🏗️ Arquitectura

El proyecto sigue los principios de **Clean Architecture**, separando el código en capas bien definidas:

```
app/
├── domain/                 # Capa de Dominio
│   ├── entities/          # Entidades de negocio
│   └── repositories/      # Contratos de repositorios
├── application/           # Capa de Aplicación
│   ├── dtos/             # Data Transfer Objects
│   ├── use_cases/        # Casos de uso
│   ├── services/         # Servicios de aplicación
│   └── exceptions/       # Excepciones personalizadas
└── infrastructure/       # Capa de Infraestructura
    ├── database/         # Configuración y modelos de BD
    ├── repositories/     # Implementaciones de repositorios
    └── api/              # Controladores y routers
```

## ✨ Funcionalidades

### Funcionalidades Principales
- ✅ **Autenticación JWT**: Registro y login de usuarios
- ✅ **CRUD de Listas**: Crear, obtener, actualizar y eliminar listas de tareas
- ✅ **CRUD de Tareas**: Gestión completa de tareas dentro de las listas
- ✅ **Estados de Tareas**: Cambio de estado (pending, in_progress, completed)
- ✅ **Filtros Avanzados**: Por estado, prioridad y porcentaje de completitud
- ✅ **Porcentaje de Completitud**: Cálculo automático por lista

### Funcionalidades Bonus
- ✅ **Asignación de Tareas**: Asignar usuarios responsables a tareas
- ✅ **Notificaciones Simuladas**: Envío ficticio de emails
- ✅ **Autorización Granular**: Control de acceso basado en propietarios
- ✅ **API Documentada**: Swagger UI automático

## 🛠️ Tecnologías Utilizadas

- **Framework**: FastAPI 0.104.1
- **Base de Datos**: PostgreSQL con SQLAlchemy (async)
- **Autenticación**: JWT con python-jose
- **Validación**: Pydantic v2
- **Migraciones**: Alembic
- **Testing**: pytest con coverage
- **Linting**: flake8, ruff
- **Formateo**: black, isort
- **Contenedores**: Docker & Docker Compose

## 🚀 Configuración del Entorno Local

### Prerrequisitos
- Python 3.11+
- PostgreSQL 15+ (o usar Docker)
- Git

### 1. Clonar el Repositorio
```bash
git clone git@github.com:MaoCarmona/chehana-backend-test.git
cd chehana-backend-test
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` basado en `env.example.txt`:
```bash
cp env.example.txt .env
```

O crea manualmente el archivo `.env` con el siguiente contenido:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://chehana_user:chehana_password@localhost:5432/chehana_db
DATABASE_URL_TEST=postgresql+asyncpg://chehana_user:chehana_password@localhost:5432/chehana_test_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (for simulated notifications)
SMTP_SERVER=localhost
SMTP_PORT=1025
SMTP_USERNAME=test@example.com
SMTP_PASSWORD=password

# Application Configuration
DEBUG=True
ENVIRONMENT=development
```

**Nota**: Cambia el `SECRET_KEY` por una clave segura en producción.

#### Variables de Entorno Disponibles

| Variable | Descripción | Valor por defecto | Requerida |
|----------|-------------|-------------------|-----------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | - | ✅ |
| `DATABASE_URL_TEST` | URL para base de datos de testing | - | ❌ |
| `SECRET_KEY` | Clave secreta para JWT | - | ✅ |
| `ALGORITHM` | Algoritmo para JWT | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de expiración del token | `30` | ❌ |
| `SMTP_SERVER` | Servidor SMTP para emails | `localhost` | ❌ |
| `SMTP_PORT` | Puerto SMTP | `1025` | ❌ |
| `SMTP_USERNAME` | Usuario SMTP | `test@example.com` | ❌ |
| `SMTP_PASSWORD` | Contraseña SMTP | `password` | ❌ |
| `DEBUG` | Modo debug | `True` | ❌ |
| `ENVIRONMENT` | Entorno de ejecución | `development` | ❌ |

### 5. Configurar Base de Datos
```bash
# Crear base de datos (opcional si usas Docker)
createdb chehana_db

# Ejecutar migraciones
alembic upgrade head
```

### 6. Ejecutar la Aplicación
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en: http://localhost:8000

## 🐳 Ejecutar con Docker

### Opción 1: Docker Compose (Recomendado)
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Detener servicios
docker-compose down
```

### Opción 2: Solo la Aplicación
```bash
# Construir imagen
docker build -t chehana-app .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e SECRET_KEY=your_secret_key \
  chehana-app
```

### Servicios Incluidos en Docker Compose
- **App**: FastAPI application (puerto 8000)
- **PostgreSQL**: Base de datos (puerto 5432)
- **PgAdmin**: Administrador de BD (puerto 5050)
- **MailHog**: Servidor SMTP para testing (puerto 8025)

## 🧪 Ejecutar Pruebas

### Ejecutar Todas las Pruebas
```bash
pytest
```

### Con Coverage
```bash
pytest --cov=app --cov-report=html
```

### Ejecutar Pruebas Específicas
```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Test específico
pytest tests/test_auth.py::test_register_user
```

### Ver Reporte de Coverage
```bash
# Abrir reporte HTML
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

## 🔧 Herramientas de Desarrollo

### Linting y Formateo
```bash
# Formatear código
black app/ tests/
isort app/ tests/

# Linting
flake8 app/ tests/
ruff check app/ tests/

# Corregir automáticamente con ruff
ruff check --fix app/ tests/
```

### Migraciones de Base de Datos
```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

## 📖 Documentación de la API

### Swagger UI
Una vez que la aplicación esté ejecutándose, visita:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual

#### Listas de Tareas
- `POST /api/v1/task-lists/` - Crear lista
- `GET /api/v1/task-lists/` - Obtener listas del usuario
- `GET /api/v1/task-lists/{id}` - Obtener lista específica
- `PUT /api/v1/task-lists/{id}` - Actualizar lista
- `DELETE /api/v1/task-lists/{id}` - Eliminar lista

#### Tareas
- `POST /api/v1/tasks/lists/{list_id}/tasks` - Crear tarea
- `GET /api/v1/tasks/lists/{list_id}/tasks` - Obtener tareas (con filtros)
- `GET /api/v1/tasks/{id}` - Obtener tarea específica
- `PUT /api/v1/tasks/{id}` - Actualizar tarea
- `PATCH /api/v1/tasks/{id}/status` - Cambiar estado
- `PATCH /api/v1/tasks/{id}/assign/{user_id}` - Asignar tarea
- `DELETE /api/v1/tasks/{id}` - Eliminar tarea

### Ejemplo de Uso

1. **Registrar usuario**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "usuario",
    "full_name": "Usuario Test",
    "password": "password123"
  }'
```

2. **Iniciar sesión**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "password123"
  }'
```

3. **Crear lista de tareas** (usar token del login):
```bash
curl -X POST "http://localhost:8000/api/v1/task-lists/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Lista de Tareas",
    "description": "Lista de ejemplo"
  }'
```

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
```bash
# Verificar que PostgreSQL esté ejecutándose
sudo service postgresql status

# Verificar variables de entorno
echo $DATABASE_URL
```

### Problemas con Migraciones
```bash
# Limpiar y recrear migraciones
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Puerto ya en Uso
```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000

# Terminar proceso
kill -9 <PID>
```

## 📊 Estructura de Testing

```
tests/
├── unit/                  # Tests unitarios
│   ├── test_entities.py   # Tests de entidades
│   ├── test_use_cases.py  # Tests de casos de uso
│   └── test_services.py   # Tests de servicios
├── integration/           # Tests de integración
│   ├── test_repositories.py
│   └── test_api.py
└── conftest.py           # Configuración de pytest
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Michael Page**
- Email: michael@example.com
- GitHub: [@MichaelPage](https://github.com/MichaelPage)

## 🙏 Agradecimientos

- Equipo de Chehana por la oportunidad
- Comunidad de FastAPI por la excelente documentación
- Contribuidores de las librerías utilizadas

---

¿Preguntas o problemas? ¡No dudes en abrir un issue! 🚀