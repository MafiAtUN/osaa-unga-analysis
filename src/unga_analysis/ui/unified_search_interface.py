"""
Unified Search Interface
Provides a consistent search experience across all tabs with enhanced capabilities
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..core.enhanced_search_engine import get_enhanced_search_engine
from ..data.simple_vector_storage import simple_vector_storage as db_manager


def render_unified_search_interface(tab_context: str = "general") -> Optional[Dict[str, Any]]:
    """
    Render a unified search interface that works across all tabs.
    
    Args:
        tab_context: Context of the current tab (e.g., "database_chat", "cross_year", etc.)
    
    Returns:
        Search results dictionary if search was performed, None otherwise
    """
    st.markdown("### 🔍 Enhanced Search Interface")
    
    # Search input
    search_query = st.text_area(
        "Ask anything about UNGA speeches:",
        placeholder="e.g., 'How has China's focus on climate change evolved over the past decade?' or 'What are the main themes in African countries' speeches about development?'",
        height=100,
        key=f"unified_search_{tab_context}"
    )
    
    # Advanced search options
    with st.expander("🔧 Advanced Search Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            search_type = st.selectbox(
                "Search Type",
                ["Auto-Detect", "Semantic", "Keyword", "Hybrid", "Temporal", "Geographic"],
                help="Auto-Detect will choose the best strategy based on your query"
            )
            
            result_limit = st.slider(
                "Result Limit",
                10, 1000, 100,
                help="Maximum number of results to return"
            )
        
        with col2:
            similarity_threshold = st.slider(
                "Similarity Threshold",
                0.1, 1.0, 0.7,
                help="Minimum similarity score for semantic search results"
            )
            
            include_citations = st.checkbox(
                "Include Detailed Citations",
                value=True,
                help="Include proper document citations with country and year"
            )
    
    # Search filters
    with st.expander("🎯 Search Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Year range filter
            year_range = st.slider(
                "Year Range",
                1946, 2025, (1946, 2025),
                help="Filter results by year range"
            )
        
        with col2:
            # Region filter
            regions = st.multiselect(
                "Regions",
                ["Africa", "Europe", "Asia", "Americas", "Middle East", "Pacific"],
                help="Filter by geographic regions"
            )
        
        with col3:
            # Country filter
            countries = st.multiselect(
                "Countries",
                get_available_countries(),
                help="Filter by specific countries"
            )
    
    # Search button
    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not search_query.strip():
            st.warning("Please enter a search query.")
            return None
        
        # Perform enhanced search
        return perform_unified_search(
            query=search_query,
            search_type=search_type,
            result_limit=result_limit,
            similarity_threshold=similarity_threshold,
            include_citations=include_citations,
            year_range=year_range,
            regions=regions,
            countries=countries,
            tab_context=tab_context
        )
    
    return None


def perform_unified_search(
    query: str,
    search_type: str = "Auto-Detect",
    result_limit: int = 100,
    similarity_threshold: float = 0.7,
    include_citations: bool = True,
    year_range: tuple = (1946, 2025),
    regions: List[str] = None,
    countries: List[str] = None,
    tab_context: str = "general"
) -> Dict[str, Any]:
    """Perform unified search using enhanced search engine."""
    try:
        with st.spinner("🔍 Performing enhanced search..."):
            # Get enhanced search engine
            enhanced_search = get_enhanced_search_engine(db_manager)
            
            # Execute search
            search_results = enhanced_search.execute_enhanced_search(query)
            
            # Apply additional filters if specified
            filtered_results = apply_search_filters(
                search_results.get('results', []),
                year_range=year_range,
                regions=regions,
                countries=countries,
                similarity_threshold=similarity_threshold
            )
            
            # Update results with filtered data
            search_results['results'] = filtered_results
            search_results['total_found'] = len(filtered_results)
            
            # Display results
            display_unified_search_results(search_results, include_citations, tab_context)
            
            return search_results
            
    except Exception as e:
        st.error(f"❌ Search failed: {e}")
        return {'results': [], 'error': str(e)}


def apply_search_filters(
    results: List[Dict[str, Any]],
    year_range: tuple = (1946, 2025),
    regions: List[str] = None,
    countries: List[str] = None,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Apply additional filters to search results."""
    filtered_results = []
    
    for result in results:
        # Year filter
        year = result.get('year', 0)
        if not (year_range[0] <= year <= year_range[1]):
            continue
        
        # Region filter
        if regions:
            region = result.get('region', '').lower()
            if not any(r.lower() in region for r in regions):
                continue
        
        # Country filter
        if countries:
            country = result.get('country_name', '').lower()
            if not any(c.lower() in country for c in countries):
                continue
        
        # Similarity threshold filter
        similarity = result.get('similarity', 1.0)
        if similarity < similarity_threshold:
            continue
        
        filtered_results.append(result)
    
    return filtered_results


