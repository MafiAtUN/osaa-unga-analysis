"""
UN GA Daily Readouts - Streamlit App
Production-ready app for analyzing UN General Assembly speeches

Developed by: SMU Data Team
"""

import os
import logging
import random
import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv
import requests
import json

# Load environment variables from .env file
load_dotenv()

# Import our modules
from prompts import SYSTEM_MESSAGE, build_user_prompt, get_question_set, build_chat_prompt
from corpus_integration import corpus_manager
from classify import infer_classification, get_au_members
from ingest import extract_text_from_file, validate_text_length
from llm import run_analysis, get_available_models, OpenAIError, chunk_and_synthesize
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
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'proceed_to_analysis' not in st.session_state:
        st.session_state.proceed_to_analysis = False
    if 'load_text_clicked' not in st.session_state:
        st.session_state.load_text_clicked = False
    if 'stored_text' not in st.session_state:
        st.session_state.stored_text = None
    if 'stored_file' not in st.session_state:
        st.session_state.stored_file = None
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    
    # Clear auto-detection data on fresh start
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        # Clear any previous auto-detection data
        if 'auto_detected_country' in st.session_state:
            del st.session_state.auto_detected_country
        if 'auto_detected_classification' in st.session_state:
            del st.session_state.auto_detected_classification
        if 'last_uploaded_file' in st.session_state:
            del st.session_state.last_uploaded_file
        if 'last_pasted_text' in st.session_state:
            del st.session_state.last_pasted_text
        if 'edit_country' in st.session_state:
            del st.session_state.edit_country

def check_password():
    """Check if user has entered the correct password."""
    return st.session_state.authenticated

def show_login_form():
    """Display the login form."""
    # Header with OSAA logo
    col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
    
    with col_header2:
        st.image("artifacts/logo/OSAA identifier acronym white.svg", width=200)
        st.title("🔐 UN GA Daily Readouts - Authentication Required")
        st.markdown("**Internal tool for UN OSAA Intergovernmental Support Team**")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please enter the password to access the application")
        
        password = st.text_input(
            "Password:",
            type="password",
            placeholder="Enter password",
            help="Enter the application password to continue"
        )
        
        col_login, col_clear = st.columns(2)
        
        with col_login:
            if st.button("🚀 Login", type="primary", use_container_width=True):
                # Get password from environment variable
                app_password = os.getenv('APP_PASSWORD')
                if not app_password:
                    st.error("❌ Application password not configured. Please set APP_PASSWORD environment variable.")
                elif password == app_password:
                    st.session_state.authenticated = True
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
        
        with col_clear:
            if st.button("🔄 Clear", use_container_width=True):
                st.rerun()
        
        # Help text
        st.info("💡 This is an internal tool created for UN OSAA Intergovernmental Support Team to analyze General Assembly speeches. Internal limited use only. If you do not have credentials, please reach out to UN OSAA IGS team.")
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 12px;'>"
            "Built for UN OSAA | Developed by: <strong>SMU Data Team</strong>"
            "</div>", 
            unsafe_allow_html=True
        )

def get_openai_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Chat Completions API (Analysis)."""
    # Use the correct analysis endpoint
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

def get_whisper_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client for Whisper API."""
    # Use the Whisper API configuration
    whisper_api_key = os.getenv('WHISPER_API_KEY')
    whisper_endpoint = os.getenv('WHISPER_ENDPOINT')
    whisper_api_version = os.getenv('WHISPER_API_VERSION', '2024-06-01')
    
    if whisper_api_key and whisper_endpoint:
        return AzureOpenAI(
            api_version=whisper_api_version,
            azure_endpoint=whisper_endpoint,
            api_key=whisper_api_key
        )
    return None

def upload_section():
    """Render the upload section."""
    # Text input first
    st.markdown("#### 📝 Paste Text")
    pasted_text = st.text_area(
        "Paste transcript here",
        height=100,
        help="Paste the speech text directly (will be automatically translated to English if needed)"
    )
    
    # File uploader (second option)
    st.markdown("#### 📁 Or Upload File")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'mp3'],
        help="Upload a PDF, Word document, or MP3 audio file"
    )
    
    return uploaded_file, pasted_text

