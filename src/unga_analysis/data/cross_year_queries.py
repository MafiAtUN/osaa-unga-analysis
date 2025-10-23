"""
Cross-year query functions for UNGA Analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from .simple_vector_storage import simple_vector_storage as db_manager

logger = logging.getLogger(__name__)

class CrossYearQueryManager:
    """Manages cross-year queries and data retrieval."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def get_available_years(self) -> List[int]:
        """Get list of available years in the database."""
        try:
            stats = self.db_manager.get_speech_statistics()
            return sorted(stats.get('year_statistics', {}).keys())
        except Exception as e:
            logger.error(f"Failed to get available years: {e}")
            return []
    
    def get_available_countries_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Get available countries for a specific year."""
        try:
            return self.db_manager.get_speech_data_by_country(year=year)
        except Exception as e:
            logger.error(f"Failed to get countries for year {year}: {e}")
            return []
    
    def get_available_regions(self) -> List[str]:
        """Get list of available regions."""
        try:
            stats = self.db_manager.get_speech_statistics()
            return sorted(stats.get('region_statistics', {}).keys())
        except Exception as e:
            logger.error(f"Failed to get available regions: {e}")
            return []
    
    def get_historical_speeches(self, 
                               countries: Optional[List[str]] = None,
                               years: Optional[List[int]] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical speeches with optional filters."""
        try:
            return self.db_manager.search_speeches(
                countries=countries,
                years=years,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get historical speeches: {e}")
            return []
    
    def search_speeches_by_criteria(self,
                                   query_text: Optional[str] = None,
                                   countries: Optional[List[str]] = None,
                                   years: Optional[List[int]] = None,
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """Search speeches by multiple criteria."""
        try:
            return self.db_manager.search_speeches(
                query_text=query_text,
                countries=countries,
                years=years,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to search speeches by criteria: {e}")
            return []
    
    def get_speeches_for_analysis(self,
                                 countries: List[str],
                                 years: List[int],
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get speeches specifically for analysis."""
        try:
            return self.db_manager.search_speeches(
                countries=countries,
                years=years,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get speeches for analysis: {e}")
            return []
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data."""
        try:
            return self.db_manager.get_speech_statistics()
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            return {}
