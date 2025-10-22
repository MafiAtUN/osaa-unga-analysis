"""
UN GA Daily Readouts - Streamlit App (Refactored)
Production-ready app for analyzing UN General Assembly speeches

Developed by: SMU Data Team
"""

import os
import logging
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="UN GA Daily Readouts",
    page_icon="🇺🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules from the new package structure
from src.unga_analysis.core.prompts import SYSTEM_MESSAGE, build_user_prompt, get_question_set, build_chat_prompt
from src.unga_analysis.core.classify import infer_classification, get_au_members
from src.unga_analysis.data.ingest import extract_text_from_file, validate_text_length
from src.unga_analysis.core.llm import run_analysis, get_available_models, OpenAIError, chunk_and_synthesize
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
from src.unga_analysis.utils.sdg_utils import extract_sdgs, detect_africa_mention, format_sdgs
from src.unga_analysis.utils.export_utils import create_export_files, format_filename
from src.unga_analysis.data.data_ingestion import data_ingestion_manager
from src.unga_analysis.data.cross_year_analysis import cross_year_manager
from src.unga_analysis.utils.visualization import UNGAVisualizationManager

# Import authentication and session management
from src.unga_analysis.ui.auth import initialize_session_state, check_password, show_login_form

# Import security utilities
from src.unga_analysis.utils.security import sanitize_input, validate_prompt_safety, validate_file_upload

# Import configuration
from src.unga_analysis.config.questions import (
    get_suggestion_questions,
    get_cross_year_topics_and_questions,
    get_country_and_group_questions
)
from src.unga_analysis.config.countries import get_all_countries, detect_country_simple

# Import UI components
from src.unga_analysis.ui.components.upload import upload_section
from src.unga_analysis.ui.components.country_selection import render_country_selection

# Import tabs
from src.unga_analysis.ui.tabs.document_context_analysis_tab import render_document_context_analysis_tab
from src.unga_analysis.ui.tabs.data_explorer_tab import render_data_explorer_tab

# Configure logging
from src.unga_analysis.utils.logging_config import LoggingConfig, get_logger, log_function_call
logging_config = LoggingConfig()
logger = get_logger("main")


# ======================
# OpenAI Client Setup
# ======================

@log_function_call
def get_openai_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Chat Completions API (Analysis)."""
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
    
    if not api_key or not azure_endpoint:
        st.error("Azure OpenAI credentials not configured")
        return None
    
    return AzureOpenAI(api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version)


@log_function_call
def get_whisper_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Whisper API."""
    whisper_api_key = os.getenv('WHISPER_API_KEY')
    whisper_endpoint = os.getenv('WHISPER_ENDPOINT')
    whisper_api_version = os.getenv('WHISPER_API_VERSION', '2024-02-15-preview')
    
    if not whisper_api_key or not whisper_endpoint:
        st.warning("Whisper API not configured - Audio transcription unavailable")
        return None
    
    return AzureOpenAI(api_key=whisper_api_key, azure_endpoint=whisper_endpoint, api_version=whisper_api_version)


# ======================
# Analysis Functions  
# ======================

def process_chat_question(question: str, analysis_context: str, country: str, classification: str, model: str = "model-router-osaa-2"):
    """Process a chat question about the analyzed text."""
    try:
        question = sanitize_input(question)
        
        if not validate_prompt_safety(question):
            return None, "Invalid question - potential security issue detected"
        
        client = get_openai_client()
        if not client:
            return None, "OpenAI client unavailable"
        
        chat_prompt = build_chat_prompt(question, analysis_context, country, classification)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": chat_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content, None
    except Exception as e:
        logger.error(f"Chat question error: {e}")
        return None, str(e)


def process_analysis_with_text(extracted_text, country, speech_date, classification, model):
    """Process analysis with already extracted text."""
    try:
        if not validate_text_length(extracted_text):
            return None
        
        with st.spinner("🔍 Analyzing speech..."):
            output, error = run_analysis(
                extracted_text,
                country,
                speech_date.isoformat() if speech_date else None,
                classification,
                model,
                get_openai_client()
            )
            
            if error:
                st.error(f"Analysis failed: {error}")
                return None
            
            if output:
                sdgs = extract_sdgs(output)
                africa_mentioned = detect_africa_mention(extracted_text)
                
                analysis_id = db_manager.save_analysis(
                    country=country,
                    speech_date=speech_date.isoformat() if speech_date else None,
                    classification=classification,
                    input_text=extracted_text,
                    output_markdown=output,
                    sdgs=sdgs,
                    africa_mentioned=africa_mentioned
                )
                
                st.session_state.current_analysis = {
                    'id': analysis_id,
                    'country': country,
                    'classification': classification,
                    'output': output,
                    'sdgs': sdgs
                }
                
                st.success("✅ Analysis completed!")
                st.markdown(output)
                
                return analysis_id
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        st.error(f"Analysis error: {e}")
        return None