def display_unified_search_results(
    search_results: Dict[str, Any],
    include_citations: bool = True,
    tab_context: str = "general"
):
    """Display unified search results with proper formatting."""
    results = search_results.get('results', [])
    
    if not results:
        st.info("No results found matching your criteria.")
        return
    
    # Display search summary
    st.success(f"✅ Found {len(results)} results using {search_results.get('strategy', 'unknown')} strategy")
    
    # Display search strategy info
    if search_results.get('analysis'):
        analysis = search_results['analysis']
        with st.expander("🔍 Search Analysis Details"):
            st.json(analysis)
    
    # Display results summary table
    st.markdown("### 📋 Search Results Summary")
    
    summary_data = []
    for result in results[:20]:  # Limit to top 20 for display
        citation = result.get('citation', f"{result.get('country_name', 'Unknown')}, {result.get('year', 'Unknown')}")
        relevance_score = result.get('relevance_score', 0)
        word_count = result.get('word_count', 0)
        
        summary_data.append({
            'Citation': citation,
            'Relevance Score': f"{relevance_score:.2f}",
            'Word Count': f"{word_count:,}",
            'Region': result.get('region', 'Unknown'),
            'Preview': result.get('speech_text', '')[:100] + '...' if len(result.get('speech_text', '')) > 100 else result.get('speech_text', '')
        })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
    
    # Display detailed results with citations
    if include_citations:
        display_detailed_results_with_citations(results)
    
    # Display relevant quotes with proper citations
    display_relevant_quotes_with_citations(results)


def display_detailed_results_with_citations(results: List[Dict[str, Any]]):
    """Display detailed results with proper citations."""
    st.markdown("### 📄 Detailed Results with Citations")
    
    for i, result in enumerate(results[:10]):  # Limit to top 10 detailed results
        citation = result.get('citation', f"{result.get('country_name', 'Unknown')}, {result.get('year', 'Unknown')}")
        relevance_score = result.get('relevance_score', 0)
        
        with st.expander(f"Result {i+1}: {citation} (Relevance: {relevance_score:.2f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Source:** {citation}")
                st.markdown(f"**Region:** {result.get('region', 'Unknown')}")
                st.markdown(f"**Word Count:** {result.get('word_count', 0):,}")
                
                # Display speech text
                speech_text = result.get('speech_text', '')
                if speech_text:
                    st.markdown("**Speech Content:**")
                    st.text(speech_text[:500] + "..." if len(speech_text) > 500 else speech_text)
            
            with col2:
                st.markdown(f"**Relevance Score:** {relevance_score:.2f}")
                st.markdown(f"**Session:** {result.get('session', 'Unknown')}")
                st.markdown(f"**African Member:** {'Yes' if result.get('is_african_member') else 'No'}")
                
                # Display relevant quotes if available
                relevant_quotes = result.get('relevant_quotes', [])
                if relevant_quotes:
                    st.markdown("**Relevant Quotes:**")
                    for quote in relevant_quotes[:3]:
                        st.markdown(f"- \"{quote['quote']}\" (Score: {quote['relevance_score']:.2f})")


