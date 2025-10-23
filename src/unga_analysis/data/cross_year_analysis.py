"""
Cross-year analysis module for UNGA speeches.
Refactored into modular structure for better maintainability.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .simple_vector_storage import simple_vector_storage as db_manager
from .data_ingestion import data_ingestion_manager
from .cross_year_queries import CrossYearQueryManager
from ..core.llm import run_analysis, get_available_models
from ..core.enhanced_search_engine import get_enhanced_search_engine

logger = logging.getLogger(__name__)

class CrossYearAnalysisManager:
    """Manages cross-year analysis of UNGA speeches."""
    
    def __init__(self):
        self.db_manager = db_manager
        self.data_ingestion = data_ingestion_manager
        self.query_manager = CrossYearQueryManager()
    
    # Delegate query methods to the query manager
    def get_available_years(self) -> List[int]:
        """Get list of available years in the database."""
        return self.query_manager.get_available_years()
    
    def get_available_countries_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Get available countries for a specific year."""
        return self.query_manager.get_available_countries_by_year(year)
    
    def get_available_regions(self) -> List[str]:
        """Get list of available regions."""
        return self.query_manager.get_available_regions()
    
    def get_historical_speeches(self, 
                               countries: Optional[List[str]] = None,
                               years: Optional[List[int]] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical speeches with optional filters."""
        return self.query_manager.get_historical_speeches(countries, years, limit)
    
    def search_speeches_by_criteria(self,
                                   query_text: Optional[str] = None,
                                   countries: Optional[List[str]] = None,
                                   years: Optional[List[int]] = None,
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """Search speeches by multiple criteria."""
        return self.query_manager.search_speeches_by_criteria(
            query_text, countries, years, limit
        )
    
    def get_speeches_for_analysis(self,
                                 countries: List[str],
                                 years: List[int],
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get speeches specifically for analysis."""
        return self.query_manager.get_speeches_for_analysis(countries, years, limit)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data."""
        return self.query_manager.get_data_summary()
    
    def analyze_cross_year_trends(self,
                                 countries: List[str],
                                 years: List[int],
                                 analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze cross-year trends."""
        try:
            # Get speeches for analysis
            speeches = self.get_speeches_for_analysis(countries, years)
            
            if not speeches:
                return {"error": "No speeches found for analysis"}
            
            # Perform trend analysis
            trends = self._calculate_trends(speeches, years)
            
            return {
                "trends": trends,
                "speech_count": len(speeches),
                "countries": countries,
                "years": years,
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-year trends: {e}")
            return {"error": str(e)}
    
    def analyze_semantic_trends(self,
                              query_text: str,
                              countries: List[str],
                              years: List[int]) -> Dict[str, Any]:
        """Analyze semantic trends across years."""
        try:
            # Get speeches matching the query
            speeches = self.search_speeches_by_criteria(
                query_text=query_text,
                countries=countries,
                years=years
            )
            
            if not speeches:
                return {"error": "No speeches found matching the query"}
            
            # Analyze semantic trends
            semantic_analysis = self._analyze_semantic_content(speeches, years)
            
            return {
                "semantic_analysis": semantic_analysis,
                "speech_count": len(speeches),
                "query": query_text,
                "countries": countries,
                "years": years
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze semantic trends: {e}")
            return {"error": str(e)}
    
    def get_analysis_suggestions(self,
                                countries: List[str],
                                years: List[int]) -> List[str]:
        """Get analysis suggestions based on available data."""
        try:
            # Get data summary
            summary = self.get_data_summary()
            
            suggestions = []
            
            # Add suggestions based on available data
            if summary.get('total_speeches', 0) > 100:
                suggestions.append("Comprehensive trend analysis across selected years")
            
            if len(countries) > 1:
                suggestions.append("Comparative analysis between countries")
            
            if len(years) > 3:
                suggestions.append("Long-term trend analysis")
            
            # Add topic-based suggestions
            suggestions.extend([
                "Climate change and environmental policies",
                "Peace and security issues",
                "Economic development and cooperation",
                "Human rights and social issues",
                "Sustainable development goals"
            ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Failed to get analysis suggestions: {e}")
            return ["General speech analysis"]
    
    def _calculate_trends(self, speeches: List[Dict[str, Any]], years: List[int]) -> Dict[str, Any]:
        """Calculate trends from speeches data."""
        try:
            # Group speeches by year
            speeches_by_year = {}
            for speech in speeches:
                year = speech.get('year')
                if year not in speeches_by_year:
                    speeches_by_year[year] = []
                speeches_by_year[year].append(speech)
            
            # Calculate basic trends
            trends = {
                "speech_counts": {year: len(speeches_by_year.get(year, [])) for year in years},
                "word_counts": {year: sum(s.get('word_count', 0) for s in speeches_by_year.get(year, [])) for year in years},
                "countries_per_year": {year: len(set(s.get('country_name') for s in speeches_by_year.get(year, []))) for year in years}
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to calculate trends: {e}")
            return {}
    
    def _analyze_semantic_content(self, speeches: List[Dict[str, Any]], years: List[int]) -> Dict[str, Any]:
        """Analyze semantic content of speeches."""
        try:
            # Basic semantic analysis
            semantic_analysis = {
                "total_speeches": len(speeches),
                "year_distribution": {},
                "content_themes": []
            }
            
            # Group by year
            for year in years:
                year_speeches = [s for s in speeches if s.get('year') == year]
                semantic_analysis["year_distribution"][year] = len(year_speeches)
            
            # Extract basic themes (simplified)
            common_themes = [
                "peace", "security", "development", "climate", "human rights",
                "cooperation", "sustainability", "equality", "justice"
            ]
            
            semantic_analysis["content_themes"] = common_themes[:5]
            
            return semantic_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze semantic content: {e}")
            return {}

# Create a global instance for backward compatibility
cross_year_manager = CrossYearAnalysisManager()