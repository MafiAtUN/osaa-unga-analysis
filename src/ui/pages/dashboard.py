"""
Dashboard page for the UN GA Daily Readouts application
"""

import streamlit as st
from datetime import datetime
from ...services.storage import DatabaseManager
from ...config.settings import settings

class DashboardPage:
    """Dashboard page component."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def render(self):
        """Render the dashboard page."""
        st.header("🏠 Dashboard")
        st.markdown("Welcome to the UN GA Daily Readouts application!")
        
        # Application info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📊 Total Analyses",
                value=self.get_total_analyses(),
                delta=None
            )
        
        with col2:
            st.metric(
                label="🌍 Countries Analyzed",
                value=self.get_unique_countries(),
                delta=None
            )
        
        with col3:
            st.metric(
                label="📅 Today's Analyses",
                value=self.get_today_analyses(),
                delta=None
            )
        
        # Recent analyses
        st.subheader("📋 Recent Analyses")
        self.render_recent_analyses()
        
        # Quick stats
        st.subheader("📈 Quick Statistics")
        self.render_quick_stats()
    
    def get_total_analyses(self) -> int:
        """Get total number of analyses."""
        try:
            return self.db_manager.get_total_analyses()
        except Exception as e:
            st.error(f"Error getting total analyses: {e}")
            return 0
    
    def get_unique_countries(self) -> int:
        """Get number of unique countries."""
        try:
            return self.db_manager.get_unique_countries()
        except Exception as e:
            st.error(f"Error getting unique countries: {e}")
            return 0
    
    def get_today_analyses(self) -> int:
        """Get today's analyses count."""
        try:
            return self.db_manager.get_today_analyses()
        except Exception as e:
            st.error(f"Error getting today's analyses: {e}")
            return 0
    
    def render_recent_analyses(self):
        """Render recent analyses list."""
        try:
            recent_analyses = self.db_manager.get_recent_analyses(limit=5)
            
            if not recent_analyses:
                st.info("No analyses found. Create your first analysis!")
                return
            
            for analysis in recent_analyses:
                with st.expander(f"📄 {analysis['country']} - {analysis['created_at']}"):
                    st.write(f"**Classification:** {analysis['classification']}")
                    st.write(f"**Date:** {analysis['speech_date']}")
                    st.write(f"**SDGs:** {analysis.get('sdgs', 'N/A')}")
                    
                    if st.button(f"View Analysis", key=f"view_{analysis['id']}"):
                        st.session_state.viewing_analysis = analysis['id']
                        st.rerun()
        except Exception as e:
            st.error(f"Error loading recent analyses: {e}")
    
    def render_quick_stats(self):
        """Render quick statistics."""
        try:
            stats = self.db_manager.get_statistics()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Classification Breakdown:**")
                for classification, count in stats.get('classifications', {}).items():
                    st.write(f"- {classification}: {count}")
            
            with col2:
                st.write("**Top Countries:**")
                for country, count in stats.get('top_countries', {}).items():
                    st.write(f"- {country}: {count}")
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
