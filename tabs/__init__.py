"""
Tabs Module
Contains all tab-specific UI components for the UN GA Daily Readouts application
"""

from .new_analysis_tab import render_new_analysis_tab
from .data_explorer_tab import render_data_explorer_tab
from .cross_year_analysis_tab import render_cross_year_analysis_tab

__all__ = [
    'render_new_analysis_tab',
    'render_data_explorer_tab', 
    'render_cross_year_analysis_tab'
]
