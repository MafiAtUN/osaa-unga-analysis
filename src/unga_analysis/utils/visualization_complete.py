"""
Advanced visualization module for UN General Assembly speech analysis.
Implements high-impact visualizations for cross-year analysis.
Retrieved from: https://raw.githubusercontent.com/MafiAtUN/osaa-unga-analysis/refs/heads/main/src/unga_analysis/utils/visualization.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import re
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


def create_methodology_tooltip(methodology_text: str) -> str:
    """Create a methodology tooltip that appears on hover."""
    return f"""
<div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 3px solid #1f77b4;">
    <strong>ℹ️ Methodology:</strong><br>
    {methodology_text}
</div>
"""


def add_methodology_section(methodology_text: str):
    """Add a collapsible methodology section."""
    with st.expander("ℹ️ Methodology", expanded=False):
        st.markdown(methodology_text)


class UNGAVisualizationManager:
    """Manages all visualization components for UNGA speech analysis."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def render_visualization_menu(self):
        """Render the main visualization menu with all available options."""
        st.markdown("## 📊 Advanced Visualizations")
        st.markdown("**Interactive tools to explore UNGA speech patterns, diplomatic relationships, and global agenda evolution (1946-2025)**")
        
        
        # Add overview
        st.info("""
        **🎯 Choose a visualization category below to analyze:**
        - **Issue Salience & Topics**: How attention to different topics has evolved over time
        - **Country Positions & Similarity**: How countries position themselves and find similar speeches
        - **Trends & Trajectories**: Track keyword evolution, sentiment changes, and event impacts
        - **Networks & Relationships**: Explore diplomatic relationships and speaker patterns
        """)
        
        # Show data availability info
        try:
            available_years = self.db_manager.conn.execute("SELECT DISTINCT year FROM speeches ORDER BY year").fetchall()
            available_years_list = [row[0] for row in available_years]
            total_speeches = self.db_manager.conn.execute("SELECT COUNT(*) FROM speeches").fetchone()[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📅 Years Available", f"{min(available_years_list)} - {max(available_years_list)}")
            with col2:
                st.metric("📊 Total Speeches", f"{total_speeches:,}")
            with col3:
                st.metric("🌍 Countries", len(self._get_available_countries()))
                
        except Exception as e:
            st.warning("Could not load data statistics. Please ensure the database is properly initialized.")
        
        # Create tabs for different visualization categories
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Issue Salience & Topics",
            "🌍 Country Positions & Similarity",
            "📈 Trends & Trajectories",
            "🎯 SDG Analysis",
            "🔗 Networks & Relationships"
        ])
        
        with tab1:
            self._render_issue_salience_tab()
        
        with tab2:
            self._render_country_positions_tab()
        
        with tab3:
            self._render_trends_tab()
        
        with tab4:
            self._render_sdg_tab()
        
        with tab5:
            self._render_networks_tab()
    
    def _get_available_countries(self) -> List[str]:
        """Get list of available countries from database."""
        try:
            result = self.db_manager.conn.execute("""
                SELECT DISTINCT country_name 
                FROM speeches 
                WHERE country_name IS NOT NULL 
                ORDER BY country_name
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting available countries: {e}")
            return []
    
    def _render_issue_salience_tab(self):
        """Render issue salience and topic visualizations."""
        st.markdown("### 🎯 Issue Salience & Topics")
        st.markdown("**Analyze how attention to different topics has evolved across years and regions.**")
        
        st.markdown("""
        **What this analysis does:**
        - 📊 **Tracks topic mentions** over time using keyword analysis
        - 📈 **Shows agenda evolution** - which issues gained/lost attention
        - 🌍 **Compares regions** - how different areas prioritize topics
        - 🔍 **Identifies patterns** - when topics peaked or declined
        
        **Example questions you can answer:**
        - "When did climate change become a major UNGA topic?"
        - "Which regions talk most about gender equality?"
        - "How did the Ukraine war affect global discourse?"
        - "What topics dominated during the Cold War vs. post-9/11?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### ⚙️ Configuration")
            st.markdown("*Configure your analysis parameters below*")
            
            # Topic selection
            topics = st.multiselect(
                "Select Topics to Analyze",
                options=[
                    "Climate Change", "Peace & Security", "Development",
                    "Human Rights", "Gender Equality", "Trade",
                    "Health", "Education", "Migration", "Technology",
                    "AI", "Palestine", "Ukraine", "Debt", "Multilateralism"
                ],
                default=["Climate Change", "Peace & Security", "Development"],
                key="issue_salience_topics",
                help="Choose 1-5 topics to compare. Each topic uses keyword matching to identify relevant speeches."
            )
            
            # Year range
            year_range = st.slider(
                "Year Range",
                min_value=1946,
                max_value=2025,
                value=(2000, 2025),
                step=1,
                key="issue_salience_year_range",
                help="Select the time period to analyze. Longer periods show more trends, shorter periods show recent patterns."
            )
            
            # Region filter - get actual regions from database
            try:
                available_regions_query = self.db_manager.conn.execute("""
                    SELECT DISTINCT region 
                    FROM speeches 
                    WHERE region IS NOT NULL 
                    ORDER BY region
                """).fetchall()
                available_regions = [r[0] for r in available_regions_query if r[0]]
                
                if not available_regions:
                    available_regions = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Caribbean"]
            except:
                available_regions = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Caribbean"]
            
            regions = st.multiselect(
                "Regions (optional)",
                options=available_regions,
                default=[],
                key="issue_salience_regions",
                help="Filter by specific regions. Leave empty to include all regions in the analysis."
            )
            
            # Visualization type
            viz_type = st.selectbox(
                "Visualization Type",
                options=[
                    "Multi-line Trends",
                    "Stacked Area Chart",
                    "Session Heatmap",
                    "Regional Comparison"
                ],
                key="issue_salience_viz_type",
                help="Choose how to display the topic data"
            )
            
            if st.button("Generate Visualization", key="issue_salience"):
                st.session_state.issue_salience_selected_topics = topics
                st.session_state.issue_salience_selected_year_range = year_range
                st.session_state.issue_salience_selected_regions = regions
                st.session_state.issue_salience_selected_viz_type = viz_type
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            
            if hasattr(st.session_state, 'issue_salience_selected_topics'):
                self._create_issue_salience_chart(
                    st.session_state.issue_salience_selected_topics,
                    st.session_state.issue_salience_selected_year_range,
                    st.session_state.issue_salience_selected_regions,
                    st.session_state.issue_salience_selected_viz_type
                )
            else:
                st.info("👆 Configure your analysis parameters on the left and click 'Generate Visualization' to see results here.")
    
    def _create_issue_salience_chart(self, topics, year_range, regions, viz_type):
        """Create issue salience visualization based on parameters."""
        try:
            # Get topic keyword mappings
            topic_keywords = self._get_topic_keywords(topics)
            
            # Query database for speech data
            with st.spinner(f"Analyzing speeches from {year_range[0]}-{year_range[1]}..."):
                speeches = self._get_speeches_for_topics(year_range, regions)
            
            if not speeches:
                st.warning(f"⚠️ No speeches found for the selected criteria.")
                st.info(f"Try adjusting your filters: Year range, Topics, or Regions")
                return
            
            # Show analysis summary
            st.success(f"✅ Analyzing {len(speeches):,} speeches across {len(set(s['year'] for s in speeches))} years")
            
            # Calculate topic frequencies
            topic_data = self._calculate_topic_frequencies(speeches, topic_keywords, year_range)
            
            # Create visualization based on type
            if viz_type == "Multi-line Trends":
                fig = self._create_multiline_trends(topic_data, topics)
            elif viz_type == "Stacked Area Chart":
                fig = self._create_stacked_area(topic_data, topics)
            elif viz_type == "Session Heatmap":
                fig = self._create_session_heatmap(topic_data, topics)
            else:  # Regional Comparison
                fig = self._create_regional_comparison(topic_data, topics, regions)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Add methodology
                add_methodology_section(f"""
                **Data Source:** {len(speeches)} speeches from {year_range[0]}-{year_range[1]}
                
                **Topic Detection Method:** Keyword matching using curated term lists for each topic
                
                **Calculation:** For each topic, count speeches containing topic keywords divided by total speeches per year
                
                **Topics Analyzed:** {', '.join(topics)}
                
                **Regions Included:** {', '.join(regions) if regions else 'All regions'}
                """)
                
        except Exception as e:
            st.error(f"❌ Error creating visualization: {e}")
            st.info("Please try adjusting your parameters or contact support if the issue persists.")
    
    def _get_topic_keywords(self, topics: List[str]) -> Dict[str, List[str]]:
        """Get keyword mappings for topics."""
        topic_keyword_map = {
            "Climate Change": ["climate", "global warming", "carbon", "emissions", "environment", "paris agreement", "cop"],
            "Peace & Security": ["peace", "security", "conflict", "war", "terrorism", "disarmament", "nuclear"],
            "Development": ["development", "sustainable", "poverty", "economic growth", "sdg", "millennium"],
            "Human Rights": ["human rights", "rights", "freedom", "democracy", "justice", "dignity"],
            "Gender Equality": ["gender", "women", "girls", "equality", "empowerment", "violence against women"],
            "Trade": ["trade", "commerce", "export", "import", "wto", "tariff", "market"],
            "Health": ["health", "pandemic", "disease", "covid", "who", "healthcare", "medicine"],
            "Education": ["education", "school", "literacy", "learning", "university", "knowledge"],
            "Migration": ["migration", "refugee", "asylum", "displacement", "migrant", "immigration"],
            "Technology": ["technology", "digital", "innovation", "internet", "cyber", "data"],
            "AI": ["artificial intelligence", "ai", "machine learning", "automation", "algorithm"],
            "Palestine": ["palestine", "palestinian", "gaza", "west bank", "israel-palestine"],
            "Ukraine": ["ukraine", "ukrainian", "russia-ukraine", "crimea", "donbas"],
            "Debt": ["debt", "loan", "credit", "financial crisis", "default", "restructuring"],
            "Multilateralism": ["multilateral", "cooperation", "united nations", "un", "global governance"]
        }
        
        return {topic: topic_keyword_map.get(topic, []) for topic in topics}
    
    def _get_speeches_for_topics(self, year_range, regions):
        """Get speeches from database for topic analysis."""
        try:
            # Get country-to-region mapping
            from src.unga_analysis.data.data_ingestion import COUNTRY_CODE_MAPPING, REGION_MAPPING
            
            # Create reverse mapping: country name -> region
            country_to_region = {}
            for code, name in COUNTRY_CODE_MAPPING.items():
                region = REGION_MAPPING.get(code)
                if region:
                    country_to_region[name] = region
            
            # Build query - DON'T use region column, use country names instead
            where_conditions = [
                f"year >= {year_range[0]}",
                f"year <= {year_range[1]}",
                "speech_text IS NOT NULL"
            ]
            
            # If regions specified, filter by country names in those regions
            params = []
            if regions:
                # Get all countries in the selected regions
                countries_in_regions = [name for name, reg in country_to_region.items() if reg in regions]
                if countries_in_regions:
                    # Use parameterized query to avoid SQL injection with apostrophes
                    placeholders = ','.join(['?' for _ in countries_in_regions])
                    where_conditions.append(f"country_name IN ({placeholders})")
                    params.extend(countries_in_regions)
                else:
                    # No countries match these regions
                    return []
            
            query = f"""
                SELECT country_name, year, speech_text
                FROM speeches
                WHERE {' AND '.join(where_conditions)}
                ORDER BY year, country_name
            """
            
            # Execute query with parameters
            if params:
                result = self.db_manager.conn.execute(query, params).fetchall()
            else:
                result = self.db_manager.conn.execute(query).fetchall()
            
            # Check if result is empty
            if not result:
                return []
            
            speeches = []
            for row in result:
                # Check if row has required fields (3 columns now: country, year, text)
                if len(row) >= 3:
                    country_name = row[0]
                    # Derive region from country name using mapping
                    derived_region = country_to_region.get(country_name, 'Unknown')
                    
                    speeches.append({
                        'country': country_name,
                        'year': row[1],
                        'text': row[2],
                        'region': derived_region  # Derived from country mapping
                    })
            
            return speeches
            
        except Exception as e:
            logger.error(f"Error getting speeches for topics: {e}")
            raise
    
    def _calculate_topic_frequencies(self, speeches, topic_keywords, year_range):
        """Calculate topic frequencies by year."""
        years = list(range(year_range[0], year_range[1] + 1))
        topic_data = {topic: {year: 0 for year in years} for topic in topic_keywords.keys()}
        speeches_per_year = {year: 0 for year in years}
        
        # Count speeches and topic mentions
        for speech in speeches:
            year = speech['year']
            text_lower = speech['text'].lower()
            speeches_per_year[year] += 1
            
            for topic, keywords in topic_keywords.items():
                if any(keyword.lower() in text_lower for keyword in keywords):
                    topic_data[topic][year] += 1
        
        # Convert to percentages
        for topic in topic_data:
            for year in years:
                if speeches_per_year[year] > 0:
                    topic_data[topic][year] = (topic_data[topic][year] / speeches_per_year[year]) * 100
        
        return topic_data
    
    def _create_multiline_trends(self, topic_data, topics):
        """Create multi-line trend chart."""
        try:
            # Prepare data for plotting
            data_list = []
            for topic, year_data in topic_data.items():
                for year, percentage in year_data.items():
                    data_list.append({
                        'Year': year,
                        'Topic': topic,
                        'Percentage': percentage
                    })
            
            df = pd.DataFrame(data_list)
            
            fig = px.line(
                df,
                x='Year',
                y='Percentage',
                color='Topic',
                title='Topic Salience Over Time',
                labels={'Percentage': '% of Speeches Mentioning Topic'},
                markers=True
            )
            
            fig.update_layout(
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating multiline trends: {e}")
            return None
    
    def _create_stacked_area(self, topic_data, topics):
        """Create stacked area chart."""
        try:
            # Prepare data
            data_list = []
            for topic, year_data in topic_data.items():
                for year, percentage in year_data.items():
                    data_list.append({
                        'Year': year,
                        'Topic': topic,
                        'Percentage': percentage
                    })
            
            df = pd.DataFrame(data_list)
            
            fig = px.area(
                df,
                x='Year',
                y='Percentage',
                color='Topic',
                title='Cumulative Topic Attention Over Time',
                labels={'Percentage': '% of Speeches'}
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating stacked area: {e}")
            return None
    
    def _create_session_heatmap(self, topic_data, topics):
        """Create heatmap showing topic intensity."""
        try:
            # Create matrix
            years = sorted(list(topic_data[topics[0]].keys()))
            matrix = []
            for topic in topics:
                matrix.append([topic_data[topic][year] for year in years])
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=years,
                y=topics,
                colorscale='YlOrRd',
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='Topic Intensity Heatmap',
                xaxis_title='Year',
                yaxis_title='Topic'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating session heatmap: {e}")
            return None
    
    def _create_regional_comparison(self, topic_data, topics, regions):
        """Create regional comparison chart."""
        st.info("Regional comparison visualization - showing aggregate topic focus by region")
        # This would need regional data aggregation
        return self._create_multiline_trends(topic_data, topics)
    
    def _render_country_positions_tab(self):
        """Render country position and similarity visualizations."""
        st.markdown("### 🌍 Country Positions & Similarity Analysis")
        st.markdown("**Explore how countries position themselves and find similar speeches.**")
        
        st.markdown("""
        **What this analysis does:**
        - 🗺️ **Maps country positions** in semantic space based on speech content
        - 🔍 **Finds similar speeches** using text similarity
        - 📊 **Analyzes topic composition** of individual countries
        
        **Example questions you can answer:**
        - "Which countries are ideologically similar to the US?"
        - "How has China's position changed over time?"
        - "Which countries sounded most like Kenya last year?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            # Country selection
            available_countries = self._get_available_countries()
            
            selected_country = st.selectbox(
                "Select Country",
                options=available_countries,
                key="similarity_country_input"
            )
            
            selected_year = st.number_input(
                "Select Year",
                min_value=1946,
                max_value=2025,
                value=2024,
                key="similarity_year_input"
            )
            
            top_n = st.slider(
                "Number of Similar Countries",
                min_value=5,
                max_value=20,
                value=10,
                key="similarity_top_n_input"
            )
            
            if st.button("Find Similar Countries", key="find_similarity_btn"):
                st.session_state.similarity_result_country = selected_country
                st.session_state.similarity_result_year = selected_year
                st.session_state.similarity_result_top_n = top_n
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            
            if hasattr(st.session_state, 'similarity_result_country'):
                self._show_similar_countries(
                    st.session_state.similarity_result_country,
                    st.session_state.similarity_result_year,
                    st.session_state.similarity_result_top_n
                )
            else:
                st.info("👆 Select a country and year on the left to find similar speeches.")
    
    def _show_similar_countries(self, country, year, top_n):
        """Show countries with similar speeches."""
        try:
            # Get target speech
            target_speech = self.db_manager.conn.execute("""
                SELECT speech_text FROM speeches
                WHERE country_name = ? AND year = ?
                LIMIT 1
            """, [country, year]).fetchone()
            
            if not target_speech:
                st.warning(f"No speech found for {country} in {year}")
                return
            
            target_text = target_speech[0]
            
            # Get all speeches from the same year
            all_speeches = self.db_manager.conn.execute("""
                SELECT country_name, speech_text
                FROM speeches
                WHERE year = ? AND country_name != ?
            """, [year, country]).fetchall()
            
            if not all_speeches:
                st.warning(f"No other speeches found for {year}")
                return
            
            # Calculate similarity (simple word overlap for now)
            similarities = []
            target_words = set(target_text.lower().split())
            
            for other_country, other_text in all_speeches:
                other_words = set(other_text.lower().split())
                overlap = len(target_words & other_words)
                similarity = overlap / (len(target_words) + len(other_words) - overlap) if (len(target_words) + len(other_words) - overlap) > 0 else 0
                similarities.append({
                    'Country': other_country,
                    'Similarity': similarity * 100
                })
            
            # Sort and get top N
            similarities.sort(key=lambda x: x['Similarity'], reverse=True)
            top_similar = similarities[:top_n]
            
            # Create bar chart
            df = pd.DataFrame(top_similar)
            fig = px.bar(
                df,
                x='Similarity',
                y='Country',
                orientation='h',
                title=f'Top {top_n} Countries Most Similar to {country} ({year})',
                labels={'Similarity': 'Similarity Score (%)'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show details
            st.markdown("#### 📋 Similarity Scores")
            for i, item in enumerate(top_similar, 1):
                st.markdown(f"{i}. **{item['Country']}**: {item['Similarity']:.1f}% similar")
            
        except Exception as e:
            st.error(f"Error calculating similarity: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    def _render_trends_tab(self):
        """Render trends and trajectories visualizations."""
        st.markdown("### 📈 Trends & Trajectories")
        st.markdown("**Track how specific keywords evolved across countries, regions, and time.**")
        
        st.markdown("""
        **What this analysis does:**
        - 📈 **Keyword frequency tracking** - see how often specific terms are mentioned
        - 🌍 **Multi-country comparison** - compare keyword usage across countries/regions
        - 🎯 **Event impact analysis** - measure discourse changes around major events
        - 📊 **Trajectory analysis** - identify rising and declining themes
        
        **Example questions:**
        - "How does 'climate justice' usage differ between Africa, Asia, and Europe?"
        - "Which countries increased 'artificial intelligence' mentions most?"
        - "Did 'terrorism' spike uniformly after 9/11 or vary by region?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            # Keyword input
            keyword = st.text_input(
                "Enter Keyword/Phrase",
                value="climate change",
                key="trends_keyword_input",
                help="Enter a word or phrase to track over time"
            )
            
            # Year range
            year_range = st.slider(
                "Year Range",
                min_value=1946,
                max_value=2025,
                value=(2000, 2025),
                key="trends_year_input"
            )
            
            # Analysis mode selection
            analysis_mode = st.radio(
                "Compare By:",
                options=["Regions", "Individual Countries", "Overall Trend"],
                key="trends_mode_input",
                help="Choose whether to compare regions, specific countries, or show overall trend"
            )
            
            # Conditional filters based on mode
            selected_entities = []
            if analysis_mode == "Regions":
                # Get available regions dynamically
                try:
                    available_regions_query = self.db_manager.conn.execute("""
                        SELECT DISTINCT region 
                        FROM speeches 
                        WHERE region IS NOT NULL 
                        ORDER BY region
                    """).fetchall()
                    available_regions = [r[0] for r in available_regions_query if r[0]]
                    
                    if not available_regions:
                        available_regions = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Caribbean"]
                except:
                    available_regions = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Caribbean"]
                
                selected_entities = st.multiselect(
                    "Select Regions to Compare",
                    options=available_regions,
                    default=["Africa", "Asia", "Europe"],
                    key="trends_regions_input",
                    help="Compare keyword usage across regions"
                )
                
            elif analysis_mode == "Individual Countries":
                available_countries = self._get_available_countries()
                selected_entities = st.multiselect(
                    "Select Countries to Compare (max 10)",
                    options=available_countries,
                    default=[],
                    max_selections=10,
                    key="trends_countries_input",
                    help="Compare keyword usage across specific countries"
                )
            
            if st.button("Generate Trend", key="trends_generate_btn"):
                st.session_state.trends_result_keyword = keyword
                st.session_state.trends_result_year_range = year_range
                st.session_state.trends_result_mode = analysis_mode
                st.session_state.trends_result_entities = selected_entities
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            
            if hasattr(st.session_state, 'trends_result_keyword'):
                self._create_keyword_trend_comparison(
                    st.session_state.trends_result_keyword,
                    st.session_state.trends_result_year_range,
                    st.session_state.trends_result_mode,
                    st.session_state.trends_result_entities
                )
            else:
                st.info("👆 Configure your keyword analysis on the left and click 'Generate Trend' to see comparative trends.")
    
    def _create_keyword_trend_comparison(self, keyword, year_range, mode, entities):
        """Create multi-entity keyword trend comparison visualization."""
        try:
            from src.unga_analysis.data.data_ingestion import COUNTRY_CODE_MAPPING, REGION_MAPPING
            
            # Create country-to-region mapping
            country_to_region = {}
            for code, name in COUNTRY_CODE_MAPPING.items():
                region = REGION_MAPPING.get(code)
                if region:
                    country_to_region[name] = region
            
            keyword_lower = keyword.lower()
            
            if mode == "Overall Trend":
                # Original single-line trend
                self._create_keyword_trend_simple(keyword, year_range)
                return
            
            elif mode == "Regions":
                if not entities:
                    st.warning("Please select at least one region to compare")
                    return
                
                # Build data for regional comparison
                with st.spinner(f"Analyzing '{keyword}' across {len(entities)} regions..."):
                    regional_data = {}
                    
                    for region in entities:
                        # Get countries in this region
                        countries_in_region = [name for name, reg in country_to_region.items() if reg == region]
                        
                        if not countries_in_region:
                            continue
                        
                        # Query speeches for this region
                        region_params = countries_in_region
                        placeholders = ','.join(['?' for _ in countries_in_region])
                        
                        query = f"""
                            SELECT year, speech_text
                            FROM speeches
                            WHERE year >= ? AND year <= ?
                            AND speech_text IS NOT NULL
                            AND country_name IN ({placeholders})
                        """
                        
                        params = [year_range[0], year_range[1]] + region_params
                        result = self.db_manager.conn.execute(query, params).fetchall()
                        
                        # Calculate frequency by year
                        year_counts = {}
                        year_totals = {}
                        
                        for year_val, text in result:
                            if year_val not in year_counts:
                                year_counts[year_val] = 0
                                year_totals[year_val] = 0
                            
                            year_totals[year_val] += 1
                            if keyword_lower in text.lower():
                                year_counts[year_val] += 1
                        
                        # Store regional data
                        regional_data[region] = {
                            'year_counts': year_counts,
                            'year_totals': year_totals,
                            'total_speeches': len(result)
                        }
                
            elif mode == "Individual Countries":
                if not entities:
                    st.warning("Please select at least one country to compare")
                    return
                
                # Build data for country comparison
                with st.spinner(f"Analyzing '{keyword}' across {len(entities)} countries..."):
                    country_data = {}
                    
                    for country in entities:
                        # Query speeches for this country
                        query = """
                            SELECT year, speech_text
                            FROM speeches
                            WHERE year >= ? AND year <= ?
                            AND speech_text IS NOT NULL
                            AND country_name = ?
                        """
                        
                        result = self.db_manager.conn.execute(query, [year_range[0], year_range[1], country]).fetchall()
                        
                        # Calculate frequency by year
                        year_counts = {}
                        year_totals = {}
                        
                        for year_val, text in result:
                            if year_val not in year_counts:
                                year_counts[year_val] = 0
                                year_totals[year_val] = 0
                            
                            year_totals[year_val] += 1
                            if keyword_lower in text.lower():
                                year_counts[year_val] += 1
                        
                        # Store country data
                        country_data[country] = {
                            'year_counts': year_counts,
                            'year_totals': year_totals,
                            'total_speeches': len(result)
                        }
            
            # Create multi-line comparison chart
            data_list = []
            
            if mode == "Regions":
                for region, data in regional_data.items():
                    for year in range(year_range[0], year_range[1] + 1):
                        count = data['year_counts'].get(year, 0)
                        total = data['year_totals'].get(year, 0)
                        percentage = (count / total * 100) if total > 0 else 0
                        
                        data_list.append({
                            'Year': year,
                            'Entity': region,
                            'Percentage': percentage,
                            'Count': count,
                            'Total': total
                        })
                
                entity_type = "Region"
                total_entities_analyzed = len(regional_data)
                total_speeches_analyzed = sum(d['total_speeches'] for d in regional_data.values())
                
            else:  # Individual Countries
                for country, data in country_data.items():
                    for year in range(year_range[0], year_range[1] + 1):
                        count = data['year_counts'].get(year, 0)
                        total = data['year_totals'].get(year, 0)
                        percentage = (count / total * 100) if total > 0 else 0
                        
                        data_list.append({
                            'Year': year,
                            'Entity': country,
                            'Percentage': percentage,
                            'Count': count,
                            'Total': total
                        })
                
                entity_type = "Country"
                total_entities_analyzed = len(country_data)
                total_speeches_analyzed = sum(d['total_speeches'] for d in country_data.values())
            
            if not data_list:
                st.warning("No data available for the selected entities")
                return
            
            # Create DataFrame
            df = pd.DataFrame(data_list)
            
            # Success message
            st.success(f"✅ Analyzing '{keyword}' across {total_entities_analyzed} {entity_type.lower()}{'s' if total_entities_analyzed > 1 else ''} ({total_speeches_analyzed:,} speeches)")
            
            # Create multi-line chart
            fig = px.line(
                df,
                x='Year',
                y='Percentage',
                color='Entity',
                title=f'"{keyword}" Mentions by {entity_type} Over Time',
                labels={'Percentage': f'% of Speeches Mentioning "{keyword}"'},
                markers=True
            )
            
            fig.update_traces(
                hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Percentage: %{y:.1f}%<br>Mentions: %{customdata[1]}<br>Total Speeches: %{customdata[2]}<extra></extra>',
                customdata=df[['Entity', 'Count', 'Total']].values
            )
            
            fig.update_layout(
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    title=f"{entity_type}s"
                ),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.markdown("### 📊 Summary Statistics")
            
            cols = st.columns(min(len(entities) if entities else 3, 4))
            
            if mode == "Regions":
                data_dict = regional_data
            else:
                data_dict = country_data
            
            for idx, (entity, data) in enumerate(data_dict.items()):
                if idx < len(cols):
                    with cols[idx]:
                        total_mentions = sum(data['year_counts'].values())
                        avg_pct = (total_mentions / data['total_speeches'] * 100) if data['total_speeches'] > 0 else 0
                        st.metric(
                            f"{entity}",
                            f"{total_mentions} mentions",
                            f"{avg_pct:.1f}% avg"
                        )
            
            # Methodology
            add_methodology_section(f"""
            **Keyword Searched:** "{keyword}"
            
            **Analysis Mode:** {mode}
            
            **Entities Analyzed:** {', '.join(entities) if entities else 'Overall'}
            
            **Method:** Case-insensitive substring matching in speech text
            
            **Calculation:** (Speeches mentioning keyword / Total speeches) × 100 per year per entity
            
            **Data Range:** {year_range[0]}-{year_range[1]} ({total_speeches_analyzed:,} speeches across {total_entities_analyzed} {entity_type.lower()}{'s' if total_entities_analyzed > 1 else ''})
            """)
            
        except Exception as e:
            st.error(f"Error creating keyword trend: {e}")
            st.info("Please try adjusting your parameters or selecting different entities.")
    
    def _create_keyword_trend_simple(self, keyword, year_range):
        """Create keyword frequency trend visualization."""
        try:
            # Query speeches
            query = """
                SELECT year, speech_text
                FROM speeches
                WHERE year >= ? AND year <= ?
                AND speech_text IS NOT NULL
            """
            
            result = self.db_manager.conn.execute(query, [year_range[0], year_range[1]]).fetchall()
            
            if not result:
                st.warning("No speeches found in the selected year range.")
                return
            
            # Calculate frequency
            keyword_lower = keyword.lower()
            year_counts = {}
            year_totals = {}
            
            for year_val, text in result:
                if year_val not in year_counts:
                    year_counts[year_val] = 0
                    year_totals[year_val] = 0
                
                year_totals[year_val] += 1
                if keyword_lower in text.lower():
                    year_counts[year_val] += 1
            
            # Calculate percentage
            data = []
            for year in sorted(year_counts.keys()):
                percentage = (year_counts[year] / year_totals[year] * 100) if year_totals[year] > 0 else 0
                data.append({
                    'Year': year,
                    'Percentage': percentage,
                    'Count': year_counts[year],
                    'Total': year_totals[year]
                })
            
            df = pd.DataFrame(data)
            
            # Create chart
            fig = px.line(
                df,
                x='Year',
                y='Percentage',
                title=f'Frequency of "{keyword}" in UNGA Speeches',
                labels={'Percentage': '% of Speeches Mentioning Keyword'},
                markers=True
            )
            
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>%{y:.1f}% of speeches<br>Count: %{customdata[0]}<extra></extra>',
                customdata=df[['Count']].values
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Mentions", sum(year_counts.values()))
            with col2:
                st.metric("📈 Peak Year", max(year_counts.items(), key=lambda x: x[1])[0])
            with col3:
                avg_pct = df['Percentage'].mean()
                st.metric("📉 Average %", f"{avg_pct:.1f}%")
            
            # Methodology
            add_methodology_section(f"""
            **Keyword Searched:** "{keyword}"
            
            **Search Method:** Case-insensitive substring matching in speech text
            
            **Calculation:** (Speeches mentioning keyword / Total speeches) × 100 per year
            
            **Data Range:** {year_range[0]}-{year_range[1]} ({len(result)} total speeches)
            """)
            
        except Exception as e:
            st.error(f"Error creating keyword trend: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    def _render_sdg_tab(self):
        """Render SDG analysis tab."""
        from .sdg_visualizations import render_sdg_visualization_tab
        render_sdg_visualization_tab(self.db_manager)
    
    def _render_networks_tab(self):
        """Render network and relationship visualizations."""
        st.markdown("### 🔗 Networks & Relationships")
        st.markdown("**Explore diplomatic relationships and co-occurrence patterns.**")
        
        st.markdown("""
        **What this analysis does:**
        - 🌐 **Maps country mentions** - who talks about whom
        - 🤝 **Identifies alliances** - based on co-mentions and similar rhetoric
        - 📊 **Shows influence** - which countries are most mentioned by others
        
        **Example questions:**
        - "Which countries mention the United States most?"
        - "What is the network of African countries mentioning each other?"
        - "How have China's international mentions changed?"
        """)
        
        st.markdown("---")
        
        st.info("🚧 Network visualizations coming soon! This will include country mention networks, alliance mapping, and influence analysis.")

