"""
Chart helper utilities for UNGA Analysis visualizations.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import re
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

def create_methodology_tooltip(methodology_text: str) -> str:
    """Create a methodology tooltip that appears on hover."""
    return f"""
    <div style="position: relative; display: inline-block;">
        <span style="color: #666; cursor: help; font-size: 0.8em;">ℹ️</span>
        <div style="
            visibility: hidden;
            width: 300px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            border: 1px solid #ccc;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 0.85em;
            line-height: 1.4;
        ">
            <strong>Methodology:</strong><br>
            {methodology_text}
        </div>
    </div>
    """

def add_methodology_section(methodology_text: str):
    """Add a collapsible methodology section."""
    with st.expander("📊 Methodology & Data Sources", expanded=False):
        st.markdown(methodology_text)

def get_color_palette(palette_name: str = "default") -> List[str]:
    """Get a color palette for visualizations."""
    palettes = {
        "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
        "un_blue": ["#0066CC", "#0099FF", "#66B3FF", "#99CCFF", "#CCE5FF"],
        "africa": ["#FF6B35", "#F7931E", "#FFD23F", "#06FFA5", "#118AB2"],
        "climate": ["#2E8B57", "#3CB371", "#20B2AA", "#00CED1", "#87CEEB"],
        "peace": ["#8B0000", "#DC143C", "#FF6347", "#FFA07A", "#FFE4E1"]
    }
    return palettes.get(palette_name, palettes["default"])

def create_theme_colors() -> Dict[str, str]:
    """Create a consistent color theme for visualizations."""
    return {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e", 
        "success": "#2ca02c",
        "danger": "#d62728",
        "warning": "#ff7f0e",
        "info": "#17becf",
        "light": "#f8f9fa",
        "dark": "#343a40",
        "africa": "#FF6B35",
        "development": "#0066CC"
    }

def format_number(num: float) -> str:
    """Format numbers for display."""
    if num >= 1e9:
        return f"{num/1e9:.1f}B"
    elif num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.0f}"

def create_plotly_layout(title: str, x_title: str = "", y_title: str = "", 
                        width: int = 800, height: int = 600) -> Dict[str, Any]:
    """Create a standardized Plotly layout."""
    return {
        "title": {
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": "#333"}
        },
        "xaxis": {
            "title": x_title,
            "showgrid": True,
            "gridcolor": "#e0e0e0",
            "gridwidth": 1
        },
        "yaxis": {
            "title": y_title,
            "showgrid": True,
            "gridcolor": "#e0e0e0",
            "gridwidth": 1
        },
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "font": {"family": "Arial, sans-serif", "size": 12},
        "width": width,
        "height": height,
        "margin": {"l": 50, "r": 50, "t": 80, "b": 50}
    }

def add_watermark(fig: go.Figure, text: str = "UNGA Analysis") -> go.Figure:
    """Add a watermark to the figure."""
    fig.add_annotation(
        text=text,
        xref="paper", yref="paper",
        x=0.5, y=0.02,
        showarrow=False,
        font=dict(size=10, color="rgba(0,0,0,0.3)"),
        xanchor="center"
    )
    return fig
