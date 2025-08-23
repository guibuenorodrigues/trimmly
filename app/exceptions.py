class BaseError(Exception):
    """Base class for all exceptions raised by the application."""

    pass


class DatabaseError(BaseError):
    """Exception raised for database-related errors."""

    pass


class EntityNotFoundError(DatabaseError):
    """Exception raised when a database query returns no results."""

    def __init__(self, entity_name: str, identifier: str | None = None):
        self.entity_name = entity_name
        self.identifier = identifier
        message = f"{entity_name} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message)


class DuplicateEntityError(DatabaseError):
    """Exception raised when trying to create an entity that already exists."""

    def __init__(self, entity_name: str, field_name: str, field_value: str):
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        message = f"{entity_name} already exists with {field_name}: {field_value}"
        super().__init__(message)


class ValidationError(BaseError):
    """Exception raised for validation errors."""

    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Validation error for {field_name}: {message}")


class ServiceError(BaseError):
    """Exception raised for service-level errors."""

    pass


class ExternalServiceError(ServiceError):
    """Exception raised when external service calls fail."""

    def __init__(self, service_name: str, message: str):
        self.service_name = service_name
        self.message = message
        super().__init__(f"External service '{service_name}' error: {message}")
