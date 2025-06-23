"""Tests de integración para la API."""

import pytest


class TestAuthAPI:
    """Tests de integración para autenticación."""
    
    def test_register_user_success(self, client):
        """Test registro exitoso de usuario."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "password123",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
    
    def test_register_user_duplicate_email(self, client):
        """Test registro con email duplicado."""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "full_name": "User 1",
            "password": "password123",
        }
        
        # Primer registro
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Segundo registro con mismo email
        user_data["username"] = "user2"
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 409
    
    def test_login_success(self, client):
        """Test login exitoso."""
        # Registrar usuario
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "full_name": "Login User",
            "password": "password123",
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_data = {
            "username": "loginuser",
            "password": "password123",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login con credenciales inválidas."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test obtener usuario actual."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "authuser"
        assert data["email"] == "auth@example.com"


class TestTaskListAPI:
    """Tests de integración para listas de tareas."""
    
    def test_create_task_list(self, client, auth_headers):
        """Test crear lista de tareas."""
        task_list_data = {
            "title": "Mi Lista de Tareas",
            "description": "Una lista de ejemplo",
        }
        
        response = client.post(
            "/api/v1/task-lists/", 
            json=task_list_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_list_data["title"]
        assert data["description"] == task_list_data["description"]
        assert "id" in data
        assert data["completion_percentage"] == 0.0
    
    def test_get_user_task_lists(self, client, auth_headers):
        """Test obtener listas del usuario."""
        # Crear una lista
        task_list_data = {
            "title": "Lista de Test",
            "description": "Descripción de test",
        }
        client.post(
            "/api/v1/task-lists/", 
            json=task_list_data, 
            headers=auth_headers
        )
        
        # Obtener listas
        response = client.get("/api/v1/task-lists/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["title"] == "Lista de Test" for item in data)
    
    def test_get_task_list_unauthorized(self, client):
        """Test obtener lista sin autenticación."""
        response = client.get("/api/v1/task-lists/")
        
        assert response.status_code == 401


class TestTaskAPI:
    """Tests de integración para tareas."""
    
    def test_create_task(self, client, auth_headers):
        """Test crear tarea."""
        # Crear lista primero
        task_list_data = {
            "title": "Lista para Tareas",
            "description": "Lista de test",
        }
        list_response = client.post(
            "/api/v1/task-lists/", 
            json=task_list_data, 
            headers=auth_headers
        )
        list_id = list_response.json()["id"]
        
        # Crear tarea
        task_data = {
            "title": "Mi Tarea",
            "description": "Una tarea de ejemplo",
            "priority": "high",
        }
        
        response = client.post(
            f"/api/v1/tasks/lists/{list_id}/tasks",
            json=task_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == "high"
        assert data["status"] == "pending"
    
    def test_get_tasks_by_list(self, client, auth_headers):
        """Test obtener tareas de una lista."""
        # Crear lista
        task_list_data = {"title": "Lista Test"}
        list_response = client.post(
            "/api/v1/task-lists/", 
            json=task_list_data, 
            headers=auth_headers
        )
        list_id = list_response.json()["id"]
        
        # Crear tarea
        task_data = {"title": "Tarea Test"}
        client.post(
            f"/api/v1/tasks/lists/{list_id}/tasks",
            json=task_data,
            headers=auth_headers,
        )
        
        # Obtener tareas
        response = client.get(
            f"/api/v1/tasks/lists/{list_id}/tasks",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["title"] == "Tarea Test" for item in data)


class TestHealthCheck:
    """Tests para health checks."""
    
    def test_root_endpoint(self, client):
        """Test endpoint raíz."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"
    
    def test_health_check(self, client):
        """Test health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data 