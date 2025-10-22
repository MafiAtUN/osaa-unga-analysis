"""
Country selection component
"""

import streamlit as st
from typing import Tuple, Optional
from src.unga_analysis.config.countries import get_all_countries
from src.unga_analysis.core.classify import get_au_members
from datetime import date


def render_country_selection() -> Tuple[str, Optional[date], Optional[str]]:
    """Render country selection section."""
    # Get comprehensive list of all world countries and entities
    all_countries = get_all_countries()
    
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


