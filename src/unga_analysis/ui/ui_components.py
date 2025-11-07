"""
UI Components Module
Reusable UI components for the Streamlit application
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..data.cross_year_analysis import cross_year_manager


def render_country_selection():
    """Render country selection interface with all UN member countries."""
    # Get all countries from the mapping
    from ..data.data_ingestion import COUNTRY_CODE_MAPPING
    
    # Create sorted list of country names
    all_countries = sorted(COUNTRY_CODE_MAPPING.values())
    
    # Country selection with searchable dropdown
    country = st.selectbox(
        "Country Name:",
        options=[""] + all_countries,  # Add empty option at start
        index=0,
        help="Select the country that delivered the speech"
    )
    
    return country if country else None


def render_speech_date_selection():
    """Render speech date selection interface."""
    # Date input
    speech_date = st.date_input(
        "Date of Speech:",
        value=datetime.now().date(),
        help="Select the date when the speech was delivered"
    )
    
    return speech_date


def render_classification_selection(country=None):
    """Render classification selection interface."""
    # Classification options
    classification_options = [
        "African Member State",
        "Development Partner",
        "Other"
    ]
    
    # Auto-detect if country is African
    default_index = 0
    if country:
        from ..data.data_ingestion import data_ingestion_manager

        if data_ingestion_manager.is_african_member(country):
            default_index = 0  # African Member State
            st.info(f"🌍 {country} is automatically classified as an African Member State")
        else:
            default_index = 1  # Development Partner
    
    classification = st.selectbox(
        "Select Classification:",
        options=classification_options,
        index=default_index,
        help="Choose the appropriate classification for the country"
    )
    
    return classification


def render_upload_section():
    """Render file upload section."""
    # File uploader (header is rendered in the calling function)
    uploaded_file = st.file_uploader(
        "Choose a file:",
        type=['txt', 'pdf', 'doc', 'docx', 'mp3', 'wav', 'm4a'],
        help="Upload a speech file (text, PDF, Word document, or audio)"
    )
    
    return uploaded_file


def render_paste_section():
    """Render text paste section."""
    # Text area for pasting (header is rendered in the calling function)
    pasted_text = st.text_area(
        "Paste speech text here:",
        height=200,
        placeholder="Paste the speech text here...",
        help="Copy and paste the speech text directly"
    )
    
    return pasted_text


def render_sidebar_metadata_section(uploaded_file=None, pasted_text=None):
    """Render sidebar metadata section."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Session Info")
    
    # Show current session info
    if uploaded_file:
        st.sidebar.info(f"📁 **File:** {uploaded_file.name}")
        st.sidebar.info(f"📏 **Size:** {len(uploaded_file.getvalue()):,} bytes")
    
    if pasted_text:
        st.sidebar.info(f"📝 **Text Length:** {len(pasted_text):,} characters")
        st.sidebar.info(f"📄 **Word Count:** {len(pasted_text.split()):,} words")
    
    # Show analysis history
    if st.session_state.get('analysis_history'):
        st.sidebar.markdown("### 📚 Recent Analyses")
        for i, analysis in enumerate(st.session_state.analysis_history[-3:], 1):
            with st.sidebar.expander(f"Analysis {i}: {analysis.get('country', 'Unknown')}"):
                st.write(f"**Date:** {analysis.get('date', 'Unknown')}")
                st.write(f"**Classification:** {analysis.get('classification', 'Unknown')}")
                st.write(f"**Word Count:** {analysis.get('word_count', 0):,}")


def render_data_availability_info():
    """Render data availability information."""
    st.subheader("📊 Data Availability")
    
    # Get data summary
    data_summary = cross_year_manager.get_data_summary()
    
    if data_summary:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🗣️ Total Countries", data_summary.get('total_countries', 0))
        with col2:
            st.metric("📝 Total Speeches", data_summary.get('total_speeches', 0))
        with col3:
            st.metric("📅 Available Years", data_summary.get('total_years', 0))
        with col4:
            # Count AU members from all years
            au_count = 0
            # AU Members metric removed as requested
    else:
        st.info("📊 No data available yet. Upload speech files to see statistics.")


