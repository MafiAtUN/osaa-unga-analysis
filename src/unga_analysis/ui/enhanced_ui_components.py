"""
Enhanced UI components for UNGA Analysis App.
Provides improved styling, user guidance, and better UX.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

def render_page_header(title: str, subtitle: str = "", show_logo: bool = True):
    """Render an enhanced page header with logo and styling."""
    if show_logo:
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            try:
                st.image("artifacts/logo/OSAA identifier acronym white.svg", width=120)
            except:
                st.markdown("### 🇺🇳")
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #1f77b4; margin-bottom: 10px; font-size: 2.5em;">
                    {title}
                </h1>
                <p style="color: #666; font-size: 1.2em; margin: 0;">
                    {subtitle}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("### 📊")
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #e0e0e0;">
            <h1 style="color: #1f77b4; margin-bottom: 10px;">
                {title}
            </h1>
            <p style="color: #666; font-size: 1.1em; margin: 0;">
                {subtitle}
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_info_card(title: str, content: str, icon: str = "ℹ️", color: str = "#e3f2fd"):
    """Render an informational card with styling."""
    st.markdown(f"""
    <div style="
        background-color: {color};
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h4 style="color: #1f77b4; margin: 0 0 10px 0;">
            {icon} {title}
        </h4>
        <p style="margin: 0; color: #333; line-height: 1.5;">
            {content}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_success_card(message: str, details: str = ""):
    """Render a success message card."""
    st.markdown(f"""
    <div style="
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h4 style="color: #4caf50; margin: 0 0 10px 0;">
            ✅ {message}
        </h4>
        <p style="margin: 0; color: #333; line-height: 1.5;">
            {details}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_warning_card(message: str, details: str = ""):
    """Render a warning message card."""
    st.markdown(f"""
    <div style="
        background-color: #fff3cd;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h4 style="color: #ff9800; margin: 0 0 10px 0;">
            ⚠️ {message}
        </h4>
        <p style="margin: 0; color: #333; line-height: 1.5;">
            {details}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_error_card(message: str, details: str = ""):
    """Render an error message card."""
    st.markdown(f"""
    <div style="
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h4 style="color: #f44336; margin: 0 0 10px 0;">
            ❌ {message}
        </h4>
        <p style="margin: 0; color: #333; line-height: 1.5;">
            {details}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_step_guide(steps: List[Dict[str, str]]):
    """Render a step-by-step guide with visual indicators."""
    st.markdown("### 📋 Step-by-Step Guide")
    
    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
        ">
            <div style="
                background-color: #1f77b4;
                color: white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                font-weight: bold;
            ">
                {i}
            </div>
            <div>
                <h4 style="margin: 0; color: #1f77b4;">
                    {step['title']}
                </h4>
                <p style="margin: 5px 0 0 0; color: #666;">
                    {step['description']}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_feature_highlights(features: List[Dict[str, str]]):
    """Render feature highlights with icons and descriptions."""
    st.markdown("### ✨ Key Features")
    
    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 2em; margin-bottom: 10px;">
                    {feature['icon']}
                </div>
                <h4 style="color: #1f77b4; margin: 0;">
                    {feature['title']}
                </h4>
                <p style="color: #666; font-size: 0.9em; margin: 5px 0 0 0;">
                    {feature['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)

def render_metric_cards(metrics: List[Dict[str, Any]]):
    """Render metric cards with enhanced styling."""
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta', None),
                help=metric.get('help', None)
            )

def render_enhanced_sidebar():
    """Render a lean sidebar with essential information."""
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1f77b4, #4a90e2);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        ">
            <h3 style="margin: 0;">🇺🇳 UNGA Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("### 📊 Database")
        try:
            from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
            speeches_count = db_manager.conn.execute('SELECT COUNT(*) FROM speeches').fetchone()[0]
            countries_count = db_manager.conn.execute('SELECT COUNT(DISTINCT country_name) FROM speeches').fetchone()[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Speeches", f"{speeches_count:,}")
            with col2:
                st.metric("Countries", f"{countries_count:,}")
        except:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Speeches", "11,094")
            with col2:
                st.metric("Countries", "200")

def render_loading_spinner(message: str = "Processing..."):
    """Render a custom loading spinner with message."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 40px;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    ">
        <div style="
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1f77b4;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        "></div>
        <p style="color: #666; margin: 0;">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add CSS animation separately
    st.markdown("""
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def render_tooltip_help(text: str, help_text: str):
    """Render text with a tooltip help icon."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 10px 0;">
        <span style="margin-right: 5px;">{text}</span>
        <span style="
            background-color: #1f77b4;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            cursor: help;
            margin-left: 5px;
        " title="{help_text}">
            ?
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_progress_bar(current: int, total: int, label: str = "Progress"):
    """Render a custom progress bar."""
    percentage = (current / total) * 100 if total > 0 else 0
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: bold;">{label}</span>
            <span style="color: #666;">{current}/{total} ({percentage:.1f}%)</span>
        </div>
        <div style="
            background-color: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #1f77b4, #4a90e2);
                height: 100%;
                width: {percentage}%;
                transition: width 0.3s ease;
                border-radius: 10px;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_enhanced_tabs(tab_configs: List[Dict[str, str]]):
    """Render enhanced tabs with better styling."""
    tab_names = [config['name'] for config in tab_configs]
    tab_icons = [config.get('icon', '📄') for config in tab_configs]
    
    # Create tabs with icons
    tabs = st.tabs([f"{icon} {name}" for icon, name in zip(tab_icons, tab_names)])
    
    return tabs

def render_data_quality_indicators(quality_metrics: Dict[str, Any]):
    """Render data quality indicators."""
    st.markdown("### 📊 Data Quality Indicators")
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            "Completeness",
            f"{quality_metrics.get('completeness', 0):.1f}%",
            help="Percentage of complete records"
        )
    
    with cols[1]:
        st.metric(
            "Accuracy",
            f"{quality_metrics.get('accuracy', 0):.1f}%",
            help="Data accuracy score"
        )
    
    with cols[2]:
        st.metric(
            "Consistency",
            f"{quality_metrics.get('consistency', 0):.1f}%",
            help="Data consistency score"
        )
    
    with cols[3]:
        st.metric(
            "Timeliness",
            f"{quality_metrics.get('timeliness', 0):.1f}%",
            help="Data freshness score"
        )

def render_enhanced_footer():
    """Render an enhanced footer with better styling."""
    st.markdown("---")
    st.markdown("""
    <div style="
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
    ">
        <h4 style="color: #1f77b4; margin: 0 0 10px 0;">
            🇺🇳 UNGA Analysis Platform
        </h4>
        <p style="color: #666; margin: 0 0 10px 0;">
            Built for UN OSAA | Supports PDF, DOCX, MP3 | Auto-classifies African Member States vs Development Partners
        </p>
        <p style="color: #999; font-size: 0.9em; margin: 0;">
            Developed by: <strong>SMU Data Team</strong> | 
            <a href="#" style="color: #1f77b4;">Documentation</a> | 
            <a href="#" style="color: #1f77b4;">Support</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
