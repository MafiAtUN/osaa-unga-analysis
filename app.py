"""
UN GA Daily Readouts - Streamlit App
Production-ready app for analyzing UN General Assembly speeches
"""

import os
import logging
import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our modules
from prompts import SYSTEM_MESSAGE, build_user_prompt, get_question_set
from classify import infer_classification, get_au_members
from ingest import extract_text_from_file, validate_text_length
from llm import run_analysis, get_available_models, OpenAIError
from storage import db_manager
from sdg_utils import extract_sdgs, detect_africa_mention, format_sdgs
from export_utils import create_export_files, format_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="UN GA Daily Readouts",
    page_icon="🇺🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

def get_openai_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client with API key and endpoint from environment or settings."""
    api_key = os.getenv('AZURE_OPENAI_API_KEY') or st.session_state.get('azure_openai_api_key')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT') or st.session_state.get('azure_openai_endpoint')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    
    if api_key and azure_endpoint:
        return AzureOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key
        )
    return None

def sidebar_upload_section():
    """Render the sidebar upload section."""
    st.sidebar.header("📁 Upload Document")
    
    # File uploader
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'mp3'],
        help="Upload a PDF, Word document, or MP3 audio file"
    )
    
    # Text input fallback
    st.sidebar.header("📝 Or Paste Text")
    pasted_text = st.sidebar.text_area(
        "Paste transcript here",
        height=100,
        help="Alternative to file upload - paste the speech text directly"
    )
    
    return uploaded_file, pasted_text

def sidebar_metadata_section():
    """Render the sidebar metadata section."""
    st.sidebar.header("📋 Metadata")
    
    # Country/Entity input
    country = st.sidebar.text_input(
        "Country/Entity",
        help="Name of the country or entity giving the speech"
    )
    
    # Speech date
    speech_date = st.sidebar.date_input(
        "Speech Date (Optional)",
        value=None,
        help="Date when the speech was given"
    )
    
    # Classification (auto-detected with override)
    if country:
        auto_classification = infer_classification(country)
        st.sidebar.info(f"Auto-detected: {auto_classification}")
        
        classification_options = ["African Member State", "Development Partner"]
        default_index = 0 if auto_classification == "African Member State" else 1
        
        classification = st.sidebar.radio(
            "Classification",
            classification_options,
            index=default_index,
            help="Override the auto-detected classification if needed"
        )
    else:
        classification = st.sidebar.radio(
            "Classification",
            ["African Member State", "Development Partner"],
            help="Select the classification for this analysis"
        )
    
    return country, speech_date, classification

def sidebar_model_section():
    """Render the sidebar model selection section."""
    st.sidebar.header("🤖 AI Model")
    
    available_models = get_available_models()
    default_model = "model-router-osaa" if "model-router-osaa" in available_models else available_models[0]
    
    model = st.sidebar.selectbox(
        "Select Model",
        available_models,
        index=available_models.index(default_model),
        help="Choose the OpenAI model for analysis"
    )
    
    return model

def process_analysis(uploaded_file, pasted_text, country, speech_date, 
                    classification, model):
    """Process the analysis."""
    if not uploaded_file and not pasted_text:
        st.error("Please upload a file or paste text to analyze.")
        return None
    
    if not country:
        st.error("Please specify the country/entity name.")
        return None
    
    client = get_openai_client()
    if not client:
        st.error("Azure OpenAI configuration not found. Please set API key and endpoint in Settings.")
        return None
    
    try:
        with st.spinner("Processing analysis..."):
            # Extract text
            if uploaded_file:
                file_bytes = uploaded_file.getvalue()
                filename = uploaded_file.name
                
                # Show processing steps
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Extracting text from file...")
                progress_bar.progress(20)
                
                raw_text = extract_text_from_file(file_bytes, filename, client)
                
                status_text.text("Analyzing with AI...")
                progress_bar.progress(60)
            else:
                raw_text = pasted_text
                filename = None
            
            # Validate text length
            if not validate_text_length(raw_text):
                st.warning("Text is very long. This may take several minutes and cost more.")
            
            # Build prompt
            question_set = get_question_set(classification)
            user_prompt = build_user_prompt(
                raw_text, classification, country, 
                speech_date.strftime('%Y-%m-%d') if speech_date else None,
                question_set
            )
            
            # Run analysis
            status_text.text("Generating analysis...")
            progress_bar.progress(80)
            
            output = run_analysis(
                SYSTEM_MESSAGE, 
                user_prompt, 
                model, 
                client
            )
            
            status_text.text("Saving analysis...")
            progress_bar.progress(95)
            
            # Extract SDGs and Africa mention
            sdgs = extract_sdgs(output)
            africa_mentioned = detect_africa_mention(output)
            
            # Save to database
            analysis_id = db_manager.save_analysis(
                country=country,
                classification=classification,
                raw_text=raw_text,
                output_markdown=output,
                prompt_used=user_prompt,
                sdgs=sdgs,
                africa_mentioned=africa_mentioned,
                speech_date=speech_date.strftime('%Y-%m-%d') if speech_date else None,
                source_filename=filename
            )
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Store in session state
            st.session_state.current_analysis = {
                'id': analysis_id,
                'country': country,
                'classification': classification,
                'speech_date': speech_date.strftime('%Y-%m-%d') if speech_date else None,
                'created_at': datetime.now(),
                'sdgs': sdgs,
                'africa_mentioned': africa_mentioned,
                'source_filename': filename,
                'raw_text': raw_text,
                'prompt_used': user_prompt,
                'output_markdown': output
            }
            
            st.session_state.analysis_count += 1
            
            return analysis_id
            
    except OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        logger.error(f"Analysis failed: {e}")
        return None

def render_new_analysis_tab():
    """Render the New Analysis tab."""
    st.header("🆕 New Analysis")
    
    # Sidebar sections
    uploaded_file, pasted_text = sidebar_upload_section()
    country, speech_date, classification = sidebar_metadata_section()
    model = sidebar_model_section()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show extracted text preview
        if uploaded_file or pasted_text:
            st.subheader("📄 Text Preview")
            
            if uploaded_file:
                st.info(f"File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Show text preview
            text_to_preview = pasted_text if pasted_text else ""
            if uploaded_file and not pasted_text:
                try:
                    client = get_openai_client()
                    if client:
                        text_to_preview = extract_text_from_file(
                            uploaded_file.getvalue(), 
                            uploaded_file.name, 
                            client
                        )
                except Exception as e:
                    if "whisper" in str(e).lower() or "audio" in str(e).lower():
                        st.warning(f"⚠️ Audio transcription not available: {e}")
                        st.info("💡 **Tip**: You can still analyze the audio by pasting the transcript text manually in the text area below.")
                    else:
                        st.warning(f"Could not preview file content: {e}")
            
            if text_to_preview:
                with st.expander("Show extracted text", expanded=False):
                    st.text_area(
                        "Extracted Text",
                        text_to_preview[:2000] + "..." if len(text_to_preview) > 2000 else text_to_preview,
                        height=200,
                        disabled=True
                    )
        
        # Analyze button
        if st.button("🚀 Analyze Speech", type="primary", use_container_width=True):
            if uploaded_file or pasted_text:
                if country:
                    analysis_id = process_analysis(
                        uploaded_file, pasted_text, country, 
                        speech_date, classification, model
                    )
                    
                    if analysis_id:
                        st.success(f"Analysis completed! ID: {analysis_id}")
                        st.rerun()
                else:
                    st.error("Please specify the country/entity name.")
            else:
                st.error("Please upload a file or paste text to analyze.")
    
    with col2:
        # Show analysis metadata
        st.subheader("📊 Analysis Info")
        
        if country:
            st.metric("Country/Entity", country)
            st.metric("Classification", classification)
            
            if speech_date:
                st.metric("Speech Date", speech_date.strftime('%Y-%m-%d'))
            
            st.metric("Model", model)
            
            # Show AU members if African
            if classification == "African Member State":
                au_members = get_au_members()
                if country in au_members:
                    st.success("✅ Confirmed AU Member")
                else:
                    st.warning("⚠️ Not in AU member list")

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
        africa_filter = st.selectbox(
            "Africa Mentioned (Partners only)",
            ["All", "Yes", "No"]
        )
    
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
    
    # Get analyses
    analyses = db_manager.list_analyses(filters)
    
    if analyses:
        st.subheader(f"Found {len(analyses)} analyses")
        
        # Display analyses in a table
        for analysis in analyses:
            with st.expander(f"📄 {analysis['country']} - {analysis['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Classification:** {analysis['classification']}")
                    st.write(f"**SDGs:** {format_sdgs(analysis['sdgs'])}")
                
                with col2:
                    st.write(f"**Date:** {analysis['created_at'].strftime('%Y-%m-%d')}")
                    if analysis['classification'] == 'Development Partner':
                        st.write(f"**Africa Mentioned:** {'Yes' if analysis['africa_mentioned'] else 'No'}")
                
                with col3:
                    if st.button(f"View Full Analysis", key=f"view_{analysis['id']}"):
                        st.session_state.viewing_analysis = analysis['id']
                        st.rerun()
                    
                    if st.button(f"Export", key=f"export_{analysis['id']}"):
                        st.session_state.exporting_analysis = analysis['id']
                        st.rerun()
        
        # Handle viewing analysis
        if 'viewing_analysis' in st.session_state:
            analysis_id = st.session_state.viewing_analysis
            analysis = db_manager.get_analysis(analysis_id)
            
            if analysis:
                st.subheader(f"📖 Analysis: {analysis['country']}")
                
                # Show analysis content
                st.markdown(analysis['output_markdown'])
                
                # Show metadata
                with st.expander("Show Analysis Details"):
                    st.json(analysis)
                
                # Show prompt used
                with st.expander("Show Prompt Used"):
                    st.code(analysis['prompt_used'], language='text')
                
                if st.button("Close Analysis"):
                    del st.session_state.viewing_analysis
                    st.rerun()
        
        # Handle export
        if 'exporting_analysis' in st.session_state:
            analysis_id = st.session_state.exporting_analysis
            analysis = db_manager.get_analysis(analysis_id)
            
            if analysis:
                try:
                    exports = create_export_files(analysis)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        docx_filename = format_filename(analysis, 'docx')
                        st.download_button(
                            label="📄 Download DOCX",
                            data=exports['docx'],
                            file_name=docx_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    with col2:
                        md_filename = format_filename(analysis, 'md')
                        st.download_button(
                            label="📝 Download Markdown",
                            data=exports['md'],
                            file_name=md_filename,
                            mime="text/markdown"
                        )
                    
                    if st.button("Close Export"):
                        del st.session_state.exporting_analysis
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Export failed: {e}")
    
    else:
        st.info("No analyses found. Create your first analysis in the 'New Analysis' tab.")

def render_settings_tab():
    """Render the Settings tab."""
    st.header("⚙️ Settings")
    
    # Azure OpenAI Configuration
    st.subheader("🔑 Azure OpenAI Configuration")
    
    current_key = os.getenv('AZURE_OPENAI_API_KEY', '')
    current_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    
    if current_key and current_endpoint:
        st.success("✅ Azure OpenAI configuration found in environment variables")
        
        # Show minimal information for security
        st.info("🔒 **API Key**: Configured and secure")
        st.info(f"🌐 **Endpoint**: {current_endpoint}")
        
        # Security note
        st.warning("🔒 **Security**: API keys are stored securely in environment variables and are not exposed in the code or GitHub repository.")
    else:
        st.warning("⚠️ Azure OpenAI configuration not found in environment variables")
        
        col1, col2 = st.columns(2)
        
        with col1:
            api_key = st.text_input(
                "Azure OpenAI API Key",
                type="password",
                help="Your Azure OpenAI API key (stored in session only)"
            )
            if api_key:
                st.session_state.azure_openai_api_key = api_key
        
        with col2:
            endpoint = st.text_input(
                "Azure OpenAI Endpoint",
                placeholder="https://your-resource.cognitiveservices.azure.com/",
                help="Your Azure OpenAI endpoint URL"
            )
            if endpoint:
                st.session_state.azure_openai_endpoint = endpoint
        
        if api_key and endpoint:
            st.success("✅ Azure OpenAI configuration set for this session")
    
    # Azure Deployment Notes
    st.subheader("☁️ Azure Deployment")
    
    with st.expander("Azure App Service Deployment Instructions"):
        st.markdown("""
        ### Deploying to Azure App Service
        
        1. **Set Environment Variables:**
           - In Azure Portal, go to your App Service
           - Navigate to Configuration > Application settings
           - Add: `AZURE_OPENAI_API_KEY` = your Azure OpenAI API key
           - Add: `AZURE_OPENAI_ENDPOINT` = your Azure OpenAI endpoint URL
           - Add: `AZURE_OPENAI_API_VERSION` = 2024-12-01-preview (optional)
        
        2. **Deployment Options:**
           - **Option A:** Deploy via Git
             ```bash
             git add .
             git commit -m "Deploy UN GA app"
             git push azure main
             ```
           
           - **Option B:** Deploy via ZIP
             - Create a ZIP of all files
             - Upload via Azure Portal
        
        3. **Startup Command:**
           ```
           streamlit run app.py --server.port $PORT --server.address 0.0.0.0
           ```
        
        4. **Requirements:**
           - Python 3.11+ runtime
           - All dependencies in requirements.txt will be installed automatically
        
        5. **Audio Processing:**
           - For MP3 transcription, Azure OpenAI Whisper API is used (no local ffmpeg required)
           - If using local audio processing, add ffmpeg buildpack
        
        6. **Database:**
           - SQLite database file will be created automatically
           - For production, consider Azure Database for PostgreSQL
        """)
    
    # Statistics
    st.subheader("📊 Database Statistics")
    
    try:
        stats = db_manager.get_statistics()
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Analyses", stats.get('total_analyses', 0))
            
            with col2:
                st.metric("African Analyses", stats.get('african_analyses', 0))
            
            with col3:
                st.metric("Partner Analyses", stats.get('partner_analyses', 0))
            
            with col4:
                st.metric("Unique Countries", stats.get('unique_countries', 0))
        else:
            st.info("No statistics available")
            
    except Exception as e:
        st.error(f"Could not load statistics: {e}")

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Initialize database
    try:
        db_manager.create_db_and_tables()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return
    
    # App title and description
    st.title("🇺🇳 UN GA Daily Readouts")
    st.markdown("**Production-ready analysis tool for UN General Assembly speeches**")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🆕 New Analysis", "📚 All Analyses", "⚙️ Settings"])
    
    with tab1:
        render_new_analysis_tab()
    
    with tab2:
        render_all_analyses_tab()
    
    with tab3:
        render_settings_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built for UN OSAA | "
        "Supports PDF, DOCX, MP3 | "
        "Auto-classifies African Member States vs Development Partners"
    )

if __name__ == "__main__":
    main()
