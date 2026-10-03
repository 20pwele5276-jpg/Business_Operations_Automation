class ApplicationError(Exception):
    """Base exception for application-specific errors."""

class FileProcessingError(ApplicationError):
    """Raised when a file cannot be processed correctly."""

class DatabaseError(ApplicationError):
    """Raised when a database operation fails."""

class ValidationError(ApplicationError):
    """Raised when business data fails validation."""
