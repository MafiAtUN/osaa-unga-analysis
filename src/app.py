"""
UN GA Daily Readouts - Main Application
Professional, modular Streamlit application for analyzing UN General Assembly speeches

Developed by: SMU Data Team
"""

import streamlit as st
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application modules
from config.settings import settings
from core.security import AuthenticationManager
from ui.pages import DashboardPage, AnalysisPage, HistoryPage, SettingsPage
from ui.components import NavigationComponent

def initialize_app():
    """Initialize the application."""
    # Page configuration
    st.set_page_config(
        page_title=settings.PAGE_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'anonymous'
    
    # Validate configuration
    is_valid, missing_vars = settings.validate_config()
    if not is_valid:
        st.error(f"❌ Configuration Error: Missing environment variables: {', '.join(missing_vars)}")
        st.stop()

def render_header():
    """Render application header."""
    st.title("🇺🇳 UN GA Daily Readouts")
    st.markdown("**Production-ready analysis of UN General Assembly speeches**")
    st.markdown("---")

def render_sidebar():
    """Render application sidebar."""
    with st.sidebar:
        st.image("artifacts/logo/OSAA identifier acronym white.svg", width=150)
        st.markdown("### Navigation")
        
        # Navigation component
        nav = NavigationComponent()
        selected_page = nav.render_navigation()
        
        st.markdown("---")
        st.markdown("**Developed by:** SMU Data Team")
        st.markdown(f"**Version:** {settings.VERSION}")
        
        return selected_page

def render_main_content(selected_page: str):
    """Render main content based on selected page."""
    if selected_page == "🏠 Dashboard":
        page = DashboardPage()
        page.render()
    elif selected_page == "📊 New Analysis":
        page = AnalysisPage()
        page.render()
    elif selected_page == "📚 All Analyses":
        page = HistoryPage()
        page.render()
    elif selected_page == "⚙️ Settings":
        page = SettingsPage()
        page.render()
    else:
        st.error("Page not found")

def main():
    """Main application entry point."""
    try:
        # Initialize application
        initialize_app()
        
        # Check authentication
        auth_manager = AuthenticationManager()
        if not auth_manager.require_authentication():
            return
        
        # Render header
        render_header()
        
        # Render sidebar and get selected page
        selected_page = render_sidebar()
        
        # Render main content
        render_main_content(selected_page)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"❌ Application Error: {e}")
        st.error("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()
