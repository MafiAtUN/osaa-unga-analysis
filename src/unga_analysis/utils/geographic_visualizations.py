"""
Geographic visualization functions for UNGA Analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from collections import Counter, defaultdict
from .chart_helpers import get_color_palette, create_plotly_layout, add_watermark

logger = logging.getLogger(__name__)

def create_geographic_distribution(data: pd.DataFrame,
                                  metric: str,
                                  title: str) -> go.Figure:
    """Create a geographic distribution chart."""
    # Group by country
    country_data = data.groupby('country_name')[metric].sum().reset_index()
    country_data = country_data.sort_values(metric, ascending=False)
    
    # Take top 20 countries
    top_countries = country_data.head(20)
    
    fig = px.bar(top_countries, x='country_name', y=metric,
                  title=title,
                  color=metric,
                  color_continuous_scale='Blues')
    
    fig.update_layout(**create_plotly_layout(
        title,
        "Country",
        metric
    ))
    
    fig.update_xaxes(tickangle=45)
    return add_watermark(fig)

def create_regional_analysis(data: pd.DataFrame,
                           regions: Dict[str, List[str]],
                           metric: str) -> go.Figure:
    """Create a regional analysis chart."""
    # Add region column
    data['region'] = data['country_name'].map(
        {country: region for region, countries in regions.items() 
         for country in countries}
    )
    
    # Group by region
    regional_data = data.groupby('region')[metric].sum().reset_index()
    
    fig = px.pie(regional_data, values=metric, names='region',
                 title=f"Regional Distribution: {metric}",
                 color_discrete_sequence=get_color_palette("default"))
    
    fig.update_layout(**create_plotly_layout(
        f"Regional Distribution: {metric}",
        "", ""
    ))
    
    return add_watermark(fig)

def create_africa_vs_development_chart(data: pd.DataFrame,
                                      metric: str) -> go.Figure:
    """Create Africa vs Development Partners comparison."""
    # Classify countries
    african_countries = [
        'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
        'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Comoros',
        'Côte d\'Ivoire', 'Democratic Republic of the Congo', 'Djibouti',
        'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia',
        'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya',
        'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali',
        'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia',
        'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Seychelles', 'Sierra Leone',
        'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania',
        'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
    ]
    
    data['classification'] = data['country_name'].apply(
        lambda x: 'African Member State' if x in african_countries else 'Development Partner'
    )
    
    # Group by classification
    classification_data = data.groupby('classification')[metric].sum().reset_index()
    
    fig = px.bar(classification_data, x='classification', y=metric,
                 title=f"Africa vs Development Partners: {metric}",
                 color='classification',
                 color_discrete_map={
                     'African Member State': '#FF6B35',
                     'Development Partner': '#0066CC'
                 })
    
    fig.update_layout(**create_plotly_layout(
        f"Africa vs Development Partners: {metric}",
        "Classification",
        metric
    ))
    
    return add_watermark(fig)

def create_country_ranking(data: pd.DataFrame,
                          metric: str,
                          top_n: int = 15) -> go.Figure:
    """Create a country ranking chart."""
    # Group by country
    country_data = data.groupby('country_name')[metric].sum().reset_index()
    country_data = country_data.sort_values(metric, ascending=True)
    
    # Take top N countries
    top_countries = country_data.tail(top_n)
    
    fig = px.bar(top_countries, x=metric, y='country_name',
                 orientation='h',
                 title=f"Top {top_n} Countries: {metric}",
                 color=metric,
                 color_continuous_scale='Blues')
    
    fig.update_layout(**create_plotly_layout(
        f"Top {top_n} Countries: {metric}",
        metric,
        "Country"
    ))
    
    return add_watermark(fig)

def create_geographic_heatmap(data: pd.DataFrame,
                             countries: List[str],
                             metric: str) -> go.Figure:
    """Create a geographic heatmap."""
    # Filter data
    filtered_data = data[data['country_name'].isin(countries)]
    
    if filtered_data.empty:
        return go.Figure()
    
    # Group by country
    country_data = filtered_data.groupby('country_name')[metric].sum().reset_index()
    
    # Create a simple heatmap representation
    fig = go.Figure(data=go.Bar(
        x=country_data['country_name'],
        y=country_data[metric],
        marker=dict(
            color=country_data[metric],
            colorscale='Blues',
            showscale=True
        )
    ))
    
    fig.update_layout(**create_plotly_layout(
        f"Geographic Heatmap: {metric}",
        "Country",
        metric
    ))
    
    fig.update_xaxes(tickangle=45)
    return add_watermark(fig)
