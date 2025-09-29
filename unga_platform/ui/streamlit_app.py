"""
Enterprise Streamlit Application
Professional UI implementation with clean architecture
"""

import streamlit as st
import logging
from typing import Optional
from datetime import datetime

from ..infrastructure.dependency_injection import Container
from ..infrastructure.config import ApplicationConfig
from .pages import DashboardPage, AnalysisPage, HistoryPage, SettingsPage
from .components import NavigationComponent, AuthenticationComponent

logger = logging.getLogger(__name__)

class StreamlitApplication:
    """Enterprise Streamlit application with clean architecture."""
    
    def __init__(self, container: Container, config: ApplicationConfig):
        self.container = container
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.navigation = NavigationComponent()
        self.auth = AuthenticationComponent(container)
        
        # Initialize pages
        self.pages = {
            "🏠 Dashboard": DashboardPage(container),
            "📊 New Analysis": AnalysisPage(container),
            "📚 All Analyses": HistoryPage(container),
            "⚙️ Settings": SettingsPage(container)
        }
    
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=self.config.name,
            page_icon="🇺🇳",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize application session state."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'anonymous'
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = "🏠 Dashboard"
    
    def render_header(self):
        """Render application header."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title(f"🇺🇳 {self.config.name}")
            st.markdown(f"**{self.config.description}**")
            st.markdown(f"*Version {self.config.version} | Environment: {self.config.environment.value.title()}*")
        
        st.markdown("---")
    
    def render_sidebar(self) -> str:
        """Render application sidebar."""
        with st.sidebar:
            # Logo and branding
            st.image("artifacts/logo/OSAA identifier acronym white.svg", width=150)
            st.markdown("### Navigation")
            
            # Navigation
            selected_page = self.navigation.render()
            
            # User info
            if st.session_state.authenticated:
                st.markdown("---")
                st.markdown(f"**User:** {st.session_state.user_id}")
                st.markdown(f"**Session:** {st.session_state.session_start.strftime('%H:%M:%S')}")
                
                if st.button("🚪 Logout", use_container_width=True):
                    self.auth.logout()
                    st.rerun()
            
            # Application info
            st.markdown("---")
            st.markdown("**Developed by:** SMU Data Team")
            st.markdown(f"**Version:** {self.config.version}")
            
            if self.config.debug:
                st.markdown("**Debug Mode:** Enabled")
        
        return selected_page
    
    def render_main_content(self, selected_page: str):
        """Render main content based on selected page."""
        try:
            if selected_page in self.pages:
                page = self.pages[selected_page]
                page.render()
            else:
                st.error(f"Page '{selected_page}' not found")
                self.logger.error(f"Unknown page: {selected_page}")
        except Exception as e:
            st.error(f"❌ Error rendering page: {e}")
            self.logger.error(f"Error rendering page {selected_page}: {e}")
    
    def handle_authentication(self) -> bool:
        """Handle user authentication."""
        if not st.session_state.authenticated:
            self.auth.render_login_form()
            return False
        return True
    
    def run(self):
        """Run the enterprise application."""
        try:
            # Configure page
            self.configure_page()
            
            # Initialize session state
            self.initialize_session_state()
            
            # Handle authentication
            if not self.handle_authentication():
                return
            
            # Render header
            self.render_header()
            
            # Render sidebar and get selected page
            selected_page = self.render_sidebar()
            
            # Render main content
            self.render_main_content(selected_page)
            
            # Performance monitoring
            if self.config.debug:
                self._log_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            st.error(f"❌ Application Error: {e}")
            st.error("Please refresh the page or contact support if the issue persists.")
    
    def _log_performance_metrics(self):
        """Log performance metrics in debug mode."""
        session_duration = datetime.now() - st.session_state.session_start
        self.logger.info(f"Session duration: {session_duration}")
        self.logger.info(f"Current page: {st.session_state.selected_page}")
        self.logger.info(f"User: {st.session_state.user_id}")
