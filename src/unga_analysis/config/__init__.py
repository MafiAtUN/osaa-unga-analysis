"""
Configuration modules for UNGA Analysis
"""

from .countries import get_all_countries, detect_country_simple
from .questions import (
    get_suggestion_questions,
    get_cross_year_topics_and_questions,
    get_country_and_group_questions
)

__all__ = [
    'get_all_countries',
    'detect_country_simple',
    'get_suggestion_questions',
    'get_cross_year_topics_and_questions',
    'get_country_and_group_questions',
]
