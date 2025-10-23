"""
Centralized country management for the UNGA Analysis app.
This ensures all country lists are consistent across the application.
"""

from typing import List, Dict, Any
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager


class CountryManager:
    """Centralized country management for consistent country lists across the app."""
    
    def __init__(self):
        self.db_manager = db_manager
        self._countries_cache = None
        self._countries_by_region_cache = None
    
    def get_all_countries(self) -> List[str]:
        """Get comprehensive list of all countries from the database."""
        if self._countries_cache is None:
            try:
                result = self.db_manager.conn.execute(
                    "SELECT DISTINCT country_name FROM speeches WHERE country_name IS NOT NULL ORDER BY country_name"
                ).fetchall()
                self._countries_cache = [row[0] for row in result]
            except Exception as e:
                print(f"Error getting countries from database: {e}")
                # Fallback to config if database fails
                from src.unga_analysis.config.countries import get_all_countries
                self._countries_cache = get_all_countries()
        
        return self._countries_cache
    
    def get_countries_by_region(self, region: str = None) -> Dict[str, List[str]]:
        """Get countries grouped by region."""
        if self._countries_by_region_cache is None:
            try:
                # Get countries with their regions from database
                result = self.db_manager.conn.execute("""
                    SELECT DISTINCT country_name, region 
                    FROM speeches 
                    WHERE country_name IS NOT NULL AND region IS NOT NULL 
                    ORDER BY region, country_name
                """).fetchall()
                
                self._countries_by_region_cache = {}
                for country_name, region in result:
                    if region not in self._countries_by_region_cache:
                        self._countries_by_region_cache[region] = []
                    if country_name not in self._countries_by_region_cache[region]:
                        self._countries_by_region_cache[region].append(country_name)
                
                # Sort countries within each region
                for region in self._countries_by_region_cache:
                    self._countries_by_region_cache[region].sort()
                    
            except Exception as e:
                print(f"Error getting countries by region: {e}")
                # Fallback to simple country list
                all_countries = self.get_all_countries()
                self._countries_by_region_cache = {"All": all_countries}
        
        if region:
            return {region: self._countries_by_region_cache.get(region, [])}
        else:
            return self._countries_by_region_cache
    
    def get_african_countries(self) -> List[str]:
        """Get list of African countries."""
        try:
            result = self.db_manager.conn.execute("""
                SELECT DISTINCT country_name 
                FROM speeches 
                WHERE country_name IS NOT NULL AND is_african_member = true 
                ORDER BY country_name
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            print(f"Error getting African countries: {e}")
            return []
    
    def get_development_partners(self) -> List[str]:
        """Get list of development partner countries."""
        try:
            result = self.db_manager.conn.execute("""
                SELECT DISTINCT country_name 
                FROM speeches 
                WHERE country_name IS NOT NULL AND is_african_member = false 
                ORDER BY country_name
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            print(f"Error getting development partners: {e}")
            return []
    
    def search_countries(self, query: str) -> List[str]:
        """Search for countries matching a query."""
        all_countries = self.get_all_countries()
        query_lower = query.lower()
        return [country for country in all_countries if query_lower in country.lower()]
    
    def get_country_stats(self) -> Dict[str, Any]:
        """Get statistics about countries in the database."""
        try:
            total_countries = len(self.get_all_countries())
            african_countries = len(self.get_african_countries())
            development_partners = len(self.get_development_partners())
            
            return {
                "total_countries": total_countries,
                "african_countries": african_countries,
                "development_partners": development_partners,
                "other_countries": total_countries - african_countries - development_partners
            }
        except Exception as e:
            print(f"Error getting country stats: {e}")
            return {}
    
    def clear_cache(self):
        """Clear the country cache to force refresh."""
        self._countries_cache = None
        self._countries_by_region_cache = None


# Global instance
country_manager = CountryManager()


def get_all_countries() -> List[str]:
    """Get all countries - convenience function."""
    return country_manager.get_all_countries()


def get_african_countries() -> List[str]:
    """Get African countries - convenience function."""
    return country_manager.get_african_countries()


def get_development_partners() -> List[str]:
    """Get development partner countries - convenience function."""
    return country_manager.get_development_partners()


def get_countries_by_region(region: str = None) -> Dict[str, List[str]]:
    """Get countries by region - convenience function."""
    return country_manager.get_countries_by_region(region)
