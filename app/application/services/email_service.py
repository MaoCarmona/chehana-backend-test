"""Servicio de email simulado."""

import asyncio
import logging
from typing import List

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class EmailSettings(BaseSettings):
    """Configuración de email."""
    
    smtp_server: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = "test@example.com"
    smtp_password: str = "password"
    
    class Config:
        env_file = ".env"


class EmailService:
    """Servicio de email simulado."""
    
    def __init__(self):
        self.settings = EmailSettings()
    
    async def send_task_assignment_notification(
        self, 
        user_email: str, 
        task_title: str, 
        task_list_title: str
    ) -> bool:
        """Simula el envío de notificación de asignación de tarea."""
        try:
            # Simulación de envío de email
            await asyncio.sleep(0.1)  # Simular latencia de red
            
            logger.info(
                f"[SIMULACIÓN] Email enviado a {user_email}: "
                f"Te han asignado la tarea '{task_title}' "
                f"en la lista '{task_list_title}'"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error simulando envío de email: {e}")
            return False
    
    async def send_task_completion_notification(
        self, 
        user_email: str, 
        task_title: str
    ) -> bool:
        """Simula el envío de notificación de tarea completada."""
        try:
            # Simulación de envío de email
            await asyncio.sleep(0.1)  # Simular latencia de red
            
            logger.info(
                f"[SIMULACIÓN] Email enviado a {user_email}: "
                f"La tarea '{task_title}' ha sido completada"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error simulando envío de email: {e}")
            return False
    
    async def send_invitation_email(
        self, 
        user_email: str, 
        inviter_name: str, 
        task_list_title: str
    ) -> bool:
        """Simula el envío de invitación a colaborar en una lista."""
        try:
            # Simulación de envío de email
            await asyncio.sleep(0.1)  # Simular latencia de red
            
            logger.info(
                f"[SIMULACIÓN] Email de invitación enviado a {user_email}: "
                f"{inviter_name} te ha invitado a colaborar en '{task_list_title}'"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error simulando envío de invitación: {e}")
            return False 