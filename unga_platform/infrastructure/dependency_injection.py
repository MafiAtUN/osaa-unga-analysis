"""
Dependency Injection Container
Enterprise-grade dependency injection for clean architecture
"""

from typing import Any, Dict, Type, Optional
import logging

logger = logging.getLogger(__name__)

class Container:
    """Dependency injection container for enterprise application."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
    
    def register_singleton(self, interface: Type, implementation: Any) -> None:
        """Register a singleton service."""
        key = interface.__name__ if hasattr(interface, '__name__') else str(interface)
        self._singletons[key] = implementation
        logger.debug(f"Registered singleton: {key}")
    
    def register_transient(self, interface: Type, implementation: Type) -> None:
        """Register a transient service."""
        key = interface.__name__ if hasattr(interface, '__name__') else str(interface)
        self._services[key] = implementation
        logger.debug(f"Registered transient: {key}")
    
    def register_factory(self, interface: Type, factory: callable) -> None:
        """Register a factory service."""
        key = interface.__name__ if hasattr(interface, '__name__') else str(interface)
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")
    
    def get(self, interface: Type) -> Any:
        """Get a service instance."""
        key = interface.__name__ if hasattr(interface, '__name__') else str(interface)
        
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check factories
        if key in self._factories:
            instance = self._factories[key]()
            logger.debug(f"Created instance from factory: {key}")
            return instance
        
        # Check transient services
        if key in self._services:
            implementation = self._services[key]
            instance = implementation()
            logger.debug(f"Created transient instance: {key}")
            return instance
        
        raise ValueError(f"Service not registered: {key}")
    
    def configure(self, config) -> None:
        """Configure the container with application dependencies."""
        try:
            # Register configuration
            self.register_singleton('ApplicationConfig', config)
            
            # Register core services
            self._register_core_services(config)
            
            # Register infrastructure services
            self._register_infrastructure_services(config)
            
            # Register application services
            self._register_application_services(config)
            
            logger.info("Dependency injection container configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure container: {e}")
            raise
    
    def _register_core_services(self, config):
        """Register core domain services."""
        from ..core.domain.entities import Analysis, Country, User
        from ..core.domain.value_objects import AnalysisId, CountryCode, Classification
        
        # Register domain entities as factories
        self.register_factory('Analysis', lambda: Analysis)
        self.register_factory('Country', lambda: Country)
        self.register_factory('User', lambda: User)
        
        logger.debug("Core services registered")
    
    def _register_infrastructure_services(self, config):
        """Register infrastructure services."""
        from .database import DatabaseManager
        from .logging import LoggingService
        from .security import SecurityService
        from .llm import LLMService
        from .file_processing import FileProcessingService
        
        # Database
        db_manager = DatabaseManager(config.database)
        self.register_singleton('DatabaseManager', db_manager)
        
        # Logging
        logging_service = LoggingService(config.logging)
        self.register_singleton('LoggingService', logging_service)
        
        # Security
        security_service = SecurityService(config.security)
        self.register_singleton('SecurityService', security_service)
        
        # LLM Service
        llm_service = LLMService(config.llm)
        self.register_singleton('LLMService', llm_service)
        
        # File Processing
        file_service = FileProcessingService(config.security)
        self.register_singleton('FileProcessingService', file_service)
        
        logger.debug("Infrastructure services registered")
    
    def _register_application_services(self, config):
        """Register application services."""
        from ..core.application.use_cases import (
            AnalyzeSpeechUseCase,
            GetAnalysisUseCase,
            ListAnalysesUseCase,
            AuthenticateUserUseCase,
            ProcessFileUseCase
        )
        
        # Get required services
        db_manager = self.get('DatabaseManager')
        llm_service = self.get('LLMService')
        security_service = self.get('SecurityService')
        file_service = self.get('FileProcessingService')
        
        # Register use cases
        self.register_singleton('AnalyzeSpeechUseCase', 
            AnalyzeSpeechUseCase(db_manager, llm_service, security_service))
        self.register_singleton('GetAnalysisUseCase',
            GetAnalysisUseCase(db_manager))
        self.register_singleton('ListAnalysesUseCase',
            ListAnalysesUseCase(db_manager))
        self.register_singleton('AuthenticateUserUseCase',
            AuthenticateUserUseCase(security_service, security_service))
        self.register_singleton('ProcessFileUseCase',
            ProcessFileUseCase(file_service, security_service))
        
        logger.debug("Application services registered")
    
    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered."""
        key = interface.__name__ if hasattr(interface, '__name__') else str(interface)
        return key in self._services or key in self._singletons or key in self._factories
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        logger.info("Container cleared")
