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
    """Render country selection interface."""
    st.subheader("🏳️ Country Selection")
    
    # Country input
    country = st.text_input(
        "Country Name:",
        placeholder="e.g., United States, China, Nigeria, Kenya...",
        help="Enter the name of the country that delivered the speech"
    )
    
    # Auto-detect country from text
    if st.checkbox("🔍 Auto-detect country from text", help="Try to automatically detect the country from the speech text"):
        if st.session_state.get('extracted_text'):
            from utils import detect_country_simple
            detected_country = detect_country_simple(st.session_state.extracted_text)
            if detected_country != "Unknown":
                st.info(f"🔍 Detected country: **{detected_country}**")
                country = detected_country
    
    return country


def render_speech_date_selection():
    """Render speech date selection interface."""
    st.subheader("📅 Speech Date")
    
    # Date input
    speech_date = st.date_input(
        "Date of Speech:",
        value=datetime.now().date(),
        help="Select the date when the speech was delivered"
    )
    
    return speech_date


def render_classification_selection():
    """Render classification selection interface."""
    st.subheader("🏷️ Classification")
    
    # Classification options
    classification_options = [
        "African Member State",
        "Development Partner",
        "Other"
    ]
    
    classification = st.selectbox(
        "Select Classification:",
        options=classification_options,
        help="Choose the appropriate classification for the country"
    )
    
    return classification


def render_upload_section():
    """Render file upload section."""
    st.subheader("📁 Upload Speech File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file:",
        type=['txt', 'pdf', 'doc', 'docx', 'mp3', 'wav', 'm4a'],
        help="Upload a speech file (text, PDF, Word document, or audio)"
    )
    
    return uploaded_file


def render_paste_section():
    """Render text paste section."""
    st.subheader("📝 Paste Speech Text")
    
    # Text area for pasting
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
    """Render analysis suggestions."""
    st.subheader("💡 Suggested Questions")
    
    from utils import get_suggestion_questions
    suggestion_questions = get_suggestion_questions(country, classification)
    
    if suggestion_questions:
        # Show first few suggestions
        st.markdown("**Try asking:**")
        for i, question in enumerate(suggestion_questions[:5], 1):
            st.markdown(f"{i}. {question}")
        
        # Show more suggestions in expander
        with st.expander("View all suggestions"):
            for i, question in enumerate(suggestion_questions, 1):
                st.markdown(f"{i}. {question}")
    else:
        st.info("No suggestions available for this classification.")


def render_chat_interface(analysis_context: str, country: str, classification: str):
    """Render chat interface for follow-up questions."""
    st.subheader("💬 Ask Follow-up Questions")
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Show chat history
    if st.session_state.chat_history:
        st.markdown("#### 📚 Chat History")
        for i, chat in enumerate(st.session_state.chat_history[-5:], 1):
            with st.expander(f"Q{i}: {chat['question'][:50]}..."):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                st.caption(f"Asked at: {chat['timestamp']}")
    
    # Chat input
    chat_question = st.text_area(
        "Ask a question about the analysis:",
        height=100,
        placeholder="Type your question here...",
        help="Ask any follow-up question about the speech analysis"
    )
    
    # Chat buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🤖 Ask Question", type="primary", use_container_width=True):
            if chat_question.strip():
                # Process the question
                from analysis import process_chat_question
                with st.spinner("🧠 AI is thinking..."):
                    response, error = process_chat_question(
                        chat_question, 
                        analysis_context, 
                        country, 
                        classification
                    )
                    
                    if response:
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'question': chat_question,
                            'answer': response,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        st.success("✅ Response generated!")
                        st.markdown("#### 🤖 AI Response")
                        st.markdown(response)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {error}")
            else:
                st.warning("⚠️ Please enter a question.")
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


def render_export_section(analysis_data: Dict[str, Any]):
    """Render export section for analysis results."""
    st.subheader("📤 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as PDF", use_container_width=True):
            from export_utils import create_export_files
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
