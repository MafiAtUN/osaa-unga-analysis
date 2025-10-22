#!/usr/bin/env python3
"""
Simplified UNGA Analysis App for Azure Deployment
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="UNGA Analysis AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🌍 UNGA Analysis AI")
    st.markdown("**United Nations General Assembly Speech Analysis Platform**")
    
    # Simple authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.subheader("🔐 Authentication Required")
        password = st.text_input("Enter password:", type="password")
        if st.button("Login"):
            if password == os.getenv("APP_PASSWORD", "default_password"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        return
    
    # Main content
    st.success("✅ Authenticated successfully!")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Analysis", "📈 Reports"])
    
    with tab1:
        st.subheader("📊 Dashboard")
        
        # Sample metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Speeches", "1,247", "12")
        
        with col2:
            st.metric("Countries", "193", "0")
        
        with col3:
            st.metric("Years Covered", "79", "1")
        
        with col4:
            st.metric("Analysis Runs", "3,456", "89")
        
        # Sample chart
        st.subheader("Sample Analysis")
        data = pd.DataFrame({
            'Year': range(2020, 2025),
            'Speeches': [45, 52, 48, 51, 47]
        })
        
        fig = px.line(data, x='Year', y='Speeches', title='Speeches by Year')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🔍 Analysis")
        
        # Analysis form
        with st.form("analysis_form"):
            st.subheader("Configure Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                year_range = st.slider("Year Range", 1946, 2025, (2020, 2024))
                country = st.selectbox("Country", ["All", "USA", "China", "India", "Brazil"])
            
            with col2:
                analysis_type = st.selectbox("Analysis Type", [
                    "Sentiment Analysis",
                    "Topic Modeling", 
                    "SDG Analysis",
                    "Cross-Year Comparison"
                ])
                confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.7)
            
            submitted = st.form_submit_button("🚀 Run Analysis")
            
            if submitted:
                with st.spinner("Running analysis..."):
                    # Simulate analysis
                    import time
                    time.sleep(2)
                    
                    st.success("✅ Analysis completed!")
                    
                    # Show results
                    results = pd.DataFrame({
                        'Metric': ['Sentiment Score', 'Topic Count', 'SDG Mentions', 'Confidence'],
                        'Value': [0.75, 12, 8, 0.85]
                    })
                    
                    st.dataframe(results, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Reports")
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Dashboard Report"):
                st.success("Report generated! (Simulated)")
        
        with col2:
            if st.button("📈 Download Analysis Report"):
                st.success("Analysis report ready! (Simulated)")
        
        # Recent reports
        st.subheader("Recent Reports")
        reports = pd.DataFrame({
            'Date': ['2024-10-20', '2024-10-19', '2024-10-18'],
            'Type': ['Dashboard', 'Analysis', 'Export'],
            'Status': ['Completed', 'Completed', 'Completed']
        })
        
        st.dataframe(reports, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Built for UN OSAA | Powered by AI | 2024")

if __name__ == "__main__":
    main()
