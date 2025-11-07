"""
Database Chat Tab Module
Handles database querying and chat functionality for data availability and insights
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
from ...data.simple_vector_storage import simple_vector_storage as db_manager
from ...core.llm import run_analysis, get_available_models
from ...core.openai_client import get_openai_client
from ...core.enhanced_search_engine import get_enhanced_search_engine
from ...utils.region_utils import (
    extract_regions_and_countries,
    expand_regions_to_countries,
)
from ..unified_search_interface import render_unified_search_interface, render_search_suggestions


def render_database_chat_tab():
    """Render the database chat tab."""
    st.header("💬 Ask Anything")
    st.markdown("**Ask questions about UNGA speeches and get comprehensive insights from the database (1946-2025)**")
    
    # Initialize session state
    if 'db_chat_history' not in st.session_state:
        st.session_state.db_chat_history = []
    
    st.markdown("---")
    
    # Search suggestions (render first to handle state before widgets)
    render_search_suggestions("database_chat")
    
    # Unified search interface (render after suggestions to pick up updates)
    search_results = render_unified_search_interface("database_chat")
    
    # Legacy chat interface (for backward compatibility)
    st.markdown("---")
    st.markdown("### 💬 Legacy Chat Interface")
    
    # Chat input
    user_question = st.text_area(
        "Ask anything about UNGA speeches:",
        placeholder="e.g., 'How has China's focus changed over the years?' or 'What were the main priorities for African countries in the 2000s?'",
        height=100,
        key="db_chat_input"
    )
    
    # Model selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        available_models = get_available_models()
        if available_models:
            model = st.selectbox(
                "AI Model:",
                options=available_models,
                index=0,
                key="database_chat_model_select",
                help="Select the AI model for analysis"
            )
        else:
            model = "model-router-osaa-2"
            st.warning("⚠️ Using default model")
    
    with col2:
        if st.button("🔍 Ask", type="primary", use_container_width=True):
            if user_question.strip():
                process_database_query(user_question, model)
            else:
                st.warning("Please enter a question")
    
    # Display chat history
    if st.session_state.db_chat_history:
        st.markdown("---")
        st.markdown("### 📜 Chat History")
        
        for i, chat in enumerate(reversed(st.session_state.db_chat_history[-5:])):  # Show last 5
            with st.expander(f"Q{i+1}: {chat['question'][:50]}...", expanded=False):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                if chat.get('data_summary'):
                    st.markdown(f"**Data Summary:** {chat['data_summary']}")
                st.markdown(f"**Timestamp:** {chat['timestamp']}")


def process_database_query(question: str, model: str):
    """Process a database query question using enhanced search engine."""
    try:
        with st.spinner("🔍 Analyzing your question and searching through all available speeches..."):
            # Get enhanced search engine
            enhanced_search = get_enhanced_search_engine(db_manager)
            
            # Execute enhanced search
            search_results = enhanced_search.execute_enhanced_search(question)
            
            # Generate AI response with comprehensive data and proper citations
            ai_response = generate_enhanced_ai_response(question, search_results, model)
            
            # Store in chat history
            st.session_state.db_chat_history.append({
                'question': question,
                'answer': ai_response,
                'search_strategy': search_results.get('strategy', 'unknown'),
                'total_found': search_results.get('total_found', 0),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Display results
            st.markdown("### 🤖 AI Response")
            st.markdown(ai_response)
            
            # Display search strategy used
            if search_results.get('strategy'):
                st.info(f"🔍 **Search Strategy Used:** {search_results['strategy'].replace('_', ' ').title()}")
            
            # Display supporting data with proper citations
            if search_results.get('results'):
                display_supporting_data_with_citations(search_results['results'])
            
            st.success("✅ Analysis completed!")
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        import traceback
        st.code(traceback.format_exc())


def comprehensive_database_search(question: str) -> Dict[str, Any]:
    """Perform comprehensive search through the database for the question."""
    try:
        question_lower = question.lower()
        
        # Extract entities from the question
        regions_detected, countries_detected = extract_regions_and_countries(question)
        countries = sorted(set(countries_detected))
        regions = regions_detected
        years = extract_years_from_question(question)
        topics = extract_topics_from_question(question)

        st.caption(
            "🔍 Extracted Entities → "
            f"Countries: {', '.join(countries) if countries else 'None'} | "
            f"Regions: {', '.join(regions) if regions else 'None'} | "
            f"Years: {', '.join(map(str, years)) if years else 'None'} | "
            f"Topics: {', '.join(topics) if topics else 'None'}"
        )
        
        # Build comprehensive search query
        search_results = {
            'summary': '',
            'table_data': None,
            'speeches': [],
            'statistics': {},
            'countries_found': [],
            'years_covered': []
        }
        
        # Search for speeches based on extracted entities
        speeches_data = search_speeches_by_entities(countries, regions, years, topics, question)
        
        if speeches_data:
            search_results['speeches'] = speeches_data
            search_results['summary'] = f"Found {len(speeches_data)} relevant speeches"
            
            # Create summary table
            if speeches_data:
                df_data = []
                for speech in speeches_data[:20]:  # Limit to 20 for display
                    df_data.append({
                        'Country': speech.get('country_name', 'Unknown'),
                        'Year': speech.get('year', 'Unknown'),
                        'Word Count': speech.get('word_count', 0),
                        'Speech Preview': speech.get('speech_text', '')[:200] + '...' if len(speech.get('speech_text', '')) > 200 else speech.get('speech_text', ''),
                        'Date Added': speech.get('created_at', 'Unknown')
                    })
                
                search_results['table_data'] = pd.DataFrame(df_data)
                
                # Extract unique countries and years
                search_results['countries_found'] = list(set([s.get('country_name', '') for s in speeches_data if s.get('country_name')]))
                search_results['years_covered'] = list(set([s.get('year', '') for s in speeches_data if s.get('year')]))
                
                # Generate statistics
                search_results['statistics'] = {
                    'total_speeches': len(speeches_data),
                    'countries_count': len(search_results['countries_found']),
                    'years_span': f"{min(search_results['years_covered'])}-{max(search_results['years_covered'])}" if search_results['years_covered'] else 'Unknown',
                    'total_words': sum([s.get('word_count', 0) for s in speeches_data]),
                    'avg_words': sum([s.get('word_count', 0) for s in speeches_data]) // len(speeches_data) if speeches_data else 0
                }
        else:
            search_results['summary'] = "No relevant speeches found. Try broadening your search criteria."
        
        return search_results
        
    except Exception as e:
        return {'summary': f'Search error: {e}', 'table_data': None, 'speeches': []}


def extract_years_from_question(question: str) -> List[int]:
    """Extract years from the question."""
    import re
    years = re.findall(r'\b(19|20)\d{2}\b', question)
    return [int(year) for year in years]


def extract_topics_from_question(question: str) -> List[str]:
    """Extract topic keywords from the question."""
    question_lower = question.lower()
    topics = []
    
    topic_keywords = {
        'climate change': ['climate', 'environment', 'global warming', 'carbon', 'emissions'],
        'economic development': ['economic', 'development', 'economy', 'trade', 'commerce'],
        'peace and security': ['peace', 'security', 'conflict', 'war', 'military'],
        'human rights': ['human rights', 'rights', 'democracy', 'freedom'],
        'health': ['health', 'pandemic', 'disease', 'medical'],
        'education': ['education', 'school', 'learning', 'knowledge'],
        'technology': ['technology', 'digital', 'innovation', 'ai', 'artificial intelligence'],
        'migration': ['migration', 'refugees', 'immigration', 'displacement'],
        'gender equality': ['gender', 'women', 'equality', 'feminism'],
        'sustainable development': ['sustainable', 'sustainability', 'sdgs', 'goals']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            topics.append(topic)
    
    return topics


def search_speeches_by_entities(countries: List[str], regions: List[str], years: List[int], topics: List[str], question: str) -> List[Dict[str, Any]]:
    """Search speeches based on extracted entities."""
    try:
        # Build SQL query based on available entities
        where_conditions = []
        params = []

        countries = sorted(set(countries))
        regions = sorted(set(regions))
        
        # Country conditions
        if countries:
            country_conditions = []
            for country in countries:
                country_conditions.append("country_name = ?")
                params.append(country)
            
            if country_conditions:
                where_conditions.append(f"({' OR '.join(country_conditions)})")

        # Region conditions (expanded to countries)
        if regions:
            region_countries = expand_regions_to_countries(regions)
            if region_countries:
                placeholders = ','.join(['?' for _ in region_countries])
                where_conditions.append(f"country_name IN ({placeholders})")
                params.extend(region_countries)
        
        # Year conditions
        if years:
            if len(years) == 1:
                where_conditions.append("year = ?")
                params.append(years[0])
            else:
                year_range = f"year BETWEEN {min(years)} AND {max(years)}"
                where_conditions.append(year_range)
        
        # Topic conditions (search in speech text)
        if topics:
            topic_conditions = []
            for topic in topics:
                topic_conditions.append("speech_text ILIKE ?")
                params.append(f"%{topic}%")
            
            if topic_conditions:
                where_conditions.append(f"({' OR '.join(topic_conditions)})")
        
        # If no specific entities, search for question keywords in speech text
        if not countries and not years and not topics:
            # Extract key words from the question for text search
            import re
            words = re.findall(r'\b\w{4,}\b', question.lower())  # Words with 4+ characters
            if words:
                text_conditions = []
                for word in words[:5]:  # Limit to 5 words
                    text_conditions.append("speech_text ILIKE ?")
                    params.append(f"%{word}%")
                
                if text_conditions:
                    where_conditions.append(f"({' OR '.join(text_conditions)})")
        
        # Build final query
        if where_conditions:
            query = f"""
                SELECT country_name, year, speech_text, word_count, created_at, region
                FROM speeches 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY year DESC, word_count DESC
                LIMIT 50
            """
        else:
            # Fallback: get recent speeches
            query = """
                SELECT country_name, year, speech_text, word_count, created_at, region
                FROM speeches 
                ORDER BY created_at DESC
                LIMIT 20
            """
            params = []
        
        # Execute query
        cursor = db_manager.conn.execute(query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        speeches = []
        for row in results:
            speeches.append({
                'country_name': row[0],
                'year': row[1],
                'speech_text': row[2],
                'word_count': row[3],
                'created_at': row[4],
                'region': row[5]
            })
        
        return speeches
        
    except Exception as e:
        print(f"Search error: {e}")
        return []


def generate_enhanced_ai_response(question: str, search_results: Dict[str, Any], model: str) -> str:
    """Generate enhanced AI response with proper document citations."""
    try:
        system_message = """You are an expert analyst for the UN General Assembly speeches database (1946-2025). 
        You provide comprehensive insights about historical trends, country priorities, and thematic analysis.
        
        CRITICAL REQUIREMENTS:
        - ALWAYS cite specific speeches with country name and year when referencing content
        - Use proper citation format: "As stated by [Country] in [Year]: '[quote]'"
        - Provide specific examples with exact quotes and their sources
        - Include document references for all claims and statistics
        - When analyzing trends, cite multiple speeches from different years/countries
        
        Your role:
        - Analyze historical trends and changes in country priorities over time
        - Provide detailed thematic analysis of speech content with proper citations
        - Compare countries and regions on various topics with specific examples
        - Explain patterns and evolution in UNGA discourse with supporting evidence
        - Use the provided speech data to give specific, evidence-based answers with proper attribution
        
        Always base your analysis on the actual speech data provided. Be specific about years, countries, and themes.
        If analyzing changes over time, compare different periods and highlight key shifts with proper citations."""
        
        # Prepare enhanced context with proper citations
        speeches_context = ""
        if search_results.get('results'):
            results = search_results['results']
            speeches_context = f"""
            Found {len(results)} relevant speeches from the database:
            
            Search Strategy: {search_results.get('strategy', 'unknown')}
            Query Analysis: {search_results.get('analysis', {})}
            
            Speech Data with Citations:
            """
            
            # Include speeches with proper citation format
            for i, speech in enumerate(results[:15]):  # Limit to 15 speeches for context
                citation = speech.get('citation', f"{speech.get('country_name', 'Unknown')}, {speech.get('year', 'Unknown')}")
                relevance_score = speech.get('relevance_score', 0)
                relevant_quotes = speech.get('relevant_quotes', [])
                
                speeches_context += f"""
            Speech {i+1}: {citation} (Relevance: {relevance_score:.2f})
            Text: {speech.get('speech_text', '')[:400]}...
            
            Relevant Quotes:
            """
                
                for quote in relevant_quotes[:3]:  # Top 3 quotes
                    speeches_context += f"            - \"{quote['quote']}\" (Relevance: {quote['relevance_score']:.2f})\n"
                
                speeches_context += "\n"
        
        user_message = f"""User Question: {question}

        {speeches_context}
        
        Please provide a comprehensive analysis answering the user's question. 
        
        REQUIREMENTS:
        1. Use the specific speech data provided to give evidence-based insights
        2. ALWAYS cite speeches using the format: "As stated by [Country] in [Year]: '[exact quote]'"
        3. Include specific examples with proper attribution
        4. If analyzing changes over time, compare different periods with specific citations
        5. If comparing countries, highlight differences and similarities with quoted examples
        6. Be specific about what the data shows and cite examples from the speeches when relevant
        7. Include document references for all statistical claims
        
        Format your response with proper citations throughout."""
        
        response = run_analysis(
            system_message,
            user_message,
            model,
            get_openai_client()
        )
        
        return response
        
    except Exception as e:
        return f"AI analysis failed: {e}. However, here's the raw data: {search_results.get('summary', 'No data available')}"


def display_supporting_data_with_citations(results: List[Dict[str, Any]]):
    """Display supporting data with proper citations."""
    if not results:
        return
    
    st.markdown("### 📋 Supporting Data with Citations")
    
    # Create a summary table
    summary_data = []
    for result in results[:20]:  # Limit to top 20 results
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
    
    # Display summary table
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
    
    # Display relevant quotes with proper citations
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
    for i, quote in enumerate(all_quotes[:10]):
        with st.expander(f"Quote {i+1}: {quote['source_citation']} (Relevance: {quote['relevance_score']:.2f})"):
            st.markdown(f"**Source:** {quote['source_citation']}")
            st.markdown(f"**Quote:** \"{quote['quote']}\"")
            st.markdown(f"**Relevance Score:** {quote['relevance_score']:.2f}")


def generate_comprehensive_ai_response(question: str, search_results: Dict[str, Any], model: str) -> str:
    """Legacy function for backward compatibility."""
    return generate_enhanced_ai_response(question, search_results, model)