def display_relevant_quotes_with_citations(results: List[Dict[str, Any]]):
    """Display relevant quotes with proper citations."""
    st.markdown("### 💬 Relevant Quotes with Citations")
    
    all_quotes = []
    for result in results[:10]:  # Top 10 results
        relevant_quotes = result.get('relevant_quotes', [])
        for quote in relevant_quotes:
            quote['source_citation'] = result.get('citation', f"{result.get('country_name', 'Unknown')}, {result.get('year', 'Unknown')}")
            all_quotes.append(quote)
    
    # Sort quotes by relevance
    all_quotes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Display top quotes
    for i, quote in enumerate(all_quotes[:15]):  # Top 15 quotes
        with st.expander(f"Quote {i+1}: {quote['source_citation']} (Relevance: {quote['relevance_score']:.2f})"):
            st.markdown(f"**Source:** {quote['source_citation']}")
            st.markdown(f"**Quote:** \"{quote['quote']}\"")
            st.markdown(f"**Relevance Score:** {quote['relevance_score']:.2f}")


def get_available_countries() -> List[str]:
    """Get list of available countries from the database."""
    from src.unga_analysis.utils.country_manager import get_all_countries
    return get_all_countries()


def render_search_suggestions(tab_context: str = "general"):
    """Render dynamic search suggestions based on available data."""
    st.markdown("### 💡 Search Suggestions")
    
    # Get suggestions based on tab context
    suggestions = get_contextual_suggestions(tab_context)
    
    # Display suggestions in columns
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"suggestion_{i}_{tab_context}", use_container_width=True):
                st.session_state[f"unified_search_{tab_context}"] = suggestion
                st.rerun()


def get_contextual_suggestions(tab_context: str) -> List[str]:
    """Get contextual search suggestions based on tab."""
    base_suggestions = [
        "How has climate change discourse evolved over time?",
        "What are the main themes in African countries' speeches?",
        "Compare China and US priorities in recent years",
        "Which countries mention gender equality most frequently?",
        "What are the trends in peace and security discussions?"
    ]
    
    contextual_suggestions = {
        "database_chat": base_suggestions + [
            "How has China's focus changed over the years?",
            "What were the main priorities for the United States in the 1990s?",
            "How did African countries' priorities evolve from 2000-2020?"
        ],
        "cross_year": base_suggestions + [
            "Analyze gender equality mentions across all countries over the past decade",
            "Compare environmental priorities between developed and developing countries",
            "What are the most frequently mentioned SDGs in speeches?"
        ],
        "data_explorer": base_suggestions + [
            "Show data availability by country and year",
            "Which countries have the most complete speech records?",
            "What are the gaps in speech data coverage?"
        ],
        "general": base_suggestions
    }
    
    return contextual_suggestions.get(tab_context, base_suggestions)


def render_search_analytics(search_history: List[Dict[str, Any]]):
    """Render search analytics and insights."""
    if not search_history:
        return
    
    st.markdown("### 📊 Search Analytics")
    
    # Calculate basic statistics
    total_searches = len(search_history)
    unique_queries = len(set(search.get('query', '') for search in search_history))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Searches", total_searches)
    with col2:
        st.metric("Unique Queries", unique_queries)
    with col3:
        avg_results = sum(search.get('total_found', 0) for search in search_history) / total_searches if total_searches > 0 else 0
        st.metric("Avg Results per Search", f"{avg_results:.1f}")
    
    # Display recent searches
    st.markdown("#### 🔍 Recent Searches")
    recent_searches = search_history[-10:]  # Last 10 searches
    
    for search in recent_searches:
        with st.expander(f"Query: {search.get('query', 'Unknown')[:50]}..."):
            st.markdown(f"**Query:** {search.get('query', 'Unknown')}")
            st.markdown(f"**Strategy:** {search.get('strategy', 'Unknown')}")
            st.markdown(f"**Results Found:** {search.get('total_found', 0)}")
            st.markdown(f"**Timestamp:** {search.get('timestamp', 'Unknown')}")
