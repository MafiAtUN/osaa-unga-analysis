"""
Advanced visualization module for UN General Assembly speech analysis.
Unified module that provides both classic and advanced visualizations.
"""

import streamlit as st

# Import both visualization systems
from .visualization_manager import UNGAVisualizationManager as ClassicVizManager
from .visualization_complete import UNGAVisualizationManager as AdvancedVizManager
from .visualization_complete import create_methodology_tooltip, add_methodology_section


class UNGAVisualizationManager:
    """Unified visualization manager with both classic and advanced visualizations."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.classic_viz = ClassicVizManager(db_manager)
        self.advanced_viz = AdvancedVizManager(db_manager)
    
    def render_visualization_menu(self):
        """Render unified visualization menu with submenu selection."""
        st.markdown("## 📊 Visualizations")
        st.markdown("**Interactive tools to explore UNGA speech data (1946-2025) • 11,094 speeches • 200 countries**")
        
        # Submenu selection
        viz_mode = st.radio(
            "Choose Visualization Mode:",
            options=["🎯 Advanced Analytics (Issue Salience, Similarity, Trends)", 
                     "📊 Classic Charts (Geographic, Rankings, Heatmaps)"],
            horizontal=True,
            key="viz_mode_selector"
        )
        
        st.markdown("---")
        
        if "Advanced Analytics" in viz_mode:
            # Render advanced visualizations from GitHub
            self.advanced_viz.render_visualization_menu()
        else:
            # Render classic visualizations
            self.classic_viz.render_visualization_menu()


# Export for backward compatibility
__all__ = [
    'UNGAVisualizationManager',
    'create_methodology_tooltip',
    'add_methodology_section'
]