def render_analysis_suggestions(country: str, classification: str):
    """Render analysis suggestions with clickable questions."""
    st.subheader("💡 Suggested Questions")
    
    from ..utils.utils import get_suggestion_questions
    suggestion_questions = get_suggestion_questions(country, classification)
    
    if suggestion_questions:
        # Initialize selected question in session state
        if 'selected_question' not in st.session_state:
            st.session_state.selected_question = ""
        
        # Show first few suggestions as clickable buttons
        st.markdown("**Click a question to load it:**")
        cols = st.columns(1)
        for i, question in enumerate(suggestion_questions[:5], 1):
            if st.button(f"💬 {question}", key=f"suggest_{i}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()  # Rerun to load the question in the text area
        
        # Show more suggestions in expander
        with st.expander("View all suggestions"):
            for i, question in enumerate(suggestion_questions, 1):
                if st.button(f"💬 {question}", key=f"suggest_all_{i}", use_container_width=True):
                    st.session_state.selected_question = question
                    st.rerun()  # Rerun to load the question in the text area
    else:
        st.info("No suggestions available for this classification.")


def render_chat_interface(analysis_context: str, country: str, classification: str):
    """Render chat interface for follow-up questions."""
    st.subheader("💬 Ask Follow-up Questions")
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize selected question if not exists
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""
    
    # Chat input - use selected question if available
    # Use a persistent key to maintain the text area value
    if 'chat_input_value' not in st.session_state:
        st.session_state.chat_input_value = ""
    
    # If there's a selected question, update the input value
    if st.session_state.selected_question:
        st.session_state.chat_input_value = st.session_state.selected_question
        st.session_state.selected_question = ""  # Clear after loading
    
    chat_question = st.text_area(
        "Ask a question about the analysis:",
        value=st.session_state.chat_input_value,
        height=100,
        placeholder="Type your question here or click a suggestion above...",
        help="Ask any follow-up question about the speech analysis",
        key="chat_question_input"
    )
    
    # Update the session state with current value
    st.session_state.chat_input_value = chat_question
    
    # Chat buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🤖 Ask Question", type="primary", use_container_width=True):
            if chat_question.strip():
                # Process the question using Azure OpenAI
                with st.spinner("🧠 AI is thinking..."):
                    try:
                        from ..core.openai_client import get_openai_client
                        from ..core.llm import run_analysis
                        
                        client = get_openai_client()
                        if not client:
                            st.error("❌ AI service is not available.")
                        else:
                            # Create context-aware prompt
                            system_msg = f"""You are an expert analyst of UN General Assembly speeches. 
                            You are answering questions about a speech from {country} ({classification}).
                            
                            Use the following analysis context to answer the question:
                            {analysis_context}
                            
                            Provide a clear, concise answer based on the analysis."""
                            
                            user_msg = chat_question
                            
                            # Get deployment name
                            import os
                            model = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'model-router')
                            
                            response = run_analysis(
                                system_msg=system_msg,
                                user_msg=user_msg,
                                model=model,
                                client=client
                            )
                            
                            if response:
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    'question': chat_question,
                                    'answer': response,
                                    'timestamp': datetime.now().strftime('%H:%M:%S')
                                })
                                
                                # Save chat history to database if we have an analysis_id
                                if 'current_analysis_data' in st.session_state:
                                    analysis_data = st.session_state.current_analysis_data
                                    if 'analysis_id' in analysis_data:
                                        from ...data.simple_vector_storage import simple_vector_storage as db_manager
                                        db_manager.update_analysis_chat_history(
                                            analysis_data['analysis_id'],
                                            st.session_state.chat_history
                                        )
                                
                                st.success("✅ Response generated and saved!")
                                # Clear the input after successful response
                                st.session_state.chat_input_value = ""
                            else:
                                st.error("❌ No response received from AI")
                                
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please enter a question.")
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ Chat history cleared!")
    
    with col3:
        if st.button("🔄 Clear Input", use_container_width=True):
            st.session_state.selected_question = ""
            st.session_state.chat_input_value = ""
            st.rerun()
    
    # Show chat history below
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("#### 📚 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
            with st.expander(f"Q: {chat['question'][:60]}...", expanded=(i==1)):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                st.caption(f"Asked at: {chat['timestamp']}")


def render_export_section(analysis_data: Dict[str, Any]):
    """Render export section for analysis results."""
    st.subheader("📤 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as PDF", use_container_width=True):
            from ..utils.export_utils import create_export_files
            try:
                export_files = create_export_files(analysis_data)
                if export_files:
                    st.success("✅ PDF exported successfully!")
                else:
                    st.error("❌ Export failed.")
            except Exception as e:
                st.error(f"❌ Export error: {e}")
    
    with col2:
        if st.button("📊 Export as Excel", use_container_width=True):
            # Export to Excel functionality
            st.info("📊 Excel export functionality coming soon!")
    
    with col3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            # Copy to clipboard functionality
            st.info("📋 Clipboard functionality coming soon!")
