"""Servicio de autenticación con JWT."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic_settings import BaseSettings

from app.application.exceptions.exceptions import AuthenticationError


class AuthSettings(BaseSettings):
    """Configuración para autenticación."""
    
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


class AuthService:
    """Servicio de autenticación."""
    
    def __init__(self):
        self.settings = AuthSettings()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña plana contra su hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Genera un hash de contraseña."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, user_id: UUID, username: str) -> str:
        """Crea un token de acceso JWT."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.access_token_expire_minutes
        )
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            self.settings.secret_key, 
            algorithm=self.settings.algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verifica y decodifica un token JWT."""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                raise AuthenticationError("Token inválido")
            
            return {
                "user_id": UUID(user_id),
                "username": username
            }
        except JWTError:
            raise AuthenticationError("Token inválido")
    
    def get_token_expire_minutes(self) -> int:
        """Obtiene los minutos de expiración del token."""
        return self.settings.access_token_expire_minutes 