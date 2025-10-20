"""
Data ingestion system for UNGA speech data.
Handles importing speech data from files and managing the database.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

from .simple_vector_storage import simple_vector_storage as db_manager
from ..core.classify import get_au_members

logger = logging.getLogger(__name__)

# Language detection and translation
try:
    from langdetect import detect, DetectorFactory
    from deep_translator import GoogleTranslator
    DetectorFactory.seed = 0  # For consistent results
    LANG_DETECTION_AVAILABLE = True
except ImportError:
    LANG_DETECTION_AVAILABLE = False
    logger.warning("Language detection libraries not available. Install langdetect and deep-translator for automatic translation.")

# Country code to full name mapping
COUNTRY_CODE_MAPPING = {
    'AFG': 'Afghanistan', 'ALB': 'Albania', 'DZA': 'Algeria', 'AND': 'Andorra',
    'AGO': 'Angola', 'ATG': 'Antigua and Barbuda', 'ARG': 'Argentina', 'ARM': 'Armenia',
    'AUS': 'Australia', 'AUT': 'Austria', 'AZE': 'Azerbaijan', 'BHS': 'Bahamas',
    'BHR': 'Bahrain', 'BGD': 'Bangladesh', 'BRB': 'Barbados', 'BLR': 'Belarus',
    'BEL': 'Belgium', 'BLZ': 'Belize', 'BEN': 'Benin', 'BTN': 'Bhutan',
    'BOL': 'Bolivia', 'BIH': 'Bosnia and Herzegovina', 'BWA': 'Botswana', 'BRA': 'Brazil',
    'BRN': 'Brunei', 'BGR': 'Bulgaria', 'BFA': 'Burkina Faso', 'BDI': 'Burundi',
    'CPV': 'Cape Verde', 'KHM': 'Cambodia', 'CMR': 'Cameroon', 'CAN': 'Canada',
    'CAF': 'Central African Republic', 'TCD': 'Chad', 'CHL': 'Chile', 'CHN': 'China',
    'COL': 'Colombia', 'COM': 'Comoros', 'COG': 'Republic of the Congo',
    'COD': 'Democratic Republic of the Congo', 'CRI': 'Costa Rica', 'CIV': 'Côte d\'Ivoire',
    'HRV': 'Croatia', 'CUB': 'Cuba', 'CYP': 'Cyprus', 'CZE': 'Czech Republic',
    'DNK': 'Denmark', 'DJI': 'Djibouti', 'DMA': 'Dominica', 'DOM': 'Dominican Republic',
    'ECU': 'Ecuador', 'EGY': 'Egypt', 'SLV': 'El Salvador', 'GNQ': 'Equatorial Guinea',
    'ERI': 'Eritrea', 'EST': 'Estonia', 'SWZ': 'Eswatini', 'ETH': 'Ethiopia',
    'FJI': 'Fiji', 'FIN': 'Finland', 'FRA': 'France', 'GAB': 'Gabon',
    'GMB': 'Gambia', 'GEO': 'Georgia', 'DEU': 'Germany', 'GHA': 'Ghana',
    'GRC': 'Greece', 'GRD': 'Grenada', 'GTM': 'Guatemala', 'GIN': 'Guinea',
    'GNB': 'Guinea-Bissau', 'GUY': 'Guyana', 'HTI': 'Haiti', 'HND': 'Honduras',
    'HUN': 'Hungary', 'ISL': 'Iceland', 'IND': 'India', 'IDN': 'Indonesia',
    'IRN': 'Iran', 'IRQ': 'Iraq', 'IRL': 'Ireland', 'ISR': 'Israel',
    'ITA': 'Italy', 'JAM': 'Jamaica', 'JPN': 'Japan', 'JOR': 'Jordan',
    'KAZ': 'Kazakhstan', 'KEN': 'Kenya', 'KIR': 'Kiribati', 'PRK': 'North Korea',
    'KOR': 'South Korea', 'KWT': 'Kuwait', 'KGZ': 'Kyrgyzstan', 'LAO': 'Laos',
    'LVA': 'Latvia', 'LBN': 'Lebanon', 'LSO': 'Lesotho', 'LBR': 'Liberia',
    'LBY': 'Libya', 'LIE': 'Liechtenstein', 'LTU': 'Lithuania', 'LUX': 'Luxembourg',
    'MKD': 'North Macedonia', 'MDG': 'Madagascar', 'MWI': 'Malawi', 'MYS': 'Malaysia',
    'MDV': 'Maldives', 'MLI': 'Mali', 'MLT': 'Malta', 'MHL': 'Marshall Islands',
    'MRT': 'Mauritania', 'MUS': 'Mauritius', 'MEX': 'Mexico', 'FSM': 'Micronesia',
    'MDA': 'Moldova', 'MCO': 'Monaco', 'MNG': 'Mongolia', 'MNE': 'Montenegro',
    'MAR': 'Morocco', 'MOZ': 'Mozambique', 'MMR': 'Myanmar', 'NAM': 'Namibia',
    'NRU': 'Nauru', 'NPL': 'Nepal', 'NLD': 'Netherlands', 'NZL': 'New Zealand',
    'NIC': 'Nicaragua', 'NER': 'Niger', 'NGA': 'Nigeria', 'NOR': 'Norway',
    'OMN': 'Oman', 'PAK': 'Pakistan', 'PLW': 'Palau', 'PSE': 'Palestine',
    'PAN': 'Panama', 'PNG': 'Papua New Guinea', 'PRY': 'Paraguay', 'PER': 'Peru',
    'PHL': 'Philippines', 'POL': 'Poland', 'PRT': 'Portugal', 'QAT': 'Qatar',
    'ROU': 'Romania', 'RUS': 'Russia', 'RWA': 'Rwanda', 'KNA': 'Saint Kitts and Nevis',
    'LCA': 'Saint Lucia', 'VCT': 'Saint Vincent and the Grenadines', 'WSM': 'Samoa',
    'SMR': 'San Marino', 'STP': 'São Tomé and Príncipe', 'SAU': 'Saudi Arabia',
    'SEN': 'Senegal', 'SRB': 'Serbia', 'SYC': 'Seychelles', 'SLE': 'Sierra Leone',
    'SGP': 'Singapore', 'SVK': 'Slovakia', 'SVN': 'Slovenia', 'SLB': 'Solomon Islands',
    'SOM': 'Somalia', 'ZAF': 'South Africa', 'SSD': 'South Sudan', 'ESP': 'Spain',
    'LKA': 'Sri Lanka', 'SDN': 'Sudan', 'SUR': 'Suriname', 'SWE': 'Sweden',
    'CHE': 'Switzerland', 'SYR': 'Syria', 'TJK': 'Tajikistan', 'TZA': 'Tanzania',
    'THA': 'Thailand', 'TLS': 'Timor-Leste', 'TGO': 'Togo', 'TON': 'Tonga',
    'TTO': 'Trinidad and Tobago', 'TUN': 'Tunisia', 'TUR': 'Turkey', 'TKM': 'Turkmenistan',
    'TUV': 'Tuvalu', 'UGA': 'Uganda', 'UKR': 'Ukraine', 'ARE': 'United Arab Emirates',
    'GBR': 'United Kingdom', 'USA': 'United States', 'URY': 'Uruguay', 'UZB': 'Uzbekistan',
    'VUT': 'Vanuatu', 'VAT': 'Vatican City', 'VEN': 'Venezuela', 'VNM': 'Vietnam',
    'YEM': 'Yemen', 'ZMB': 'Zambia', 'ZWE': 'Zimbabwe'
}

# Region mapping for countries
REGION_MAPPING = {
    # Africa
    'DZA': 'Africa', 'AGO': 'Africa', 'BEN': 'Africa', 'BWA': 'Africa', 'BFA': 'Africa',
    'BDI': 'Africa', 'CPV': 'Africa', 'CMR': 'Africa', 'CAF': 'Africa', 'TCD': 'Africa',
    'COM': 'Africa', 'COG': 'Africa', 'COD': 'Africa', 'CIV': 'Africa', 'DJI': 'Africa',
    'EGY': 'Africa', 'GNQ': 'Africa', 'ERI': 'Africa', 'SWZ': 'Africa', 'ETH': 'Africa',
    'GAB': 'Africa', 'GMB': 'Africa', 'GHA': 'Africa', 'GIN': 'Africa', 'GNB': 'Africa',
    'KEN': 'Africa', 'LSO': 'Africa', 'LBR': 'Africa', 'LBY': 'Africa', 'MDG': 'Africa',
    'MWI': 'Africa', 'MLI': 'Africa', 'MRT': 'Africa', 'MUS': 'Africa', 'MAR': 'Africa',
    'MOZ': 'Africa', 'NAM': 'Africa', 'NER': 'Africa', 'NGA': 'Africa', 'RWA': 'Africa',
    'STP': 'Africa', 'SEN': 'Africa', 'SYC': 'Africa', 'SLE': 'Africa', 'SOM': 'Africa',
    'ZAF': 'Africa', 'SSD': 'Africa', 'SDN': 'Africa', 'TZA': 'Africa', 'TGO': 'Africa',
    'TUN': 'Africa', 'UGA': 'Africa', 'ZMB': 'Africa', 'ZWE': 'Africa',
    
    # Asia
    'AFG': 'Asia', 'BGD': 'Asia', 'BTN': 'Asia', 'BRN': 'Asia', 'KHM': 'Asia',
    'CHN': 'Asia', 'IDN': 'Asia', 'IRN': 'Asia', 'IRQ': 'Asia', 'ISR': 'Asia',
    'JPN': 'Asia', 'JOR': 'Asia', 'KAZ': 'Asia', 'KWT': 'Asia', 'KGZ': 'Asia',
    'LAO': 'Asia', 'LBN': 'Asia', 'MYS': 'Asia', 'MDV': 'Asia', 'MNG': 'Asia',
    'MMR': 'Asia', 'NPL': 'Asia', 'PRK': 'Asia', 'KOR': 'Asia', 'OMN': 'Asia',
    'PAK': 'Asia', 'PSE': 'Asia', 'PHL': 'Asia', 'QAT': 'Asia', 'SAU': 'Asia',
    'SGP': 'Asia', 'LKA': 'Asia', 'SYR': 'Asia', 'TJK': 'Asia', 'THA': 'Asia',
    'TLS': 'Asia', 'TKM': 'Asia', 'ARE': 'Asia', 'UZB': 'Asia', 'VNM': 'Asia',
    'YEM': 'Asia',
    
    # Europe
    'ALB': 'Europe', 'AND': 'Europe', 'ARM': 'Europe', 'AUT': 'Europe', 'AZE': 'Europe',
    'BLR': 'Europe', 'BEL': 'Europe', 'BIH': 'Europe', 'BGR': 'Europe', 'HRV': 'Europe',
    'CYP': 'Europe', 'CZE': 'Europe', 'DNK': 'Europe', 'EST': 'Europe', 'FIN': 'Europe',
    'FRA': 'Europe', 'GEO': 'Europe', 'DEU': 'Europe', 'GRC': 'Europe', 'HUN': 'Europe',
    'ISL': 'Europe', 'IRL': 'Europe', 'ITA': 'Europe', 'LVA': 'Europe', 'LIE': 'Europe',
    'LTU': 'Europe', 'LUX': 'Europe', 'MKD': 'Europe', 'MLT': 'Europe', 'MDA': 'Europe',
    'MCO': 'Europe', 'MNE': 'Europe', 'NLD': 'Europe', 'NOR': 'Europe', 'POL': 'Europe',
    'PRT': 'Europe', 'ROU': 'Europe', 'RUS': 'Europe', 'SMR': 'Europe', 'SRB': 'Europe',
    'SVK': 'Europe', 'SVN': 'Europe', 'ESP': 'Europe', 'SWE': 'Europe', 'CHE': 'Europe',
    'TUR': 'Europe', 'UKR': 'Europe', 'GBR': 'Europe', 'VAT': 'Europe',
    
    # North America
    'CAN': 'North America', 'CRI': 'North America', 'CUB': 'North America', 'DOM': 'North America',
    'SLV': 'North America', 'GTM': 'North America', 'HND': 'North America', 'JAM': 'North America',
    'MEX': 'North America', 'NIC': 'North America', 'PAN': 'North America', 'TTO': 'North America',
    'USA': 'North America',
    
    # South America
    'ARG': 'South America', 'BOL': 'South America', 'BRA': 'South America', 'CHL': 'South America',
    'COL': 'South America', 'ECU': 'South America', 'GUY': 'South America', 'PRY': 'South America',
    'PER': 'South America', 'SUR': 'South America', 'URY': 'South America', 'VEN': 'South America',
    
    # Oceania
    'AUS': 'Oceania', 'FJI': 'Oceania', 'KIR': 'Oceania', 'MHL': 'Oceania', 'FSM': 'Oceania',
    'NRU': 'Oceania', 'NZL': 'Oceania', 'PLW': 'Oceania', 'PNG': 'Oceania', 'WSM': 'Oceania',
    'SLB': 'Oceania', 'TON': 'Oceania', 'TUV': 'Oceania', 'VUT': 'Oceania',
    
    # Caribbean
    'ATG': 'Caribbean', 'BHS': 'Caribbean', 'BRB': 'Caribbean', 'BLZ': 'Caribbean',
    'DMA': 'Caribbean', 'GRD': 'Caribbean', 'HTI': 'Caribbean', 'KNA': 'Caribbean',
    'LCA': 'Caribbean', 'VCT': 'Caribbean'
}

class DataIngestionManager:
    """Manages data ingestion for UNGA speech data."""
    
    def __init__(self):
        self.db_manager = db_manager
        self.au_members = get_au_members()
    
    def get_country_name_from_code(self, country_code: str) -> str:
        """Get full country name from ISO3 code."""
        return COUNTRY_CODE_MAPPING.get(country_code.upper(), country_code)
    
    def get_region_from_code(self, country_code: str) -> str:
        """Get region from ISO3 country code."""
        return REGION_MAPPING.get(country_code.upper(), 'Unknown')
    
    def is_african_member(self, country_name: str) -> bool:
        """Check if country is an African Union member."""
        return country_name in self.au_members
    
    def parse_filename(self, filename: str) -> Optional[Tuple[str, int, int]]:
        """
        Parse filename to extract country code, session, and year.
        Expected format: {ISO3}_80_2025.txt
        
        Returns:
            Tuple of (country_code, session, year) or None if invalid format
        """
        try:
            # Remove .txt extension
            name = filename.replace('.txt', '')
            
            # Split by underscore
            parts = name.split('_')
            if len(parts) != 3:
                return None
            
            country_code = parts[0].upper()
            session = int(parts[1])
            year = int(parts[2])
            
            return country_code, session, year
            
        except (ValueError, IndexError):
            return None
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'fr', 'es') or 'unknown' if detection fails
        """
        if not LANG_DETECTION_AVAILABLE or not text.strip():
            return 'unknown'
        
        try:
            # Use first 1000 characters for detection (faster and more reliable)
            sample_text = text[:1000] if len(text) > 1000 else text
            detected_lang = detect(sample_text)
            logger.info(f"Detected language: {detected_lang}")
            return detected_lang
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'unknown'
    
    def translate_to_english(self, text: str, source_lang: str = None) -> Tuple[str, str]:
        """
        Translate text to English if it's not already in English.
        
        Args:
            text: Text to translate
            source_lang: Source language code (optional, will be detected if not provided)
            
        Returns:
            Tuple of (translated_text, detected_source_lang)
        """
        if not LANG_DETECTION_AVAILABLE:
            logger.warning("Translation not available - language detection libraries not installed")
            return text, 'unknown'
        
        try:
            # Detect language if not provided
            if not source_lang:
                source_lang = self.detect_language(text)
            
            # If already English or detection failed, return original
            if source_lang == 'en' or source_lang == 'unknown':
                return text, source_lang
            
            # Translate to English using deep-translator
            translator = GoogleTranslator(source=source_lang, target='en')
            # Translate in chunks to handle long texts
            max_chunk_size = 4000  # Google Translate limit
            
            if len(text) <= max_chunk_size:
                translated_text = translator.translate(text)
            else:
                # Split into chunks and translate each
                chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
                translated_chunks = []
                
                for chunk in chunks:
                    translated_chunk = translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
                
                translated_text = ' '.join(translated_chunks)
            
            logger.info(f"Translated text from {source_lang} to English ({len(text)} -> {len(translated_text)} chars)")
            return translated_text, source_lang
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text, source_lang or 'unknown'
    
    def read_speech_file(self, file_path: str) -> str:
        """Read speech text from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""
    
    def ingest_speech_file(self, file_path: str, filename: str) -> bool:
        """
        Ingest a single speech file into the database.
        
        Args:
            file_path: Full path to the file
            filename: Just the filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse filename
            parsed = self.parse_filename(filename)
            if not parsed:
                logger.error(f"Invalid filename format: {filename}")
                return False
            
            country_code, session, year = parsed
            
            # Get country name and region
            country_name = self.get_country_name_from_code(country_code)
            region = self.get_region_from_code(country_code)
            is_african_member = self.is_african_member(country_name)
            
            # Read speech text
            original_text = self.read_speech_file(file_path)
            if not original_text:
                logger.error(f"Empty or unreadable file: {filename}")
                return False
            
            # Detect language and translate if needed
            detected_lang = self.detect_language(original_text)
            if detected_lang != 'en' and detected_lang != 'unknown':
                logger.info(f"Non-English speech detected ({detected_lang}), translating to English...")
                speech_text, source_lang = self.translate_to_english(original_text, detected_lang)
                logger.info(f"Translation completed: {source_lang} -> English")
            else:
                speech_text = original_text
                source_lang = detected_lang
            
            # Save to database
            speech_id = self.db_manager.save_speech_data(
                country_code=country_code,
                country_name=country_name,
                region=region,
                session=session,
                year=year,
                speech_text=speech_text,
                source_filename=filename,
                is_african_member=is_african_member
            )
            
            logger.info(f"Successfully ingested {filename} -> {country_name} ({country_code})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}")
            return False
    
    def process_uploaded_file(self, file_content: bytes, filename: str, 
                            country_code: str = None, session: int = None, 
                            year: int = None) -> Dict[str, any]:
        """
        Process an uploaded file with language detection and translation.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            country_code: Country code (optional, will be extracted from filename if not provided)
            session: Session number (optional)
            year: Year (optional)
            
        Returns:
            Dictionary with processing results including original text, translated text, and metadata
        """
        try:
            # Extract text from file
            if filename.lower().endswith('.txt'):
                text = file_content.decode('utf-8')
            elif filename.lower().endswith('.pdf'):
                # Use existing PDF extraction from ingest.py
                from ingest import extract_text_from_file
                text = extract_text_from_file(file_content, filename)
            elif filename.lower().endswith(('.doc', '.docx')):
                # Use existing Word extraction from ingest.py
                from ingest import extract_text_from_file
                text = extract_text_from_file(file_content, filename)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {filename.split(".")[-1]}',
                    'original_text': '',
                    'translated_text': '',
                    'detected_language': 'unknown'
                }
            
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'No text content found in file',
                    'original_text': '',
                    'translated_text': '',
                    'detected_language': 'unknown'
                }
            
            # Detect language
            detected_lang = self.detect_language(text)
            
            # Translate if needed
            if detected_lang != 'en' and detected_lang != 'unknown':
                translated_text, source_lang = self.translate_to_english(text, detected_lang)
                translation_applied = True
            else:
                translated_text = text
                source_lang = detected_lang
                translation_applied = False
            
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'detected_language': detected_lang,
                'translation_applied': translation_applied,
                'source_language': source_lang,
                'filename': filename,
                'text_length': len(text),
                'translated_length': len(translated_text)
            }
            
        except Exception as e:
            logger.error(f"Failed to process uploaded file {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_text': '',
                'translated_text': '',
                'detected_language': 'unknown'
            }
    
    def ingest_directory(self, directory_path: str) -> Dict[str, int]:
        """
        Ingest all speech files from a directory.
        
        Args:
            directory_path: Path to directory containing speech files
            
        Returns:
            Dictionary with ingestion statistics
        """
        stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                logger.error(f"Directory does not exist: {directory_path}")
                return stats
            
            # Find all .txt files
            txt_files = list(directory.glob('*.txt'))
            stats['total_files'] = len(txt_files)
            
            logger.info(f"Found {len(txt_files)} speech files to ingest")
            
            for file_path in txt_files:
                filename = file_path.name
                
                # Skip README and other non-speech files
                if filename.lower() in ['readme.txt', 'readme.md']:
                    stats['skipped'] += 1
                    continue
                
                # Ingest the file
                if self.ingest_speech_file(str(file_path), filename):
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
            
            logger.info(f"Ingestion complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to ingest directory {directory_path}: {e}")
            return stats
    
    def get_ingestion_status(self) -> Dict[str, any]:
        """Get current ingestion status and statistics."""
        try:
            stats = self.db_manager.get_speech_statistics()
            return stats
        except Exception as e:
            logger.error(f"Failed to get ingestion status: {e}")
            return {}

# Global data ingestion manager instance
data_ingestion_manager = DataIngestionManager()


