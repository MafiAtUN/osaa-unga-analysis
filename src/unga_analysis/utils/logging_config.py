"""
Comprehensive logging configuration for UNGA Analysis application.
Provides structured logging with file rotation, error tracking, and analysis capabilities.
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback
import functools
import sys
from contextlib import contextmanager

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'component'):
            log_entry['component'] = record.component
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'file_size'):
            log_entry['file_size'] = record.file_size
        if hasattr(record, 'model_used'):
            log_entry['model_used'] = record.model_used
        if hasattr(record, 'tokens_used'):
            log_entry['tokens_used'] = record.tokens_used
        
        return json.dumps(log_entry, ensure_ascii=False)

class ErrorTracker:
    """Tracks and analyzes errors for better understanding."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.error_summary_file = self.log_dir / "error_summary.json"
        self.error_patterns = {}
        
    def track_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Track an error occurrence."""
        error_key = f"{error_type}:{error_message[:100]}"
        
        if error_key not in self.error_patterns:
            self.error_patterns[error_key] = {
                'count': 0,
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'contexts': [],
                'error_type': error_type,
                'error_message': error_message
            }
        
        self.error_patterns[error_key]['count'] += 1
        self.error_patterns[error_key]['last_seen'] = datetime.now().isoformat()
        
        if context:
            self.error_patterns[error_key]['contexts'].append({
                'timestamp': datetime.now().isoformat(),
                'context': context
            })
            # Keep only last 10 contexts
            if len(self.error_patterns[error_key]['contexts']) > 10:
                self.error_patterns[error_key]['contexts'] = self.error_patterns[error_key]['contexts'][-10:]
        
        self._save_summary()
    
    def _save_summary(self):
        """Save error summary to file."""
        try:
            with open(self.error_summary_file, 'w') as f:
                json.dump(self.error_patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save error summary: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get current error summary."""
        if self.error_summary_file.exists():
            try:
                with open(self.error_summary_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def get_top_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top errors by frequency."""
        summary = self.get_error_summary()
        sorted_errors = sorted(
            summary.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return sorted_errors[:limit]

class LoggingConfig:
    """Main logging configuration class."""
    
    def __init__(self, log_dir: str = "logs", max_file_size: int = 10 * 1024 * 1024, 
                 backup_count: int = 5):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.error_tracker = ErrorTracker(str(self.log_dir))
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all loggers with appropriate handlers."""
        # Main application logger
        self._setup_logger(
            name="unga_analysis",
            log_file="app.log",
            level=logging.INFO
        )
        
        # Error-specific logger
        self._setup_logger(
            name="unga_analysis.errors",
            log_file="errors.log",
            level=logging.ERROR
        )
        
        # Performance logger
        self._setup_logger(
            name="unga_analysis.performance",
            log_file="performance.log",
            level=logging.INFO
        )
        
        # API logger
        self._setup_logger(
            name="unga_analysis.api",
            log_file="api.log",
            level=logging.INFO
        )
        
        # UI logger
        self._setup_logger(
            name="unga_analysis.ui",
            log_file="ui.log",
            level=logging.INFO
        )
        
        # Data processing logger
        self._setup_logger(
            name="unga_analysis.data",
            log_file="data.log",
            level=logging.INFO
        )
    
    def _setup_logger(self, name: str, log_file: str, level: int):
        """Setup individual logger with file rotation."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
        
        # Console handler for development
        if os.getenv('ENVIRONMENT', 'production') == 'development':
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"unga_analysis.{name}")

def log_function_call(func):
    """Decorator to log function calls with timing and error handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        # Extract context information
        context = {
            'function': func.__name__,
            'module_name': func.__module__,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        }
        
        logger.info(f"Calling {func.__name__}", extra={
            'operation': 'function_call',
            'component_name': func.__module__,
            **context
        })
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Completed {func.__name__} successfully", extra={
                'operation': 'function_success',
                'component_name': func.__module__,
                'duration': duration,
                **context
            })
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_context = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration': duration,
                **context
            }
            
            logger.error(f"Error in {func.__name__}: {e}", extra={
                'operation': 'function_error',
                'component_name': func.__module__,
                **error_context
            }, exc_info=True)
            
            # Track error for analysis
            config = LoggingConfig()
            config.error_tracker.track_error(
                type(e).__name__,
                str(e),
                error_context
            )
            
            raise
    
    return wrapper

