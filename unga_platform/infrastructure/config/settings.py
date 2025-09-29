"""
Enterprise Configuration Management
Professional configuration system with validation and environment management
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import logging

class Environment(Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create from environment variables."""
        return cls(
            url=os.getenv('DATABASE_URL', 'sqlite:///analyses.db'),
            echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DATABASE_POOL_RECYCLE', '3600'))
        )

@dataclass
class LLMConfig:
    """LLM service configuration."""
    provider: str
    api_key: str
    endpoint: str
    api_version: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 30
    retry_attempts: int = 3
    
    @classmethod
    def azure_openai_from_env(cls) -> 'LLMConfig':
        """Create Azure OpenAI config from environment."""
        return cls(
            provider="azure_openai",
            api_key=os.getenv('AZURE_OPENAI_API_KEY', ''),
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
            model=os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o'),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '4000')),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.1')),
            timeout=int(os.getenv('LLM_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('LLM_RETRY_ATTEMPTS', '3'))
        )

@dataclass
class SecurityConfig:
    """Security configuration."""
    app_password: str
    rate_limit_attempts: int = 5
    rate_limit_window: int = 300
    max_input_length: int = 10000
    max_file_size: int = 52428800  # 50MB
    allowed_file_types: List[str] = None
    session_timeout: int = 3600
    enable_csrf: bool = True
    enable_rate_limiting: bool = True
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.pdf', '.docx', '.mp3']
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create from environment variables."""
        return cls(
            app_password=os.getenv('APP_PASSWORD', ''),
            rate_limit_attempts=int(os.getenv('RATE_LIMIT_ATTEMPTS', '5')),
            rate_limit_window=int(os.getenv('RATE_LIMIT_WINDOW', '300')),
            max_input_length=int(os.getenv('MAX_INPUT_LENGTH', '10000')),
            max_file_size=int(os.getenv('MAX_FILE_SIZE', '52428800')),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600')),
            enable_csrf=os.getenv('ENABLE_CSRF', 'true').lower() == 'true',
            enable_rate_limiting=os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
        )

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = False
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create from environment variables."""
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE_PATH'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', '10485760')),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
            enable_console=os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true',
            enable_file=os.getenv('LOG_ENABLE_FILE', 'false').lower() == 'true'
        )

@dataclass
class ApplicationConfig:
    """Main application configuration."""
    name: str = "UN GA Daily Readouts"
    version: str = "2.1.0"
    description: str = "Professional UN General Assembly speech analysis platform"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8501
    
    # Sub-configurations
    database: DatabaseConfig = None
    llm: LLMConfig = None
    security: SecurityConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig.from_env()
        if self.llm is None:
            self.llm = LLMConfig.azure_openai_from_env()
        if self.security is None:
            self.security = SecurityConfig.from_env()
        if self.logging is None:
            self.logging = LoggingConfig.from_env()
    
    @classmethod
    def from_env(cls) -> 'ApplicationConfig':
        """Create application config from environment."""
        return cls(
            name=os.getenv('APP_NAME', 'UN GA Daily Readouts'),
            version=os.getenv('APP_VERSION', '2.1.0'),
            description=os.getenv('APP_DESCRIPTION', 'Professional UN General Assembly speech analysis platform'),
            environment=Environment(os.getenv('ENVIRONMENT', 'development')),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', '8501'))
        )
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Validate required fields
        if not self.security.app_password:
            errors.append("APP_PASSWORD is required")
        
        if not self.llm.api_key:
            errors.append("AZURE_OPENAI_API_KEY is required")
        
        if not self.llm.endpoint:
            errors.append("AZURE_OPENAI_ENDPOINT is required")
        
        # Validate numeric fields
        if self.security.rate_limit_attempts <= 0:
            errors.append("RATE_LIMIT_ATTEMPTS must be positive")
        
        if self.security.max_file_size <= 0:
            errors.append("MAX_FILE_SIZE must be positive")
        
        return errors
