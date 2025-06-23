"""Excepciones personalizadas de la aplicación."""


class ApplicationException(Exception):
    """Excepción base de la aplicación."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(ApplicationException):
    """Error cuando un recurso no es encontrado."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} con identificador '{identifier}' no encontrado"
        super().__init__(message, "NOT_FOUND")


class ValidationError(ApplicationException):
    """Error de validación."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(ApplicationException):
    """Error de autenticación."""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(ApplicationException):
    """Error de autorización."""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class ConflictError(ApplicationException):
    """Error de conflicto (ej. recurso ya existe)."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT_ERROR")


class BusinessRuleError(ApplicationException):
    """Error de regla de negocio."""
    
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_RULE_ERROR") 