def process_analysis(uploaded_file, pasted_text, country, speech_date, classification, model):
    """Process the analysis."""
    if not uploaded_file and not pasted_text:
        st.error("Please upload a file or paste text to analyze.")
        return None
    
    # Extract text
    try:
        if pasted_text:
            extracted_text = pasted_text
        else:
            client = get_whisper_client() if uploaded_file.name.lower().endswith('.mp3') else get_openai_client()
            extracted_text = extract_text_from_file(uploaded_file.getvalue(), uploaded_file.name, client)
        
        if not extracted_text:
            st.error("Failed to extract text")
            return None
        
        return process_analysis_with_text(extracted_text, country, speech_date, classification, model)
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        st.error(f"Error: {e}")
        return None


# ======================
# Tab Rendering Functions
# ======================

def render_new_analysis_tab():
    """Render the New Analysis tab."""
    st.markdown("### 📝 Please paste your text or upload a file to begin analysis")
    st.markdown("*The system will automatically translate any non-English speech to English using UN terminology.*")
    
    uploaded_file, pasted_text = upload_section()
    
    st.markdown("---")
    st.markdown("### 🌍 Select Country/Entity and Date")
    country, speech_date, classification = render_country_selection()
    
    st.markdown("---")
    if st.button("🚀 Analyze Speech", type="primary", use_container_width=True):
        if country and (uploaded_file or pasted_text):
            model = st.session_state.get('selected_model', 'model-router-osaa-2')
            process_analysis(uploaded_file, pasted_text, country, speech_date, classification, model)
        else:
            st.warning("Please provide both text/file and country selection")


