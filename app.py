"""
UN GA Daily Readouts - Streamlit App
Production-ready app for analyzing UN General Assembly speeches
"""

import os
import logging
import random
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

def sidebar_upload_section():
    """Render the sidebar upload section."""
    st.sidebar.header("📁 Upload Document")
    
    # Clear session button
    if st.sidebar.button("🔄 Clear Session", help="Clear all auto-detected data and start fresh"):
        # Clear auto-detection data
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
        st.rerun()
    
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
                
                # Fun messages for audio processing
                fun_messages = [
                    "🎤 Converting audio to words... (This might take a moment)",
                    "🤖 Our AI is listening carefully to every word...",
                    "📝 Transforming sound waves into beautiful text...",
                    "🎧 The Whisper AI is working its magic...",
                    "⚡ Converting audio to text... (Almost there!)",
                    "🔊 Processing your speech... (AI is all ears!)",
                    "📄 Turning sound into sentences...",
                    "🎵 From audio to alphabet... (This is music to our AI's ears!)"
                ]
                
                import random
                fun_message = random.choice(fun_messages)
                status_text.text(fun_message)
                progress_bar.progress(20)
                
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
    
    # Search functionality
    search_term = st.text_input(
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
        country = st.selectbox(
            "Select Country/Entity",
            options=[""] + filtered_countries,
            help=f"Found {len(filtered_countries)} matches. Select one or type more to refine search."
        )
    else:
        st.warning("No countries found matching your search.")
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

def process_and_show_text(uploaded_file, pasted_text):
    """Process uploaded file and show extracted text."""
    text_to_preview = pasted_text if pasted_text else ""
    
    if uploaded_file:
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        # Process the file
        try:
            client = get_openai_client()
            if client:
                # Use appropriate client based on file type
                if uploaded_file.name.lower().endswith('.mp3'):
                    # Show audio processing message
                    with st.spinner("🎤 Converting audio to text... This may take a moment."):
                        whisper_client = get_whisper_client()
                        text_to_preview = extract_text_from_file(
                            uploaded_file.getvalue(), 
                            uploaded_file.name, 
                            whisper_client
                        )
                else:
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
        # Show extracted text
        st.text_area(
            "Extracted Text",
            text_to_preview,
            height=300,
            disabled=True,
            help="Full transcribed text from the file"
        )
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as TXT
            st.download_button(
                label="📄 Download as TXT",
                data=text_to_preview,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download as plain text file"
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
                    help="Download as Microsoft Word document"
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
                    help="Download as OpenDocument Text (LibreOffice/OpenOffice)"
                )
            except Exception as e:
                st.error(f"ODT export not available: {e}")
    
    return text_to_preview

def render_analysis_section(country, speech_date, classification, uploaded_file, pasted_text, text_to_preview):
    """Render the analysis section."""
    # Analyze button
    if st.button("🚀 Analyze Speech", type="primary", use_container_width=True):
        if country:
            analysis_id = process_analysis(
                uploaded_file, pasted_text, country, 
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
            else:
                st.error("Analysis not found in database.")
        except Exception as e:
            st.error(f"Error loading analysis: {e}")

def render_new_analysis_tab():
    """Render the New Analysis tab."""
    st.header("🆕 New Analysis")
    
    # Step 1: Country Selection (always first)
    st.subheader("🌍 Step 1: Select Country/Entity")
    country, speech_date, classification = render_country_selection()
    
    # Step 2: File Upload (only after country is selected)
    if country:
        st.subheader("📁 Step 2: Upload File or Paste Text")
        uploaded_file, pasted_text = sidebar_upload_section()
        
        # Step 3: Process file and show text
        if uploaded_file or pasted_text:
            st.subheader("📄 Step 3: Text Preview")
            text_to_preview = process_and_show_text(uploaded_file, pasted_text)
            
            # Step 4: Analysis (only if we have text)
            if text_to_preview:
                st.subheader("🚀 Step 4: Analyze")
                render_analysis_section(country, speech_date, classification, uploaded_file, pasted_text, text_to_preview)
    else:
        st.info("👆 Please select a country/entity to begin analysis")

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
    tab1, tab2 = st.tabs(["🆕 New Analysis", "📚 All Analyses"])
    
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

if __name__ == "__main__":
    main()
