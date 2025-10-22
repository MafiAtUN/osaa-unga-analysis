"""
Authentication and Security Module
Handles user authentication, rate limiting, and security validation
"""

import os
import time
import re
import logging
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)

# Rate limiting storage
user_attempts: Dict[str, List[float]] = defaultdict(list)


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
    allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.mp3', '.wav', '.m4a'}
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in allowed_extensions:
        logger.warning(f"File type not allowed: {file_ext}")
        return False
    
    return True


def authenticate_user(password: str) -> bool:
    """Authenticate user with password."""
    correct_password = os.getenv("APP_PASSWORD", "default_password")
    return password == correct_password


def check_password():
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def show_login_form():
    """Display login form."""
    st.markdown("### 🔐 Authentication Required")
    st.markdown("Please enter the password to access the UN GA Daily Readouts application.")
    
    with st.form("login_form"):
        password = st.text_input("Password:", type="password", placeholder="Enter password...")
        submit_button = st.form_submit_button("Login", type="primary")
        
        if submit_button:
            if authenticate_user(password):
                st.session_state.authenticated = True
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password. Please try again.")
    
    # Add some styling
    st.markdown("---")
    st.markdown("**Note:** This application is for authorized UN OSAA personnel only.")