def render_all_analyses_tab():
    """Render the All Analyses tab."""
    st.header("📚 All Analyses")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        country_filter = st.text_input("Filter by Country", placeholder="Enter country name")
    
    with col2:
        classification_filter = st.selectbox(
            "Filter by Classification",
            ["All", "African Member State", "Development Partner"]
        )
    
    with col3:
        africa_filter = st.selectbox("Africa Mentioned", ["All", "Yes", "No"])
    
    with col4:
        search_text = st.text_input("Search in content", placeholder="Search text")
    
    # Build filters
    filters = {}
    if country_filter:
        filters['country'] = country_filter
    if classification_filter != "All":
        filters['classification'] = classification_filter
    if africa_filter != "All":
        filters['africa_mentioned'] = africa_filter == "Yes"
    if search_text:
        filters['search_text'] = search_text
    
    # Get and display analyses
    analyses = db_manager.list_analyses(filters)
    
    if analyses:
        st.subheader(f"Found {len(analyses)} analyses")
        for analysis in analyses:
            with st.expander(f"📄 {analysis['country']} - {analysis['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                st.markdown(analysis['output_markdown'])
                
                if st.button(f"Export", key=f"export_{analysis['id']}"):
                    exports = create_export_files(analysis)
                    st.download_button(
                        label="📄 Download DOCX",
                        data=exports['docx'],
                        file_name=format_filename(analysis, 'docx'),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    else:
        st.info("No analyses found. Create your first analysis in the 'New Analysis' tab.")


def render_cross_year_analysis_tab():
    """Render the cross-year analysis tab."""
    st.header("🌍 Cross-Year Analysis")
    st.markdown("**Advanced analysis across multiple years and countries (1946-2025)**")
    
    if 'cross_year_chat_history' not in st.session_state:
        st.session_state.cross_year_chat_history = []
    
    # Get questions organized by country/group
    country_group_questions = get_country_and_group_questions()
    
    st.info("""
    **📋 Instructions:**
    1. Select Category: Individual Countries or Country Groups
    2. Select Target: Pick countries or a group
    3. Select Question Category
    4. Choose Specific Question
    5. Customize Prompt
    6. Run Analysis
    """)
    
    category_options = list(country_group_questions.keys())
    selected_category = st.radio(
        "Choose analysis category:",
        options=category_options,
        horizontal=True
    )
    
    # Country/Group Selection
    if selected_category == "Individual Countries":
        all_countries = get_all_countries()
        selected_countries = st.multiselect(
            "Choose countries:",
            options=all_countries,
            default=[],
            placeholder="Start typing to search countries..."
        )
        selected_target = ", ".join(selected_countries) if selected_countries else None
    else:
        target_options = list(country_group_questions[selected_category].keys())
        selected_target = st.selectbox(f"Choose {selected_category.lower()}:", options=target_options)
    
    if selected_target:
        # Question selection
        if selected_category == "Individual Countries":
            question_categories = list(country_group_questions[selected_category].keys())
        else:
            question_categories = list(country_group_questions[selected_category][selected_target].keys())
        
        selected_question_category = st.selectbox("Choose a question category:", options=question_categories)
        
        if selected_question_category:
            if selected_category == "Individual Countries":
                questions = country_group_questions[selected_category][selected_question_category]
            else:
                questions = country_group_questions[selected_category][selected_target][selected_question_category]
            
            question_options = [f"{i}. {q}" for i, q in enumerate(questions, 1)]
            selected_question_idx = st.selectbox(
                "Choose a specific question:",
                options=range(len(questions)),
                format_func=lambda x: question_options[x]
            )
            
            selected_question = questions[selected_question_idx]
            
            # Customize prompt
            st.markdown("**Customize the prompt:**")
            customized_prompt = st.text_area(
                "Analysis Prompt:",
                value=selected_question,
                height=150
            )
            
            if st.button("🔍 Analyze", type="primary"):
                if customized_prompt.strip():
                    with st.spinner("Analyzing data across years..."):
                        try:
                            result = cross_year_manager.analyze_cross_year_trends(
                                query=f"Target: {selected_target}\nPrompt: {customized_prompt}",
                                years=list(range(1946, 2026)),
                                regions=[]
                            )
                            
                            if result:
                                st.subheader("📊 Analysis Result")
                                st.markdown(result)
                            else:
                                st.error("❌ Analysis failed")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")


def render_visualizations_tab():
    """Render the dedicated visualizations tab."""
    st.header("📊 Advanced Visualizations")
    st.markdown("**Interactive visualizations for UNGA speech analysis and exploration**")
    
    viz_manager = UNGAVisualizationManager(db_manager)
    viz_manager.render_visualization_menu()


# ======================
# Main Application
# ======================

def main():
    """Main application function."""
    initialize_session_state()
    
    if not check_password():
        show_login_form()
        return
    
    # Initialize database
    try:
        db_manager.create_db_and_tables()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return
    
    # Header with OSAA logo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.image("artifacts/logo/OSAA identifier acronym white.svg", width=150)
    
    with col2:
        st.title("🇺🇳 UN GA Daily Readouts")
        st.markdown("**Production-ready analysis tool for UN General Assembly speeches**")
    
    with col3:
        if st.button("🚪 Logout", help="Logout from the application"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📝 New Analysis", 
        "📚 All Analyses", 
        "🗺️ Data Explorer", 
        "🌍 Cross-Year Analysis", 
        "📊 Visualizations", 
        "📄 Document Context",
        "🔍 Error Insights"
    ])
    
    with tab1:
        render_new_analysis_tab()
    
    with tab2:
        render_all_analyses_tab()
    
    with tab3:
        render_data_explorer_tab()
    
    with tab4:
        render_cross_year_analysis_tab()
    
    with tab5:
        render_visualizations_tab()
    
    with tab6:
        render_document_context_analysis_tab()
    
    with tab7:
        from src.unga_analysis.ui.tabs.error_insights_tab import render_error_insights_tab
        render_error_insights_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built for UN OSAA | "
        "Supports PDF, DOCX, MP3 | "
        "Auto-classifies African Member States vs Development Partners"
    )
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 12px;'>"
        "Developed by: <strong>SMU Data Team</strong>"
        "</div>", 
        unsafe_allow_html=True
    )


def render_error_insights_tab():
    """Render the Error Insights tab."""
    from src.unga_analysis.ui.tabs.error_insights_tab import render_error_insights_tab
    render_error_insights_tab()


if __name__ == "__main__":
    main()