def detect_country_simple(text: str) -> str:
    """
    Simple keyword-based country detection.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected country name or None
    """
    text_lower = text.lower()
    
    # Common country keywords and their full names
    country_keywords = {
        'kenya': 'Kenya',
        'nigeria': 'Nigeria', 
        'south africa': 'South Africa',
        'ethiopia': 'Ethiopia',
        'egypt': 'Egypt',
        'ghana': 'Ghana',
        'tanzania': 'Tanzania',
        'uganda': 'Uganda',
        'morocco': 'Morocco',
        'algeria': 'Algeria',
        'tunisia': 'Tunisia',
        'libya': 'Libya',
        'sudan': 'Sudan',
        'cameroon': 'Cameroon',
        'ivory coast': 'Côte d\'Ivoire',
        'cote d\'ivoire': 'Côte d\'Ivoire',
        'senegal': 'Senegal',
        'mali': 'Mali',
        'burkina faso': 'Burkina Faso',
        'niger': 'Niger',
        'chad': 'Chad',
        'central african republic': 'Central African Republic',
        'democratic republic of congo': 'Democratic Republic of Congo',
        'congo': 'Republic of Congo',
        'gabon': 'Gabon',
        'equatorial guinea': 'Equatorial Guinea',
        'sao tome': 'São Tomé and Príncipe',
        'angola': 'Angola',
        'zambia': 'Zambia',
        'zimbabwe': 'Zimbabwe',
        'botswana': 'Botswana',
        'namibia': 'Namibia',
        'lesotho': 'Lesotho',
        'swaziland': 'Swaziland',
        'madagascar': 'Madagascar',
        'mauritius': 'Mauritius',
        'seychelles': 'Seychelles',
        'comoros': 'Comoros',
        'djibouti': 'Djibouti',
        'somalia': 'Somalia',
        'eritrea': 'Eritrea',
        'rwanda': 'Rwanda',
        'burundi': 'Burundi',
        'malawi': 'Malawi',
        'mozambique': 'Mozambique',
        'cape verde': 'Cape Verde',
        'guinea-bissau': 'Guinea-Bissau',
        'guinea': 'Guinea',
        'sierra leone': 'Sierra Leone',
        'liberia': 'Liberia',
        'gambia': 'Gambia',
        'mauritania': 'Mauritania',
        'benin': 'Benin',
        'togo': 'Togo',
        'united states': 'United States',
        'usa': 'United States',
        'america': 'United States',
        'united kingdom': 'United Kingdom',
        'uk': 'United Kingdom',
        'britain': 'United Kingdom',
        'france': 'France',
        'germany': 'Germany',
        'japan': 'Japan',
        'canada': 'Canada',
        'australia': 'Australia',
        'china': 'China',
        'india': 'India',
        'russia': 'Russia',
        'brazil': 'Brazil',
        'argentina': 'Argentina',
        'chile': 'Chile',
        'mexico': 'Mexico',
        'colombia': 'Colombia',
        'peru': 'Peru',
        'venezuela': 'Venezuela',
        'ecuador': 'Ecuador',
        'uruguay': 'Uruguay',
        'paraguay': 'Paraguay',
        'bolivia': 'Bolivia',
        'guyana': 'Guyana',
        'suriname': 'Suriname',
        'thailand': 'Thailand',
        'malaysia': 'Malaysia',
        'indonesia': 'Indonesia',
        'philippines': 'Philippines',
        'vietnam': 'Vietnam',
        'bangladesh': 'Bangladesh',
        'pakistan': 'Pakistan',
        'sri lanka': 'Sri Lanka',
        'nepal': 'Nepal',
        'bhutan': 'Bhutan',
        'maldives': 'Maldives',
        'afghanistan': 'Afghanistan',
        'iran': 'Iran',
        'iraq': 'Iraq',
        'syria': 'Syria',
        'lebanon': 'Lebanon',
        'jordan': 'Jordan',
        'palestine': 'Palestine',
        'israel': 'Israel',
        'saudi arabia': 'Saudi Arabia',
        'united arab emirates': 'United Arab Emirates',
        'uae': 'United Arab Emirates',
        'qatar': 'Qatar',
        'kuwait': 'Kuwait',
        'bahrain': 'Bahrain',
        'turkey': 'Turkey',
        'greece': 'Greece',
        'cyprus': 'Cyprus',
        'malta': 'Malta',
        'iceland': 'Iceland',
        'norway': 'Norway',
        'sweden': 'Sweden',
        'denmark': 'Denmark',
        'finland': 'Finland',
        'poland': 'Poland',
        'czech republic': 'Czech Republic',
        'slovakia': 'Slovakia',
        'hungary': 'Hungary',
        'romania': 'Romania',
        'bulgaria': 'Bulgaria',
        'croatia': 'Croatia',
        'slovenia': 'Slovenia',
        'bosnia': 'Bosnia and Herzegovina',
        'serbia': 'Serbia',
        'montenegro': 'Montenegro',
        'north macedonia': 'North Macedonia',
        'albania': 'Albania',
        'kosovo': 'Kosovo',
        'moldova': 'Moldova',
        'ukraine': 'Ukraine',
        'belarus': 'Belarus',
        'lithuania': 'Lithuania',
        'latvia': 'Latvia',
        'estonia': 'Estonia',
        'kazakhstan': 'Kazakhstan',
        'uzbekistan': 'Uzbekistan',
        'kyrgyzstan': 'Kyrgyzstan',
        'tajikistan': 'Tajikistan',
        'turkmenistan': 'Turkmenistan',
        'azerbaijan': 'Azerbaijan',
        'armenia': 'Armenia',
        'georgia': 'Georgia',
        'mongolia': 'Mongolia',
        'north korea': 'North Korea',
        'south korea': 'South Korea',
        'taiwan': 'Taiwan',
        'hong kong': 'Hong Kong',
        'singapore': 'Singapore',
        'brunei': 'Brunei',
        'timor-leste': 'Timor-Leste',
        'fiji': 'Fiji',
        'papua new guinea': 'Papua New Guinea',
        'solomon islands': 'Solomon Islands',
        'vanuatu': 'Vanuatu',
        'samoa': 'Samoa',
        'tonga': 'Tonga',
        'kiribati': 'Kiribati',
        'tuvalu': 'Tuvalu',
        'nauru': 'Nauru',
        'palau': 'Palau',
        'marshall islands': 'Marshall Islands',
        'micronesia': 'Micronesia',
        'cuba': 'Cuba',
        'haiti': 'Haiti',
        'dominican republic': 'Dominican Republic',
        'jamaica': 'Jamaica',
        'trinidad and tobago': 'Trinidad and Tobago',
        'barbados': 'Barbados',
        'saint lucia': 'Saint Lucia',
        'saint vincent': 'Saint Vincent and the Grenadines',
        'grenada': 'Grenada',
        'antigua': 'Antigua and Barbuda',
        'saint kitts': 'Saint Kitts and Nevis',
        'dominica': 'Dominica',
        'belize': 'Belize',
        'costa rica': 'Costa Rica',
        'panama': 'Panama',
        'nicaragua': 'Nicaragua',
        'honduras': 'Honduras',
        'el salvador': 'El Salvador',
        'guatemala': 'Guatemala'
    }
    
    # Look for country keywords in the text
    for keyword, country_name in country_keywords.items():
        if keyword in text_lower:
            return country_name
    
    return None


