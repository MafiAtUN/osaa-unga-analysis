"""
Visualizations Tab
Advanced data visualizations for UNGA speech analysis
"""

import streamlit as st
from typing import Dict, List, Any
from ...utils.visualization import UNGAVisualizationManager
from ...data.simple_vector_storage import simple_vector_storage as db_manager


def render_visualizations_tab():
    """Render the dedicated visualizations tab."""
    st.header("📊 Advanced Visualizations")
    st.markdown("**Interactive visualizations for UNGA speech analysis and exploration**")
    
    try:
        # Initialize visualization manager
        viz_manager = UNGAVisualizationManager(db_manager)
        
        # Render the visualization menu
        viz_manager.render_visualization_menu()
        
    except Exception as e:
        st.error(f"Error initializing visualizations: {e}")
        st.info("This might be because the database is not properly initialized or visualization dependencies are missing.")
        
        # Fallback visualization options
        st.markdown("### Basic Visualization Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Available Charts")
            st.markdown("- Country distribution")
            st.markdown("- Year-over-year trends")
            st.markdown("- Word count analysis")
            st.markdown("- SDG coverage")
            st.markdown("- Regional analysis")
        
        with col2:
            st.markdown("#### 🔧 Chart Types")
            st.markdown("- Bar charts")
            st.markdown("- Line graphs")
            st.markdown("- Heatmaps")
            st.markdown("- Scatter plots")
            st.markdown("- Interactive maps")
        
        st.info("💡 To enable full visualization capabilities, ensure all dependencies are installed and the database is properly configured.")
