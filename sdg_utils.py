"""
SDG detection utilities.
"""

import re
from typing import List, Set

# SDG mapping with various ways they might be referenced
SDG_MAPPINGS = {
    # SDG 1: No Poverty
    1: [
        "sdg 1", "goal 1", "sustainable development goal 1",
        "no poverty", "poverty eradication", "poverty reduction",
        "ending poverty", "eradicate poverty"
    ],
    # SDG 2: Zero Hunger
    2: [
        "sdg 2", "goal 2", "sustainable development goal 2",
        "zero hunger", "hunger", "food security", "malnutrition",
        "undernourishment", "famine"
    ],
    # SDG 3: Good Health and Well-being
    3: [
        "sdg 3", "goal 3", "sustainable development goal 3",
        "good health", "well-being", "wellbeing", "health care",
        "universal health", "maternal health", "child health",
        "hiv/aids", "tuberculosis", "malaria", "non-communicable diseases"
    ],
    # SDG 4: Quality Education
    4: [
        "sdg 4", "goal 4", "sustainable development goal 4",
        "quality education", "education", "learning", "literacy",
        "primary education", "secondary education", "tertiary education"
    ],
    # SDG 5: Gender Equality
    5: [
        "sdg 5", "goal 5", "sustainable development goal 5",
        "gender equality", "gender equity", "women's empowerment",
        "women empowerment", "girls' education", "violence against women",
        "gender-based violence", "gender discrimination"
    ],
    # SDG 6: Clean Water and Sanitation
    6: [
        "sdg 6", "goal 6", "sustainable development goal 6",
        "clean water", "sanitation", "water and sanitation",
        "safe drinking water", "water scarcity", "water management"
    ],
    # SDG 7: Affordable and Clean Energy
    7: [
        "sdg 7", "goal 7", "sustainable development goal 7",
        "affordable energy", "clean energy", "renewable energy",
        "energy access", "energy poverty", "solar energy",
        "wind energy", "hydroelectric"
    ],
    # SDG 8: Decent Work and Economic Growth
    8: [
        "sdg 8", "goal 8", "sustainable development goal 8",
        "decent work", "economic growth", "employment",
        "unemployment", "labor rights", "worker rights",
        "economic productivity", "job creation"
    ],
    # SDG 9: Industry, Innovation and Infrastructure
    9: [
        "sdg 9", "goal 9", "sustainable development goal 9",
        "industry", "innovation", "infrastructure",
        "manufacturing", "technological development",
        "research and development", "rd&d", "r&d"
    ],
    # SDG 10: Reduced Inequalities
    10: [
        "sdg 10", "goal 10", "sustainable development goal 10",
        "reduced inequalities", "inequality", "inequalities",
        "income inequality", "social inclusion", "migration",
        "refugees", "displacement"
    ],
    # SDG 11: Sustainable Cities and Communities
    11: [
        "sdg 11", "goal 11", "sustainable development goal 11",
        "sustainable cities", "sustainable communities",
        "urban development", "urbanization", "slums",
        "urban planning", "smart cities"
    ],
    # SDG 12: Responsible Consumption and Production
    12: [
        "sdg 12", "goal 12", "sustainable development goal 12",
        "responsible consumption", "responsible production",
        "sustainable consumption", "sustainable production",
        "waste management", "recycling", "circular economy"
    ],
    # SDG 13: Climate Action
    13: [
        "sdg 13", "goal 13", "sustainable development goal 13",
        "climate action", "climate change", "global warming",
        "greenhouse gases", "carbon emissions", "climate adaptation",
        "climate mitigation", "paris agreement"
    ],
    # SDG 14: Life Below Water
    14: [
        "sdg 14", "goal 14", "sustainable development goal 14",
        "life below water", "ocean", "marine", "sea",
        "marine conservation", "ocean acidification",
        "marine pollution", "overfishing", "coral reefs"
    ],
    # SDG 15: Life on Land
    15: [
        "sdg 15", "goal 15", "sustainable development goal 15",
        "life on land", "biodiversity", "ecosystems",
        "deforestation", "desertification", "land degradation",
        "wildlife conservation", "forests"
    ],
    # SDG 16: Peace, Justice and Strong Institutions
    16: [
        "sdg 16", "goal 16", "sustainable development goal 16",
        "peace", "justice", "strong institutions", "rule of law",
        "corruption", "transparency", "accountability",
        "human rights", "access to justice"
    ],
    # SDG 17: Partnerships for the Goals
    17: [
        "sdg 17", "goal 17", "sustainable development goal 17",
        "partnerships", "global partnership", "south-south cooperation",
        "triangular cooperation", "technology transfer",
        "capacity building", "trade", "finance", "debt"
    ]
}

def extract_sdgs(text: str) -> List[int]:
    """
    Extract SDG numbers from text based on explicit mentions.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of SDG numbers (1-17) that are explicitly mentioned
    """
    if not text:
        return []
    
    text_lower = text.lower()
    mentioned_sdgs = set()
    
    # Look for explicit SDG mentions
    for sdg_num, keywords in SDG_MAPPINGS.items():
        for keyword in keywords:
            if keyword in text_lower:
                mentioned_sdgs.add(sdg_num)
                break
    
    return sorted(list(mentioned_sdgs))

def format_sdgs(sdg_list: List[int]) -> str:
    """
    Format SDG list for display.
    
    Args:
        sdg_list: List of SDG numbers
        
    Returns:
        Formatted string of SDGs
    """
    if not sdg_list:
        return "None mentioned"
    
    return ", ".join([f"SDG {num}" for num in sdg_list])

def detect_africa_mention(text: str) -> bool:
    """
    Detect if Africa is explicitly mentioned in the text.
    
    Args:
        text: Text to analyze
        
    Returns:
        True if Africa is mentioned, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Africa-related keywords
    africa_keywords = [
        "africa", "african", "sub-saharan", "subsaharan",
        "north africa", "west africa", "east africa",
        "southern africa", "central africa",
        "african union", "au", "african development bank",
        "african continent", "continent of africa"
    ]
    
    return any(keyword in text_lower for keyword in africa_keywords)

def get_sdg_descriptions() -> dict:
    """
    Get SDG descriptions for reference.
    
    Returns:
        Dictionary mapping SDG numbers to descriptions
    """
    return {
        1: "No Poverty",
        2: "Zero Hunger", 
        3: "Good Health and Well-being",
        4: "Quality Education",
        5: "Gender Equality",
        6: "Clean Water and Sanitation",
        7: "Affordable and Clean Energy",
        8: "Decent Work and Economic Growth",
        9: "Industry, Innovation and Infrastructure",
        10: "Reduced Inequalities",
        11: "Sustainable Cities and Communities",
        12: "Responsible Consumption and Production",
        13: "Climate Action",
        14: "Life Below Water",
        15: "Life on Land",
        16: "Peace, Justice and Strong Institutions",
        17: "Partnerships for the Goals"
    }
