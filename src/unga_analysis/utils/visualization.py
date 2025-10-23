"""
Advanced visualization module for UN General Assembly speech analysis.
Refactored into modular structure for better maintainability.
"""

# Import the main visualization manager
from .visualization_manager import UNGAVisualizationManager

# Import specialized visualization functions
from .chart_helpers import (
    create_methodology_tooltip,
    add_methodology_section,
    get_color_palette,
    create_theme_colors,
    format_number,
    create_plotly_layout,
    add_watermark
)

from .trend_visualizations import (
    create_trend_analysis_chart,
    create_cross_year_comparison,
    create_temporal_heatmap,
    create_trend_decomposition
)

from .geographic_visualizations import (
    create_geographic_distribution,
    create_regional_analysis,
    create_africa_vs_development_chart,
    create_country_ranking,
    create_geographic_heatmap
)

# Export the main class and functions for backward compatibility
__all__ = [
    'UNGAVisualizationManager',
    'create_methodology_tooltip',
    'add_methodology_section',
    'get_color_palette',
    'create_theme_colors',
    'format_number',
    'create_plotly_layout',
    'add_watermark',
    'create_trend_analysis_chart',
    'create_cross_year_comparison',
    'create_temporal_heatmap',
    'create_trend_decomposition',
    'create_geographic_distribution',
    'create_regional_analysis',
    'create_africa_vs_development_chart',
    'create_country_ranking',
    'create_geographic_heatmap'
]