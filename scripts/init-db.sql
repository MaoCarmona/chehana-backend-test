-- Script de inicialización de base de datos para Docker
-- Este script se ejecuta automáticamente cuando se crea el contenedor de PostgreSQL

-- Crear extensión para UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear esquema para testing si no existe
CREATE SCHEMA IF NOT EXISTS test_schema;

-- Configurar timezone
SET timezone = 'UTC';

-- Mensaje de confirmación
SELECT 'Base de datos inicializada correctamente para Chehana Backend Test' as status; 