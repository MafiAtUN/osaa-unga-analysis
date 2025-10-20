"""
New Analysis Tab Module
Handles the main analysis interface for new speech uploads
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from ui_components import (
    render_upload_section, 
    render_paste_section, 
    render_country_selection,
    render_speech_date_selection,
    render_classification_selection,
    render_sidebar_metadata_section,
    render_analysis_suggestions,
    render_chat_interface,
    render_export_section
)
from analysis import process_analysis
from auth import validate_file_upload, check_rate_limit


def render_new_analysis_tab():
    """Render the new analysis tab."""
    st.header("📝 New Analysis")
    st.markdown("**Upload or paste a UN General Assembly speech for AI analysis**")
    
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Create two columns for upload and paste
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Upload File")
        uploaded_file = render_upload_section()
    
    with col2:
        st.markdown("### 📝 Paste Text")
        pasted_text = render_paste_section()
    
    # Check if either input is provided
    if not uploaded_file and not pasted_text:
        st.info("👆 Please upload a file or paste text to begin analysis.")
        return
    
    # Validate file if uploaded
    if uploaded_file:
        if not validate_file_upload(uploaded_file.getvalue(), uploaded_file.name):
            st.error("❌ Invalid file. Please check file size and type.")
            return
    
    # Country and metadata selection
    st.markdown("---")
    st.markdown("### 🏷️ Speech Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country = render_country_selection()
    
    with col2:
        speech_date = render_speech_date_selection()
    
    with col3:
        classification = render_classification_selection()
    
    # Model selection
    st.markdown("### 🤖 AI Model Selection")
    from llm import get_available_models
    available_models = get_available_models()
    
    if available_models:
        model = st.selectbox(
            "Choose AI Model:",
            options=available_models,
            index=0,
            help="Select the AI model for analysis"
        )
    else:
        model = "model-router-osaa-2"
        st.warning("⚠️ Using default model. AI service may not be available.")
    
    # Analysis button
    st.markdown("---")
    
    # Check rate limit
    user_id = st.session_state.get('user_id', 'anonymous')
    if not check_rate_limit(user_id):
        st.error("❌ Rate limit exceeded. Please wait before making another request.")
        return
    
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        if not country.strip():
            st.error("❌ Please enter a country name.")
            return
        
        if not classification:
            st.error("❌ Please select a classification.")
            return
        
        # Process the analysis
        analysis_data = process_analysis(
            uploaded_file=uploaded_file,
            pasted_text=pasted_text,
            country=country,
            speech_date=speech_date,
            classification=classification,
            model=model
        )
        
        if analysis_data:
            # Add to analysis history
            st.session_state.analysis_history.append(analysis_data)
            
            # Display results
            render_analysis_results(analysis_data)
        else:
            st.error("❌ Analysis failed. Please try again.")
    
    # Render sidebar metadata
    render_sidebar_metadata_section(uploaded_file, pasted_text)


def render_analysis_results(analysis_data: Dict[str, Any]):
    """Render the analysis results."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Display basic info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏳️ Country", analysis_data['country'])
    with col2:
        st.metric("📅 Date", analysis_data['date'])
    with col3:
        st.metric("🏷️ Classification", analysis_data['classification'])
    with col4:
        st.metric("📝 Word Count", f"{analysis_data['word_count']:,}")
    
    # Display the analysis
    st.markdown("### 🤖 AI Analysis")
    st.markdown(analysis_data['output_markdown'])
    
    # Analysis suggestions
    render_analysis_suggestions(analysis_data['country'], analysis_data['classification'])
    
    # Chat interface
    render_chat_interface(
        analysis_data['output_markdown'],
        analysis_data['country'],
        analysis_data['classification']
    )
    
    # Export section
    render_export_section(analysis_data)
    
    # Store in session state for other tabs
    st.session_state.current_analysis = analysis_data