def sidebar_metadata_section(uploaded_file=None, pasted_text=None):
    """Render the sidebar metadata section."""
    st.sidebar.header("📋 Metadata")
    
    # Only show metadata section if there's content to analyze
    if not uploaded_file and not pasted_text:
        st.sidebar.info("👆 Upload a file or paste text to begin analysis")
        return None, None, None
    
    # Country/Entity input with searchable dropdown
    st.sidebar.subheader("🌍 Country/Entity Selection")
    
    # Get comprehensive list of all world countries and entities
    all_countries = [
        # African Countries (AU Members)
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", 
        "Central African Republic", "Chad", "Comoros", "Democratic Republic of the Congo", "Republic of the Congo",
        "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia",
        "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
        "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia",
        "Niger", "Nigeria", "Rwanda", "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda",
        "Zambia", "Zimbabwe",
        
        # North America
        "United States", "Canada", "Mexico", "Guatemala", "Belize", "El Salvador", "Honduras", "Nicaragua",
        "Costa Rica", "Panama", "Cuba", "Jamaica", "Haiti", "Dominican Republic", "Trinidad and Tobago",
        "Barbados", "Saint Lucia", "Grenada", "Saint Vincent and the Grenadines", "Antigua and Barbuda",
        "Dominica", "Saint Kitts and Nevis", "Bahamas",
        
        # South America
        "Brazil", "Argentina", "Chile", "Colombia", "Peru", "Venezuela", "Ecuador", "Bolivia", "Paraguay",
        "Uruguay", "Guyana", "Suriname", "French Guiana",
        
        # Europe
        "United Kingdom", "France", "Germany", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland",
        "Austria", "Sweden", "Norway", "Denmark", "Finland", "Poland", "Czech Republic", "Slovakia",
        "Hungary", "Romania", "Bulgaria", "Croatia", "Slovenia", "Estonia", "Latvia", "Lithuania",
        "Portugal", "Greece", "Ireland", "Luxembourg", "Malta", "Cyprus", "Iceland", "Liechtenstein",
        "Monaco", "San Marino", "Vatican City", "Andorra", "Albania", "Bosnia and Herzegovina", "Montenegro",
        "North Macedonia", "Serbia", "Kosovo", "Moldova", "Ukraine", "Belarus", "Russia",
        
        # Asia
        "China", "Japan", "South Korea", "North Korea", "Mongolia", "India", "Pakistan", "Bangladesh",
        "Sri Lanka", "Nepal", "Bhutan", "Afghanistan", "Kazakhstan", "Kyrgyzstan", "Tajikistan",
        "Turkmenistan", "Uzbekistan", "Iran", "Iraq", "Turkey", "Syria", "Lebanon", "Jordan", "Israel",
        "Palestine", "Saudi Arabia", "United Arab Emirates", "Qatar", "Bahrain", "Kuwait", "Oman",
        "Yemen", "Thailand", "Vietnam", "Laos", "Cambodia", "Myanmar", "Malaysia", "Singapore",
        "Indonesia", "Philippines", "Brunei", "East Timor", "Taiwan", "Hong Kong", "Macau",
        
        # Oceania
        "Australia", "New Zealand", "Papua New Guinea", "Fiji", "Solomon Islands", "Vanuatu", "Samoa",
        "Tonga", "Kiribati", "Tuvalu", "Nauru", "Palau", "Marshall Islands", "Micronesia",
        
        # International Organizations and Entities
        "UN Secretary-General", "President of the General Assembly", "European Union", "African Union",
        "Organization of Islamic Cooperation", "Non-Aligned Movement", "G77", "Group of 20", "BRICS",
        "OECD", "World Bank", "International Monetary Fund", "World Health Organization",
        "United Nations Development Programme", "United Nations Children's Fund", "World Food Programme",
        "United Nations Educational, Scientific and Cultural Organization", "International Labour Organization",
        "International Atomic Energy Agency", "World Trade Organization", "North Atlantic Treaty Organization",
        "Association of Southeast Asian Nations", "Caribbean Community", "Pacific Islands Forum",
        "Arab League", "Gulf Cooperation Council", "Shanghai Cooperation Organization"
    ]
    
    # Sort countries alphabetically
    all_countries = sorted(list(set(all_countries)))
    
    # Search functionality
    search_term = st.sidebar.text_input(
        "🔍 Search for country/entity",
        placeholder="Type a few letters to search...",
        help="Start typing to filter the list below"
    )
    
    # Filter countries based on search
    if search_term:
        filtered_countries = [c for c in all_countries if search_term.lower() in c.lower()]
    else:
        filtered_countries = all_countries[:20]  # Show first 20 by default
    
    # Searchable dropdown
    if filtered_countries:
        country = st.sidebar.selectbox(
            "Select Country/Entity",
            options=[""] + filtered_countries,
            help=f"Found {len(filtered_countries)} matches. Select one or type more to refine search."
        )
    else:
        st.sidebar.warning("No countries found matching your search.")
        country = ""
    
    # Alternative: Allow manual input if not found in list
    if country == "":
        country = st.text_input(
            "Or enter custom country/entity name",
            help="If your country/entity is not in the list above, enter it here"
        )
    
    # Auto-detect if it's an African Member State
    if country:
        is_african_member = country in get_au_members()
        classification = "African Member State" if is_african_member else "Development Partner"
        
        # Show classification
        if is_african_member:
            st.sidebar.success(f"✅ **{country}** is an African Member State")
        else:
            st.sidebar.info(f"ℹ️ **{country}** is classified as a Development Partner")
    else:
        classification = None
    
    # Speech date
    speech_date = st.sidebar.date_input(
        "Speech Date (Optional)",
        value=None,
        help="Date when the speech was given"
        )
    
    return country, speech_date, classification

    """Render the sidebar model selection section."""
    st.sidebar.header("🤖 AI Model")
    
    # Only show model selection if there's content to analyze
    if not uploaded_file and not pasted_text:
        return None
    
    available_models = get_available_models()
    default_model = "model-router-osaa-2" if "model-router-osaa-2" in available_models else "gpt-4" if "gpt-4" in available_models else available_models[0]
    
    model = st.sidebar.selectbox(
        "Select Model",
        available_models,
        index=available_models.index(default_model),
        help="Choose the OpenAI model for analysis"
    )
    
    return model

