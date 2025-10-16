"""
UN GA Daily Readouts - Modular Streamlit App
Production-ready app for analyzing UN General Assembly speeches

Developed by: SMU Data Team
"""

import os
import logging
import streamlit as st
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import modules
from auth import check_password, show_login_form
from ui_components import render_data_availability_info
from tabs.new_analysis_tab import render_new_analysis_tab
from tabs.data_explorer_tab import render_data_explorer_tab
from tabs.cross_year_analysis_tab import render_cross_year_analysis_tab

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="UN GA Daily Readouts",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def render_sidebar():
    """Render the sidebar with navigation and info."""
    st.sidebar.markdown("## 🌍 UN GA Daily Readouts")
    st.sidebar.markdown("**Advanced Speech Analysis Platform**")
    
    # Navigation
    st.sidebar.markdown("### 📋 Navigation")
    
    # Tab selection
    tab = st.sidebar.radio(
        "Select Tab:",
        ["📝 New Analysis", "📊 Data Explorer", "🌍 Cross-Year Analysis"],
        index=0
    )
    
    # Data availability info
    st.sidebar.markdown("---")
    render_data_availability_info()
    
    # Session info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Session Info")
    st.sidebar.info(f"👤 **User:** {st.session_state.user_id}")
    st.sidebar.info(f"🕒 **Session:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Analysis history
    if st.session_state.get('analysis_history'):
        st.sidebar.markdown("### 📚 Recent Analyses")
        for i, analysis in enumerate(st.session_state.analysis_history[-3:], 1):
            with st.sidebar.expander(f"Analysis {i}: {analysis.get('country', 'Unknown')}"):
                st.write(f"**Date:** {analysis.get('date', 'Unknown')}")
                st.write(f"**Classification:** {analysis.get('classification', 'Unknown')}")
                st.write(f"**Word Count:** {analysis.get('word_count', 0):,}")
    
    return tab


def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">🌍 UN GA Daily Readouts</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced AI-powered analysis of UN General Assembly speeches</p>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🗣️ Countries", "195+")
    with col2:
        st.metric("📅 Years", "1946-2025")
    with col3:
        st.metric("🤖 AI Models", "Multiple")
    with col4:
        st.metric("🌍 Languages", "100+")


def render_footer():
    """Render the footer."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🌍 <strong>UN GA Daily Readouts</strong> | Developed by SMU Data Team</p>
        <p>Advanced AI-powered analysis platform for UN General Assembly speeches</p>
        <p>© 2025 - All rights reserved</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not check_password():
        show_login_form()
        return
    
    # Render header
    render_header()
    
    # Render sidebar and get selected tab
    selected_tab = render_sidebar()
    
    # Render main content based on selected tab
    st.markdown("---")
    
    try:
        if selected_tab == "📝 New Analysis":
            render_new_analysis_tab()
        elif selected_tab == "📊 Data Explorer":
            render_data_explorer_tab()
        elif selected_tab == "🌍 Cross-Year Analysis":
            render_cross_year_analysis_tab()
        else:
            st.error("❌ Invalid tab selected.")
    
    except Exception as e:
        logger.error(f"Error rendering tab {selected_tab}: {e}")
        st.error(f"❌ An error occurred: {e}")
        st.info("Please try refreshing the page or contact support if the issue persists.")
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
