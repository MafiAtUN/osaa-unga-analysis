"""
UNGA Corpus Integration System
Integrates historical UNGA speeches (1946-2024) for comparative analysis
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

class UNGACorpusManager:
    """Manages the UNGA speech corpus for historical analysis."""
    
    def __init__(self, corpus_path: str = "artifacts/logo/unga-1946-2024-corpus"):
        self.corpus_path = corpus_path
        self.country_code_mapping = self._create_country_mapping()
        self.session_years = self._get_session_years()
        
    def _create_country_mapping(self) -> Dict[str, str]:
        """Create mapping from 3-letter country codes to full country names."""
        return {
            # Major countries
            'USA': 'United States', 'CHN': 'China', 'RUS': 'Russia', 'GBR': 'United Kingdom',
            'FRA': 'France', 'DEU': 'Germany', 'JPN': 'Japan', 'IND': 'India', 'BRA': 'Brazil',
            'CAN': 'Canada', 'AUS': 'Australia', 'ITA': 'Italy', 'ESP': 'Spain', 'MEX': 'Mexico',
            'ZAF': 'South Africa', 'NGA': 'Nigeria', 'EGY': 'Egypt', 'TUR': 'Turkey',
            'SAU': 'Saudi Arabia', 'IRN': 'Iran', 'IRQ': 'Iraq', 'ISR': 'Israel', 'PSE': 'Palestine',
            
            # African countries
            'KEN': 'Kenya', 'ETH': 'Ethiopia', 'GHA': 'Ghana', 'TZA': 'Tanzania', 'UGA': 'Uganda',
            'MWI': 'Malawi', 'ZWE': 'Zimbabwe', 'BWA': 'Botswana', 'NAM': 'Namibia', 'ZMB': 'Zambia',
            'AGO': 'Angola', 'MOZ': 'Mozambique', 'SEN': 'Senegal', 'MLI': 'Mali', 'BFA': 'Burkina Faso',
            'NER': 'Niger', 'TCD': 'Chad', 'CMR': 'Cameroon', 'GAB': 'Gabon', 'GNQ': 'Equatorial Guinea',
            'CAF': 'Central African Republic', 'COD': 'Democratic Republic of Congo', 'COG': 'Republic of Congo',
            'CIV': 'Côte d\'Ivoire', 'GIN': 'Guinea', 'GNB': 'Guinea-Bissau', 'SLE': 'Sierra Leone',
            'LBR': 'Liberia', 'GMB': 'Gambia', 'BEN': 'Benin', 'TGO': 'Togo', 'DJI': 'Djibouti',
            'SOM': 'Somalia', 'ERI': 'Eritrea', 'SSD': 'South Sudan', 'SDN': 'Sudan', 'LBY': 'Libya',
            'TUN': 'Tunisia', 'DZA': 'Algeria', 'MAR': 'Morocco', 'LSO': 'Lesotho', 'SWZ': 'Swaziland',
            'MUS': 'Mauritius', 'SYC': 'Seychelles', 'COM': 'Comoros', 'MDG': 'Madagascar',
            'CPV': 'Cape Verde', 'STP': 'São Tomé and Príncipe', 'RWA': 'Rwanda', 'BDI': 'Burundi',
            
            # Other countries
            'ARG': 'Argentina', 'CHL': 'Chile', 'COL': 'Colombia', 'PER': 'Peru', 'VEN': 'Venezuela',
            'ECU': 'Ecuador', 'BOL': 'Bolivia', 'PRY': 'Paraguay', 'URY': 'Uruguay', 'GUY': 'Guyana',
            'SUR': 'Suriname', 'CUB': 'Cuba', 'JAM': 'Jamaica', 'HTI': 'Haiti', 'DOM': 'Dominican Republic',
            'TTO': 'Trinidad and Tobago', 'BRB': 'Barbados', 'LCA': 'Saint Lucia', 'VCT': 'Saint Vincent and the Grenadines',
            'GRD': 'Grenada', 'ATG': 'Antigua and Barbuda', 'KNA': 'Saint Kitts and Nevis', 'DMA': 'Dominica',
            'BLZ': 'Belize', 'CRI': 'Costa Rica', 'PAN': 'Panama', 'NIC': 'Nicaragua', 'HND': 'Honduras',
            'SLV': 'El Salvador', 'GTM': 'Guatemala', 'PHL': 'Philippines', 'IDN': 'Indonesia', 'MYS': 'Malaysia',
            'SGP': 'Singapore', 'THA': 'Thailand', 'VNM': 'Vietnam', 'KHM': 'Cambodia', 'LAO': 'Laos',
            'MMR': 'Myanmar', 'BGD': 'Bangladesh', 'PAK': 'Pakistan', 'LKA': 'Sri Lanka', 'NPL': 'Nepal',
            'BTN': 'Bhutan', 'MDV': 'Maldives', 'AFG': 'Afghanistan', 'UZB': 'Uzbekistan', 'KAZ': 'Kazakhstan',
            'KGZ': 'Kyrgyzstan', 'TJK': 'Tajikistan', 'TKM': 'Turkmenistan', 'AZE': 'Azerbaijan', 'ARM': 'Armenia',
            'GEO': 'Georgia', 'MNG': 'Mongolia', 'PRK': 'North Korea', 'KOR': 'South Korea', 'TWN': 'Taiwan',
            'HKG': 'Hong Kong', 'MAC': 'Macau', 'BRN': 'Brunei', 'TLS': 'Timor-Leste', 'FJI': 'Fiji',
            'PNG': 'Papua New Guinea', 'SLB': 'Solomon Islands', 'VUT': 'Vanuatu', 'WSM': 'Samoa',
            'TON': 'Tonga', 'KIR': 'Kiribati', 'TUV': 'Tuvalu', 'NRU': 'Nauru', 'PLW': 'Palau',
            'MHL': 'Marshall Islands', 'FSM': 'Micronesia', 'POL': 'Poland', 'CZE': 'Czech Republic',
            'SVK': 'Slovakia', 'HUN': 'Hungary', 'ROU': 'Romania', 'BGR': 'Bulgaria', 'HRV': 'Croatia',
            'SVN': 'Slovenia', 'BIH': 'Bosnia and Herzegovina', 'MNE': 'Montenegro', 'MKD': 'North Macedonia',
            'SRB': 'Serbia', 'XKX': 'Kosovo', 'ALB': 'Albania', 'MDA': 'Moldova', 'UKR': 'Ukraine',
            'BLR': 'Belarus', 'LTU': 'Lithuania', 'LVA': 'Latvia', 'EST': 'Estonia', 'LUX': 'Luxembourg',
            'LIE': 'Liechtenstein', 'MCO': 'Monaco', 'SMR': 'San Marino', 'VAT': 'Vatican City',
            'AND': 'Andorra', 'GRC': 'Greece', 'CYP': 'Cyprus', 'MLT': 'Malta', 'ISL': 'Iceland',
            'NOR': 'Norway', 'SWE': 'Sweden', 'DNK': 'Denmark', 'FIN': 'Finland', 'IRL': 'Ireland',
            'PRT': 'Portugal', 'NLD': 'Netherlands', 'BEL': 'Belgium', 'CHE': 'Switzerland',
            'AUT': 'Austria', 'LBN': 'Lebanon', 'JOR': 'Jordan', 'SYR': 'Syria', 'YEM': 'Yemen',
            'OMN': 'Oman', 'ARE': 'United Arab Emirates', 'QAT': 'Qatar', 'BHR': 'Bahrain', 'KWT': 'Kuwait',
            'CSK': 'Czechoslovakia', 'YUG': 'Yugoslavia', 'SUN': 'Soviet Union', 'DDR': 'East Germany',
            'VDR': 'South Vietnam', 'RVN': 'South Vietnam', 'VNM': 'Vietnam'
        }
    
    def _get_session_years(self) -> Dict[int, int]:
        """Map session numbers to years."""
        return {i: 1945 + i for i in range(1, 80)}  # Sessions 1-79, Years 1946-2024
    
    def get_country_code(self, country_name: str) -> Optional[str]:
        """Get 3-letter country code from full country name."""
        for code, name in self.country_code_mapping.items():
            if name.lower() == country_name.lower():
                return code
        return None
    
    def get_country_name(self, country_code: str) -> Optional[str]:
        """Get full country name from 3-letter code."""
        return self.country_code_mapping.get(country_code.upper())
    
    def find_historical_speeches(self, country: str, years: List[int] = None) -> List[Dict[str, str]]:
        """Find historical speeches for a country in specified years."""
        if years is None:
            # Default to last 5 years
            current_year = datetime.now().year
            years = list(range(current_year - 5, current_year))
        
        country_code = self.get_country_code(country)
        if not country_code:
            return []
        
        speeches = []
        for year in years:
            session = year - 1945  # Convert year to session number
            if session < 1 or session > 79:
                continue
                
            session_dir = f"Session {session:02d} - {year}"
            session_path = os.path.join(self.corpus_path, session_dir)
            
            if os.path.exists(session_path):
                speech_file = f"{country_code}_{session:02d}_{year}.txt"
                speech_path = os.path.join(session_path, speech_file)
                
                if os.path.exists(speech_path):
                    try:
                        with open(speech_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        speeches.append({
                            'country': country,
                            'year': year,
                            'session': session,
                            'content': content,
                            'file_path': speech_path,
                            'word_count': len(content.split())
                        })
                    except Exception as e:
                        logging.error(f"Error reading {speech_path}: {e}")
        
        return speeches
    
    def get_recent_speeches(self, country: str, num_years: int = 5) -> List[Dict[str, str]]:
        """Get recent speeches for a country."""
        current_year = datetime.now().year
        years = list(range(current_year - num_years, current_year))
        return self.find_historical_speeches(country, years)
    
    def search_speeches_by_keywords(self, country: str, keywords: List[str], years: List[int] = None) -> List[Dict[str, str]]:
        """Search speeches by keywords."""
        speeches = self.find_historical_speeches(country, years)
        matching_speeches = []
        
        for speech in speeches:
            content_lower = speech['content'].lower()
            if any(keyword.lower() in content_lower for keyword in keywords):
                matching_speeches.append(speech)
        
        return matching_speeches
    
    def get_speech_summary(self, speech: Dict[str, str]) -> str:
        """Get a summary of a speech."""
        content = speech['content']
        word_count = speech['word_count']
        
        # Get first 500 characters as preview
        preview = content[:500] + "..." if len(content) > 500 else content
        
        return f"""
**{speech['country']} - {speech['year']} (Session {speech['session']})**
- Word Count: {word_count:,}
- Preview: {preview}
"""
    
    def create_comparative_analysis_data(self, current_speech: str, country: str, years: List[int] = None) -> str:
        """Create data for comparative analysis between current and historical speeches."""
        historical_speeches = self.find_historical_speeches(country, years)
        
        if not historical_speeches:
            return "No historical speeches found for comparison."
        
        analysis_data = f"""
**HISTORICAL SPEECHES FOR COMPARISON:**
Country: {country}
Current Speech Word Count: {len(current_speech.split()):,}

**Available Historical Speeches:**
"""
        
        for speech in historical_speeches:
            analysis_data += f"""
**{speech['year']} (Session {speech['session']}):**
- Word Count: {speech['word_count']:,}
- Content Preview: {speech['content'][:300]}...

---
"""
        
        return analysis_data

# Global instance
corpus_manager = UNGACorpusManager()
