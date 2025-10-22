"""
Log analysis utility for understanding application errors and performance.
Provides AI-readable error summaries and insights.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging

from .logging_config import LoggingConfig, get_log_insights, analyze_recent_errors

class LogAnalyzer:
    """Analyzes application logs to provide insights for AI understanding."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.config = LoggingConfig(log_dir)
    
    def get_error_summary_for_ai(self) -> str:
        """Get a comprehensive error summary formatted for AI understanding."""
        insights = get_log_insights()
        recent_errors = analyze_recent_errors(hours=24)
        
        summary = f"""
# Application Error Analysis Report
Generated: {datetime.now().isoformat()}

## Current Error Status
- Total unique errors: {insights['total_unique_errors']}
- Recent errors (24h): {recent_errors['total_errors']}
- Error types: {', '.join(recent_errors['error_types'])}

## Most Common Issues
"""
        
        if insights['most_common_errors']:
            for i, error in enumerate(insights['most_common_errors'], 1):
                summary += f"""
{i}. **{error['type']}**: {error['error']}
   - Occurrences: {error['count']}
   - First seen: {error['first_seen']}
   - Last seen: {error['last_seen']}
"""
        else:
            summary += "\nNo errors recorded in the system.\n"
        
        summary += f"""
## Component Error Breakdown
"""
        for component, count in insights['component_breakdown'].items():
            summary += f"- {component}: {count} errors\n"
        
        if recent_errors['top_errors']:
            summary += f"""
## Recent High-Priority Errors (Last 24h)
"""
            for error_key, error_data in recent_errors['top_errors'][:5]:
                summary += f"""
- **{error_data['error_type']}**: {error_data['error_message']}
  - Count: {error_data['count']}
  - Last seen: {error_data['last_seen']}
"""
        
        return summary
    
    def analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in errors to identify root causes."""
        error_summary = self.config.error_tracker.get_error_summary()
        
        patterns = {
            'api_errors': [],
            'ui_errors': [],
            'data_errors': [],
            'authentication_errors': [],
            'file_processing_errors': [],
            'performance_issues': []
        }
        
        for error_key, error_data in error_summary.items():
            error_type = error_data['error_type']
            error_message = error_data['error_message'].lower()
            
            # Categorize errors
            if 'api' in error_message or 'openai' in error_message or 'rate limit' in error_message:
                patterns['api_errors'].append(error_data)
            elif 'streamlit' in error_message or 'ui' in error_message or 'session' in error_message:
                patterns['ui_errors'].append(error_data)
            elif 'file' in error_message or 'upload' in error_message or 'processing' in error_message:
                patterns['file_processing_errors'].append(error_data)
            elif 'auth' in error_message or 'password' in error_message or 'login' in error_message:
                patterns['authentication_errors'].append(error_data)
            elif 'timeout' in error_message or 'slow' in error_message or 'performance' in error_message:
                patterns['performance_issues'].append(error_data)
            elif 'data' in error_message or 'database' in error_message or 'query' in error_message:
                patterns['data_errors'].append(error_data)
        
        return patterns
    
    def get_suggested_fixes(self) -> List[Dict[str, str]]:
        """Get suggested fixes based on error patterns."""
        patterns = self.analyze_error_patterns()
        suggestions = []
        
        # API errors
        if patterns['api_errors']:
            suggestions.append({
                'category': 'API Issues',
                'description': 'Multiple API-related errors detected',
                'suggestions': [
                    'Check OpenAI API key and endpoint configuration',
                    'Implement better rate limiting and retry logic',
                    'Add API quota monitoring',
                    'Consider using fallback models'
                ]
            })
        
        # UI errors
        if patterns['ui_errors']:
            suggestions.append({
                'category': 'User Interface Issues',
                'description': 'Streamlit UI errors detected',
                'suggestions': [
                    'Add better error boundaries in UI components',
                    'Implement session state validation',
                    'Add loading states for long operations',
                    'Improve user feedback for errors'
                ]
            })
        
        # File processing errors
        if patterns['file_processing_errors']:
            suggestions.append({
                'category': 'File Processing Issues',
                'description': 'File upload and processing errors',
                'suggestions': [
                    'Add better file validation',
                    'Implement file size limits',
                    'Add support for more file formats',
                    'Improve error handling for corrupted files'
                ]
            })
        
        # Authentication errors
        if patterns['authentication_errors']:
            suggestions.append({
                'category': 'Authentication Issues',
                'description': 'Login and authentication problems',
                'suggestions': [
                    'Check password configuration',
                    'Implement better session management',
                    'Add password reset functionality',
                    'Improve authentication error messages'
                ]
            })
        
        # Performance issues
        if patterns['performance_issues']:
            suggestions.append({
                'category': 'Performance Issues',
                'description': 'Slow operations and timeouts',
                'suggestions': [
                    'Optimize database queries',
                    'Implement caching for frequent operations',
                    'Add progress indicators for long operations',
                    'Consider async processing for heavy tasks'
                ]
            })
        
        return suggestions
    
    def get_health_score(self) -> Dict[str, Any]:
        """Calculate application health score based on errors."""
        error_summary = self.config.error_tracker.get_error_summary()
        recent_errors = analyze_recent_errors(hours=24)
        
        # Base score
        health_score = 100
        
        # Deduct points for errors
        total_errors = sum(error_data['count'] for error_data in error_summary.values())
        recent_error_count = recent_errors['total_errors']
        
        # Deduct points based on error frequency
        health_score -= min(total_errors * 2, 50)  # Max 50 points deduction
        health_score -= min(recent_error_count * 5, 30)  # Max 30 points deduction
        
        # Deduct points for error severity
        for error_data in error_summary.values():
            if 'critical' in error_data['error_message'].lower() or 'fatal' in error_data['error_message'].lower():
                health_score -= 10
            elif 'error' in error_data['error_message'].lower():
                health_score -= 5
            elif 'warning' in error_data['error_message'].lower():
                health_score -= 2
        
        health_score = max(0, health_score)
        
        # Determine health status
        if health_score >= 90:
            status = "Excellent"
        elif health_score >= 70:
            status = "Good"
        elif health_score >= 50:
            status = "Fair"
        elif health_score >= 30:
            status = "Poor"
        else:
            status = "Critical"
        
        return {
            'score': health_score,
            'status': status,
            'total_errors': total_errors,
            'recent_errors': recent_error_count,
            'unique_errors': len(error_summary),
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_ai_report(self) -> str:
        """Generate a comprehensive report for AI understanding."""
        health = self.get_health_score()
        suggestions = self.get_suggested_fixes()
        error_summary = self.get_error_summary_for_ai()
        
        report = f"""
