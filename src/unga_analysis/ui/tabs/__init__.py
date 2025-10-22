"""
Tabs Module
Contains all tab-specific UI components for the UN GA Daily Readouts application
"""

from .data_explorer_tab import render_data_explorer_tab
from .cross_year_analysis_tab import render_cross_year_analysis_tab
from .document_context_analysis_tab import render_document_context_analysis_tab
from .error_insights_tab import render_error_insights_tab

__all__ = [
    'render_data_explorer_tab', 
    'render_cross_year_analysis_tab',
    'render_document_context_analysis_tab',
    'render_error_insights_tab'
]
