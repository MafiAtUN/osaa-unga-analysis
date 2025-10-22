# Comprehensive Error Logging System

This document describes the comprehensive error logging system implemented for the UNGA Analysis application to help AI assistants better understand application issues.

## Overview

The logging system provides:
- **Structured JSON logging** with detailed context
- **Error tracking and analysis** for pattern recognition
- **AI-readable error summaries** for better assistance
- **Performance monitoring** and health scoring
- **Streamlit UI integration** for real-time monitoring

## Components

### 1. Logging Configuration (`src/unga_analysis/utils/logging_config.py`)

- **StructuredFormatter**: Creates JSON-formatted log entries
- **ErrorTracker**: Tracks and analyzes error patterns
- **LoggingConfig**: Manages multiple loggers with file rotation
- **Decorators**: `@log_function_call`, `@log_streamlit_error`
- **Context Managers**: `log_operation()` for operation tracking

### 2. Log Analyzer (`src/unga_analysis/utils/log_analyzer.py`)

- **LogAnalyzer**: Main analysis class
- **Error pattern recognition** and categorization
- **Health score calculation** (0-100)
- **AI report generation** for comprehensive understanding
- **Suggested fixes** based on error patterns

### 3. Error Insights UI (`src/unga_analysis/ui/tabs/error_insights_tab.py`)

- **Health Overview**: System health score and metrics
- **Error Analysis**: Pattern analysis and categorization
- **AI Insights**: Comprehensive error report for AI understanding
- **Performance Metrics**: Operation timing and bottlenecks

## Usage

### For AI Assistants

The system automatically logs errors and provides AI-readable summaries. To get error insights:

```python
from src.unga_analysis.utils.log_analyzer import get_error_insights, get_application_health

# Get quick health status
health = get_application_health()
print(health)

# Get comprehensive error analysis
insights = get_error_insights()
print(insights)
```

### For Developers

Use the logging decorators in your functions:

```python
from src.unga_analysis.utils.logging_config import log_function_call, log_operation

@log_function_call
def my_function():
    # Function will be automatically logged with timing and error handling
    pass

# Or use context manager
with log_operation("data_processing", "data", record_count=1000):
    # Operation will be logged with context
    process_data()
```

### Command Line Analysis

Run the log analysis tool:

```bash
python analyze_logs.py
```

This provides:
- Application health score
- Recent error summary
- AI-readable error report
- Suggested improvements

## Log Files

The system creates several log files in the `logs/` directory:

- `app.log`: General application logs
- `errors.log`: Error-specific logs
- `performance.log`: Performance metrics
- `api.log`: API call logs
- `ui.log`: User interface logs
- `data.log`: Data processing logs
- `error_summary.json`: Error pattern analysis

## Error Categories

The system automatically categorizes errors:

- **API Errors**: OpenAI, rate limiting, authentication
- **UI Errors**: Streamlit, session management
- **Data Errors**: File processing, database queries
- **Authentication Errors**: Login, password issues
- **Performance Issues**: Timeouts, slow operations
- **File Processing Errors**: Upload, format issues

## Health Scoring

The health score (0-100) is calculated based on:

- **Error frequency**: More errors = lower score
- **Error severity**: Critical errors = bigger penalty
- **Recent activity**: Recent errors = higher impact
- **Error diversity**: More unique errors = lower score

## AI Understanding Features

### 1. Structured Error Context

Each error includes:
- Timestamp and duration
- Function/module information
- User session context
- Operation details
- File/request information

### 2. Pattern Recognition

The system identifies:
- Recurring error patterns
- Component-specific issues
- Performance bottlenecks
- User behavior patterns

### 3. Suggested Fixes

Based on error patterns, the system suggests:
- Code improvements
- Configuration changes
- Performance optimizations
- User experience enhancements

## Integration with Streamlit

The error insights are available in the Streamlit UI:

1. **Error Insights Tab**: Real-time error monitoring
2. **Health Dashboard**: System status overview
3. **Performance Metrics**: Operation timing analysis
4. **AI Report**: Comprehensive error understanding

## Benefits for AI Assistance

1. **Contextual Understanding**: AI can see exactly what went wrong and when
2. **Pattern Recognition**: Identify recurring issues and their causes
3. **Proactive Suggestions**: Suggest fixes before users report issues
4. **Performance Optimization**: Identify slow operations and bottlenecks
5. **User Experience**: Understand user behavior and common issues

## Monitoring and Maintenance

### Log Rotation

- Files rotate when they reach 10MB
- Keep 5 backup files
- Automatic cleanup of old logs

### Error Tracking

- Track error frequency and patterns
- Monitor error trends over time
- Identify critical issues quickly

### Performance Monitoring

- Track operation durations
- Identify performance bottlenecks
- Monitor resource usage

## Example AI Error Understanding

When an error occurs, the AI can now understand:

```json
{
  "timestamp": "2025-01-27T10:30:45",
  "level": "ERROR",
  "component": "api",
  "operation": "openai_call",
  "error_type": "RateLimitError",
  "error_message": "Rate limit exceeded",
  "context": {
    "model": "gpt-4o",
    "tokens_used": 15000,
    "retry_count": 3,
    "user_id": "user123"
  },
  "suggestions": [
    "Implement exponential backoff",
    "Add request queuing",
    "Consider model fallback"
  ]
}
```

This comprehensive logging system ensures that AI assistants can provide much better support by understanding the full context of application issues.
