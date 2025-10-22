"""
Enhanced Unified Search Engine
Provides advanced search capabilities with proper document referencing and citations
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EnhancedSearchEngine:
    """Enhanced search engine with hybrid search capabilities and proper referencing."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.embedding_model = None
        self.embeddings_enabled = False
        
        # Initialize embedding model if available
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_enabled = True
            logger.info("Enhanced search engine initialized with embeddings")
        except Exception as e:
            logger.warning(f"Embeddings not available: {e}")
            self.embeddings_enabled = False
    
    def intelligent_query_analysis(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand intent and extract entities."""
        query_lower = query.lower()
        
        # Query intent classification
        intent = self.classify_query_intent(query_lower)
        
        # Extract entities
        entities = self.extract_entities_advanced(query)
        
        # Assess complexity
        complexity = self.assess_query_complexity(query)
        
        # Select search strategy
        strategy = self.select_search_strategy(intent, entities, complexity)
        
        return {
            'intent': intent,
            'entities': entities,
            'strategy': strategy,
            'complexity': complexity,
            'original_query': query
        }
    
    def classify_query_intent(self, query: str) -> str:
        """Classify the intent of the query."""
        # Trend analysis indicators
        if any(term in query for term in ['trend', 'evolved', 'changed', 'over time', 'past', 'years']):
            return 'trend_analysis'
        
        # Comparison indicators
        if any(term in query for term in ['compare', 'versus', 'vs', 'difference', 'similarity']):
            return 'comparison'
        
        # Content analysis indicators
        if any(term in query for term in ['mentioned', 'discussed', 'talked about', 'content', 'themes']):
            return 'content_analysis'
        
        # Statistical indicators
        if any(term in query for term in ['how many', 'count', 'frequency', 'statistics', 'percentage']):
            return 'statistical'
        
        # Specific information indicators
        if any(term in query for term in ['what', 'who', 'when', 'where', 'which']):
            return 'specific_information'
        
        return 'general'
    
    def extract_entities_advanced(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query using advanced techniques."""
        entities = {
            'countries': [],
            'years': [],
            'topics': [],
            'regions': [],
            'organizations': []
        }
        
        # Extract countries
        entities['countries'] = self.extract_countries_from_query(query)
        
        # Extract years
        entities['years'] = self.extract_years_from_query(query)
        
        # Extract topics
        entities['topics'] = self.extract_topics_from_query(query)
        
        # Extract regions
        entities['regions'] = self.extract_regions_from_query(query)
        
        # Extract organizations
        entities['organizations'] = self.extract_organizations_from_query(query)
        
        return entities
    
    def extract_countries_from_query(self, query: str) -> List[str]:
        """Extract country names from query with enhanced matching."""
        query_lower = query.lower()
        countries = []
        
        # Enhanced country mapping with more variations
        country_mappings = {
            'china': ['china', 'chinese', 'peoples republic of china', 'prc', 'beijing'],
            'united states': ['united states', 'usa', 'us', 'america', 'american', 'washington'],
            'russia': ['russia', 'russian', 'soviet union', 'ussr', 'moscow'],
            'united kingdom': ['united kingdom', 'uk', 'britain', 'british', 'london'],
            'france': ['france', 'french', 'paris'],
            'germany': ['germany', 'german', 'berlin'],
            'japan': ['japan', 'japanese', 'tokyo'],
            'india': ['india', 'indian', 'new delhi'],
            'brazil': ['brazil', 'brazilian', 'brasilia'],
            'canada': ['canada', 'canadian', 'ottawa'],
            'australia': ['australia', 'australian', 'canberra'],
            'south africa': ['south africa', 'south african', 'pretoria'],
            'nigeria': ['nigeria', 'nigerian', 'abuja'],
            'egypt': ['egypt', 'egyptian', 'cairo'],
            'turkey': ['turkey', 'turkish', 'ankara'],
            'iran': ['iran', 'iranian', 'tehran'],
            'saudi arabia': ['saudi arabia', 'saudi', 'riyadh'],
            'african': ['african', 'africa', 'au', 'african union'],
            'european': ['european', 'europe', 'eu', 'european union'],
            'asian': ['asian', 'asia'],
            'latin american': ['latin american', 'latin america'],
            'developing': ['developing countries', 'developing', 'global south'],
            'developed': ['developed countries', 'developed', 'global north']
        }
        
        for country, variations in country_mappings.items():
            if any(var in query_lower for var in variations):
                countries.append(country)
        
        return countries
    
    def extract_years_from_query(self, query: str) -> List[int]:
        """Extract years from query with enhanced patterns."""
        # Standard year patterns
        year_patterns = [
            r'\b(19|20)\d{2}\b',  # 4-digit years
            r'\b\d{2}s\b',  # Decades like "90s"
            r'\b(early|mid|late)\s+(19|20)\d{2}s?\b',  # Early 2000s, etc.
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle decade patterns
                    if match[1]:  # Has century
                        decade = int(match[1] + '0')
                        years.extend(range(decade, decade + 10))
                    else:
                        years.append(int(match))
                else:
                    try:
                        years.append(int(match))
                    except ValueError:
                        continue
        
        # Handle relative year references
        current_year = datetime.now().year
        if 'past decade' in query.lower():
            years.extend(range(current_year - 10, current_year + 1))
        elif 'past 5 years' in query.lower():
            years.extend(range(current_year - 5, current_year + 1))
        elif 'past 50 years' in query.lower():
            years.extend(range(current_year - 50, current_year + 1))
        
        return sorted(list(set(years)))
    
    def extract_topics_from_query(self, query: str) -> List[str]:
        """Extract topic keywords from query with enhanced matching."""
        query_lower = query.lower()
        topics = []
        
        # Enhanced topic keywords
        topic_keywords = {
            'climate change': ['climate', 'environment', 'global warming', 'carbon', 'emissions', 'greenhouse', 'sustainability'],
            'economic development': ['economic', 'development', 'economy', 'trade', 'commerce', 'growth', 'poverty', 'inequality'],
            'peace and security': ['peace', 'security', 'conflict', 'war', 'military', 'terrorism', 'violence', 'stability'],
            'human rights': ['human rights', 'rights', 'democracy', 'freedom', 'justice', 'equality', 'dignity'],
            'health': ['health', 'pandemic', 'disease', 'medical', 'healthcare', 'public health', 'wellbeing'],
            'education': ['education', 'school', 'learning', 'knowledge', 'literacy', 'training', 'skills'],
            'technology': ['technology', 'digital', 'innovation', 'ai', 'artificial intelligence', 'cyber', 'internet'],
            'migration': ['migration', 'refugees', 'immigration', 'displacement', 'mobility', 'asylum'],
            'gender equality': ['gender', 'women', 'equality', 'feminism', 'empowerment', 'girls', 'feminist'],
            'sustainable development': ['sustainable', 'sustainability', 'sdgs', 'goals', 'agenda 2030', 'development goals'],
            'multilateralism': ['multilateral', 'cooperation', 'international', 'global governance', 'united nations'],
            'development assistance': ['aid', 'assistance', 'development cooperation', 'oda', 'foreign aid'],
            'disarmament': ['disarmament', 'arms control', 'nuclear', 'weapons', 'non-proliferation'],
            'humanitarian': ['humanitarian', 'crisis', 'emergency', 'relief', 'assistance', 'vulnerable']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def extract_regions_from_query(self, query: str) -> List[str]:
        """Extract regions from query."""
        query_lower = query.lower()
        regions = []
        
        region_mappings = {
            'africa': ['africa', 'african', 'sub-saharan', 'north africa', 'west africa', 'east africa', 'southern africa'],
            'europe': ['europe', 'european', 'eastern europe', 'western europe', 'northern europe', 'southern europe'],
            'asia': ['asia', 'asian', 'southeast asia', 'south asia', 'east asia', 'central asia'],
            'americas': ['americas', 'north america', 'south america', 'latin america', 'caribbean'],
            'middle east': ['middle east', 'mideast', 'gulf', 'persian gulf', 'arab'],
            'pacific': ['pacific', 'oceania', 'pacific islands', 'small island states']
        }
        
        for region, variations in region_mappings.items():
            if any(var in query_lower for var in variations):
                regions.append(region)
        
        return regions
    
    def extract_organizations_from_query(self, query: str) -> List[str]:
        """Extract organizations from query."""
        query_lower = query.lower()
        organizations = []
        
        org_mappings = {
            'united nations': ['un', 'united nations', 'unga', 'general assembly'],
            'african union': ['au', 'african union', 'oau'],
            'european union': ['eu', 'european union'],
            'g7': ['g7', 'group of seven'],
            'g20': ['g20', 'group of twenty'],
            'nato': ['nato', 'north atlantic treaty organization'],
            'who': ['who', 'world health organization'],
            'world bank': ['world bank', 'wb'],
            'imf': ['imf', 'international monetary fund'],
            'wto': ['wto', 'world trade organization']
        }
        
        for org, variations in org_mappings.items():
            if any(var in query_lower for var in variations):
                organizations.append(org)
        
        return organizations
    
    def assess_query_complexity(self, query: str) -> str:
        """Assess the complexity of the query."""
        query_lower = query.lower()
        
        # Simple queries (1-2 entities)
        if len(query.split()) <= 5 and not any(connector in query_lower for connector in ['and', 'or', 'but', 'however', 'while']):
            return 'simple'
        
        # Complex queries (multiple entities, temporal ranges, comparisons)
        if any(indicator in query_lower for indicator in ['compare', 'versus', 'between', 'across', 'over time', 'evolution']):
            return 'complex'
        
        # Medium complexity
        return 'medium'
    
    def select_search_strategy(self, intent: str, entities: Dict[str, List[str]], complexity: str) -> str:
        """Select the optimal search strategy based on query analysis."""
        if intent == 'trend_analysis' and complexity == 'complex':
            return 'comprehensive_temporal'
        elif intent == 'comparison' and len(entities['countries']) > 1:
            return 'comparative'
        elif intent == 'content_analysis' and entities['topics']:
            return 'semantic_content'
        elif intent == 'statistical':
            return 'statistical_analysis'
        elif entities['years'] and len(entities['years']) > 5:
            return 'temporal_broad'
        elif self.embeddings_enabled and complexity == 'simple':
            return 'semantic_simple'
        else:
            return 'hybrid'
    
    def execute_enhanced_search(self, query: str, strategy: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute search using the selected strategy."""
        if not strategy:
            analysis = self.intelligent_query_analysis(query)
            strategy = analysis['strategy']
        else:
            analysis = self.intelligent_query_analysis(query)
        
        # Execute search based on strategy
        if strategy == 'semantic_simple':
            results = self.semantic_search(query, limit=50)
        elif strategy == 'comprehensive_temporal':
            results = self.comprehensive_temporal_search(query, analysis['entities'])
        elif strategy == 'comparative':
            results = self.comparative_search(query, analysis['entities'])
        elif strategy == 'semantic_content':
            results = self.semantic_content_search(query, analysis['entities'])
        elif strategy == 'statistical_analysis':
            results = self.statistical_search(query, analysis['entities'])
        elif strategy == 'temporal_broad':
            results = self.temporal_broad_search(query, analysis['entities'])
        else:
            results = self.hybrid_search(query, analysis['entities'])
        
        # Enhance results with proper referencing
        enhanced_results = self.enhance_results_with_references(results, query, analysis)
        
        return {
            'results': enhanced_results,
            'analysis': analysis,
            'strategy': strategy,
            'total_found': len(enhanced_results)
        }
    
    def semantic_search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Perform semantic search with embeddings."""
        try:
            if not self.embeddings_enabled:
                return self.fallback_text_search(query, limit)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search using vector similarity
            results = self.db_manager.conn.execute("""
                SELECT id, country_code, country_name, region, session, year, 
                       speech_text, word_count, source_filename, is_african_member, created_at,
                       array_cosine_similarity(embedding, ?) as similarity
                FROM speeches 
                WHERE embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT ?
            """, [query_embedding.tolist(), limit]).fetchall()
            
            # Convert to list of dictionaries
            speeches = []
            for row in results:
                speeches.append({
                    'id': row[0],
                    'country_code': row[1],
                    'country_name': row[2],
                    'region': row[3],
                    'session': row[4],
                    'year': row[5],
                    'speech_text': row[6],
                    'word_count': row[7],
                    'source_filename': row[8],
                    'is_african_member': row[9],
                    'created_at': row[10],
                    'similarity': row[11]
                })
            
            return speeches
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self.fallback_text_search(query, limit)
    
    def comprehensive_temporal_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Comprehensive search for temporal trend analysis."""
        try:
            # Build comprehensive search criteria
            countries = entities.get('countries', [])
            years = entities.get('years', [])
            regions = entities.get('regions', [])
            topics = entities.get('topics', [])
            
            # Use cross-year manager for comprehensive search
            from ..data.cross_year_analysis import cross_year_manager
            
            speeches = cross_year_manager.search_speeches_by_criteria(
                query_text=query,
                countries=countries,
                years=years,
                regions=regions,
                african_members_only=False,
                use_semantic_search=True,
                limit=5000
            )
            
            return speeches
            
        except Exception as e:
            logger.error(f"Comprehensive temporal search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def comparative_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Search optimized for comparative analysis."""
        try:
            countries = entities.get('countries', [])
            years = entities.get('years', [])
            
            # Search for each country separately to ensure balanced results
            all_speeches = []
            for country in countries:
                country_speeches = self.db_manager.search_speeches(
                    countries=[country],
                    years=years,
                    limit=100
                )
                all_speeches.extend(country_speeches)
            
            return all_speeches
            
        except Exception as e:
            logger.error(f"Comparative search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def semantic_content_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Search optimized for content analysis."""
        try:
            topics = entities.get('topics', [])
            countries = entities.get('countries', [])
            years = entities.get('years', [])
            
            # Search for speeches containing topic keywords
            speeches = []
            for topic in topics:
                topic_speeches = self.db_manager.search_speeches(
                    query_text=topic,
                    countries=countries,
                    years=years,
                    limit=200
                )
                speeches.extend(topic_speeches)
            
            # Remove duplicates
            seen_ids = set()
            unique_speeches = []
            for speech in speeches:
                if speech.get('id') not in seen_ids:
                    seen_ids.add(speech.get('id'))
                    unique_speeches.append(speech)
            
            return unique_speeches
            
        except Exception as e:
            logger.error(f"Semantic content search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def statistical_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Search optimized for statistical analysis."""
        try:
            countries = entities.get('countries', [])
            years = entities.get('years', [])
            topics = entities.get('topics', [])
            
            # Get comprehensive data for statistical analysis
            speeches = self.db_manager.search_speeches(
                query_text=query,
                countries=countries,
                years=years,
                limit=5000
            )
            
            return speeches
            
        except Exception as e:
            logger.error(f"Statistical search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def temporal_broad_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Search for broad temporal analysis."""
        try:
            years = entities.get('years', [])
            countries = entities.get('countries', [])
            regions = entities.get('regions', [])
            
            # Use broad search for temporal analysis
            speeches = self.db_manager.search_speeches(
                query_text=query,
                countries=countries,
                years=years,
                regions=regions,
                limit=3000
            )
            
            return speeches
            
        except Exception as e:
            logger.error(f"Temporal broad search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def hybrid_search(self, query: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Hybrid search combining multiple approaches."""
        try:
            # Combine semantic and text search
            semantic_results = []
            if self.embeddings_enabled:
                semantic_results = self.semantic_search(query, limit=100)
            
            text_results = self.db_manager.search_speeches(
                query_text=query,
                countries=entities.get('countries', []),
                years=entities.get('years', []),
                regions=entities.get('regions', []),
                limit=100
            )
            
            # Combine and deduplicate results
            all_results = semantic_results + text_results
            seen_ids = set()
            unique_results = []
            
            for result in all_results:
                if result.get('id') not in seen_ids:
                    seen_ids.add(result.get('id'))
                    unique_results.append(result)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return self.fallback_text_search(query, 100)
    
    def fallback_text_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback text search when other methods fail."""
        try:
            return self.db_manager.search_speeches(
                query_text=query,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Fallback text search failed: {e}")
            return []
    
    def enhance_results_with_references(self, results: List[Dict[str, Any]], query: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance search results with proper document references and citations."""
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add citation information
            enhanced_result['citation'] = self.generate_citation(result)
            
            # Add relevance score based on query analysis
            enhanced_result['relevance_score'] = self.calculate_relevance_score(result, query, analysis)
            
            # Add contextual information
            enhanced_result['context'] = self.generate_context_info(result, analysis)
            
            # Add extracted quotes that match the query
            enhanced_result['relevant_quotes'] = self.extract_relevant_quotes(result, query)
            
            enhanced_results.append(enhanced_result)
        
        # Sort by relevance score
        enhanced_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return enhanced_results
    
    def generate_citation(self, result: Dict[str, Any]) -> str:
        """Generate proper citation for a speech result."""
        country = result.get('country_name', 'Unknown Country')
        year = result.get('year', 'Unknown Year')
        session = result.get('session', '')
        
        citation = f"{country}, {year}"
        if session:
            citation += f" (Session {session})"
        
        return citation
    
    def calculate_relevance_score(self, result: Dict[str, Any], query: str, analysis: Dict[str, Any]) -> float:
        """Calculate relevance score for a result."""
        score = 0.0
        
        # Base similarity score if available
        if 'similarity' in result:
            score += result['similarity'] * 0.4
        
        # Country match bonus
        result_country = result.get('country_name', '').lower()
        query_countries = [c.lower() for c in analysis['entities'].get('countries', [])]
        if any(country in result_country for country in query_countries):
            score += 0.3
        
        # Year match bonus
        result_year = result.get('year')
        query_years = analysis['entities'].get('years', [])
        if result_year in query_years:
            score += 0.2
        
        # Topic match bonus
        result_text = result.get('speech_text', '').lower()
        query_topics = analysis['entities'].get('topics', [])
        for topic in query_topics:
            if topic.lower() in result_text:
                score += 0.1
                break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def generate_context_info(self, result: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual information for a result."""
        return {
            'word_count': result.get('word_count', 0),
            'region': result.get('region', 'Unknown'),
            'is_african_member': result.get('is_african_member', False),
            'session': result.get('session', ''),
            'created_at': result.get('created_at', ''),
            'source_filename': result.get('source_filename', '')
        }
    
    def extract_relevant_quotes(self, result: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Extract relevant quotes from the speech that match the query."""
        speech_text = result.get('speech_text', '')
        if not speech_text:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', speech_text)
        
        relevant_quotes = []
        query_words = set(query.lower().split())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            sentence_words = set(sentence.lower().split())
            # Calculate word overlap
            overlap = len(query_words.intersection(sentence_words))
            
            if overlap > 0:
                relevance_score = overlap / len(query_words)
                if relevance_score > 0.1:  # Minimum relevance threshold
                    relevant_quotes.append({
                        'quote': sentence[:300] + '...' if len(sentence) > 300 else sentence,
                        'relevance_score': relevance_score,
                        'country': result.get('country_name', 'Unknown'),
                        'year': result.get('year', 'Unknown'),
                        'citation': self.generate_citation(result)
                    })
        
        # Sort by relevance and return top quotes
        relevant_quotes.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_quotes[:5]  # Return top 5 relevant quotes


# Global enhanced search engine instance
enhanced_search_engine = None

def get_enhanced_search_engine(db_manager):
    """Get or create the enhanced search engine instance."""
    global enhanced_search_engine
    if enhanced_search_engine is None:
        enhanced_search_engine = EnhancedSearchEngine(db_manager)
    return enhanced_search_engine
