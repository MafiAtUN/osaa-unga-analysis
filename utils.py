"""
Utility Functions Module
Common utility functions used across the application
"""

import os
import re
import html
import logging
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS attacks."""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()


def get_openai_client() -> Optional[AzureOpenAI]:
    """Get OpenAI client for Azure OpenAI."""
    try:
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return None


def get_whisper_client() -> Optional[AzureOpenAI]:
    """Get Whisper client for audio transcription."""
    try:
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    except Exception as e:
        logger.error(f"Failed to initialize Whisper client: {e}")
        return None


def detect_country_simple(text: str) -> str:
    """Simple country detection from text."""
    # Common country patterns in UN speeches
    country_patterns = {
        r'\b(?:United States|USA|US)\b': 'United States',
        r'\b(?:China|People\'s Republic of China|PRC)\b': 'China',
        r'\b(?:Russia|Russian Federation|USSR)\b': 'Russia',
        r'\b(?:United Kingdom|UK|Britain|Great Britain)\b': 'United Kingdom',
        r'\b(?:France|French Republic)\b': 'France',
        r'\b(?:Germany|Federal Republic of Germany)\b': 'Germany',
        r'\b(?:Japan|Japan)\b': 'Japan',
        r'\b(?:India|Republic of India)\b': 'India',
        r'\b(?:Brazil|Federative Republic of Brazil)\b': 'Brazil',
        r'\b(?:Canada|Canada)\b': 'Canada',
        r'\b(?:Australia|Commonwealth of Australia)\b': 'Australia',
        r'\b(?:South Africa|Republic of South Africa)\b': 'South Africa',
        r'\b(?:Nigeria|Federal Republic of Nigeria)\b': 'Nigeria',
        r'\b(?:Kenya|Republic of Kenya)\b': 'Kenya',
        r'\b(?:Egypt|Arab Republic of Egypt)\b': 'Egypt',
        r'\b(?:Ghana|Republic of Ghana)\b': 'Ghana',
        r'\b(?:Ethiopia|Federal Democratic Republic of Ethiopia)\b': 'Ethiopia',
        r'\b(?:Morocco|Kingdom of Morocco)\b': 'Morocco',
        r'\b(?:Tunisia|Republic of Tunisia)\b': 'Tunisia',
        r'\b(?:Algeria|People\'s Democratic Republic of Algeria)\b': 'Algeria',
        r'\b(?:Senegal|Republic of Senegal)\b': 'Senegal',
        r'\b(?:Mali|Republic of Mali)\b': 'Mali',
        r'\b(?:Burkina Faso|Burkina Faso)\b': 'Burkina Faso',
        r'\b(?:Niger|Republic of Niger)\b': 'Niger',
        r'\b(?:Chad|Republic of Chad)\b': 'Chad',
        r'\b(?:Cameroon|Republic of Cameroon)\b': 'Cameroon',
        r'\b(?:Central African Republic|CAR)\b': 'Central African Republic',
        r'\b(?:Democratic Republic of the Congo|DRC|Congo-Kinshasa)\b': 'Democratic Republic of the Congo',
        r'\b(?:Republic of the Congo|Congo-Brazzaville)\b': 'Republic of the Congo',
        r'\b(?:Gabon|Gabonese Republic)\b': 'Gabon',
        r'\b(?:Equatorial Guinea|Republic of Equatorial Guinea)\b': 'Equatorial Guinea',
        r'\b(?:São Tomé and Príncipe|Sao Tome and Principe)\b': 'São Tomé and Príncipe',
        r'\b(?:Angola|Republic of Angola)\b': 'Angola',
        r'\b(?:Zambia|Republic of Zambia)\b': 'Zambia',
        r'\b(?:Zimbabwe|Republic of Zimbabwe)\b': 'Zimbabwe',
        r'\b(?:Botswana|Republic of Botswana)\b': 'Botswana',
        r'\b(?:Namibia|Republic of Namibia)\b': 'Namibia',
        r'\b(?:Lesotho|Kingdom of Lesotho)\b': 'Lesotho',
        r'\b(?:Eswatini|Kingdom of Eswatini|Swaziland)\b': 'Eswatini',
        r'\b(?:Madagascar|Republic of Madagascar)\b': 'Madagascar',
        r'\b(?:Mauritius|Republic of Mauritius)\b': 'Mauritius',
        r'\b(?:Seychelles|Republic of Seychelles)\b': 'Seychelles',
        r'\b(?:Comoros|Union of the Comoros)\b': 'Comoros',
        r'\b(?:Djibouti|Republic of Djibouti)\b': 'Djibouti',
        r'\b(?:Somalia|Federal Republic of Somalia)\b': 'Somalia',
        r'\b(?:Sudan|Republic of the Sudan)\b': 'Sudan',
        r'\b(?:South Sudan|Republic of South Sudan)\b': 'South Sudan',
        r'\b(?:Eritrea|State of Eritrea)\b': 'Eritrea',
        r'\b(?:Libya|State of Libya)\b': 'Libya',
        r'\b(?:Côte d\'Ivoire|Ivory Coast)\b': 'Côte d\'Ivoire',
        r'\b(?:Liberia|Republic of Liberia)\b': 'Liberia',
        r'\b(?:Sierra Leone|Republic of Sierra Leone)\b': 'Sierra Leone',
        r'\b(?:Guinea|Republic of Guinea)\b': 'Guinea',
        r'\b(?:Guinea-Bissau|Republic of Guinea-Bissau)\b': 'Guinea-Bissau',
        r'\b(?:Gambia|Republic of the Gambia)\b': 'Gambia',
        r'\b(?:Cape Verde|Republic of Cabo Verde)\b': 'Cape Verde',
        r'\b(?:Mauritania|Islamic Republic of Mauritania)\b': 'Mauritania',
        r'\b(?:Togo|Togolese Republic)\b': 'Togo',
        r'\b(?:Benin|Republic of Benin)\b': 'Benin',
        r'\b(?:Rwanda|Republic of Rwanda)\b': 'Rwanda',
        r'\b(?:Burundi|Republic of Burundi)\b': 'Burundi',
        r'\b(?:Uganda|Republic of Uganda)\b': 'Uganda',
        r'\b(?:Tanzania|United Republic of Tanzania)\b': 'Tanzania',
        r'\b(?:Malawi|Republic of Malawi)\b': 'Malawi',
        r'\b(?:Mozambique|Republic of Mozambique)\b': 'Mozambique',
    }
    
    for pattern, country in country_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return country
    
    return "Unknown"


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web for additional context."""
    try:
        # This would integrate with a search API
        # For now, return empty results
        return []
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []


def search_past_speeches(country: str, year: int = None) -> List[Dict[str, str]]:
    """Search for past speeches by the same country."""
    try:
        # This would search the database for past speeches
        # For now, return empty results
        return []
    except Exception as e:
        logger.error(f"Past speeches search failed: {e}")
        return []


def get_suggestion_questions(country: str, classification: str) -> list:
    """Get suggested questions based on country and classification."""
    base_questions = [
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
            "How did they address their development assistance programs?",
            "What were their views on South-South cooperation?",
            "How did they discuss technology transfer to developing countries?",
            "What commitments did they make to global development goals?"
        ]
        return base_questions + partner_questions