# UNGA Analysis Application - AI Error Understanding Report

## Application Health Status
- **Health Score**: {health['score']}/100 ({health['status']})
- **Total Errors**: {health['total_errors']}
- **Recent Errors (24h)**: {health['recent_errors']}
- **Unique Error Types**: {health['unique_errors']}

## Error Analysis
{error_summary}

## Suggested Improvements
"""
        
        for suggestion in suggestions:
            report += f"""
### {suggestion['category']}
**Issue**: {suggestion['description']}

**Recommended Actions**:
"""
            for action in suggestion['suggestions']:
                report += f"- {action}\n"
        
        report += f"""
## Next Steps for AI Assistant
1. **Monitor**: Watch for the most common error patterns
2. **Focus**: Prioritize fixes for high-frequency errors
3. **Test**: Implement suggested improvements incrementally
4. **Track**: Monitor health score improvements over time

---
*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def get_recent_logs(self, hours: int = 1, log_type: str = "errors") -> List[Dict[str, Any]]:
        """Get recent log entries for analysis."""
        log_file = self.log_dir / f"{log_type}.log"
        if not log_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        log_time = datetime.fromisoformat(log_entry['timestamp'])
                        if log_time > cutoff_time:
                            recent_logs.append(log_entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return recent_logs
    
    def find_error_context(self, error_message: str) -> List[Dict[str, Any]]:
        """Find context around specific error messages."""
        all_logs = []
        for log_file in self.log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if error_message.lower() in log_entry.get('message', '').lower():
                                all_logs.append(log_entry)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            except Exception:
                continue
        
        return all_logs

def get_application_health() -> str:
    """Quick health check for the application."""
    analyzer = LogAnalyzer()
    health = analyzer.get_health_score()
    
    if health['score'] >= 80:
        return f"✅ Application is healthy (Score: {health['score']}/100)"
    elif health['score'] >= 60:
        return f"⚠️ Application has some issues (Score: {health['score']}/100)"
    else:
        return f"❌ Application needs attention (Score: {health['score']}/100)"

def get_error_insights() -> str:
    """Get quick error insights for AI understanding."""
    analyzer = LogAnalyzer()
    return analyzer.generate_ai_report()