def log_streamlit_error(func):
    """Decorator specifically for Streamlit UI functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger("ui")
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Streamlit UI error in {func.__name__}: {e}", extra={
                'operation': 'ui_error',
                'component': 'streamlit',
                'function': func.__name__
            }, exc_info=True)
            
            # Track error
            config = LoggingConfig()
            config.error_tracker.track_error(
                type(e).__name__,
                str(e),
                {'component': 'streamlit', 'function': func.__name__}
            )
            
            raise
    
    return wrapper

@contextmanager
def log_operation(operation_name: str, component: str, **context):
    """Context manager for logging operations."""
    logger = get_logger(component)
    start_time = datetime.now()
    
    logger.info(f"Starting {operation_name}", extra={
        'operation': operation_name,
        'component': component,
        **context
    })
    
    try:
        yield
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Completed {operation_name}", extra={
            'operation': f"{operation_name}_success",
            'component': component,
            'duration': duration,
            **context
        })
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Failed {operation_name}: {e}", extra={
            'operation': f"{operation_name}_error",
            'component': component,
            'duration': duration,
            **context
        }, exc_info=True)
        
        # Track error
        config = LoggingConfig()
        config.error_tracker.track_error(
            type(e).__name__,
            str(e),
            {'operation': operation_name, 'component': component, **context}
        )
        
        raise

def log_api_call(api_name: str, endpoint: str, method: str = "POST", **context):
    """Log API calls with detailed context."""
    logger = get_logger("api")
    logger.info(f"API call to {api_name}", extra={
        'operation': 'api_call',
        'component': 'api',
        'api_name': api_name,
        'endpoint': endpoint,
        'method': method,
        **context
    })

def log_performance(operation: str, duration: float, **metrics):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(f"Performance: {operation}", extra={
        'operation': 'performance',
        'component': 'performance',
        'duration': duration,
        **metrics
    })

def log_data_processing(operation: str, record_count: int = None, file_size: int = None, **context):
    """Log data processing operations."""
    logger = get_logger("data")
    logger.info(f"Data processing: {operation}", extra={
        'operation': 'data_processing',
        'component': 'data',
        'record_count': record_count,
        'file_size': file_size,
        **context
    })

def analyze_recent_errors(hours: int = 24) -> Dict[str, Any]:
    """Analyze recent errors from logs."""
    config = LoggingConfig()
    error_summary = config.error_tracker.get_error_summary()
    
    # Filter recent errors
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_errors = {}
    
    for error_key, error_data in error_summary.items():
        last_seen = datetime.fromisoformat(error_data['last_seen'])
        if last_seen > cutoff_time:
            recent_errors[error_key] = error_data
    
    return {
        'total_errors': len(recent_errors),
        'top_errors': sorted(
            recent_errors.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10],
        'error_types': list(set(error_data['error_type'] for error_data in recent_errors.values())),
        'analysis_time': datetime.now().isoformat(),
        'time_range_hours': hours
    }

def get_log_insights() -> Dict[str, Any]:
    """Get insights from error logs for AI understanding."""
    config = LoggingConfig()
    error_summary = config.error_tracker.get_error_summary()
    
    insights = {
        'total_unique_errors': len(error_summary),
        'most_common_errors': [],
        'recent_error_trends': [],
        'component_breakdown': {},
        'error_patterns': []
    }
    
    if error_summary:
        # Most common errors
        sorted_errors = sorted(
            error_summary.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        insights['most_common_errors'] = [
            {
                'error': error_data['error_message'],
                'type': error_data['error_type'],
                'count': error_data['count'],
                'first_seen': error_data['first_seen'],
                'last_seen': error_data['last_seen']
            }
            for error_key, error_data in sorted_errors[:5]
        ]
        
        # Component breakdown
        for error_data in error_summary.values():
            for context in error_data.get('contexts', []):
                component = context.get('context', {}).get('component', 'unknown')
                if component not in insights['component_breakdown']:
                    insights['component_breakdown'][component] = 0
                insights['component_breakdown'][component] += 1
    
    return insights

# Initialize logging configuration
config = LoggingConfig()
