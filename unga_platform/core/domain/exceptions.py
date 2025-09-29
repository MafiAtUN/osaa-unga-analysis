"""
Domain Exceptions - Business Logic Exceptions
Custom exceptions for domain-specific business rules
"""

class DomainException(Exception):
    """Base domain exception."""
    pass

class AnalysisException(DomainException):
    """Analysis-related domain exceptions."""
    pass

class SecurityException(DomainException):
    """Security-related domain exceptions."""
    pass

class ValidationException(DomainException):
    """Validation-related domain exceptions."""
    pass

class BusinessRuleViolationException(DomainException):
    """Business rule violation exception."""
    pass

class EntityNotFoundException(DomainException):
    """Entity not found exception."""
    pass

class InvalidOperationException(DomainException):
    """Invalid operation exception."""
    pass
