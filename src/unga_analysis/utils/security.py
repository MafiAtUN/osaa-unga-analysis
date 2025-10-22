"""
Security utilities for input validation and rate limiting
"""

import os
import re
import html
import time
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)

# Rate limiting storage
user_attempts: Dict[str, List[float]] = defaultdict(list)


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove potential injection patterns
    text = re.sub(r'[<>"\']', '', text)
    text = html.escape(text)
    # Limit length to prevent abuse
    text = text[:10000]  # Reasonable limit
    return text


def validate_prompt_safety(prompt: str) -> bool:
    """Validate prompt for safety against injection attacks."""
    if not prompt:
        return False
        
    dangerous_patterns = [
        r'ignore\s+previous\s+instructions',
        r'you\s+are\s+now',
        r'system\s+prompt',
        r'jailbreak',
        r'bypass',
        r'admin',
        r'root',
        r'execute',
        r'command',
        r'shell',
        r'<script',
        r'javascript:',
        r'data:',
        r'vbscript:'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            logger.warning(f"Blocked potentially dangerous prompt pattern: {pattern}")
            return False
    return True


def check_rate_limit(user_id: str, max_attempts: int = 5, window: int = 300) -> bool:
    """Check if user has exceeded rate limit."""
    now = time.time()
    attempts = user_attempts[user_id]
    
    # Remove old attempts outside the window
    attempts[:] = [attempt for attempt in attempts if now - attempt < window]
    
    if len(attempts) >= max_attempts:
        logger.warning(f"Rate limit exceeded for user: {user_id}")
        return False
    
    attempts.append(now)
    return True


def validate_file_upload(file_bytes: bytes, filename: str) -> bool:
    """Validate uploaded file for security."""
    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
    if len(file_bytes) > max_size:
        logger.warning(f"File too large: {len(file_bytes)} bytes")
        return False
    
    # Check file extension
    allowed_extensions = ['.pdf', '.docx', '.mp3']
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in allowed_extensions:
        logger.warning(f"Invalid file type: {file_ext}")
        return False
    
    return True


