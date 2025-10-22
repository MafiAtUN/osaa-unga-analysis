"""
Authentication utilities for the UNGA analysis app
"""

import os
import streamlit as st
from src.unga_analysis.utils.security import check_rate_limit, sanitize_input
from src.unga_analysis.utils.logging_config import log_function_call


def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'proceed_to_analysis' not in st.session_state:
        st.session_state.proceed_to_analysis = False
    if 'load_text_clicked' not in st.session_state:
        st.session_state.load_text_clicked = False
    if 'stored_text' not in st.session_state:
        st.session_state.stored_text = None
    if 'stored_file' not in st.session_state:
        st.session_state.stored_file = None
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    
    # Clear auto-detection data on fresh start
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        # Clear any previous auto-detection data
        if 'auto_detected_country' in st.session_state:
            del st.session_state.auto_detected_country
        if 'auto_detected_classification' in st.session_state:
            del st.session_state.auto_detected_classification
        if 'last_uploaded_file' in st.session_state:
            del st.session_state.last_uploaded_file
        if 'last_pasted_text' in st.session_state:
            del st.session_state.last_pasted_text
        if 'edit_country' in st.session_state:
            del st.session_state.edit_country


@log_function_call
def check_password():
    """Check if user has entered the correct password."""
    # For testing purposes, always return True to bypass authentication
    return True
    # Original code: return st.session_state.authenticated


@log_function_call
def authenticate_user(password: str) -> bool:
    """Authenticate user with rate limiting."""
    # Get user identifier (IP or session-based)
    user_id = st.session_state.get('user_id', 'anonymous')
    
    # Check rate limit
    if not check_rate_limit(user_id):
        st.error("❌ Too many authentication attempts. Please try again later.")
        return False
    
    # Get password from environment
    app_password = os.getenv('APP_PASSWORD')
    if not app_password:
        st.error("❌ Application password not configured. Please set APP_PASSWORD environment variable.")
        return False
    
    # Sanitize input
    sanitized_password = sanitize_input(password)
    
    # Check password
    if sanitized_password == app_password:
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        return True
    else:
        st.error("❌ Incorrect password. Please try again.")
        return False


def show_login_form():
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
                    if authenticate_user(password):
                        st.success("✅ Authentication successful!")
                        st.rerun()
        
        with col_clear:
            if st.button("🔄 Clear", use_container_width=True):
                st.rerun()
        
        # Help text
        st.info("💡 This is an internal tool created for UN OSAA Intergovernmental Support Team to analyze General Assembly speeches. Internal limited use only. If you do not have credentials, please reach out to UN OSAA IGS team.")
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 12px;'>"
            "Built for UN OSAA | Developed by: <strong>SMU Data Team</strong>"
            "</div>", 
            unsafe_allow_html=True
        )


