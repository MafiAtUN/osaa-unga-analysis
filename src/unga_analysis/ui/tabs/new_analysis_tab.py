"""
New Analysis Tab Module
Handles the main analysis interface for new speech uploads
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from ..ui_components import (
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
from ..enhanced_ui_components import (
    render_info_card, render_success_card, render_warning_card, 
    render_error_card, render_step_guide, render_loading_spinner,
    render_tooltip_help, render_progress_bar
)
from ...core.auth import validate_file_upload, check_rate_limit
from ...data.simple_vector_storage import simple_vector_storage as db_manager


def check_existing_data(country: str, year: int) -> Optional[Dict[str, Any]]:
    """Check if data already exists for the given country and year."""
    try:
        # Query the database for existing speeches
        query = """
            SELECT id, country_name, year, speech_text, word_count, created_at
            FROM speeches 
            WHERE country_name = ? AND year = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = db_manager.conn.execute(query, [country, year]).fetchone()
        
        if result:
            return {
                'id': result[0],
                'country': result[1],
                'year': result[2],
                'text': result[3],
                'word_count': result[4],
                'created_at': result[5]
            }
        return None
    except Exception as e:
        st.error(f"Error checking existing data: {e}")
        return None


def render_new_analysis_tab():
    """Render the enhanced new analysis tab."""
    st.header("📝 New Analysis")
    st.markdown("**Upload or paste a UN General Assembly speech for AI analysis**")
    
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Step-by-step guide
    steps = [
        {
            "title": "Upload or Paste Content",
            "description": "Upload a PDF, DOCX, or MP3 file, or paste text directly"
        },
        {
            "title": "Provide Speech Information", 
            "description": "Select country, date, and classification details"
        },
        {
            "title": "Choose Analysis Options",
            "description": "Select AI model and analysis depth"
        },
        {
            "title": "Review and Analyze",
            "description": "Review settings and start the AI analysis"
        }
    ]
    render_step_guide(steps)
    
    # Information card about supported formats
    render_info_card(
        "Supported Formats",
        "Upload PDF documents, Word files (DOCX), or audio files (MP3). You can also paste text directly. The system will automatically extract and analyze the content."
    )
    
    # Create two columns for upload and paste
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Upload File")
        render_tooltip_help(
            "File Upload",
            "Supported formats: PDF, DOCX, MP3. Maximum size: 10MB"
        )
        uploaded_file = render_upload_section()
    
    with col2:
        st.markdown("### 📝 Paste Text")
        render_tooltip_help(
            "Text Input",
            "Paste speech text directly. Minimum 100 words recommended for best analysis."
        )
        pasted_text = render_paste_section()
    
    # Check if either input is provided
    if not uploaded_file and not pasted_text:
        render_warning_card(
            "No Content Provided",
            "Please upload a file or paste text to begin analysis. The system needs content to analyze."
        )
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
    
    # Check for existing data if country and year are selected
    existing_data = None
    if country and speech_date:
        year = speech_date.year
        existing_data = check_existing_data(country, year)
        
        if existing_data:
            st.success(f"✅ **Data already available!** Found existing speech for {country} in {year}")
            st.info(f"📊 **Existing Data:** {existing_data['word_count']:,} words, added on {existing_data['created_at']}")
            
            # Show options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 Chat with Existing Data", type="primary"):
                    # Load existing data for chat
                    st.session_state.existing_analysis = {
                        'country': existing_data['country'],
                        'year': existing_data['year'],
                        'text': existing_data['text'],
                        'word_count': existing_data['word_count'],
                        'date': speech_date.isoformat(),
                        'classification': classification,
                        'model': 'existing-data'
                    }
                    st.rerun()
            
            with col2:
                if st.button("📝 Upload New Speech Anyway"):
                    st.info("You can proceed with uploading new speech data below.")
    
    # Model selection
    st.markdown("### 🤖 AI Model Selection")
    from llm import get_available_models
    available_models = get_available_models()
    
    if available_models:
        model = st.selectbox(
            "Choose AI Model:",
            options=available_models,
            key="new_analysis_model_select",
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
    
    # Handle existing data chat interface
    if hasattr(st.session_state, 'existing_analysis') and st.session_state.existing_analysis:
        st.markdown("---")
        st.markdown("## 💬 Chat with Existing Data")
        
        # Display existing data info
        existing = st.session_state.existing_analysis
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏳️ Country", existing['country'])
        with col2:
            st.metric("📅 Year", existing['year'])
        with col3:
            st.metric("📝 Word Count", f"{existing['word_count']:,}")
        with col4:
            st.metric("🏷️ Classification", existing['classification'])
        
        # Chat interface for existing data
        render_chat_interface(existing['text'], existing['country'], existing['year'])
        
        # Option to clear and start fresh
        if st.button("🔄 Start Fresh Analysis"):
            del st.session_state.existing_analysis
            st.rerun()
        
        return
    
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
