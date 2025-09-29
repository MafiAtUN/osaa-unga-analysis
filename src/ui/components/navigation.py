"""
Navigation component for the application
"""

import streamlit as st
from typing import str

class NavigationComponent:
    """Navigation component for the application."""
    
    def __init__(self):
        self.pages = [
            "🏠 Dashboard",
            "📊 New Analysis", 
            "📚 All Analyses",
            "⚙️ Settings"
        ]
    
    def render_navigation(self) -> str:
        """
        Render navigation and return selected page.
        
        Returns:
            Selected page name
        """
        # Initialize session state for navigation
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = self.pages[0]
        
        # Render page selection
        selected_page = st.radio(
            "Select Page:",
            self.pages,
            index=self.pages.index(st.session_state.selected_page)
        )
        
        # Update session state
        st.session_state.selected_page = selected_page
        
        return selected_page
    
    def get_current_page(self) -> str:
        """Get current selected page."""
        return st.session_state.get('selected_page', self.pages[0])
    
    def set_page(self, page: str) -> None:
        """Set current page."""
        if page in self.pages:
            st.session_state.selected_page = page
            st.rerun()
