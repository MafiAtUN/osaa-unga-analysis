"""
Application Configuration Management
Centralized configuration for the UN GA Daily Readouts application
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # Application Info
    APP_NAME = "UN GA Daily Readouts"
    VERSION = "2.1.0"
    DESCRIPTION = "Production-ready Streamlit application for analyzing UN General Assembly speeches"
    DEVELOPER = "SMU Data Team"
    
    # Security Settings
    SECURITY_ENABLED = True
    RATE_LIMIT_ATTEMPTS = int(os.getenv("RATE_LIMIT_ATTEMPTS", "5"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "300"))  # 5 minutes
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
    
    # File Upload Settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    ALLOWED_FILE_TYPES = ['.pdf', '.docx', '.mp3']
    
    # API Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    
    # Whisper API Configuration
    WHISPER_API_KEY = os.getenv('WHISPER_API_KEY')
    WHISPER_ENDPOINT = os.getenv('WHISPER_ENDPOINT')
    WHISPER_API_VERSION = os.getenv('WHISPER_API_VERSION', '2024-06-01')
    
    # Authentication
    APP_PASSWORD = os.getenv('APP_PASSWORD')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///analyses.db')
    
    # UI Settings
    PAGE_TITLE = "UN GA Daily Readouts"
    PAGE_ICON = "🇺🇳"
    LAYOUT = "wide"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, missing_vars)."""
        missing = []
        
        if not cls.AZURE_OPENAI_API_KEY:
            missing.append('AZURE_OPENAI_API_KEY')
        if not cls.AZURE_OPENAI_ENDPOINT:
            missing.append('AZURE_OPENAI_ENDPOINT')
        if not cls.APP_PASSWORD:
            missing.append('APP_PASSWORD')
            
        return len(missing) == 0, missing
    
    @classmethod
    def get_azure_config(cls) -> dict:
        """Get Azure OpenAI configuration."""
        return {
            'api_key': cls.AZURE_OPENAI_API_KEY,
            'endpoint': cls.AZURE_OPENAI_ENDPOINT,
            'api_version': cls.AZURE_OPENAI_API_VERSION
        }
    
    @classmethod
    def get_whisper_config(cls) -> dict:
        """Get Whisper API configuration."""
        return {
            'api_key': cls.WHISPER_API_KEY or cls.AZURE_OPENAI_API_KEY,
            'endpoint': cls.WHISPER_ENDPOINT or cls.AZURE_OPENAI_ENDPOINT,
            'api_version': cls.WHISPER_API_VERSION
        }

# Global settings instance
settings = Settings()
