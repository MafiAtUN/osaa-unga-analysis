"""
Logging configuration for the UNGA Analysis App
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Set up comprehensive logging for the application."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "errors.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Performance handler
    perf_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "performance.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(detailed_formatter)
    
    # Create performance logger
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    
    # Data handler
    data_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "data.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    data_handler.setLevel(logging.INFO)
    data_handler.setFormatter(detailed_formatter)
    
    # Create data logger
    data_logger = logging.getLogger("data")
    data_logger.addHandler(data_handler)
    data_logger.setLevel(logging.INFO)
    
    # UI handler
    ui_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "ui.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    ui_handler.setLevel(logging.INFO)
    ui_handler.setFormatter(detailed_formatter)
    
    # Create UI logger
    ui_logger = logging.getLogger("ui")
    ui_logger.addHandler(ui_handler)
    ui_logger.setLevel(logging.INFO)
    
    # API handler
    api_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "api.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)
    
    # Create API logger
    api_logger = logging.getLogger("api")
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized successfully")
    logger.info(f"Log files will be written to: {logs_dir.absolute()}")
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)

def log_performance(operation: str, duration: float, details: str = ""):
    """Log performance metrics."""
    perf_logger = logging.getLogger("performance")
    perf_logger.info(f"PERF: {operation} took {duration:.3f}s {details}")

def log_data_operation(operation: str, details: str = ""):
    """Log data operations."""
    data_logger = logging.getLogger("data")
    data_logger.info(f"DATA: {operation} - {details}")

def log_ui_event(event: str, details: str = ""):
    """Log UI events."""
    ui_logger = logging.getLogger("ui")
    ui_logger.info(f"UI: {event} - {details}")

def log_api_call(endpoint: str, method: str, status_code: int, duration: float):
    """Log API calls."""
    api_logger = logging.getLogger("api")
    api_logger.info(f"API: {method} {endpoint} - {status_code} - {duration:.3f}s")

# Initialize logging when module is imported
setup_logging()
