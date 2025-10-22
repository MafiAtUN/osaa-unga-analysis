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
from src.unga_analysis.core.openai_client import get_openai_client, get_whisper_client
from src.unga_analysis.utils.export_utils import create_export_files, format_filename
from src.unga_analysis.data.data_ingestion import data_ingestion_manager
from src.unga_analysis.data.cross_year_analysis import cross_year_manager
from src.unga_analysis.utils.visualization import UNGAVisualizationManager
from src.unga_analysis.ui.auth_interface import render_auth_interface, is_user_authenticated, get_current_user, logout_user
from src.unga_analysis.core.enhanced_search_engine import get_enhanced_search_engine


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
            # Construct system and user messages
            system_message = f"""You are an expert analyst of UN General Assembly speeches. 
            Analyze the provided speech from {country} and provide insights on:
            - Key themes and topics
            - Policy positions
            - International relations focus
            - Development priorities
            - Regional cooperation
            - Global challenges addressed
            
            Classification: {classification}
            Date: {speech_date.isoformat() if speech_date else 'Not specified'}
            """
            
            user_message = f"""Please analyze this UN General Assembly speech from {country}:

            {extracted_text}
            
            Provide a comprehensive analysis focusing on the key themes, policy positions, and international relations aspects."""
            
            try:
                output = run_analysis(
                    system_message,
                    user_message,
                    model,
                    get_openai_client()
                )
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return None
            
            if output:
                sdgs = extract_sdgs(output)
                africa_mentioned = detect_africa_mention(extracted_text)
                
                # Save analysis to analyses table
                analysis_id = db_manager.save_analysis(
                    country=country,
                    classification=classification,
                    raw_text=extracted_text,
                    output_markdown=output,
                    prompt_used=system_message,
                    sdgs=sdgs,
                    africa_mentioned=africa_mentioned,
                    speech_date=speech_date.isoformat() if speech_date else None
                )
                
                # Also save speech data to speeches table for future reference
                try:
                    # Determine country code and region
                    country_code = country.upper()[:3] if len(country) >= 3 else country.upper()
                    
                    # Better region detection
                    def get_region(country_name):
                        african_countries = [
                            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", 
                            "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
                            "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti",
                            "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
                            "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya",
                            "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
                            "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
                            "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
                            "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
                            "Tunisia", "Uganda", "Zambia", "Zimbabwe"
                        ]
                        
                        asian_countries = [
                            "Afghanistan", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "China",
                            "India", "Indonesia", "Japan", "Kazakhstan", "Kyrgyzstan", "Laos",
                            "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea",
                            "Pakistan", "Philippines", "Singapore", "South Korea", "Sri Lanka",
                            "Tajikistan", "Thailand", "Timor-Leste", "Turkmenistan", "Uzbekistan",
                            "Vietnam"
                        ]
                        
                        european_countries = [
                            "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina",
                            "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                            "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland",
                            "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
                            "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway",
                            "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
                            "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine",
                            "United Kingdom", "Vatican City"
                        ]
                        
                        american_countries = [
                            "Argentina", "Bahamas", "Barbados", "Belize", "Bolivia", "Brazil",
                            "Canada", "Chile", "Colombia", "Costa Rica", "Cuba", "Dominica",
                            "Dominican Republic", "Ecuador", "El Salvador", "Grenada", "Guatemala",
                            "Guyana", "Haiti", "Honduras", "Jamaica", "Mexico", "Nicaragua",
                            "Panama", "Paraguay", "Peru", "Saint Kitts and Nevis", "Saint Lucia",
                            "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago",
                            "United States", "Uruguay", "Venezuela"
                        ]
                        
                        if country_name in african_countries:
                            return "Africa"
                        elif country_name in asian_countries:
                            return "Asia"
                        elif country_name in european_countries:
                            return "Europe"
                        elif country_name in american_countries:
                            return "Americas"
                        else:
                            return "Other"
                    
                    region = get_region(country)
                    
                    # Determine if it's an African Union member (reuse the list from get_region)
                    african_countries = [
                        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", 
                        "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
                        "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti",
                        "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
                        "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya",
                        "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
                        "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
                        "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
                        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
                        "Tunisia", "Uganda", "Zambia", "Zimbabwe"
                    ]
                    is_african_member = country in african_countries
                    
                    # Get session number (approximate based on year)
                    session = speech_date.year - 1945 if speech_date else 2024 - 1945
                    
                    # Save speech to speeches table
                    speech_id = db_manager.save_speech(
                        country_code=country_code,
                        country_name=country,
                        region=region,
                        session=session,
                        year=speech_date.year if speech_date else 2024,
                        speech_text=extracted_text,
                        source_filename=f"analysis_{analysis_id}",
                        is_african_member=is_african_member,
                        metadata={"analysis_id": analysis_id, "classification": classification}
                    )
                    
                    logger.info(f"Saved speech {speech_id} for {country} to speeches table")
                    
                    # Show success message to user
                    st.success(f"💾 **Data saved to database!** Speech for {country} ({region}) is now available for future analysis.")
                    
                except Exception as e:
                    logger.warning(f"Failed to save speech data: {e}")
                    st.warning(f"⚠️ Analysis completed but failed to save speech data: {e}")
                    # Don't fail the analysis if speech saving fails
                
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
    # Initialize session state for authentication
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # Check if user is authenticated
    if not is_user_authenticated():
        render_auth_interface()
        return
    
    # Get current user info
    current_user = get_current_user()
    
    # Display user info in sidebar
    with st.sidebar:
        st.markdown("### 👤 User Information")
        st.markdown(f"**Name:** {current_user.full_name}")
        st.markdown(f"**Title:** {current_user.title}")
        st.markdown(f"**Office:** {current_user.office}")
        st.markdown(f"**Last Login:** {current_user.last_login.strftime('%Y-%m-%d %H:%M') if current_user.last_login else 'First time'}")
        
        if st.button("🚪 Logout"):
            logout_user()
            return
        
        st.markdown("---")
    
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
    
    # Create tabs - add admin tab for islam50@un.org
    if current_user.email == "islam50@un.org":
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "📝 New Analysis", 
            "🌍 Cross-Year Analysis", 
            "📄 Document Context",
            "📚 All Analyses", 
            "📊 Visualizations", 
            "🗺️ Data Explorer", 
            "🗄️ Database Chat",
            "🔍 Error Insights",
            "🛡️ Admin Portal"
        ])
    else:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📝 New Analysis", 
            "🌍 Cross-Year Analysis", 
            "📄 Document Context",
            "📚 All Analyses", 
            "📊 Visualizations", 
            "🗺️ Data Explorer", 
            "🗄️ Database Chat",
            "🔍 Error Insights"
        ])
    
    with tab1:
        render_new_analysis_tab()
    
    with tab2:
        render_cross_year_analysis_tab()
    
    with tab3:
        render_document_context_analysis_tab()
    
    with tab4:
        render_all_analyses_tab()
    
    with tab5:
        render_visualizations_tab()
    
    with tab6:
        render_data_explorer_tab()

    with tab7:
        from src.unga_analysis.ui.tabs.database_chat_tab import render_database_chat_tab
        render_database_chat_tab()

    with tab8:
        from src.unga_analysis.ui.tabs.error_insights_tab import render_error_insights_tab
        render_error_insights_tab()
    
    # Admin tab (only for islam50@un.org)
    if current_user.email == "islam50@un.org":
        with tab9:
            render_admin_tab()
    
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