def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web for relevant information."""
    try:
        # Use DuckDuckGo search API (free and no API key required)
        search_url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Extract relevant results
            for result in data.get('results', [])[:max_results]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('text', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Also try to get related topics
            for topic in data.get('related_topics', [])[:max_results]:
                if isinstance(topic, dict) and 'text' in topic:
                    results.append({
                        'title': topic.get('text', ''),
                        'url': topic.get('url', ''),
                        'snippet': topic.get('text', ''),
                        'source': 'DuckDuckGo Related'
                    })
            
            return results
        else:
            return []
            
    except Exception as e:
        logging.error(f"Web search failed: {e}")
        return []

def search_past_speeches(country: str, year: int = None) -> List[Dict[str, str]]:
    """Search for past speeches by the country."""
    if year is None:
        year = datetime.now().year - 1
    
    # Create search queries for past speeches
    queries = [
        f'"{country}" "UN General Assembly" speech {year}',
        f'"{country}" "General Debate" {year} transcript',
        f'"{country}" "UNGA" {year} statement',
        f'"{country}" "United Nations" speech {year}',
        f'"{country}" "General Assembly" {year} address'
    ]
    
    all_results = []
    for query in queries:
        results = search_web(query, max_results=3)
        all_results.extend(results)
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result['url'] not in seen_urls:
            seen_urls.add(result['url'])
            unique_results.append(result)
    
    return unique_results[:10]  # Return top 10 unique results

def get_suggestion_questions(country: str, classification: str) -> list:
    """Get compelling suggestion questions based on country and classification."""
    
    # Base questions for all countries
    base_questions = [
        # Multi-year analysis questions (prioritized)
        "Compare this speech with their speeches from the past 5 years",
        "What trends can be observed in this country's UNGA statements over time?",
        "How has their focus on climate change evolved in recent years?",
        "What changes in their diplomatic priorities can be seen compared to previous sessions?",
        "How has their approach to international cooperation changed from previous years?",
        "What new themes or priorities emerged compared to past speeches?",
        "How has this country's position evolved since their previous UNGA speech?",
        "What are the priorities and key topics discussed compared to last year's speech?",
        "Analyze the evolution of this country's stance on global governance over the past decade",
        "How has their emphasis on sustainable development changed since 2015?",
        "What patterns can be identified in their UNGA speeches from 2010-2024?",
        "Compare their current priorities with speeches from the 1990s and 2000s",
        "How has their approach to multilateralism evolved since the Cold War era?",
        "What continuity and change can be observed in their diplomatic language over 20 years?",
        "How has their focus on peace and security issues shifted since the 1990s?",
        "What generational changes in leadership priorities are reflected in their speeches?",
        "How has their engagement with global challenges evolved since the Millennium Development Goals?",
        "What historical context from their past speeches helps explain current positions?",
        "How has their relationship with international organizations changed over time?",
        "What long-term trends in their foreign policy can be identified from UNGA speeches?",
        # Current analysis questions
        "What specific SDGs were mentioned in this speech?",
        "What were the main challenges discussed for achieving sustainable development?",
        "What partnerships or collaborations were proposed?",
        "How did they address climate change and environmental issues?",
        "What role did they see for multilateralism and international cooperation?",
        "How did they discuss youth empowerment and inclusion?",
        "What were their views on digital transformation and AI?",
        "How did they address gender equality and women's empowerment?"
    ]
    
    # African Member State specific questions
    if classification == "African Member State":
        african_questions = [
            "How did they discuss Agenda 2063 and African integration?",
            "What specific African development priorities were highlighted?",
            "How did they address peace and security in Africa?",
            "What role did they see for the African Union?",
            "How did they discuss debt relief and financial support for Africa?",
            "What were their views on African youth and education?",
            "How did they address food security and agricultural development?",
            "What partnerships did they propose with other African countries?"
        ]
        return base_questions + african_questions
    
    # Development Partner specific questions
    else:
        partner_questions = [
            "How did they address their commitment to Africa's development?",
            "What specific support did they offer to African countries?",
            "How did they discuss their partnership with African institutions?",
            "What role did they see for international cooperation in Africa?",
            "How did they address global inequality and development gaps?",
            "What were their views on South-South cooperation?",
            "How did they discuss technology transfer to developing countries?",
            "What commitments did they make to support the SDGs in Africa?"
        ]
        return base_questions + partner_questions

def process_chat_question(question: str, analysis_context: str, country: str, classification: str, model: str = "model-router-osaa-2"):
    """Process a chat question about the analyzed text."""
    try:
        # Check if question requires historical analysis (comparison questions)
        historical_data = ""
        if any(keyword in question.lower() for keyword in ['compare', 'compared to', 'last year', 'previous', 'past', 'evolution', 'change', 'historical', 'trend']):
            with st.spinner("📚 Searching historical UNGA speeches..."):
                # Get historical speeches from corpus
                historical_speeches = corpus_manager.get_recent_speeches(country, num_years=5)
                
                if historical_speeches:
                    historical_data = "\n\nHISTORICAL UNGA SPEECHES FOR COMPARISON:\n"
                    historical_data += f"Found {len(historical_speeches)} historical speeches for {country}:\n\n"
                    
                    for i, speech in enumerate(historical_speeches[:3], 1):  # Show top 3
                        historical_data += f"{i}. {speech['year']} (Session {speech['session']}):\n"
                        historical_data += f"   Word Count: {speech['word_count']:,}\n"
                        historical_data += f"   Content Preview: {speech['content'][:400]}...\n\n"
                    
                    historical_data += "Use this historical data to provide comprehensive comparative analysis."
                else:
                    # Fallback to web search if no corpus data
                    past_speeches = search_past_speeches(country)
                    if past_speeches:
                        historical_data = "\n\nADDITIONAL WEB SEARCH RESULTS:\n"
                        historical_data += "The following information was found about past speeches by this country:\n\n"
                        
                        for i, speech in enumerate(past_speeches[:5], 1):
                            historical_data += f"{i}. {speech['title']}\n"
                            historical_data += f"   URL: {speech['url']}\n"
                            historical_data += f"   Summary: {speech['snippet'][:200]}...\n\n"
        
        # Build chat prompt with historical data
        chat_prompt = build_chat_prompt(question, analysis_context, country, classification, historical_data)
        
        # Get OpenAI client
        client = get_openai_client()
        if not client:
            return None, "OpenAI client not available."
        
        # Run chat analysis
        response = run_analysis(
            "You are a UN OSAA expert assistant. Provide detailed, expert responses based on the analysis context. Use UN terminology and diplomatic language. Be precise and factual.",
            chat_prompt,
            model=model,
            client=client
        )
        
        return response, None
        
    except Exception as e:
        return None, f"Chat processing failed: {e}"

def process_analysis_with_text(extracted_text, country, speech_date, classification, model):
    """Process analysis with already extracted text."""
    try:
        # Validate text length
        if not validate_text_length(extracted_text):
            st.warning("Text is very long. This may take several minutes and cost more.")
        
        # Build prompt
        question_set = get_question_set(classification)
        user_prompt = build_user_prompt(
            extracted_text, classification, country, 
            speech_date.strftime('%Y-%m-%d') if speech_date else None,
            question_set
        )
        
        # Run analysis
        with st.spinner("🧠 AI is analyzing your speech..."):
            client = get_openai_client()
            if not client:
                st.error("❌ OpenAI client not available.")
                return None
            
            response = run_analysis(
                SYSTEM_MESSAGE, 
                user_prompt, 
                model=model,
                client=client
            )
        
        if response:
            # Save to database
            analysis_id = db_manager.save_analysis(
                country=country,
                classification=classification,
                speech_date=speech_date.strftime('%Y-%m-%d') if speech_date else None,
                raw_text=extracted_text,
                output_markdown=response,
                prompt_used=user_prompt
            )
            return analysis_id
        else:
            st.error("❌ Analysis failed.")
            return None
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        return None

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
                
                # Enhanced messages for audio processing
                fun_messages = [
                    "🎤 Converting audio to text... (This may take 30-60 seconds)",
                    "🤖 AI Whisper is listening carefully to every word...",
                    "📝 Transforming sound waves into beautiful text...",
                    "🎧 Processing your speech with advanced AI...",
                    "⚡ Converting audio to text... (Almost there!)",
                    "🔊 AI is analyzing your speech patterns...",
                    "📄 Turning sound into sentences...",
                    "🎵 From audio to alphabet... (This is music to our AI's ears!)",
                    "🧠 AI is understanding your speech context...",
                    "✨ Creating a perfect transcript for you...",
                    "🎯 AI is processing your audio with precision...",
                    "🔍 Whisper AI is working its magic on your speech..."
                ]
                
                import random
                import time
                
                # Show initial message
                fun_message = random.choice(fun_messages)
                status_text.text(fun_message)
                progress_bar.progress(10)
                
                # Show progress updates
                for i in range(2):
                    time.sleep(0.3)
                    fun_message = random.choice(fun_messages)
                    status_text.text(fun_message)
                    progress_bar.progress(20 + (i * 30))
                
                # Use appropriate client based on file type
                if filename.lower().endswith('.mp3'):
                    whisper_client = get_whisper_client()
                    raw_text = extract_text_from_file(file_bytes, filename, whisper_client)
                else:
                    raw_text = extract_text_from_file(file_bytes, filename, client)
                
                # Fun messages for AI analysis
                analysis_messages = [
                    "🧠 Our AI is thinking deeply about your speech...",
                    "🤔 Analyzing every word for UN insights...",
                    "📊 The AI is connecting the dots...",
                    "🔍 Searching for SDGs and partnerships...",
                    "💭 AI is pondering the deeper meaning...",
                    "🎯 Focusing on key themes and messages...",
                    "📈 Building a comprehensive analysis...",
                    "🌟 Creating UN-style readouts with AI magic..."
                ]
                
                analysis_message = random.choice(analysis_messages)
                status_text.text(analysis_message)
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
            final_messages = [
                "✨ Generating your personalized UN readout...",
                "📋 Creating a masterpiece of analysis...",
                "🎨 Painting a picture with words and insights...",
                "🏆 Crafting the perfect UN-style summary...",
                "📝 Writing your custom readout...",
                "🌟 Polishing the final analysis...",
                "🎯 Perfecting every detail...",
                "💎 Creating a gem of an analysis..."
            ]
            
            final_message = random.choice(final_messages)
            status_text.text(final_message)
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
            
            # Fun completion messages
            completion_messages = [
                "🎉 Analysis complete! Your UN readout is ready!",
                "✨ Ta-da! Your personalized analysis is here!",
                "🏆 Mission accomplished! Check out your readout!",
                "🌟 Voilà! Your UN-style analysis is ready!",
                "🎯 Perfect! Your analysis is complete!",
                "💎 Your gem of an analysis is ready!",
                "🚀 Success! Your readout has landed!",
                "🎊 Congratulations! Your analysis is done!"
            ]
            
            completion_message = random.choice(completion_messages)
            status_text.text(completion_message)
            
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

def render_country_selection():
    """Render country selection section."""
    # Get comprehensive list of all world countries and entities
    all_countries = [
        # African Countries (AU Members)
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", 
        "Central African Republic", "Chad", "Comoros", "Democratic Republic of the Congo", "Republic of the Congo",
        "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia",
        "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
        "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia",
        "Niger", "Nigeria", "Rwanda", "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda",
        "Zambia", "Zimbabwe",
        
        # North America
        "United States", "Canada", "Mexico", "Guatemala", "Belize", "El Salvador", "Honduras", "Nicaragua",
        "Costa Rica", "Panama", "Cuba", "Jamaica", "Haiti", "Dominican Republic", "Trinidad and Tobago",
        "Barbados", "Saint Lucia", "Grenada", "Saint Vincent and the Grenadines", "Antigua and Barbuda",
        "Dominica", "Saint Kitts and Nevis", "Bahamas",
        
        # South America
        "Brazil", "Argentina", "Chile", "Colombia", "Peru", "Venezuela", "Ecuador", "Bolivia", "Paraguay",
        "Uruguay", "Guyana", "Suriname", "French Guiana",
        
        # Europe
        "United Kingdom", "France", "Germany", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland",
        "Austria", "Sweden", "Norway", "Denmark", "Finland", "Poland", "Czech Republic", "Slovakia",
        "Hungary", "Romania", "Bulgaria", "Croatia", "Slovenia", "Estonia", "Latvia", "Lithuania",
        "Portugal", "Greece", "Ireland", "Luxembourg", "Malta", "Cyprus", "Iceland", "Liechtenstein",
        "Monaco", "San Marino", "Vatican City", "Andorra", "Albania", "Bosnia and Herzegovina", "Montenegro",
        "North Macedonia", "Serbia", "Kosovo", "Moldova", "Ukraine", "Belarus", "Russia",
        
        # Asia
        "China", "Japan", "South Korea", "North Korea", "Mongolia", "India", "Pakistan", "Bangladesh",
        "Sri Lanka", "Nepal", "Bhutan", "Afghanistan", "Kazakhstan", "Kyrgyzstan", "Tajikistan",
        "Turkmenistan", "Uzbekistan", "Iran", "Iraq", "Turkey", "Syria", "Lebanon", "Jordan", "Israel",
        "Palestine", "Saudi Arabia", "United Arab Emirates", "Qatar", "Bahrain", "Kuwait", "Oman",
        "Yemen", "Thailand", "Vietnam", "Laos", "Cambodia", "Myanmar", "Malaysia", "Singapore",
        "Indonesia", "Philippines", "Brunei", "East Timor", "Taiwan", "Hong Kong", "Macau",
        
        # Oceania
        "Australia", "New Zealand", "Papua New Guinea", "Fiji", "Solomon Islands", "Vanuatu", "Samoa",
        "Tonga", "Kiribati", "Tuvalu", "Nauru", "Palau", "Marshall Islands", "Micronesia",
        
        # International Organizations and Entities
        "UN Secretary-General", "President of the General Assembly", "European Union", "African Union",
        "Organization of Islamic Cooperation", "Non-Aligned Movement", "G77", "Group of 20", "BRICS",
        "OECD", "World Bank", "International Monetary Fund", "World Health Organization",
        "United Nations Development Programme", "United Nations Children's Fund", "World Food Programme",
        "United Nations Educational, Scientific and Cultural Organization", "International Labour Organization",
        "International Atomic Energy Agency", "World Trade Organization", "North Atlantic Treaty Organization",
        "Association of Southeast Asian Nations", "Caribbean Community", "Pacific Islands Forum",
        "Arab League", "Gulf Cooperation Council", "Shanghai Cooperation Organization"
    ]
    
    # Sort countries alphabetically
    all_countries = sorted(list(set(all_countries)))
    
    # Simple dropdown with all countries
    country = st.selectbox(
        "Select Country/Entity",
        options=[""] + all_countries,
        help="Choose from the complete list of countries and entities"
    )
    
    # Auto-detect if it's an African Member State
    if country:
        is_african_member = country in get_au_members()
        classification = "African Member State" if is_african_member else "Development Partner"
        
        # Show classification
        if is_african_member:
            st.success(f"✅ **{country}** is an African Member State")
        else:
            st.info(f"ℹ️ **{country}** is classified as a Development Partner")
    else:
        classification = None
    
    # Speech date
    speech_date = st.date_input(
        "Speech Date (Optional)",
        value=None,
        help="Date when the speech was given"
    )
    
    return country, speech_date, classification

def process_and_show_text(uploaded_file, pasted_text, show_ui=True):
    """Process uploaded file and show extracted text."""
    # Check if we already have extracted text in session state
    if 'extracted_text' in st.session_state and st.session_state.extracted_text:
        text_to_preview = st.session_state.extracted_text
        if show_ui:
            st.info("📄 Using previously extracted text")
    else:
        # Clear any previous extracted text if we have a new file
        if 'extracted_text' in st.session_state:
            del st.session_state.extracted_text
        text_to_preview = pasted_text if pasted_text else ""
        
        # Set flag for auto-scroll if pasted text is provided
        if pasted_text and pasted_text.strip():
            st.session_state.text_ready_for_scroll = True
            if show_ui:
                st.rerun()
        
        if uploaded_file:
            if show_ui:
                st.info(f"File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Process the file
            try:
                client = get_openai_client()
                if client:
                    # Use appropriate client based on file type
                    if uploaded_file.name.lower().endswith('.mp3'):
                        # Show comprehensive audio processing message
                        if show_ui:
                            # Create a more detailed loading experience for audio
                            progress_container = st.container()
                            with progress_container:
                                st.info("🎤 **Audio File Detected** - Processing with AI Whisper...")
                                
                                # Progress bar and status
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                # Fun loading messages for audio processing
                                audio_messages = [
                                    "🎤 Converting audio to text... (This may take 30-60 seconds)",
                                    "🤖 AI Whisper is listening carefully to every word...",
                                    "📝 Transforming sound waves into beautiful text...",
                                    "🎧 Processing your speech with advanced AI...",
                                    "⚡ Converting audio to text... (Almost there!)",
                                    "🔊 AI is analyzing your speech patterns...",
                                    "📄 Turning sound into sentences...",
                                    "🎵 From audio to alphabet... (This is music to our AI's ears!)",
                                    "🧠 AI is understanding your speech context...",
                                    "✨ Creating a perfect transcript for you..."
                                ]
                                
                                import random
                                import time
                                
                                # Show initial message
                                status_text.text(random.choice(audio_messages))
                                progress_bar.progress(10)
                                
                                # Simulate progress updates
                                for i in range(3):
                                    time.sleep(0.5)
                                    status_text.text(random.choice(audio_messages))
                                    progress_bar.progress(20 + (i * 20))
                                
                                # Final processing message
                                status_text.text("🎯 Finalizing transcription...")
                                progress_bar.progress(90)
                            
                            # Actually process the audio
                            whisper_client = get_whisper_client()
                            text_to_preview = extract_text_from_file(
                                uploaded_file.getvalue(), 
                                uploaded_file.name, 
                                whisper_client
                            )
                            
                            # Complete the progress
                            progress_bar.progress(100)
                            status_text.text("✅ Audio transcription completed!")
                            
                        else:
                            whisper_client = get_whisper_client()
                            text_to_preview = extract_text_from_file(
                                uploaded_file.getvalue(), 
                                uploaded_file.name, 
                                whisper_client
                            )
                    else:
                        # Add loading UI for PDF and Word documents
                        if show_ui:
                            file_type = "PDF" if uploaded_file.name.lower().endswith('.pdf') else "Word Document"
                            st.info(f"📄 **{file_type} Detected** - Extracting text...")
                            
                            # Create loading spinner
                            with st.spinner(f"📖 Reading {file_type.lower()} content... (This may take a few seconds)"):
                                text_to_preview = extract_text_from_file(
                                    uploaded_file.getvalue(), 
                                    uploaded_file.name, 
                                    client
                                )
                        else:
                            text_to_preview = extract_text_from_file(
                                uploaded_file.getvalue(), 
                                uploaded_file.name, 
                                client
                            )
                    
                    if text_to_preview:
                        if show_ui:
                            st.success("✅ Text extracted successfully!")
                        # Store in session state to avoid re-extraction
                        st.session_state.extracted_text = text_to_preview
                        # Set flag to trigger auto-scroll and rerun
                        st.session_state.text_ready_for_scroll = True
                        if show_ui:
                            st.rerun()
                    else:
                        if show_ui:
                            st.error("❌ Failed to extract text from file.")
                else:
                    if show_ui:
                        st.error("❌ OpenAI client not available.")
            except Exception as e:
                if show_ui:
                    if "whisper" in str(e).lower() or "audio" in str(e).lower():
                        st.error("🎤 **Audio Transcription Failed**")
                        st.warning(f"⚠️ Audio transcription not available: {e}")
                        st.info("💡 **Tip**: You can still analyze the audio by pasting the transcript text manually in the text area below.")
                        st.info("🔧 **Alternative**: Try uploading a different audio format or check your Azure OpenAI Whisper configuration.")
                    else:
                        st.warning(f"Could not preview file content: {e}")
    
    if text_to_preview and show_ui:
        # Auto-scroll to text preview section when text is ready
        if st.session_state.get('text_ready_for_scroll', False):
            # Check if this was an audio file for special message
            if uploaded_file and uploaded_file.name.lower().endswith('.mp3'):
                st.success("🎉 **Audio Successfully Transcribed!** Your speech has been converted to text.")
            else:
                st.success("✅ Text extracted successfully! Please scroll down to see the text preview below.")
            st.info("📄 **Text Preview Section** - Your extracted text is displayed below. You can now proceed to the analysis step.")
            
            # Reset the flag
            st.session_state.text_ready_for_scroll = False
        
        # Show extracted text with clear instructions
        st.markdown("### 📄 Extracted Text Preview (English)")
        st.markdown("*Review the extracted text below. The system automatically translates any non-English speech to English using UN terminology.*")
        
        # Add a prominent proceed button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Proceed to Analysis", type="primary", help="Click to proceed to the analysis step"):
                st.session_state.proceed_to_analysis = True
                st.rerun()
        
        st.text_area(
            "Extracted Text (English)",
            text_to_preview,
            height=300,
            disabled=True,
            help="Full transcribed text from the file (automatically translated to English if needed)",
            key="extracted_text_preview_old"
        )
        
        # Clear session button for debugging
        if st.button("🔄 Clear Extracted Text", help="Clear the extracted text and start over"):
            if 'extracted_text' in st.session_state:
                del st.session_state.extracted_text
            st.rerun()
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as TXT
            st.download_button(
                label="📄 Download as TXT",
                data=text_to_preview,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download as plain text file",
                key="download_txt_old"
            )
        
        with col2:
            # Download as DOCX
            try:
                from export_utils import create_docx_from_text
                docx_content = create_docx_from_text(text_to_preview, "Audio Transcript")
                st.download_button(
                    label="📝 Download as DOCX",
                    data=docx_content,
                    file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    help="Download as Microsoft Word document",
                    key="download_docx_old"
                )
            except Exception as e:
                st.error(f"DOCX export not available: {e}")
        
        with col3:
            # Download as ODT (OpenDocument)
            try:
                from export_utils import create_odt_from_text
                odt_content = create_odt_from_text(text_to_preview, "Audio Transcript")
                st.download_button(
                    label="📄 Download as ODT",
                    data=odt_content,
                    file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.odt",
                    mime="application/vnd.oasis.opendocument.text",
                    help="Download as OpenDocument Text (LibreOffice/OpenOffice)",
                    key="download_odt_old"
                )
            except Exception as e:
                st.error(f"ODT export not available: {e}")
    
    return text_to_preview

def render_analysis_section(country, speech_date, classification, uploaded_file, pasted_text, text_to_preview):
    """Render the analysis section."""
    # Analyze button
    if st.button("🚀 Analyze Speech", type="primary", use_container_width=True):
        if country:
            analysis_id = process_analysis_with_text(
                text_to_preview, country, 
                speech_date, classification, "model-router-osaa-2"
            )
            
            if analysis_id:
                st.success(f"Analysis completed! ID: {analysis_id}")
                # Store analysis ID in session state for display
                st.session_state.current_analysis_id = analysis_id
                st.rerun()
        else:
            st.error("Please specify the country/entity name.")
    
    # Display analysis results if available
    if hasattr(st.session_state, 'current_analysis_id') and st.session_state.current_analysis_id:
        st.subheader("📋 Analysis Results")
        try:
            # Get the analysis from database
            analysis = db_manager.get_analysis(st.session_state.current_analysis_id)
            if analysis:
                st.success(f"✅ Analysis ID: {analysis['id']}")
                st.write(f"**Country:** {analysis['country']}")
                st.write(f"**Classification:** {analysis['classification']}")
                st.write(f"**Date:** {analysis['speech_date']}")
                
                # Display the structured readout with question headlines
                if analysis.get('structured_readout'):
                    st.subheader("📊 Analysis Results")
                    
                    # Parse and display with question headlines
                    analysis_text = analysis['structured_readout']
                    
                    # Split by numbered sections (1., 2., 3., etc.)
                    import re
                    sections = re.split(r'\n(?=\d+\.)', analysis_text)
                    
                    for i, section in enumerate(sections):
                        if section.strip():
                            # Extract the question headline (first line)
                            lines = section.strip().split('\n')
                            if lines:
                                headline = lines[0].strip()
                                content = '\n'.join(lines[1:]).strip()
                                
                                # Use different formatting for section 1 vs others
                                if i == 0:  # First section (Summary) - 3 bullet points
                                    # Display headline as a larger subheader
                                    st.markdown(f"**{headline}**")
                                    # Display content as bullet points
                                    if content:
                                        st.markdown(content)
                                else:  # Sections 2-5 - single paragraph with question heading
                                    # Display headline as a smaller subheader
                                    st.markdown(f"**{headline}**")
                                    # Display content as smaller text
                                    if content:
                                        st.markdown(f"<div style='font-size: 14px; line-height: 1.4;'>{content}</div>", unsafe_allow_html=True)
                                
                                st.write("---")  # Separator between sections
                
                # Chat with Analysis Section
                st.subheader("💬 Chat with Analysis")
                st.info("📚 **Historical Access**: This app has access to all UNGA speeches from 1946 to 2024, enabling comprehensive comparative analysis across nearly eight decades of diplomatic history.")
                st.markdown("Ask questions about the analyzed speech to get more detailed insights.")
                
                # Initialize chat history in session state
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                
                # Initialize selected question in session state
                if 'selected_question' not in st.session_state:
                    st.session_state.selected_question = ""
                
                # Suggestion Questions Section
                st.markdown("### 💡 Suggested Questions")
                
                # Get suggestion questions based on country and classification
                suggestion_questions = get_suggestion_questions(analysis['country'], analysis['classification'])
                
                # Create dropdown for suggested questions
                st.markdown("**💡 Choose a suggested question or write your own:**")
                
                selected_suggestion = st.selectbox(
                    "Select a suggested question:",
                    options=[""] + suggestion_questions,
                    help="Choose a question from the list or write your own below",
                    key="suggestion_dropdown_main"
                )
                
                # Button to ask the selected question
                col_suggest, col_custom = st.columns([1, 1])
                
                with col_suggest:
                    if st.button("🤖 Ask Selected Question", type="primary", use_container_width=True, disabled=not selected_suggestion):
                        if selected_suggestion:
                            # Process the selected question directly
                            with st.spinner("🧠 AI is thinking about your question..."):
                                # Get the full analysis context
                                analysis_context = analysis['output_markdown']
                                
                                # Process the selected question
                                chat_response, error = process_chat_question(
                                    selected_suggestion, 
                                    analysis_context, 
                                    analysis['country'], 
                                    analysis['classification']
                                )
                                
                                if chat_response:
                                    # Add to chat history
                                    st.session_state.chat_history.append({
                                        'question': selected_suggestion,
                                        'answer': chat_response,
                                        'timestamp': datetime.now().strftime('%H:%M:%S')
                                    })
                                    st.success("✅ Response generated!")
                                    
                                    # Show the answer immediately
                                    st.markdown("### 🤖 AI Response")
                                    st.markdown(chat_response)
                                    
                                    # Clear the selected question
                                    st.session_state.selected_question = ""
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {error}")
                
                with col_custom:
                    st.markdown("**Or write your own question:**")
                
                # Chat input for custom questions
                chat_question = st.text_area(
                    "Write your own question:",
                    value=st.session_state.get('selected_question', ''),
                    placeholder="Type your question here...",
                    height=100,
                    help="Write any question about the analysis",
                    key="chat_input_main"
                )
                
                col_chat, col_clear = st.columns([3, 1])
                
                with col_chat:
                    if st.button("🤖 Ask Question", type="primary", use_container_width=True):
                        if chat_question.strip():
                            # Clear selected question after use
                            if st.session_state.get('selected_question'):
                                st.session_state.selected_question = ""
                            
                            with st.spinner("🧠 AI is thinking about your question..."):
                                # Get the full analysis context
                                analysis_context = analysis['output_markdown']
                                
                                # Process the chat question
                                chat_response, error = process_chat_question(
                                    chat_question, 
                                    analysis_context, 
                                    analysis['country'], 
                                    analysis['classification']
                                )
                                
                                if chat_response:
                                    # Add to chat history
                                    st.session_state.chat_history.append({
                                        'question': chat_question,
                                        'answer': chat_response,
                                        'timestamp': datetime.now().strftime('%H:%M:%S')
                                    })
                                    st.success("✅ Response generated!")
                                    
                                    # Show the answer immediately
                                    st.subheader("🤖 AI Response")
                                    st.markdown(chat_response)
                                    st.markdown("---")
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ {error}")
                        else:
                            st.warning("Please enter a question.")
                
                with col_clear:
                    if st.button("🗑️ Clear Chat", use_container_width=True):
                        st.session_state.chat_history = []
                        st.rerun()
                
                # Display chat history
                if st.session_state.chat_history:
                    st.subheader("📝 Chat History")
                    for i, chat in enumerate(st.session_state.chat_history):
                        with st.expander(f"Q{i+1}: {chat['question'][:50]}... ({chat['timestamp']})"):
                            st.markdown(f"**Question:** {chat['question']}")
                            st.markdown(f"**Answer:** {chat['answer']}")
            else:
                st.error("Analysis not found in database.")
        except Exception as e:
            st.error(f"Error loading analysis: {e}")

def render_new_analysis_tab():
    """Render the New Analysis tab."""
    
    # Nice welcoming message
    st.markdown("### 📝 Please paste your text or upload a file to begin analysis")
    st.markdown("*The system will automatically translate any non-English speech to English using UN terminology.*")
    
    # Text input and file upload
    uploaded_file, pasted_text = upload_section()
    
    # Country and date selection (always visible)
    st.markdown("---")
    st.markdown("### 🌍 Select Country/Entity and Date")
    country, speech_date, classification = render_country_selection()
    
    # Load Text button - always show it
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Load Text", type="primary", help="Click to process and display the text"):
            # Store the text in session state
            if pasted_text:
                st.session_state.stored_text = pasted_text
                st.success("✅ Text stored!")
            elif uploaded_file:
                # Show immediate feedback for file processing
                file_extension = uploaded_file.name.lower().split('.')[-1]
                if file_extension in ['mp3', 'wav', 'm4a']:
                    st.info("🎤 **Audio file detected** - Starting transcription process...")
                elif file_extension == 'pdf':
                    st.info("📄 **PDF file detected** - Extracting text content...")
                elif file_extension in ['docx', 'doc']:
                    st.info("📝 **Word document detected** - Reading document content...")
                else:
                    st.info(f"📁 **{file_extension.upper()} file detected** - Processing content...")
                
                st.session_state.stored_file = uploaded_file
                st.success("✅ File stored!")
            else:
                st.warning("⚠️ Please paste text or upload a file first!")
                return
            st.session_state.load_text_clicked = True
            st.rerun()
    
    
    # Show text preview and download options when Load Text is clicked
    if st.session_state.get('load_text_clicked', False):
        # Get the text to display from session state
        if 'stored_text' in st.session_state and st.session_state.stored_text:
            text_to_preview = st.session_state.stored_text
        elif 'stored_file' in st.session_state and st.session_state.stored_file:
            text_to_preview = process_and_show_text(st.session_state.stored_file, None, show_ui=False)
        else:
            text_to_preview = None
        
        if text_to_preview:
            st.markdown("---")
            st.markdown("### 📄 English Text Preview")
            st.markdown("*The system automatically translates any non-English speech to English using UN terminology.*")
            
            # Show text in a nice window
            st.text_area(
                "Extracted Text (English)",
                text_to_preview,
                height=300,
                disabled=True,
                help="Full transcribed text (automatically translated to English if needed)",
                key="extracted_text_preview_new"
            )
            
            # Download options
            st.markdown("#### 📥 Download Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download as TXT
                st.download_button(
                    label="📄 Download as TXT",
                    data=text_to_preview,
                    file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download as plain text file",
                    key="download_txt_new"
                )
            
            with col2:
                # Download as DOCX
                try:
                    from docx import Document
                    doc = Document()
                    doc.add_paragraph(text_to_preview)
                    
                    # Save to bytes
                    import io
                    doc_bytes = io.BytesIO()
                    doc.save(doc_bytes)
                    doc_bytes.seek(0)
                    
                    st.download_button(
                        label="📝 Download as DOCX",
                        data=doc_bytes.getvalue(),
                        file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        help="Download as Word document",
                        key="download_docx_new"
                    )
                except ImportError:
                    st.info("📝 DOCX download not available")
            
            with col3:
                # Download as Markdown
                markdown_content = f"# Speech Transcript\n\n{text_to_preview}"
                st.download_button(
                    label="📋 Download as Markdown",
                    data=markdown_content,
                    file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Download as Markdown file",
                    key="download_md_new"
                )
            
            # Show analysis results immediately after text is loaded
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            # Use stored file/text for analysis
            stored_file = st.session_state.get('stored_file', None)
            stored_text = st.session_state.get('stored_text', None)
            render_analysis_section(country, speech_date, classification, stored_file, stored_text, text_to_preview)
        else:
            st.warning("⚠️ No text available. Please paste text or upload a file first.")

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
                
                # Chat with Analysis Section
                st.subheader("💬 Chat with Analysis")
                st.info("📚 **Historical Access**: This app has access to all UNGA speeches from 1946 to 2024, enabling comprehensive comparative analysis across nearly eight decades of diplomatic history.")
                st.markdown("Ask questions about this analyzed speech to get more detailed insights.")
                
                # Initialize chat history for this analysis
                chat_key = f"chat_history_{analysis_id}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = []
                
                # Initialize selected question for this analysis
                selected_question_key = f"selected_question_{analysis_id}"
                if selected_question_key not in st.session_state:
                    st.session_state[selected_question_key] = ""
                
                # Suggestion Questions Section
                st.markdown("### 💡 Suggested Questions")
                
                # Get suggestion questions based on country and classification
                suggestion_questions = get_suggestion_questions(analysis['country'], analysis['classification'])
                
                # Create dropdown for suggested questions
                st.markdown("**💡 Choose a suggested question or write your own:**")
                
                selected_suggestion = st.selectbox(
                    "Select a suggested question:",
                    options=[""] + suggestion_questions,
                    help="Choose a question from the list or write your own below",
                    key=f"suggestion_dropdown_{analysis_id}"
                )
                
                # Button to ask the selected question
                col_suggest, col_custom = st.columns([1, 1])
                
                with col_suggest:
                    if st.button("🤖 Ask Selected Question", type="primary", use_container_width=True, disabled=not selected_suggestion, key=f"ask_selected_{analysis_id}"):
                        if selected_suggestion:
                            # Process the selected question directly
                            with st.spinner("🧠 AI is thinking about your question..."):
                                # Get the full analysis context
                                analysis_context = analysis['output_markdown']
                                
                                # Process the selected question
                                chat_response, error = process_chat_question(
                                    selected_suggestion, 
                                    analysis_context, 
                                    analysis['country'], 
                                    analysis['classification']
                                )
                                
                                if chat_response:
                                    # Add to chat history
                                    st.session_state[chat_key].append({
                                        'question': selected_suggestion,
                                        'answer': chat_response,
                                        'timestamp': datetime.now().strftime('%H:%M:%S')
                                    })
                                    st.success("✅ Response generated!")
                                    
                                    # Show the answer immediately
                                    st.markdown("### 🤖 AI Response")
                                    st.markdown(chat_response)
                                    
                                    # Clear the selected question
                                    st.session_state[selected_question_key] = ""
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {error}")
                
                with col_custom:
                    st.markdown("**Or write your own question:**")
                
                # Chat input for custom questions
                chat_question = st.text_area(
                    "Write your own question:",
                    value=st.session_state.get(selected_question_key, ''),
                    placeholder="Type your question here...",
                    height=100,
                    help="Write any question about the analysis",
                    key=f"chat_input_{analysis_id}"
                )
                
                col_chat, col_clear = st.columns([3, 1])
                
                with col_chat:
                    if st.button("🤖 Ask Question", type="primary", use_container_width=True, key=f"ask_btn_{analysis_id}"):
                        if chat_question.strip():
                            # Clear selected question after use
                            if st.session_state[selected_question_key]:
                                st.session_state[selected_question_key] = ""
                            
                            with st.spinner("🧠 AI is thinking about your question..."):
                                # Get the full analysis context
                                analysis_context = analysis['output_markdown']
                                
                                # Process the chat question
                                chat_response, error = process_chat_question(
                                    chat_question, 
                                    analysis_context, 
                                    analysis['country'], 
                                    analysis['classification']
                                )
                                
                                if chat_response:
                                    # Add to chat history for this analysis
                                    st.session_state[chat_key].append({
                                        'question': chat_question,
                                        'answer': chat_response,
                                        'timestamp': datetime.now().strftime('%H:%M:%S')
                                    })
                                    st.success("✅ Response generated!")
                                    
                                    # Show the answer immediately
                                    st.subheader("🤖 AI Response")
                                    st.markdown(chat_response)
                                    st.markdown("---")
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ {error}")
                        else:
                            st.warning("Please enter a question.")
                
                with col_clear:
                    if st.button("🗑️ Clear Chat", use_container_width=True, key=f"clear_btn_{analysis_id}"):
                        st.session_state[chat_key] = []
                        st.rerun()
                
                # Display chat history for this analysis
                if st.session_state[chat_key]:
                    st.subheader("📝 Chat History")
                    for i, chat in enumerate(st.session_state[chat_key]):
                        with st.expander(f"Q{i+1}: {chat['question'][:50]}... ({chat['timestamp']})"):
                            st.markdown(f"**Question:** {chat['question']}")
                            st.markdown(f"**Answer:** {chat['answer']}")
                
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

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Check authentication first
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
        # Add logout button
        if st.button("🚪 Logout", help="Logout from the application"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 New Analysis", "📚 All Analyses"])
    
    with tab1:
        render_new_analysis_tab()
    
    with tab2:
        render_all_analyses_tab()
    
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

if __name__ == "__main__":
    main()
