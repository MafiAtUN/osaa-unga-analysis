"""
Classification logic for African Member States vs Development Partners.
"""

from typing import List

# African Union member states (55 members)
AU_MEMBERS = {
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo", "Côte d'Ivoire",
    "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea",
    "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
    "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
    "Nigeria", "Rwanda", "Sahrawi Arab Democratic Republic", "São Tomé and Príncipe",
    "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan",
    "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
}

# Alternative names and common variations
AU_MEMBER_ALIASES = {
    "United Republic of Tanzania": "Tanzania",
    "DRC": "Democratic Republic of the Congo",
    "DR Congo": "Democratic Republic of the Congo",
    "Congo (Democratic Republic)": "Democratic Republic of the Congo",
    "Congo (DRC)": "Democratic Republic of the Congo",
    "Republic of the Congo": "Congo",
    "Congo (Republic)": "Congo",
    "Cabo Verde": "Cape Verde",
    "Côte d'Ivoire": "Ivory Coast",
    "Eswatini": "Swaziland",
    "Sahrawi Arab Democratic Republic": "Western Sahara",
    "São Tomé and Príncipe": "Sao Tome and Principe"
}

# Special entities that should be classified as Development Partners
DEVELOPMENT_PARTNER_ENTITIES = {
    "Secretary-General", "President of the General Assembly", "PGA",
    "UN Secretary-General", "UN SG", "SG"
}

def normalize_country_name(country: str) -> str:
    """Normalize country name for matching."""
    if not country:
        return ""
    
    country = country.strip()
    
    # Check aliases first
    if country in AU_MEMBER_ALIASES:
        return AU_MEMBER_ALIASES[country]
    
    return country

def infer_classification(country: str) -> str:
    """
    Infer classification based on country/entity name.
    
    Args:
        country: Country or entity name
        
    Returns:
        "African Member State" or "Development Partner"
    """
    if not country:
        return "Development Partner"
    
    country = normalize_country_name(country)
    
    # Check for special entities first
    if country in DEVELOPMENT_PARTNER_ENTITIES:
        return "Development Partner"
    
    # Check if it's an AU member
    if country in AU_MEMBERS:
        return "African Member State"
    
    # Default to Development Partner
    return "Development Partner"

def is_african_member_state(country: str) -> bool:
    """Check if country is an African Member State."""
    return infer_classification(country) == "African Member State"

def get_au_members() -> List[str]:
    """Get the list of AU member states."""
    return sorted(AU_MEMBERS)

