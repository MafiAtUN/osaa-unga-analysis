"""
Country and organization lists for UNGA analysis
"""

from typing import List


def get_all_countries() -> List[str]:
    """Get comprehensive list of all world countries and entities."""
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
    return sorted(list(set(all_countries)))


def detect_country_simple(text: str) -> str:
    """
    Simple keyword-based country detection.
    
    Args:
        text: Text to analyze for country detection
    
    Returns:
        Detected country name or None
    """
    text_lower = text.lower()
    
    # Common country keywords and their full names
    country_keywords = {
        # African countries
        "algeria": "Algeria", "angola": "Angola", "benin": "Benin", "botswana": "Botswana",
        "burkina faso": "Burkina Faso", "burundi": "Burundi", "cameroon": "Cameroon",
        "cabo verde": "Cape Verde", "cape verde": "Cape Verde",
        "central african republic": "Central African Republic", "chad": "Chad",
        "comoros": "Comoros", "congo": "Democratic Republic of the Congo",
        "democratic republic of the congo": "Democratic Republic of the Congo",
        "republic of the congo": "Republic of the Congo",
        "djibouti": "Djibouti", "egypt": "Egypt", "equatorial guinea": "Equatorial Guinea",
        "eritrea": "Eritrea", "eswatini": "Eswatini", "swaziland": "Eswatini",
        "ethiopia": "Ethiopia", "gabon": "Gabon", "gambia": "Gambia", "ghana": "Ghana",
        "guinea": "Guinea", "guinea-bissau": "Guinea-Bissau", "ivory coast": "Ivory Coast",
        "côte d'ivoire": "Ivory Coast", "kenya": "Kenya", "lesotho": "Lesotho",
        "liberia": "Liberia", "libya": "Libya", "madagascar": "Madagascar", "malawi": "Malawi",
        "mali": "Mali", "mauritania": "Mauritania", "mauritius": "Mauritius", "morocco": "Morocco",
        "mozambique": "Mozambique", "namibia": "Namibia", "niger": "Niger", "nigeria": "Nigeria",
        "rwanda": "Rwanda", "são tomé and príncipe": "São Tomé and Príncipe",
        "sao tome and principe": "São Tomé and Príncipe", "senegal": "Senegal",
        "seychelles": "Seychelles", "sierra leone": "Sierra Leone", "somalia": "Somalia",
        "south africa": "South Africa", "south sudan": "South Sudan", "sudan": "Sudan",
        "tanzania": "Tanzania", "togo": "Togo", "tunisia": "Tunisia", "uganda": "Uganda",
        "zambia": "Zambia", "zimbabwe": "Zimbabwe",
        
        # North America
        "united states": "United States", "usa": "United States", "u.s.a": "United States",
        "america": "United States", "canada": "Canada", "mexico": "Mexico",
        "guatemala": "Guatemala", "belize": "Belize", "el salvador": "El Salvador",
        "honduras": "Honduras", "nicaragua": "Nicaragua", "costa rica": "Costa Rica",
        "panama": "Panama", "cuba": "Cuba", "jamaica": "Jamaica", "haiti": "Haiti",
        "dominican republic": "Dominican Republic", "trinidad and tobago": "Trinidad and Tobago",
        "barbados": "Barbados", "saint lucia": "Saint Lucia", "grenada": "Grenada",
        "saint vincent and the grenadines": "Saint Vincent and the Grenadines",
        "antigua and barbuda": "Antigua and Barbuda", "dominica": "Dominica",
        "saint kitts and nevis": "Saint Kitts and Nevis", "bahamas": "Bahamas",
        
        # South America
        "brazil": "Brazil", "argentina": "Argentina", "chile": "Chile", "colombia": "Colombia",
        "peru": "Peru", "venezuela": "Venezuela", "ecuador": "Ecuador", "bolivia": "Bolivia",
        "paraguay": "Paraguay", "uruguay": "Uruguay", "guyana": "Guyana", "suriname": "Suriname",
        
        # Europe
        "united kingdom": "United Kingdom", "uk": "United Kingdom", "britain": "United Kingdom",
        "france": "France", "germany": "Germany", "italy": "Italy", "spain": "Spain",
        "netherlands": "Netherlands", "belgium": "Belgium", "switzerland": "Switzerland",
        "austria": "Austria", "sweden": "Sweden", "norway": "Norway", "denmark": "Denmark",
        "finland": "Finland", "poland": "Poland", "czech republic": "Czech Republic",
        "czechia": "Czech Republic", "slovakia": "Slovakia", "hungary": "Hungary",
        "romania": "Romania", "bulgaria": "Bulgaria", "croatia": "Croatia", "slovenia": "Slovenia",
        "estonia": "Estonia", "latvia": "Latvia", "lithuania": "Lithuania", "portugal": "Portugal",
        "greece": "Greece", "ireland": "Ireland", "luxembourg": "Luxembourg", "malta": "Malta",
        "cyprus": "Cyprus", "iceland": "Iceland", "liechtenstein": "Liechtenstein",
        "monaco": "Monaco", "san marino": "San Marino", "vatican": "Vatican City",
        "andorra": "Andorra", "albania": "Albania", "bosnia and herzegovina": "Bosnia and Herzegovina",
        "montenegro": "Montenegro", "north macedonia": "North Macedonia", "macedonia": "North Macedonia",
        "serbia": "Serbia", "kosovo": "Kosovo", "moldova": "Moldova", "ukraine": "Ukraine",
        "belarus": "Belarus", "russia": "Russia", "russian federation": "Russia",
        
        # Asia
        "china": "China", "people's republic of china": "China", "prc": "China",
        "japan": "Japan", "south korea": "South Korea", "korea, republic of": "South Korea",
        "north korea": "North Korea", "korea, democratic people's republic of": "North Korea",
        "mongolia": "Mongolia", "india": "India", "pakistan": "Pakistan",
        "bangladesh": "Bangladesh", "sri lanka": "Sri Lanka", "nepal": "Nepal",
        "bhutan": "Bhutan", "afghanistan": "Afghanistan", "kazakhstan": "Kazakhstan",
        "kyrgyzstan": "Kyrgyzstan", "tajikistan": "Tajikistan", "turkmenistan": "Turkmenistan",
        "uzbekistan": "Uzbekistan", "iran": "Iran", "iraq": "Iraq", "turkey": "Turkey",
        "türkiye": "Turkey", "syria": "Syria", "lebanon": "Lebanon", "jordan": "Jordan",
        "israel": "Israel", "palestine": "Palestine", "saudi arabia": "Saudi Arabia",
        "united arab emirates": "United Arab Emirates", "uae": "United Arab Emirates",
        "qatar": "Qatar", "bahrain": "Bahrain", "kuwait": "Kuwait", "oman": "Oman",
        "yemen": "Yemen", "thailand": "Thailand", "vietnam": "Vietnam", "viet nam": "Vietnam",
        "laos": "Laos", "cambodia": "Cambodia", "myanmar": "Myanmar", "burma": "Myanmar",
        "malaysia": "Malaysia", "singapore": "Singapore", "indonesia": "Indonesia",
        "philippines": "Philippines", "brunei": "Brunei", "timor-leste": "East Timor",
        "east timor": "East Timor",
        
        # Oceania
        "australia": "Australia", "new zealand": "New Zealand", "papua new guinea": "Papua New Guinea",
        "fiji": "Fiji", "solomon islands": "Solomon Islands", "vanuatu": "Vanuatu",
        "samoa": "Samoa", "tonga": "Tonga", "kiribati": "Kiribati", "tuvalu": "Tuvalu",
        "nauru": "Nauru", "palau": "Palau", "marshall islands": "Marshall Islands",
        "micronesia": "Micronesia"
    }
    
    # Check for multi-word country names first (longer matches have priority)
    sorted_keywords = sorted(country_keywords.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword in text_lower:
            return country_keywords[keyword]
    
    return None


