"""
Trend visualization functions for UNGA Analysis.
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
from collections import Counter, defaultdict
from .chart_helpers import get_color_palette, create_plotly_layout, add_watermark

logger = logging.getLogger(__name__)

def create_trend_analysis_chart(data: pd.DataFrame, 
                               x_col: str, 
                               y_col: str, 
                               title: str,
                               color_col: Optional[str] = None) -> go.Figure:
    """Create a trend analysis chart."""
    colors = get_color_palette("default")
    
    if color_col:
        fig = px.line(data, x=x_col, y=y_col, color=color_col, 
                     title=title, color_discrete_sequence=colors)
    else:
        fig = px.line(data, x=x_col, y=y_col, title=title)
    
    fig.update_layout(**create_plotly_layout(title, x_col, y_col))
    return add_watermark(fig)

def create_cross_year_comparison(data: pd.DataFrame,
                                countries: List[str],
                                years: List[int],
                                metric: str) -> go.Figure:
    """Create a cross-year comparison chart."""
    filtered_data = data[
        (data['country_name'].isin(countries)) & 
        (data['year'].isin(years))
    ]
    
    if filtered_data.empty:
        return go.Figure()
    
    # Group by country and year
    grouped = filtered_data.groupby(['country_name', 'year'])[metric].sum().reset_index()
    
    fig = px.line(grouped, x='year', y=metric, color='country_name',
                  title=f"Cross-Year Comparison: {metric}",
                  color_discrete_sequence=get_color_palette("default"))
    
    fig.update_layout(**create_plotly_layout(
        f"Cross-Year Comparison: {metric}",
        "Year", 
        metric
    ))
    
    return add_watermark(fig)

def create_temporal_heatmap(data: pd.DataFrame,
                           countries: List[str],
                           years: List[int],
                           metric: str) -> go.Figure:
    """Create a temporal heatmap."""
    filtered_data = data[
        (data['country_name'].isin(countries)) & 
        (data['year'].isin(years))
    ]
    
    if filtered_data.empty:
        return go.Figure()
    
    # Create pivot table for heatmap
    pivot_data = filtered_data.pivot_table(
        values=metric, 
        index='country_name', 
        columns='year', 
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Blues',
        showscale=True
    ))
    
    fig.update_layout(**create_plotly_layout(
        f"Temporal Heatmap: {metric}",
        "Year",
        "Country"
    ))
    
    return add_watermark(fig)

def create_trend_decomposition(data: pd.DataFrame,
                              country: str,
                              years: List[int],
                              metric: str) -> go.Figure:
    """Create a trend decomposition chart."""
    country_data = data[
        (data['country_name'] == country) & 
        (data['year'].isin(years))
    ]
    
    if country_data.empty:
        return go.Figure()
    
    # Sort by year
    country_data = country_data.sort_values('year')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f"Original Trend: {country}", "Trend Analysis"),
        vertical_spacing=0.1
    )
    
    # Original trend
    fig.add_trace(
        go.Scatter(x=country_data['year'], y=country_data[metric],
                  mode='lines+markers', name='Original',
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    # Trend analysis (simplified)
    if len(country_data) > 1:
        # Calculate moving average
        window_size = min(3, len(country_data))
        moving_avg = country_data[metric].rolling(window=window_size, center=True).mean()
        
        fig.add_trace(
            go.Scatter(x=country_data['year'], y=moving_avg,
                      mode='lines', name='Moving Average',
                      line=dict(color='#ff7f0e', width=2, dash='dash')),
            row=2, col=1
        )
    
    fig.update_layout(**create_plotly_layout(
        f"Trend Decomposition: {country}",
        "Year",
        metric,
        height=800
    ))
    
    return add_watermark(fig)
