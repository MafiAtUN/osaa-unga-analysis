"""
Cross-year analysis module for UNGA speeches.
Provides advanced querying and analysis capabilities across multiple years.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from .simple_vector_storage import simple_vector_storage as db_manager
from .data_ingestion import data_ingestion_manager
from ..core.llm import run_analysis, get_available_models
from ..core.enhanced_search_engine import get_enhanced_search_engine
from openai import AzureOpenAI
import os

logger = logging.getLogger(__name__)

class CrossYearAnalysisManager:
    """Manages cross-year analysis of UNGA speeches."""
    
    def __init__(self):
        self.db_manager = db_manager
        self.data_ingestion = data_ingestion_manager
    
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
    
    def search_speeches_by_criteria(self, query_text: str = None, 
                                  countries: List[str] = None,
                                  years: List[int] = None,
                                  regions: List[str] = None,
                                  african_members_only: bool = False,
                                  use_semantic_search: bool = False) -> List[Dict[str, Any]]:
        """
        Search speeches by multiple criteria with comprehensive coverage.
        
        Args:
            query_text: Text to search for in speeches (semantic search)
            countries: List of country codes to filter by
            years: List of years to filter by
            regions: List of regions to filter by
            african_members_only: If True, only include African Union members
            use_semantic_search: If True, use vector similarity search
            
        Returns:
            List of matching speeches with comprehensive coverage
        """
        try:
            # For comprehensive analysis, we need to ensure we get ALL relevant speeches
            # Use a multi-step approach to get complete coverage
            
            speeches = []
            
            # Step 1: Try to get comprehensive results with high limit
            if use_semantic_search:
                try:
                    # Use semantic search for better results
                    speeches = self.db_manager.semantic_search(
                        query_text=query_text or "general speech content",
                        countries=countries,
                        years=years,
                        regions=regions,
                        limit=5000  # Much higher limit for comprehensive coverage
                    )
                except Exception as e:
                    logger.warning(f"Semantic search failed: {e}")
                    # Fall back to traditional text search
                    speeches = self.db_manager.search_speeches(
                        query_text=query_text,
                        countries=countries,
                        years=years,
                        regions=regions,
                        limit=5000  # Much higher limit
                    )
            else:
                # Use traditional text search with high limit
                speeches = self.db_manager.search_speeches(
                    query_text=query_text,
                    countries=countries,
                    years=years,
                    regions=regions,
                    limit=5000  # Much higher limit for comprehensive coverage
                )
            
            # Step 2: If we have specific countries, ensure we get ALL their speeches
            if countries and len(speeches) < 100:  # If we got very few results
                logger.info(f"Got only {len(speeches)} speeches, trying comprehensive search for countries: {countries}")
                
                # Try without year/region filters to get all speeches for these countries
                all_country_speeches = self.db_manager.search_speeches(
                    countries=countries,
                    limit=10000  # Get all speeches for these countries
                )
                
                # Filter by years and regions if specified
                if years or regions:
                    filtered_speeches = []
                    for speech in all_country_speeches:
                        include = True
                        if years and speech.get('year') not in years:
                            include = False
                        if regions and speech.get('region') not in regions:
                            include = False
                        if include:
                            filtered_speeches.append(speech)
                    all_country_speeches = filtered_speeches
                
                # Use the comprehensive results if we got more
                if len(all_country_speeches) > len(speeches):
                    speeches = all_country_speeches
                    logger.info(f"Comprehensive search found {len(speeches)} speeches")
            
            # Step 3: If we have specific years, ensure we get good coverage across years
            if years and len(years) > 10:  # For large year ranges
                # Group speeches by year to check coverage
                year_coverage = {}
                for speech in speeches:
                    year = speech.get('year')
                    if year in years:
                        if year not in year_coverage:
                            year_coverage[year] = []
                        year_coverage[year].append(speech)
                
                # If we're missing many years, try to get more comprehensive results
                missing_years = [year for year in years if year not in year_coverage or len(year_coverage[year]) < 2]
                if len(missing_years) > len(years) * 0.3:  # If missing more than 30% of years
                    logger.info(f"Missing coverage for {len(missing_years)} years, trying broader search")
                    
                    # Try a broader search without country filters
                    broader_speeches = self.db_manager.search_speeches(
                        years=years,
                        regions=regions,
                        limit=10000
                    )
                    
                    # Filter by countries if specified
                    if countries:
                        broader_speeches = [s for s in broader_speeches if s.get('country_name') in countries or s.get('country_code') in countries]
                    
                    # Use broader results if we got better coverage
                    if len(broader_speeches) > len(speeches):
                        speeches = broader_speeches
                        logger.info(f"Broader search found {len(speeches)} speeches with better year coverage")
            
            # Filter by African members if requested
            if african_members_only:
                speeches = [s for s in speeches if s.get('is_african_member', False)]
            
            logger.info(f"Final search result: {len(speeches)} speeches")
            return speeches
            
        except Exception as e:
            logger.error(f"Failed to search speeches: {e}")
            return []
    
    def get_historical_speeches(self, country_name: str, num_years: int = 5) -> List[Dict[str, Any]]:
        """Get historical speeches for a country using the vector database."""
        try:
            # Get speeches for the country from the database
            speeches = self.db_manager.search_speeches(
                countries=[country_name],
                limit=50  # Get more speeches to filter by recent years
            )
            
            # Filter by recent years and sort by year descending
            recent_speeches = []
            current_year = datetime.now().year
            
            for speech in speeches:
                year = speech.get('year', 0)
                if current_year - year <= num_years:
                    recent_speeches.append(speech)
            
            # Sort by year descending (most recent first)
            recent_speeches.sort(key=lambda x: x.get('year', 0), reverse=True)
            
            return recent_speeches[:10]  # Return top 10 most recent
            
        except Exception as e:
            logger.error(f"Failed to get historical speeches for {country_name}: {e}")
            return []
    
    def search_by_text_content(self, query_text: str, years: List[int] = None, 
                             regions: List[str] = None, limit: int = 10000) -> List[Dict[str, Any]]:
        """
        Search for speeches containing specific text content across all countries.
        This is essential for questions like "how many countries mentioned CEDAW".
        """
        try:
            logger.info(f"Searching for text '{query_text}' across all speeches")
            
            # Search for speeches containing the query text
            speeches = self.db_manager.search_speeches(
                query_text=query_text,
                years=years,
                regions=regions,
                limit=limit
            )
            
            logger.info(f"Found {len(speeches)} speeches containing '{query_text}'")
            return speeches
            
        except Exception as e:
            logger.error(f"Failed to search by text content: {e}")
            return []

    def get_comprehensive_speeches(self, countries: List[str] = None, 
                                 years: List[int] = None, regions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get comprehensive speech data ensuring complete coverage for analysis.
        This function prioritizes completeness over speed.
        """
        try:
            all_speeches = []
            
            # If we have specific countries, get ALL their speeches
            if countries:
                for country in countries:
                    logger.info(f"Getting all speeches for {country}")
                    country_speeches = self.db_manager.search_speeches(
                        countries=[country],
                        limit=10000  # Get all speeches for this country
                    )
                    
                    # Filter by years and regions if specified
                    if years or regions:
                        filtered_speeches = []
                        for speech in country_speeches:
                            include = True
                            if years and speech.get('year') not in years:
                                include = False
                            if regions and speech.get('region') not in regions:
                                include = False
                            if include:
                                filtered_speeches.append(speech)
                        country_speeches = filtered_speeches
                    
                    all_speeches.extend(country_speeches)
                    logger.info(f"Found {len(country_speeches)} speeches for {country}")
            
            # If we have specific years but no countries, get comprehensive year coverage
            elif years:
                logger.info(f"Getting comprehensive coverage for years {min(years)}-{max(years)}")
                all_speeches = self.db_manager.search_speeches(
                    years=years,
                    regions=regions,
                    limit=10000
                )
            
            # If we have regions but no countries, get comprehensive regional coverage
            elif regions:
                logger.info(f"Getting comprehensive coverage for regions: {regions}")
                all_speeches = self.db_manager.search_speeches(
                    regions=regions,
                    limit=10000
                )
            
            # Remove duplicates based on speech ID
            seen_ids = set()
            unique_speeches = []
            for speech in all_speeches:
                speech_id = speech.get('id')
                if speech_id not in seen_ids:
                    seen_ids.add(speech_id)
                    unique_speeches.append(speech)
            
            logger.info(f"Comprehensive search found {len(unique_speeches)} unique speeches")
            return unique_speeches
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive speeches: {e}")
            return []

    def get_speeches_for_analysis(self, query: str, countries: List[str] = None,
                                 years: List[int] = None, regions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Smart function to determine the best search strategy based on the query type.
        """
        try:
            query_lower = query.lower()
            
            # Check if this is a text content search (e.g., "countries mentioned CEDAW")
            text_search_indicators = [
                'mentioned', 'mentioned by', 'countries that mentioned', 'speeches containing',
                'how many countries', 'which countries', 'countries that said',
                'references to', 'mentions of', 'discussed', 'talked about'
            ]
            
            # Check if query contains specific terms to search for
            search_terms = []
            for indicator in text_search_indicators:
                if indicator in query_lower:
                    # Extract potential search terms from the query
                    # Look for capitalized terms that might be what we're searching for
                    import re
                    capitalized_terms = re.findall(r'\b[A-Z][A-Z\s]+\b', query)
                    search_terms.extend(capitalized_terms)
                    break
            
            # If we found search terms, use text content search
            if search_terms:
                # Use the first search term found
                search_term = search_terms[0].strip()
                logger.info(f"Detected text content search for: '{search_term}'")
                return self.search_by_text_content(
                    query_text=search_term,
                    years=years,
                    regions=regions
                )
            
            # Otherwise, use comprehensive country/year search
            else:
                logger.info("Using comprehensive country/year search")
                return self.get_comprehensive_speeches(
                    countries=countries,
                    years=years,
                    regions=regions
                )
                
        except Exception as e:
            logger.error(f"Failed to determine search strategy: {e}")
            # Fallback to comprehensive search
            return self.get_comprehensive_speeches(
                countries=countries,
                years=years,
                regions=regions
            )

    def analyze_cross_year_trends(self, query: str, countries: List[str] = None,
                                years: List[int] = None, regions: List[str] = None) -> str:
        """
        Perform cross-year trend analysis using AI with enhanced search and proper citations.
        
        Args:
            query: The analysis query
            countries: List of country codes to analyze
            years: List of years to analyze
            regions: List of regions to analyze
            
        Returns:
            Analysis result as markdown with proper citations
        """
        try:
            # Use enhanced search engine for better results
            enhanced_search = get_enhanced_search_engine(self.db_manager)
            
            # Execute enhanced search with proper context
            search_results = enhanced_search.execute_enhanced_search(query)
            speeches = search_results.get('results', [])
            
            if not speeches:
                return "❌ No speeches found matching the specified criteria."
            
            # Prepare enhanced context with proper citations
            context = self._prepare_enhanced_analysis_context(speeches, query, search_results)
            
            # Generate structured tables with citations
            tables = self._generate_analysis_tables_with_citations(speeches, query)
            
            # Generate topic-specific tables with citations
            topic_tables = self._generate_topic_analysis_tables_with_citations(speeches, query)
            
            # Build enhanced analysis prompt with citation requirements
            system_prompt = """You are a UN OSAA expert analyst specializing in cross-year trend analysis of UN General Assembly speeches. 
            Analyze the provided speeches to identify patterns, trends, and insights across different years and countries.
            Provide comprehensive analysis with specific examples, data points, and structured tables when applicable.
            
            CRITICAL REQUIREMENTS:
            - ALWAYS cite specific speeches with country name and year when referencing content
            - Use proper citation format: "As stated by [Country] in [Year]: '[quote]'"
            - Provide specific examples with exact quotes and their sources
            - Include document references for all claims and statistics
            - When analyzing trends, cite multiple speeches from different years/countries
            
            IMPORTANT: When presenting data that can be organized in tables (such as country comparisons, year-over-year changes, 
            topic frequencies, etc.), always format them as markdown tables for better readability and analysis."""
            
            user_prompt = f"""
            Analysis Query: {query}
            
            Search Strategy Used: {search_results.get('strategy', 'unknown')}
            Query Analysis: {search_results.get('analysis', {})}
            
            Available Data with Citations:
            {context}
            
            Pre-generated Tables with Citations:
            {tables}
            
            Topic-Specific Tables with Citations:
            {topic_tables}
            
            Please provide a comprehensive analysis that includes:
            1. Key trends and patterns identified with proper citations
            2. Specific examples from the speeches with exact quotes and sources
            3. Comparative analysis across years/countries (use tables when comparing multiple entities)
            4. Statistical insights where applicable (present in table format when relevant)
            5. Conclusions and recommendations based on cited evidence
            
            FORMATTING REQUIREMENTS:
            - Use the pre-generated tables above as reference
            - Create additional markdown tables for any comparative data (countries, years, topics, etc.)
            - Include specific numbers, percentages, and statistics with proper citations
            - Structure data in clear, readable tables
            - Use headers like "Country", "Year", "Frequency", "Percentage", "Citation", etc.
            - When showing trends over time, use tables with years as columns and include citation columns
            - When comparing countries, use tables with countries as rows and include citation columns
            - ALWAYS include proper citations for all quoted material and statistical claims
            
            Format your response in clear, professional markdown with well-structured tables and proper citations.
            """
            
            # Get OpenAI client
            client = self._get_openai_client()
            if not client:
                return "❌ OpenAI client not available."
            
            # Run analysis
            result = run_analysis(
                system_prompt,
                user_prompt,
                model="model-router-osaa-2",
                client=client
            )
            
            return result if result else "❌ Analysis failed."
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-year trends: {e}")
            return f"❌ Analysis failed: {e}"
    
    def analyze_semantic_trends(self, theme_query: str, countries: List[str] = None,
                              years: List[int] = None, regions: List[str] = None) -> str:
        """
        Perform semantic trend analysis using vector similarity.
        
        Args:
            theme_query: The theme to analyze (e.g., "climate change", "gender equality")
            countries: List of country codes to analyze
            years: List of years to analyze
            regions: List of regions to analyze
            
        Returns:
            Analysis result as markdown
        """
        try:
            # Use smart search strategy based on query type
            speeches = self.get_speeches_for_analysis(
                query=theme_query,
                countries=countries,
                years=years,
                regions=regions
            )
            
            # If we have a theme query, filter speeches by relevance
            if theme_query and speeches:
                # For now, use text-based filtering for theme relevance
                # This is more reliable than the broken semantic search
                relevant_speeches = []
                theme_terms = theme_query.lower().split()
                
                for speech in speeches:
                    speech_text = speech.get('speech_text', '').lower()
                    # Check if any theme terms appear in the speech
                    if any(term in speech_text for term in theme_terms):
                        relevant_speeches.append(speech)
                
                # If we found relevant speeches, use them; otherwise use all speeches
                if relevant_speeches:
                    speeches = relevant_speeches
                    logger.info(f"Filtered to {len(speeches)} speeches relevant to theme: {theme_query}")
                else:
                    logger.info(f"No speeches found relevant to theme, using all {len(speeches)} speeches")
            
            if not speeches:
                return f"❌ No speeches found related to '{theme_query}'."
            
            # Group by year and analyze trends
            by_year = {}
            for speech in speeches:
                year = speech.get('year', 'Unknown')
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(speech)
            
            # Prepare context for AI analysis with structured data
            context = f"Found {len(speeches)} speeches related to '{theme_query}':\n\n"
            
            # Add summary statistics
            context += "## Summary Statistics\n\n"
            context += f"- **Total Speeches**: {len(speeches)}\n"
            context += f"- **Years Covered**: {len(by_year)} ({min(by_year.keys()) if by_year else 'N/A'} - {max(by_year.keys()) if by_year else 'N/A'})\n"
            context += f"- **Average Speeches per Year**: {len(speeches) / len(by_year) if by_year else 0:.1f}\n\n"
            
            # Add year-over-year trend table
            if by_year:
                context += "## Year-over-Year Trend\n\n"
                context += "| Year | Speech Count | Percentage of Total |\n"
                context += "|------|--------------|-------------------|\n"
                for year in sorted(by_year.keys()):
                    count = len(by_year[year])
                    percentage = (count / len(speeches)) * 100
                    context += f"| {year} | {count} | {percentage:.1f}% |\n"
                context += "\n"
            
            # Add detailed content by year
            for year in sorted(by_year.keys(), reverse=True):
                year_speeches = by_year[year]
                context += f"## {year} ({len(year_speeches)} speeches)\n\n"
                
                for speech in year_speeches[:3]:  # Limit to 3 speeches per year
                    country = speech.get('country_name', 'Unknown')
                    similarity = speech.get('similarity', 0)
                    text_preview = speech.get('speech_text', '')[:300] + "..." if len(speech.get('speech_text', '')) > 300 else speech.get('speech_text', '')
                    
                    context += f"**{country}** (similarity: {similarity:.3f}):\n"
                    context += f"{text_preview}\n\n"
            
            # Build analysis prompt
            system_prompt = f"""You are a UN OSAA expert analyst specializing in semantic trend analysis. 
            Analyze the provided speeches to identify how the theme '{theme_query}' has evolved over time.
            Focus on semantic similarities, thematic evolution, and cross-year patterns.
            
            IMPORTANT: When presenting data that can be organized in tables (such as year-over-year trends, 
            country comparisons, similarity scores, etc.), always format them as markdown tables for better readability."""
            
            user_prompt = f"""
            Theme Analysis: {theme_query}
            
            Speech Data:
            {context}
            
            Please provide a comprehensive analysis that includes:
            1. How the theme has evolved semantically over time (use tables for year-over-year trends)
            2. Key patterns and trends in the speeches
            3. Similarity scores and their significance (present in table format)
            4. Cross-year thematic evolution
            5. Regional or country-specific patterns (use tables for comparisons)
            6. Conclusions and insights
            
            FORMATTING REQUIREMENTS:
            - Use markdown tables for any comparative data (years, countries, similarity scores, etc.)
            - Include specific numbers, percentages, and statistics
            - Structure data in clear, readable tables
            - Use headers like "Year", "Country", "Similarity Score", "Percentage", etc.
            - When showing trends over time, use tables with years as rows
            - When comparing countries, use tables with countries as rows
            
            Format your response in clear, professional markdown with well-structured tables.
            """
            
            # Get OpenAI client and run analysis
            client = self._get_openai_client()
            if not client:
                return "❌ OpenAI client not available."
            
            result = run_analysis(
                system_prompt,
                user_prompt,
                model="model-router-osaa-2",
                client=client
            )
            
            return result if result else "❌ Semantic analysis failed."
            
        except Exception as e:
            logger.error(f"Failed to analyze semantic trends: {e}")
            return f"❌ Semantic analysis failed: {e}"
    
    def _prepare_enhanced_analysis_context(self, speeches: List[Dict[str, Any]], query: str, search_results: Dict[str, Any]) -> str:
        """Prepare enhanced analysis context with proper citations."""
        context = f"Found {len(speeches)} speeches for analysis:\n\n"
        
        # Group by year and country for better organization
        by_year = {}
        by_country = {}
        year_country_matrix = {}
        
        for speech in speeches:
            year = speech.get('year', 'Unknown')
            country = speech.get('country_name', 'Unknown')
            citation = speech.get('citation', f"{country}, {year}")
            
            # Group by year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(speech)
            
            # Group by country
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(speech)
            
            # Create year-country matrix
            if year not in year_country_matrix:
                year_country_matrix[year] = {}
            if country not in year_country_matrix[year]:
                year_country_matrix[year][country] = {'count': 0, 'citations': []}
            year_country_matrix[year][country]['count'] += 1
            year_country_matrix[year][country]['citations'].append(citation)
        
        # Add summary statistics with citations
        context += "## Summary Statistics\n\n"
        context += f"- **Total Speeches**: {len(speeches)}\n"
        context += f"- **Years Covered**: {len(by_year)} ({min(by_year.keys()) if by_year else 'N/A'} - {max(by_year.keys()) if by_year else 'N/A'})\n"
        context += f"- **Countries**: {len(by_country)}\n"
        context += f"- **Average Speeches per Year**: {len(speeches) / len(by_year) if by_year else 0:.1f}\n\n"
        
        # Add year-country matrix as a table with citations
        if year_country_matrix:
            context += "## Speeches by Year and Country (with Citations)\n\n"
            context += "| Year | " + " | ".join(sorted(by_country.keys())[:8]) + " | Total |\n"  # Limit to 8 countries for readability
            context += "|------|" + "|".join(["------" for _ in range(min(8, len(by_country)))]) + "|-------|\n"
            
            for year in sorted(by_year.keys(), reverse=True):
                row = f"| {year} |"
                year_total = 0
                for country in sorted(by_country.keys())[:8]:
                    count = year_country_matrix[year].get(country, {'count': 0})['count']
                    row += f" {count} |"
                    year_total += count
                row += f" {year_total} |\n"
                context += row
            context += "\n"
        
        # Add top countries by speech count with citations
        if by_country:
            context += "## Top Countries by Speech Count (with Citations)\n\n"
            sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
            context += "| Country | Speech Count | Percentage | Sample Citations |\n"
            context += "|---------|--------------|------------|------------------|\n"
            for country, country_speeches in sorted_countries[:10]:
                percentage = (len(country_speeches) / len(speeches)) * 100
                sample_citations = [s.get('citation', f"{country}, {s.get('year', 'Unknown')}") for s in country_speeches[:3]]
                citations_str = "; ".join(sample_citations)
                context += f"| {country} | {len(country_speeches)} | {percentage:.1f}% | {citations_str} |\n"
            context += "\n"
        
        # Add detailed speech content with proper citations
        context += "## Sample Speech Content with Citations\n\n"
        for year in sorted(by_year.keys(), reverse=True)[:3]:  # Limit to 3 most recent years
            year_speeches = by_year[year]
            context += f"### {year} ({len(year_speeches)} speeches)\n\n"
            
            for speech in year_speeches[:3]:  # Limit to 3 speeches per year
                country = speech.get('country_name', 'Unknown')
                word_count = speech.get('word_count', 0)
                citation = speech.get('citation', f"{country}, {year}")
                text_preview = speech.get('speech_text', '')[:300] + "..." if len(speech.get('speech_text', '')) > 300 else speech.get('speech_text', '')
                relevant_quotes = speech.get('relevant_quotes', [])
                
                context += f"**{citation}** ({word_count:,} words):\n"
                context += f"{text_preview}\n\n"
                
                # Add relevant quotes with citations
                if relevant_quotes:
                    context += f"**Relevant Quotes from {citation}:**\n"
                    for quote in relevant_quotes[:2]:  # Top 2 quotes
                        context += f"- \"{quote['quote']}\" (Relevance: {quote['relevance_score']:.2f})\n"
                    context += "\n"
        
        return context
    
    def _prepare_analysis_context(self, speeches: List[Dict[str, Any]], query: str) -> str:
        """Prepare context for AI analysis from speeches with structured data."""
        context = f"Found {len(speeches)} speeches for analysis:\n\n"
        
        # Group by year and country for better organization
        by_year = {}
        by_country = {}
        year_country_matrix = {}
        
        for speech in speeches:
            year = speech.get('year', 'Unknown')
            country = speech.get('country_name', 'Unknown')
            
            # Group by year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(speech)
            
            # Group by country
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(speech)
            
            # Create year-country matrix
            if year not in year_country_matrix:
                year_country_matrix[year] = {}
            if country not in year_country_matrix[year]:
                year_country_matrix[year][country] = 0
            year_country_matrix[year][country] += 1
        
        # Add summary statistics
        context += "## Summary Statistics\n\n"
        context += f"- **Total Speeches**: {len(speeches)}\n"
        context += f"- **Years Covered**: {len(by_year)} ({min(by_year.keys()) if by_year else 'N/A'} - {max(by_year.keys()) if by_year else 'N/A'})\n"
        context += f"- **Countries**: {len(by_country)}\n"
        context += f"- **Average Speeches per Year**: {len(speeches) / len(by_year) if by_year else 0:.1f}\n\n"
        
        # Add year-country matrix as a table
        if year_country_matrix:
            context += "## Speeches by Year and Country\n\n"
            context += "| Year | " + " | ".join(sorted(by_country.keys())[:10]) + " | Total |\n"  # Limit to 10 countries for readability
            context += "|------|" + "|".join(["------" for _ in range(min(10, len(by_country)))]) + "|-------|\n"
            
            for year in sorted(by_year.keys(), reverse=True):
                row = f"| {year} |"
                year_total = 0
                for country in sorted(by_country.keys())[:10]:
                    count = year_country_matrix[year].get(country, 0)
                    row += f" {count} |"
                    year_total += count
                row += f" {year_total} |\n"
                context += row
            context += "\n"
        
        # Add top countries by speech count
        if by_country:
            context += "## Top Countries by Speech Count\n\n"
            sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
            context += "| Country | Speech Count | Percentage |\n"
            context += "|---------|--------------|------------|\n"
            for country, country_speeches in sorted_countries[:10]:
                percentage = (len(country_speeches) / len(speeches)) * 100
                context += f"| {country} | {len(country_speeches)} | {percentage:.1f}% |\n"
            context += "\n"
        
        # Add detailed speech content (limited)
        context += "## Sample Speech Content\n\n"
        for year in sorted(by_year.keys(), reverse=True)[:3]:  # Limit to 3 most recent years
            year_speeches = by_year[year]
            context += f"### {year} ({len(year_speeches)} speeches)\n\n"
            
            for speech in year_speeches[:3]:  # Limit to 3 speeches per year
                country = speech.get('country_name', 'Unknown')
                word_count = speech.get('word_count', 0)
                text_preview = speech.get('speech_text', '')[:300] + "..." if len(speech.get('speech_text', '')) > 300 else speech.get('speech_text', '')
                
                context += f"**{country}** ({word_count:,} words):\n"
                context += f"{text_preview}\n\n"
        
        return context
    
    def _generate_analysis_tables_with_citations(self, speeches: List[Dict[str, Any]], query: str) -> str:
        """Generate structured tables for analysis with proper citations."""
        tables = ""
        
        # Group data for table generation
        by_year = {}
        by_country = {}
        by_region = {}
        
        for speech in speeches:
            year = speech.get('year', 'Unknown')
            country = speech.get('country_name', 'Unknown')
            region = speech.get('region', 'Unknown')
            citation = speech.get('citation', f"{country}, {year}")
            
            # Group by year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(speech)
            
            # Group by country
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(speech)
            
            # Group by region
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(speech)
        
        # Generate year-over-year trend table with citations
        if by_year:
            tables += "## Year-over-Year Analysis (with Citations)\n\n"
            tables += "| Year | Speech Count | Countries | Avg Words | Sample Citations |\n"
            tables += "|------|--------------|-----------|-----------|------------------|\n"
            
            for year in sorted(by_year.keys()):
                year_speeches = by_year[year]
                countries = len(set(speech.get('country_name', '') for speech in year_speeches))
                avg_words = sum(speech.get('word_count', 0) for speech in year_speeches) / len(year_speeches) if year_speeches else 0
                sample_citations = [s.get('citation', f"{s.get('country_name', 'Unknown')}, {year}") for s in year_speeches[:3]]
                citations_str = "; ".join(sample_citations)
                tables += f"| {year} | {len(year_speeches)} | {countries} | {avg_words:.0f} | {citations_str} |\n"
            tables += "\n"
        
        # Generate top countries table with citations
        if by_country:
            tables += "## Top Countries by Speech Count (with Citations)\n\n"
            tables += "| Country | Speech Count | Percentage | Avg Words | Sample Citations |\n"
            tables += "|---------|--------------|------------|-----------|------------------|\n"
            
            sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
            for country, country_speeches in sorted_countries[:10]:
                percentage = (len(country_speeches) / len(speeches)) * 100
                avg_words = sum(speech.get('word_count', 0) for speech in country_speeches) / len(country_speeches)
                sample_citations = [s.get('citation', f"{country}, {s.get('year', 'Unknown')}") for s in country_speeches[:3]]
                citations_str = "; ".join(sample_citations)
                tables += f"| {country} | {len(country_speeches)} | {percentage:.1f}% | {avg_words:.0f} | {citations_str} |\n"
            tables += "\n"
        
        # Generate regional analysis table with citations
        if by_region and len(by_region) > 1:
            tables += "## Regional Analysis (with Citations)\n\n"
            tables += "| Region | Speech Count | Percentage | Countries | Sample Citations |\n"
            tables += "|--------|--------------|------------|-----------|------------------|\n"
            
            for region, region_speeches in sorted(by_region.items(), key=lambda x: len(x[1]), reverse=True):
                percentage = (len(region_speeches) / len(speeches)) * 100
                countries = len(set(speech.get('country_name', '') for speech in region_speeches))
                sample_citations = [s.get('citation', f"{s.get('country_name', 'Unknown')}, {s.get('year', 'Unknown')}") for s in region_speeches[:3]]
                citations_str = "; ".join(sample_citations)
                tables += f"| {region} | {len(region_speeches)} | {percentage:.1f}% | {countries} | {citations_str} |\n"
            tables += "\n"
        
        return tables
    
    def _generate_analysis_tables(self, speeches: List[Dict[str, Any]], query: str) -> str:
        """Generate structured tables for analysis."""
        tables = ""
        
        # Group data for table generation
        by_year = {}
        by_country = {}
        by_region = {}
        
        for speech in speeches:
            year = speech.get('year', 'Unknown')
            country = speech.get('country_name', 'Unknown')
            region = speech.get('region', 'Unknown')
            
            # Group by year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(speech)
            
            # Group by country
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(speech)
            
            # Group by region
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(speech)
        
        # Generate year-over-year trend table
        if by_year:
            tables += "## Year-over-Year Analysis\n\n"
            tables += "| Year | Speech Count | Countries | Avg Words per Speech |\n"
            tables += "|------|--------------|-----------|---------------------|\n"
            
            for year in sorted(by_year.keys()):
                year_speeches = by_year[year]
                countries = len(set(speech.get('country_name', '') for speech in year_speeches))
                avg_words = sum(speech.get('word_count', 0) for speech in year_speeches) / len(year_speeches) if year_speeches else 0
                tables += f"| {year} | {len(year_speeches)} | {countries} | {avg_words:.0f} |\n"
            tables += "\n"
        
        # Generate top countries table
        if by_country:
            tables += "## Top Countries by Speech Count\n\n"
            tables += "| Country | Speech Count | Percentage | Avg Words |\n"
            tables += "|---------|--------------|------------|----------|\n"
            
            sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
            for country, country_speeches in sorted_countries[:10]:
                percentage = (len(country_speeches) / len(speeches)) * 100
                avg_words = sum(speech.get('word_count', 0) for speech in country_speeches) / len(country_speeches)
                tables += f"| {country} | {len(country_speeches)} | {percentage:.1f}% | {avg_words:.0f} |\n"
            tables += "\n"
        
        # Generate regional analysis table
        if by_region and len(by_region) > 1:
            tables += "## Regional Analysis\n\n"
            tables += "| Region | Speech Count | Percentage | Countries |\n"
            tables += "|--------|--------------|------------|----------|\n"
            
            for region, region_speeches in sorted(by_region.items(), key=lambda x: len(x[1]), reverse=True):
                percentage = (len(region_speeches) / len(speeches)) * 100
                countries = len(set(speech.get('country_name', '') for speech in region_speeches))
                tables += f"| {region} | {len(region_speeches)} | {percentage:.1f}% | {countries} |\n"
            tables += "\n"
        
        return tables
    
    def _generate_topic_analysis_tables_with_citations(self, speeches: List[Dict[str, Any]], topic: str) -> str:
        """Generate topic-specific analysis tables with proper citations."""
        tables = ""
        
        # For gender and equality analysis, create specific tables
        if "gender" in topic.lower() or "equality" in topic.lower() or "women" in topic.lower():
            tables += "## Gender and Equality Analysis (with Citations)\n\n"
            
            # Group by year for gender-related speeches
            by_year = {}
            for speech in speeches:
                year = speech.get('year', 'Unknown')
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(speech)
            
            # Create year-over-year gender mentions table with citations
            if by_year:
                tables += "### Year-over-Year Gender Mentions (with Citations)\n\n"
                tables += "| Year | Total Speeches | Gender-Related Speeches | Percentage | Sample Citations |\n"
                tables += "|------|----------------|------------------------|------------|------------------|\n"
                
                for year in sorted(by_year.keys()):
                    year_speeches = by_year[year]
                    # Count speeches that mention gender-related terms
                    gender_mentions = 0
                    gender_citations = []
                    for speech in year_speeches:
                        text = speech.get('speech_text', '').lower()
                        if any(term in text for term in ['gender', 'women', 'girls', 'equality', 'empowerment', 'feminist']):
                            gender_mentions += 1
                            citation = speech.get('citation', f"{speech.get('country_name', 'Unknown')}, {year}")
                            gender_citations.append(citation)
                    
                    percentage = (gender_mentions / len(year_speeches)) * 100 if year_speeches else 0
                    citations_str = "; ".join(gender_citations[:3])  # Top 3 citations
                    tables += f"| {year} | {len(year_speeches)} | {gender_mentions} | {percentage:.1f}% | {citations_str} |\n"
                tables += "\n"
            
            # Create country comparison table for gender mentions with citations
            by_country = {}
            for speech in speeches:
                country = speech.get('country_name', 'Unknown')
                if country not in by_country:
                    by_country[country] = []
                by_country[country].append(speech)
            
            if by_country:
                tables += "### Country Comparison - Gender Mentions (with Citations)\n\n"
                tables += "| Country | Total Speeches | Gender Mentions | Percentage | Sample Citations |\n"
                tables += "|---------|----------------|-----------------|------------|------------------|\n"
                
                country_gender_data = []
                for country, country_speeches in by_country.items():
                    gender_mentions = 0
                    gender_citations = []
                    for speech in country_speeches:
                        text = speech.get('speech_text', '').lower()
                        if any(term in text for term in ['gender', 'women', 'girls', 'equality', 'empowerment', 'feminist']):
                            gender_mentions += 1
                            citation = speech.get('citation', f"{country}, {speech.get('year', 'Unknown')}")
                            gender_citations.append(citation)
                    
                    percentage = (gender_mentions / len(country_speeches)) * 100 if country_speeches else 0
                    citations_str = "; ".join(gender_citations[:3])  # Top 3 citations
                    country_gender_data.append((country, len(country_speeches), gender_mentions, percentage, citations_str))
                
                # Sort by percentage of gender mentions
                country_gender_data.sort(key=lambda x: x[3], reverse=True)
                
                for country, total, mentions, percentage, citations in country_gender_data[:15]:  # Top 15 countries
                    tables += f"| {country} | {total} | {mentions} | {percentage:.1f}% | {citations} |\n"
                tables += "\n"
        
        return tables
    
    def _generate_topic_analysis_tables(self, speeches: List[Dict[str, Any]], topic: str) -> str:
        """Generate topic-specific analysis tables."""
        tables = ""
        
        # For gender and equality analysis, create specific tables
        if "gender" in topic.lower() or "equality" in topic.lower() or "women" in topic.lower():
            tables += "## Gender and Equality Analysis\n\n"
            
            # Group by year for gender-related speeches
            by_year = {}
            for speech in speeches:
                year = speech.get('year', 'Unknown')
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(speech)
            
            # Create year-over-year gender mentions table
            if by_year:
                tables += "### Year-over-Year Gender Mentions\n\n"
                tables += "| Year | Total Speeches | Gender-Related Speeches | Percentage |\n"
                tables += "|------|----------------|------------------------|------------|\n"
                
                for year in sorted(by_year.keys()):
                    year_speeches = by_year[year]
                    # Count speeches that mention gender-related terms
                    gender_mentions = 0
                    for speech in year_speeches:
                        text = speech.get('speech_text', '').lower()
                        if any(term in text for term in ['gender', 'women', 'girls', 'equality', 'empowerment', 'feminist']):
                            gender_mentions += 1
                    
                    percentage = (gender_mentions / len(year_speeches)) * 100 if year_speeches else 0
                    tables += f"| {year} | {len(year_speeches)} | {gender_mentions} | {percentage:.1f}% |\n"
                tables += "\n"
            
            # Create country comparison table for gender mentions
            by_country = {}
            for speech in speeches:
                country = speech.get('country_name', 'Unknown')
                if country not in by_country:
                    by_country[country] = []
                by_country[country].append(speech)
            
            if by_country:
                tables += "### Country Comparison - Gender Mentions\n\n"
                tables += "| Country | Total Speeches | Gender Mentions | Percentage |\n"
                tables += "|---------|----------------|-----------------|------------|\n"
                
                country_gender_data = []
                for country, country_speeches in by_country.items():
                    gender_mentions = 0
                    for speech in country_speeches:
                        text = speech.get('speech_text', '').lower()
                        if any(term in text for term in ['gender', 'women', 'girls', 'equality', 'empowerment', 'feminist']):
                            gender_mentions += 1
                    
                    percentage = (gender_mentions / len(country_speeches)) * 100 if country_speeches else 0
                    country_gender_data.append((country, len(country_speeches), gender_mentions, percentage))
                
                # Sort by percentage of gender mentions
                country_gender_data.sort(key=lambda x: x[3], reverse=True)
                
                for country, total, mentions, percentage in country_gender_data[:15]:  # Top 15 countries
                    tables += f"| {country} | {total} | {mentions} | {percentage:.1f}% |\n"
                tables += "\n"
        
        return tables
    
    def _get_openai_client(self) -> Optional[AzureOpenAI]:
        """Get Azure OpenAI client."""
        try:
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
            
            if not api_key or not azure_endpoint:
                return None
            
            return AzureOpenAI(
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"Failed to get OpenAI client: {e}")
            return None
    
    def get_analysis_suggestions(self, available_years: List[int], 
                               available_regions: List[str]) -> List[str]:
        """Get suggested analysis queries based on available data."""
        suggestions = [
            # Gender and equality analysis
            "Analyze gender equality mentions in African countries over the past 10 years",
            "Compare women's empowerment discussions between African and European countries",
            "What are the trends in gender-related language in UNGA speeches since 2015?",
            
            # Climate and environment
            "How has climate change discourse evolved in small island states over the past 5 years?",
            "Compare environmental priorities between developed and developing countries",
            "Analyze renewable energy mentions in speeches from 2020-2024",
            
            # Development and SDGs
            "What are the most frequently mentioned SDGs in African countries' speeches?",
            "How has the focus on sustainable development changed since 2015?",
            "Compare development priorities between different regions",
            
            # Peace and security
            "Analyze peace and security discussions in conflict-affected regions",
            "How have security concerns evolved in speeches over the past decade?",
            "Compare multilateralism approaches between different country groups",
            
            # Technology and innovation
            "What are the trends in digital transformation mentions across regions?",
            "How has AI and technology discourse evolved in recent years?",
            "Compare innovation priorities between developed and developing countries",
            
            # Economic and trade
            "Analyze economic cooperation discussions in regional groups",
            "How have trade and globalization themes evolved over time?",
            "Compare debt relief discussions between different time periods",
            
            # Health and pandemic
            "Analyze health system strengthening discussions post-COVID",
            "How have pandemic preparedness themes evolved in speeches?",
            "Compare global health cooperation approaches across regions"
        ]
        
        # Filter suggestions based on available data
        filtered_suggestions = []
        for suggestion in suggestions:
            # Check if we have data for the time periods mentioned
            if "past 10 years" in suggestion.lower():
                if any(year >= 2015 for year in available_years):
                    filtered_suggestions.append(suggestion)
            elif "past 5 years" in suggestion.lower():
                if any(year >= 2020 for year in available_years):
                    filtered_suggestions.append(suggestion)
            elif "2020-2024" in suggestion:
                if any(year >= 2020 for year in available_years):
                    filtered_suggestions.append(suggestion)
            elif "since 2015" in suggestion:
                if any(year >= 2015 for year in available_years):
                    filtered_suggestions.append(suggestion)
            else:
                # General suggestions that don't specify time periods
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions[:15]  # Return top 15 suggestions
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary for the interface."""
        try:
            stats = self.db_manager.get_speech_statistics()
            available_years = self.get_available_years()
            available_regions = self.get_available_regions()
            
            # Get country counts by region for 2025
            countries_2025 = self.db_manager.get_available_countries_by_region(2025)
            
            summary = {
                'total_speeches': stats.get('total_speeches', 0),
                'total_countries': stats.get('total_countries', 0),
                'total_years': stats.get('total_years', 0),
                'available_years': available_years,
                'available_regions': available_regions,
                'countries_2025_by_region': countries_2025,
                'year_statistics': stats.get('year_statistics', {}),
                'region_statistics': stats.get('region_statistics', {})
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            return {}

# Global cross-year analysis manager instance
cross_year_manager = CrossYearAnalysisManager()
