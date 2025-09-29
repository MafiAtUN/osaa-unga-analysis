"""
Rate limiting implementation for security
"""

import time
import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for preventing abuse."""
    
    def __init__(self, max_attempts: int = 5, window: int = 300):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum attempts allowed
            window: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window = window
        self.attempts = defaultdict(list)
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if within limits, False if exceeded
        """
        now = time.time()
        user_attempts = self.attempts[user_id]
        
        # Remove old attempts outside the window
        user_attempts[:] = [attempt for attempt in user_attempts if now - attempt < self.window]
        
        if len(user_attempts) >= self.max_attempts:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return False
        
        user_attempts.append(now)
        return True
    
    def get_remaining_attempts(self, user_id: str) -> int:
        """Get remaining attempts for user."""
        now = time.time()
        user_attempts = self.attempts[user_id]
        
        # Remove old attempts
        user_attempts[:] = [attempt for attempt in user_attempts if now - attempt < self.window]
        
        return max(0, self.max_attempts - len(user_attempts))
    
    def reset_user(self, user_id: str) -> None:
        """Reset rate limit for specific user."""
        if user_id in self.attempts:
            del self.attempts[user_id]
    
    def get_wait_time(self, user_id: str) -> int:
        """Get wait time in seconds until next attempt is allowed."""
        if user_id not in self.attempts or not self.attempts[user_id]:
            return 0
        
        oldest_attempt = min(self.attempts[user_id])
        wait_time = int(self.window - (time.time() - oldest_attempt))
        return max(0, wait_time)

# Global rate limiter instance
rate_limiter = RateLimiter()
