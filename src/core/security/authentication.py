"""
Authentication management for the application
"""

import os
import logging
import streamlit as st
from typing import Optional
from .rate_limiting import rate_limiter
from .input_validation import sanitize_input
from ..config.settings import settings

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Manages user authentication and session security."""
    
    def __init__(self):
        self.app_password = settings.APP_PASSWORD
    
    def authenticate_user(self, password: str, user_id: str = "anonymous") -> tuple[bool, str]:
        """
        Authenticate user with rate limiting and security checks.
        
        Args:
            password: User provided password
            user_id: User identifier for rate limiting
            
        Returns:
            Tuple of (success, message)
        """
        # Check rate limit
        if not rate_limiter.check_rate_limit(user_id):
            remaining = rate_limiter.get_remaining_attempts(user_id)
            wait_time = rate_limiter.get_wait_time(user_id)
            return False, f"❌ Too many authentication attempts. {remaining} attempts remaining. Try again in {wait_time} seconds."
        
        # Validate configuration
        if not self.app_password:
            logger.error("Application password not configured")
            return False, "❌ Application password not configured. Please set APP_PASSWORD environment variable."
        
        # Sanitize input
        sanitized_password = sanitize_input(password)
        
        # Check password
        if sanitized_password == self.app_password:
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            logger.info(f"User {user_id} authenticated successfully")
            return True, "✅ Authentication successful!"
        else:
            logger.warning(f"Failed authentication attempt for user {user_id}")
            return False, "❌ Incorrect password. Please try again."
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return st.session_state.get('authenticated', False)
    
    def logout(self) -> None:
        """Logout user and clear session."""
        st.session_state.authenticated = False
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        logger.info("User logged out")
    
    def get_user_id(self) -> str:
        """Get current user ID."""
        return st.session_state.get('user_id', 'anonymous')
    
    def require_authentication(self) -> bool:
        """Require authentication - returns True if authenticated, False otherwise."""
        if not self.is_authenticated():
            self.show_login_form()
            return False
        return True
    
    def show_login_form(self) -> None:
        """Display the login form."""
        # Header with OSAA logo
        col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
        
        with col_header2:
            st.image("artifacts/logo/OSAA identifier acronym white.svg", width=200)
            st.title("🔐 UN GA Daily Readouts - Authentication Required")
            st.markdown("**Internal tool for UN OSAA Intergovernmental Support Team**")
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Please enter the password to access the application")
            
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="Enter password",
                help="Enter the application password to continue"
            )
            
            col_login, col_clear = st.columns(2)
            
            with col_login:
                if st.button("🚀 Login", type="primary", use_container_width=True):
                    if password:
                        success, message = self.authenticate_user(password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            with col_clear:
                if st.button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            # Information section
            st.info("💡 This is an internal tool created for UN OSAA Intergovernmental Support Team to analyze General Assembly speeches. Internal limited use only. If you do not have credentials, please reach out to UN OSAA IGS team.")
            
            # Footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
                "Built for UN OSAA | Developed by: <strong>SMU Data Team</strong>"
                "</div>", 
                unsafe_allow_html=True
            )

# Global authentication manager
auth_manager = AuthenticationManager()