def render_admin_tab():
    """Render the Admin Portal tab."""
    import sqlite3
    import hashlib
    import os
    from datetime import datetime
    
    st.header("🛡️ Admin Portal")
    st.markdown("**User Management and System Administration**")
    
    # Database connection
    DB_PATH = "user_auth.db"
    
    def get_db_connection():
        return sqlite3.connect(DB_PATH)
    
    def get_all_users():
        """Get all users from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, full_name, title, office, purpose, 
                       status, created_at, approved_at, last_login, login_count
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'email': row[1],
                    'full_name': row[2],
                    'title': row[3],
                    'office': row[4],
                    'purpose': row[5],
                    'status': row[6],
                    'created_at': row[7],
                    'approved_at': row[8],
                    'last_login': row[9],
                    'login_count': row[10]
                })
            
            conn.close()
            return users
        except Exception as e:
            st.error(f"Database error: {e}")
            return []
    
    def get_usage_logs(user_id=None):
        """Get usage logs"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT ul.id, ul.user_id, ul.action, ul.details, ul.timestamp, u.full_name, u.email
                    FROM usage_logs ul
                    JOIN users u ON ul.user_id = u.id
                    WHERE ul.user_id = ?
                    ORDER BY ul.timestamp DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT ul.id, ul.user_id, ul.action, ul.details, ul.timestamp, u.full_name, u.email
                    FROM usage_logs ul
                    JOIN users u ON ul.user_id = u.id
                    ORDER BY ul.timestamp DESC
                """)
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'user_id': row[1],
                    'action': row[2],
                    'details': row[3],
                    'timestamp': row[4],
                    'full_name': row[5],
                    'email': row[6]
                })
            
            conn.close()
            return logs
        except Exception as e:
            st.error(f"Database error: {e}")
            return []
    
    def update_user_status(user_id, status):
        """Update user status"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET status = ?, approved_at = ?, approved_by = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), "admin@unga.org", user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating user status: {e}")
            return False
    
    def delete_user(user_id):
        """Delete user and all related data"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Delete usage logs first
            cursor.execute("DELETE FROM usage_logs WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False
    
    def reset_user_password(user_id, new_password):
        """Reset user password"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hash the new password
            salt = os.urandom(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), salt, 100000)
            password_hash_str = salt.hex() + password_hash.hex()
            
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?
                WHERE id = ?
            """, (password_hash_str, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error resetting password: {e}")
            return False
    
    # Get data
    all_users = get_all_users()
    pending_users = [u for u in all_users if u['status'] == 'pending']
    approved_users = [u for u in all_users if u['status'] == 'approved']
    denied_users = [u for u in all_users if u['status'] == 'denied']
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", len(all_users))
    
    with col2:
        st.metric("⏳ Pending", len(pending_users))
    
    with col3:
        st.metric("✅ Approved", len(approved_users))
    
    with col4:
        st.metric("❌ Denied", len(denied_users))
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Pending Approvals", "All Users", "User Activity", "Password Management"])
    
    with tab1:
        st.markdown("### ⏳ Pending User Approvals")
        
        if not pending_users:
            st.info("No pending user registrations")
        else:
            for user in pending_users:
                with st.expander(f"👤 {user['full_name']} - {user['email']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Name:** {user['full_name']}")
                        st.markdown(f"**Email:** {user['email']}")
                        st.markdown(f"**Title:** {user['title']}")
                        st.markdown(f"**Office:** {user['office']}")
                        st.markdown(f"**Purpose:** {user['purpose']}")
                        st.markdown(f"**Registered:** {user['created_at']}")
                    
                    with col2:
                        if st.button(f"✅ Approve", key=f"approve_{user['id']}"):
                            if update_user_status(user['id'], 'approved'):
                                st.success(f"✅ {user['full_name']} approved!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to approve user")
                        
                        if st.button(f"❌ Deny", key=f"deny_{user['id']}"):
                            if update_user_status(user['id'], 'denied'):
                                st.success(f"❌ {user['full_name']} denied!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to deny user")
    
    with tab2:
        st.markdown("### 👥 All Users Management")
        
        if not all_users:
            st.info("No users registered")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.selectbox("Filter by Status:", ["All", "Pending", "Approved", "Denied"])
            
            with col2:
                search_term = st.text_input("Search by name or email:")
            
            # Filter users
            filtered_users = all_users
            if status_filter != "All":
                filtered_users = [u for u in filtered_users if u['status'] == status_filter.lower()]
            
            if search_term:
                filtered_users = [u for u in filtered_users if 
                                 search_term.lower() in u['full_name'].lower() or 
                                 search_term.lower() in u['email'].lower()]
            
            # Display users
            for user in filtered_users:
                status_color = {
                    'pending': '🟡',
                    'approved': '🟢',
                    'denied': '🔴'
                }
                
                with st.expander(f"{status_color.get(user['status'], '⚪')} {user['full_name']} - {user['email']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Status:** {user['status'].title()}")
                        st.markdown(f"**Title:** {user['title']}")
                        st.markdown(f"**Office:** {user['office']}")
                        st.markdown(f"**Purpose:** {user['purpose']}")
                        st.markdown(f"**Registered:** {user['created_at']}")
                        if user['approved_at']:
                            st.markdown(f"**Approved:** {user['approved_at']}")
                        if user['last_login']:
                            st.markdown(f"**Last Login:** {user['last_login']}")
                        st.markdown(f"**Login Count:** {user['login_count']}")
                    
                    with col2:
                        # Action buttons
                        if user['status'] == 'pending':
                            if st.button(f"✅ Approve", key=f"approve_all_{user['id']}"):
                                if update_user_status(user['id'], 'approved'):
                                    st.success("User approved!")
                                    st.rerun()
                        
                        if st.button(f"🗑️ Delete User", key=f"delete_{user['id']}"):
                            if delete_user(user['id']):
                                st.success("User deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete user")
    
    with tab3:
        st.markdown("### 📊 User Activity & Usage Analytics")
        
        # User selection
        user_options = {f"{u['full_name']} ({u['email']})": u['id'] for u in approved_users}
        
        if user_options:
            selected_user_name = st.selectbox("Select User:", list(user_options.keys()))
            
            if selected_user_name:
                user_id = user_options[selected_user_name]
                user = next(u for u in approved_users if u['id'] == user_id)
                
                # Get usage logs for this user
                logs = get_usage_logs(user_id)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Activities", len(logs))
                
                with col2:
                    login_count = user['login_count']
                    st.metric("Login Count", login_count)
                
                with col3:
                    last_login = user['last_login'] if user['last_login'] else 'Never'
                    st.metric("Last Login", last_login)
                
                # Recent activities
                st.markdown("#### Recent Activities")
                if logs:
                    for log in logs[:20]:  # Show last 20 activities
                        st.markdown(f"**{log['action']}** - {log['timestamp']} - {log['details']}")
                else:
                    st.info("No activities recorded for this user")
        else:
            st.info("No approved users to analyze")
    
    with tab4:
        st.markdown("### 🔐 Password Management")
        
        if not all_users:
            st.info("No users to manage")
        else:
            # User selection for password reset
            user_options = {f"{u['full_name']} ({u['email']})": u['id'] for u in all_users}
            selected_user_name = st.selectbox("Select User for Password Reset:", list(user_options.keys()))
            
            if selected_user_name:
                user_id = user_options[selected_user_name]
                user = next(u for u in all_users if u['id'] == user_id)
                
                st.markdown(f"**Resetting password for:** {user['full_name']} ({user['email']})")
                
                new_password = st.text_input("New Password:", type="password")
                confirm_password = st.text_input("Confirm Password:", type="password")
                
                if st.button("🔐 Reset Password"):
                    if not new_password:
                        st.error("Please enter a new password")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        if reset_user_password(user_id, new_password):
                            st.success(f"✅ Password reset successfully for {user['full_name']}")
                            st.info(f"📧 New password: {new_password}")
                        else:
                            st.error("❌ Failed to reset password")


if __name__ == "__main__":
    main()


