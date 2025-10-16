"""
Advanced visualization module for UN General Assembly speech analysis.
Implements high-impact visualizations for cross-year analysis.
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
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Issue Salience & Topics", 
            "🌍 Country Positions & Similarity", 
            "📈 Trends & Trajectories", 
            "🔗 Networks & Relationships"
        ])
        
        with tab1:
            self._render_issue_salience_tab()
        
        with tab2:
            self._render_country_positions_tab()
        
        with tab3:
            self._render_trends_tab()
        
        with tab4:
            self._render_networks_tab()
    
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
                    "Climate Change", "Peace & Security", "Development", "Human Rights",
                    "Gender Equality", "Trade", "Health", "Education", "Migration",
                    "Technology", "AI", "Palestine", "Ukraine", "Debt", "Multilateralism"
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
            
            # Region filter
            regions = st.multiselect(
                "Regions (optional)",
                options=["Africa", "Asia", "Europe", "Americas", "Oceania"],
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
                help="Choose how to display the topic data: Multi-line shows trends over time, Stacked shows cumulative totals, Heatmap shows intensity by year, Regional compares across areas"
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
    
    def _render_country_positions_tab(self):
        """Render country position and similarity visualizations."""
        st.markdown("### 🌍 Country Positions & Similarity Analysis")
        st.markdown("**Explore how countries position themselves in semantic space and find similar speeches.**")
        
        st.markdown("""
        **What this analysis does:**
        - 🗺️ **Maps country positions** in 2D semantic space based on speech content
        - 🔍 **Finds similar speeches** using text similarity algorithms
        - 📊 **Analyzes topic composition** of individual countries
        - 📋 **Creates country dossiers** with comprehensive analysis
        
        **Example questions you can answer:**
        - "Which countries are ideologically similar to the US?"
        - "How has China's position changed over time?"
        - "What did Brazil focus on in their 2023 speech?"
        - "Which countries sounded most like Kenya last year?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            # Show available countries info
            available_countries = self._get_available_countries()
            common_countries = self._get_common_countries_for_defaults()
            
            if available_countries:
                st.info(f"📊 **{len(available_countries)} countries** available in database")
                if common_countries:
                    st.info(f"🎯 **Common countries:** {', '.join(common_countries[:5])}{'...' if len(common_countries) > 5 else ''}")
            
            analysis_type = st.radio(
                "Analysis Type",
                options=[
                    "Country Position Map",
                    "Similar Speech Finder",
                    "Topic Composition",
                    "Country Dossier"
                ],
                key="country_positions_analysis_type",
                help="Choose your analysis: Position Map shows countries in 2D space, Similar Speech Finder finds comparable speeches, Topic Composition shows what countries focus on, Country Dossier provides comprehensive analysis"
            )
            
            if analysis_type == "Country Position Map":
                year = st.slider("Year", 1946, 2025, 2025, key="position_map_year")
                countries = st.multiselect(
                    "Countries to Highlight",
                    options=self._get_available_countries(),
                    default=self._get_common_countries_for_defaults()[:5],  # First 5 common countries
                    key="position_map_countries",
                    help="Select countries to highlight on the position map. Use the search box to find specific countries."
                )
                
                if st.button("Generate Position Map", key="position_map"):
                    st.session_state.position_map_selected_year = year
                    st.session_state.position_map_selected_countries = countries
                    st.session_state.position_map_type = "position_map"
                    st.rerun()
            
            elif analysis_type == "Similar Speech Finder":
                reference_country = st.selectbox(
                    "Reference Country",
                    options=self._get_available_countries(),
                    key="similar_speeches_country"
                )
                reference_year = st.slider("Reference Year", 1946, 2025, 2025, key="similar_speeches_year")
                similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, key="similar_speeches_threshold")
                
                if st.button("Find Similar Speeches", key="similar_speeches"):
                    st.session_state.similar_speeches_selected_country = reference_country
                    st.session_state.similar_speeches_selected_year = reference_year
                    st.session_state.similar_speeches_selected_threshold = similarity_threshold
                    st.session_state.position_map_type = "similar_speeches"
                    st.rerun()
            
            elif analysis_type == "Topic Composition":
                country = st.selectbox(
                    "Country",
                    options=self._get_available_countries(),
                    key="topic_composition_country"
                )
                year = st.slider("Year", 1946, 2025, 2025, key="topic_composition_year")
                
                if st.button("Analyze Topic Composition", key="topic_composition"):
                    st.session_state.topic_composition_selected_country = country
                    st.session_state.topic_composition_selected_year = year
                    st.session_state.position_map_type = "topic_composition"
                    st.rerun()
            
            elif analysis_type == "Country Dossier":
                country = st.selectbox(
                    "Country for Dossier",
                    options=self._get_available_countries(),
                    key="country_dossier_country"
                )
                
                if st.button("Generate Country Dossier", key="country_dossier"):
                    st.session_state.country_dossier_selected_country = country
                    st.session_state.position_map_type = "country_dossier"
                    st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            if hasattr(st.session_state, 'position_map_type'):
                if st.session_state.position_map_type == "position_map":
                    self._create_country_position_map(
                        st.session_state.position_map_selected_year,
                        st.session_state.position_map_selected_countries
                    )
                elif st.session_state.position_map_type == "similar_speeches":
                    self._create_similar_speech_finder(
                        st.session_state.similar_speeches_selected_country,
                        st.session_state.similar_speeches_selected_year,
                        st.session_state.similar_speeches_selected_threshold
                    )
                elif st.session_state.position_map_type == "topic_composition":
                    self._create_topic_composition_chart(
                        st.session_state.topic_composition_selected_country,
                        st.session_state.topic_composition_selected_year
                    )
                elif st.session_state.position_map_type == "country_dossier":
                    self._create_country_dossier(
                        st.session_state.country_dossier_selected_country
                    )
            else:
                st.info("👆 Select an analysis type and configure parameters on the left, then click the generate button to see results here.")
    
    def _render_trends_tab(self):
        """Render trend and trajectory visualizations."""
        st.markdown("### 📈 Trends & Trajectories")
        st.markdown("**Track keyword evolution, sentiment changes, and event-aligned timelines.**")
        
        st.markdown("""
        **What this analysis does:**
        - 🔤 **Tracks keyword evolution** - how specific terms gained/lost popularity
        - 😊 **Analyzes sentiment changes** - emotional tone over time
        - 📅 **Event-aligned analysis** - how speeches changed around major events
        - 🌍 **Regional comparisons** - differences in trends across areas
        
        **Example questions you can answer:**
        - "When did 'sustainable development' become popular?"
        - "Were speeches more pessimistic during COVID-19?"
        - "How did 9/11 change global discourse?"
        - "Which regions are most optimistic about the future?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            trend_type = st.radio(
                "Trend Analysis Type",
                options=[
                    "Keyword Trajectories",
                    "Sentiment & Tone",
                    "Event-Aligned Timeline",
                    "Regional Comparisons"
                ],
                key="trends_analysis_type"
            )
            
            if trend_type == "Keyword Trajectories":
                keywords = st.text_area(
                    "Keywords/Phrases (one per line)",
                    value="sustainable development\ngender equality\nclimate change\nartificial intelligence",
                    key="keyword_trajectories_text"
                ).split('\n')
                
                year_range = st.slider("Year Range", 1946, 2025, (2010, 2025), key="keyword_trajectories_year_range")
                
                if st.button("Track Keywords", key="keyword_tracking"):
                    st.session_state.keyword_trajectories_selected = keywords
                    st.session_state.keyword_year_range_selected = year_range
                    st.session_state.trends_type = "keyword_trajectories"
                    st.rerun()
            
            elif trend_type == "Sentiment & Tone":
                countries = st.multiselect(
                    "Countries",
                    options=self._get_available_countries(),
                    default=self._get_common_countries_for_defaults()[:3],  # First 3 common countries
                    key="sentiment_countries",
                    help="Select countries to analyze for sentiment and tone patterns."
                )
                
                year_range = st.slider("Year Range", 1946, 2025, (2000, 2025), key="sentiment_year_range")
                
                if st.button("Analyze Sentiment", key="sentiment_analysis"):
                    st.session_state.sentiment_selected_countries = countries
                    st.session_state.sentiment_selected_year_range = year_range
                    st.session_state.trends_type = "sentiment_analysis"
                    st.rerun()
            
            elif trend_type == "Event-Aligned Timeline":
                events = st.multiselect(
                    "Major Events",
                    options=[
                        "Cold War End (1991)", "9/11 (2001)", "Financial Crisis (2008)",
                        "Arab Spring (2011)", "Paris Agreement (2015)", "COVID-19 (2020)",
                        "Ukraine War (2022)"
                    ],
                    default=["Cold War End (1991)", "9/11 (2001)", "COVID-19 (2020)"],
                    key="event_timeline_events"
                )
                
                if st.button("Create Timeline", key="event_timeline"):
                    st.session_state.event_timeline_events = events
                    st.session_state.trends_type = "event_timeline"
                    st.rerun()
            
            elif trend_type == "Regional Comparisons":
                regions = st.multiselect(
                    "Regions",
                    options=["Africa", "Asia", "Europe", "Americas", "Oceania"],
                    default=["Africa", "Asia", "Europe"],
                    key="regional_comparison_regions"
                )
                
                metric = st.selectbox(
                    "Comparison Metric",
                    options=["Topic Focus", "Speech Length", "Sentiment", "Keyword Usage"],
                    key="regional_comparison_metric"
                )
                
                if st.button("Compare Regions", key="regional_comparison"):
                    st.session_state.regional_comparison_selected_regions = regions
                    st.session_state.regional_comparison_selected_metric = metric
                    st.session_state.trends_type = "regional_comparison"
                    st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            if hasattr(st.session_state, 'trends_type'):
                if st.session_state.trends_type == "keyword_trajectories":
                    self._create_keyword_trajectory_chart(
                        st.session_state.keyword_trajectories_selected,
                        st.session_state.keyword_year_range_selected
                    )
                elif st.session_state.trends_type == "sentiment_analysis":
                    self._create_sentiment_trend_chart(
                        st.session_state.sentiment_selected_countries,
                        st.session_state.sentiment_selected_year_range
                    )
                elif st.session_state.trends_type == "event_timeline":
                    self._create_event_timeline_chart(
                        st.session_state.event_timeline_events
                    )
                elif st.session_state.trends_type == "regional_comparison":
                    self._create_regional_comparison_chart(
                        st.session_state.regional_comparison_selected_regions,
                        st.session_state.regional_comparison_selected_metric
                    )
            else:
                st.info("👆 Select a trend analysis type and configure parameters on the left, then click the generate button to see results here.")
    
    def _render_networks_tab(self):
        """Render network and relationship visualizations."""
        st.markdown("### 🔗 Networks & Relationships")
        st.markdown("**Explore country-topic networks, co-mentions, and speaker patterns.**")
        
        st.markdown("""
        **What this analysis does:**
        - 🕸️ **Country-topic networks** - which countries focus on which issues
        - 🤝 **Co-mention networks** - diplomatic relationships and references
        - 👥 **Speaker patterns** - who speaks, when, and how
        - 🤝 **Alliance networks** - political groupings and alignments
        
        **Example questions you can answer:**
        - "Which countries drive the climate agenda?"
        - "Who are the strongest diplomatic allies?"
        - "How has female representation changed over time?"
        - "Which countries form the strongest political blocs?"
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            network_type = st.radio(
                "Network Type",
                options=[
                    "Country-Topic Network",
                    "Co-mention Network",
                    "Speaker Patterns",
                    "Alliance Networks"
                ],
                key="networks_analysis_type",
                help="Choose your network analysis: Country-Topic shows which countries focus on which issues, Co-mention shows diplomatic relationships, Speaker Patterns analyzes who speaks, Alliance Networks shows political groupings"
            )
            
            if network_type == "Country-Topic Network":
                year = st.slider("Year", 1946, 2025, 2025, key="country_topic_year")
                min_mentions = st.slider("Minimum Topic Mentions", 1, 50, 5, key="country_topic_min_mentions")
                
                if st.button("Create Network", key="country_topic_network"):
                    st.session_state.network_type = "country_topic"
                    st.session_state.network_year = year
                    st.session_state.network_min_mentions = min_mentions
                    st.rerun()
            
            elif network_type == "Co-mention Network":
                year = st.slider("Year", 1946, 2025, 2025, key="co_mention_year")
                min_co_mentions = st.slider("Minimum Co-mentions", 1, 20, 3, key="co_mention_min_mentions")
                
                if st.button("Create Co-mention Network", key="co_mention_network"):
                    st.session_state.network_type = "co_mention"
                    st.session_state.network_year = year
                    st.session_state.network_min_co_mentions = min_co_mentions
                    st.rerun()
            
            elif network_type == "Speaker Patterns":
                year_range = st.slider("Year Range", 1946, 2025, (2010, 2025), key="speaker_patterns_year_range")
                
                if st.button("Analyze Speaker Patterns", key="speaker_patterns"):
                    st.session_state.network_type = "speaker_patterns"
                    st.session_state.network_year_range = year_range
                    st.rerun()
            
            elif network_type == "Alliance Networks":
                year = st.slider("Year", 1946, 2025, 2025, key="alliance_network_year")
                
                if st.button("Create Alliance Network", key="alliance_network"):
                    st.session_state.network_type = "alliance"
                    st.session_state.network_year = year
                    st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            if hasattr(st.session_state, 'network_type'):
                if st.session_state.network_type == "country_topic":
                    self._create_country_topic_network(
                        st.session_state.network_year,
                        st.session_state.network_min_mentions
                    )
                elif st.session_state.network_type == "co_mention":
                    self._create_co_mention_network(
                        st.session_state.network_year,
                        st.session_state.network_min_co_mentions
                    )
                elif st.session_state.network_type == "speaker_patterns":
                    self._create_speaker_pattern_chart(
                        st.session_state.network_year_range
                    )
                elif st.session_state.network_type == "alliance":
                    self._create_alliance_network(
                        st.session_state.network_year
                    )
            else:
                st.info("👆 Select a network analysis type and configure parameters on the left, then click the generate button to see results here.")
    
    def _create_issue_salience_chart(self, topics: List[str], year_range: Tuple[int, int], 
                                   regions: List[str], viz_type: str):
        """Create issue salience visualization."""
        try:
            # Get data for the selected topics and years
            data = self._get_topic_salience_data(topics, year_range, regions)
            
            if data.empty:
                st.warning("No data found for the selected criteria.")
                return
            
            if viz_type == "Multi-line Trends":
                fig = px.line(
                    data, 
                    x='year', 
                    y='mentions_per_1000_words', 
                    color='topic',
                    title="Topic Salience Over Time",
                    labels={'mentions_per_1000_words': 'Mentions per 1,000 Words', 'year': 'Year'}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Stacked Area Chart":
                fig = px.area(
                    data, 
                    x='year', 
                    y='mentions_per_1000_words', 
                    color='topic',
                    title="Topic Salience - Stacked View"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Session Heatmap":
                # Create a pivot table for heatmap
                pivot_data = data.pivot_table(
                    index='topic', 
                    columns='year', 
                    values='mentions_per_1000_words', 
                    fill_value=0
                )
                
                fig = px.imshow(
                    pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    title="Topic Salience Heatmap",
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Regional Comparison":
                if regions:
                    fig = px.bar(
                        data, 
                        x='region', 
                        y='mentions_per_1000_words', 
                        color='topic',
                        title="Topic Salience by Region",
                        barmode='group'
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select regions to compare.")
            
            # Add summary statistics
            st.markdown("#### Summary Statistics")
            summary = data.groupby('topic')['mentions_per_1000_words'].agg(['mean', 'std', 'max']).round(2)
            st.dataframe(summary)
            
        except Exception as e:
            st.error(f"Error creating issue salience chart: {e}")
            logger.error(f"Error in _create_issue_salience_chart: {e}")
    
    def _create_country_position_map(self, year: int, highlight_countries: List[str]):
        """Create country position map using semantic embeddings."""
        try:
            # Get country embeddings for the specified year
            embeddings_data = self._get_country_embeddings(year)
            
            if embeddings_data.empty:
                # Show available years and suggest alternatives
                available_years = self.db_manager.conn.execute("SELECT DISTINCT year FROM speeches ORDER BY year").fetchall()
                available_years_list = [row[0] for row in available_years]
                
                st.warning(f"No data found for year {year}.")
                st.info(f"**Available years in database:** {min(available_years_list)} - {max(available_years_list)}")
                st.info(f"**Recent years with data:** {sorted(available_years_list)[-10:]}")
                st.info("💡 **Tip:** Try selecting a year from the available range above.")
                return
            
            # Create 2D scatter plot
            fig = px.scatter(
                embeddings_data,
                x='dimension_1',
                y='dimension_2',
                color='region',
                size='speech_count',
                hover_data=['country', 'region', 'speech_count'],
                title=f"Country Positions in Semantic Space ({year})"
            )
            
            # Highlight selected countries
            if highlight_countries:
                highlight_data = embeddings_data[embeddings_data['country'].isin(highlight_countries)]
                fig.add_trace(go.Scatter(
                    x=highlight_data['dimension_1'],
                    y=highlight_data['dimension_2'],
                    mode='markers+text',
                    text=highlight_data['country'],
                    textposition='top center',
                    marker=dict(size=15, color='red', symbol='star'),
                    name='Highlighted Countries',
                    showlegend=True
                ))
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add interpretation
            st.markdown("#### Interpretation")
            st.markdown("""
            - **X-axis**: First principal component (typically captures major ideological dimensions)
            - **Y-axis**: Second principal component (often captures secondary policy dimensions)
            - **Size**: Number of speeches by the country
            - **Color**: Geographic region
            - **Red stars**: Countries you selected to highlight
            """)
            
        except Exception as e:
            st.error(f"Error creating country position map: {e}")
            logger.error(f"Error in _create_country_position_map: {e}")
    
    def _create_similar_speech_finder(self, reference_country: str, reference_year: int, 
                                    similarity_threshold: float):
        """Create similar speech finder visualization."""
        try:
            # Get similar speeches
            similar_speeches = self._find_similar_speeches(reference_country, reference_year, similarity_threshold)
            
            if similar_speeches.empty:
                st.warning(f"No similar speeches found for {reference_country} in {reference_year}.")
                return
            
            # Create scatter plot
            fig = px.scatter(
                similar_speeches,
                x='year',
                y='similarity_score',
                color='region',
                size='speech_length',
                hover_data=['country', 'year', 'similarity_score', 'speech_length'],
                title=f"Speeches Similar to {reference_country} ({reference_year})"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top similar speeches in a table
            st.markdown("#### Top Similar Speeches")
            top_similar = similar_speeches.nlargest(10, 'similarity_score')
            st.dataframe(
                top_similar[['country', 'year', 'similarity_score', 'speech_length']],
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error creating similar speech finder: {e}")
            logger.error(f"Error in _create_similar_speech_finder: {e}")
    
    def _create_topic_composition_chart(self, country: str, year: int):
        """Create topic composition visualization for a specific country and year."""
        try:
            # Get topic composition data
            topic_data = self._get_topic_composition_data(country, year)
            
            if topic_data.empty:
                st.warning(f"No data found for {country} in {year}.")
                return
            
            # Create donut chart
            fig = px.pie(
                topic_data,
                values='percentage',
                names='topic',
                title=f"Topic Composition: {country} ({year})",
                hole=0.4
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add detailed breakdown
            st.markdown("#### Detailed Breakdown")
            st.dataframe(topic_data, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating topic composition chart: {e}")
            logger.error(f"Error in _create_topic_composition_chart: {e}")
    
    def _create_country_dossier(self, country: str):
        """Create comprehensive country dossier."""
        try:
            # Get comprehensive country data
            dossier_data = self._get_country_dossier_data(country)
            
            if not dossier_data:
                st.warning(f"No data found for {country}.")
                return
            
            # Create multiple visualizations in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Topic mix over time
                fig1 = px.line(
                    dossier_data['topic_trends'],
                    x='year',
                    y='percentage',
                    color='topic',
                    title=f"{country}: Topic Evolution"
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # Speech count over time
                fig2 = px.bar(
                    dossier_data['speech_counts'],
                    x='year',
                    y='count',
                    title=f"{country}: Speech Frequency"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Current topic composition
                fig3 = px.pie(
                    dossier_data['current_topics'],
                    values='percentage',
                    names='topic',
                    title=f"{country}: Current Topic Focus"
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Similar countries
                st.markdown("#### Most Similar Countries")
                st.dataframe(dossier_data['similar_countries'], use_container_width=True)
            
            # Key quotes
            st.markdown("#### Signature Quotes")
            for quote in dossier_data['key_quotes']:
                st.markdown(f"> {quote}")
            
        except Exception as e:
            st.error(f"Error creating country dossier: {e}")
            logger.error(f"Error in _create_country_dossier: {e}")
    
    def _create_keyword_trajectory_chart(self, keywords: List[str], year_range: Tuple[int, int]):
        """Create keyword trajectory visualization."""
        try:
            # Get keyword data
            keyword_data = self._get_keyword_trajectory_data(keywords, year_range)
            
            if keyword_data.empty:
                st.warning("No data found for the selected keywords.")
                return
            
            # Create line chart
            fig = px.line(
                keyword_data,
                x='year',
                y='mentions_per_1000_words',
                color='keyword',
                title="Keyword Trajectories Over Time"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add burst detection
            st.markdown("#### Keyword Burst Detection")
            bursts = self._detect_keyword_bursts(keyword_data)
            if not bursts.empty:
                st.dataframe(bursts, use_container_width=True)
            else:
                st.info("No significant keyword bursts detected.")
            
        except Exception as e:
            st.error(f"Error creating keyword trajectory chart: {e}")
            logger.error(f"Error in _create_keyword_trajectory_chart: {e}")
    
    def _create_sentiment_trend_chart(self, countries: List[str], year_range: Tuple[int, int]):
        """Create sentiment trend visualization."""
        try:
            # Get sentiment data
            sentiment_data = self._get_sentiment_data(countries, year_range)
            
            if sentiment_data.empty:
                st.warning("No sentiment data found.")
                return
            
            # Create line chart
            fig = px.line(
                sentiment_data,
                x='year',
                y='sentiment_score',
                color='country',
                title="Sentiment Trends by Country"
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add sentiment distribution
            st.markdown("#### Sentiment Distribution")
            fig2 = px.box(
                sentiment_data,
                x='country',
                y='sentiment_score',
                title="Sentiment Distribution by Country"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating sentiment trend chart: {e}")
            logger.error(f"Error in _create_sentiment_trend_chart: {e}")
    
    def _create_event_timeline_chart(self, events: List[str]):
        """Create event-aligned timeline visualization."""
        try:
            # Get timeline data
            timeline_data = self._get_event_timeline_data(events)
            
            if timeline_data.empty:
                st.warning("No timeline data found.")
                return
            
            # Create timeline chart with event markers
            fig = go.Figure()
            
            # Add event trend lines
            for event in timeline_data['event'].unique():
                event_data = timeline_data[timeline_data['event'] == event]
                fig.add_trace(go.Scatter(
                    x=event_data['year'],
                    y=event_data['mentions_per_1000_words'],
                    mode='lines',
                    name=event,
                    line=dict(width=2)
                ))
            
            # Add event markers
            event_years = {
                "Cold War End (1991)": 1991,
                "9/11 (2001)": 2001,
                "Financial Crisis (2008)": 2008,
                "Arab Spring (2011)": 2011,
                "Paris Agreement (2015)": 2015,
                "COVID-19 (2020)": 2020,
                "Ukraine War (2022)": 2022
            }
            
            for event in events:
                if event in event_years:
                    fig.add_vline(
                        x=event_years[event],
                        line_dash="dash",
                        line_color="red",
                        annotation_text=event
                    )
            
            fig.update_layout(
                title="Event-Aligned Timeline",
                height=500,
                xaxis_title="Year",
                yaxis_title="Mentions per 1,000 Words"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating event timeline chart: {e}")
            logger.error(f"Error in _create_event_timeline_chart: {e}")
    
    def _create_regional_comparison_chart(self, regions: List[str], metric: str):
        """Create regional comparison visualization."""
        try:
            # Get regional data
            regional_data = self._get_regional_comparison_data(regions, metric)
            
            if regional_data.empty:
                st.warning("No regional data found.")
                return
            
            # Create comparison chart
            fig = px.bar(
                regional_data,
                x='region',
                y='value',
                color='metric',
                title=f"Regional Comparison: {metric}",
                barmode='group'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating regional comparison chart: {e}")
            logger.error(f"Error in _create_regional_comparison_chart: {e}")
    
    def _create_country_topic_network(self, year: int, min_mentions: int):
        """Create country-topic bipartite network."""
        try:
            # Get network data
            network_data = self._get_country_topic_network_data(year, min_mentions)
            
            if not network_data:
                st.warning("No network data found.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add edges
            for edge in network_data['edges']:
                fig.add_trace(go.Scatter(
                    x=[edge['source_x'], edge['target_x']],
                    y=[edge['source_y'], edge['target_y']],
                    mode='lines',
                    line=dict(width=edge['weight'], color='gray'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Add nodes
            for node in network_data['nodes']:
                fig.add_trace(go.Scatter(
                    x=[node['x']],
                    y=[node['y']],
                    mode='markers+text',
                    text=[node['label']],
                    textposition='middle center',
                    marker=dict(size=node['size'], color=node['color']),
                    name=node['type'],
                    showlegend=True
                ))
            
            fig.update_layout(
                title=f"Country-Topic Network ({year})",
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating country-topic network: {e}")
            logger.error(f"Error in _create_country_topic_network: {e}")
    
    def _create_co_mention_network(self, year: int, min_co_mentions: int):
        """Create co-mention network visualization."""
        try:
            # Get co-mention data
            co_mention_data = self._get_co_mention_data(year, min_co_mentions)
            
            if co_mention_data.empty:
                st.warning("No co-mention data found.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add edges
            for _, row in co_mention_data.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['country1_x'], row['country2_x']],
                    y=[row['country1_y'], row['country2_y']],
                    mode='lines',
                    line=dict(width=row['co_mentions'], color='blue'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            fig.update_layout(
                title=f"Country Co-mention Network ({year})",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating co-mention network: {e}")
            logger.error(f"Error in _create_co_mention_network: {e}")
    
    def _create_speaker_pattern_chart(self, year_range: Tuple[int, int]):
        """Create speaker pattern visualization."""
        try:
            # Get speaker data
            speaker_data = self._get_speaker_pattern_data(year_range)
            
            if speaker_data.empty:
                st.warning("No speaker data found.")
                return
            
            # Create multiple charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Speaker type distribution
                fig1 = px.pie(
                    speaker_data['speaker_types'],
                    values='count',
                    names='speaker_type',
                    title="Speaker Type Distribution"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Gender distribution
                fig2 = px.bar(
                    speaker_data['gender_distribution'],
                    x='year',
                    y='percentage',
                    color='gender',
                    title="Gender Distribution Over Time"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating speaker pattern chart: {e}")
            logger.error(f"Error in _create_speaker_pattern_chart: {e}")
    
    def _create_alliance_network(self, year: int):
        """Create alliance network visualization."""
        try:
            # Get alliance data
            alliance_data = self._get_alliance_data(year)
            
            if alliance_data.empty:
                st.warning("No alliance data found.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add alliance connections
            for _, row in alliance_data.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['country1_x'], row['country2_x']],
                    y=[row['country1_y'], row['country2_y']],
                    mode='lines',
                    line=dict(width=row['alliance_strength'], color='green'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            fig.update_layout(
                title=f"Alliance Network ({year})",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating alliance network: {e}")
            logger.error(f"Error in _create_alliance_network: {e}")
    
    # Data retrieval methods (to be implemented based on your database structure)
    
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
    
    def _get_common_countries_for_defaults(self) -> List[str]:
        """Get a list of common countries that are likely to be in the database for use as defaults."""
        try:
            # Get all available countries
            all_countries = self._get_available_countries()
            
            # Common countries that are likely to be in UNGA speeches
            common_countries = [
                "United States", "China", "Russia", "India", "Brazil", "Germany", "France", 
                "United Kingdom", "Japan", "Canada", "Australia", "South Africa", "Nigeria",
                "Egypt", "Mexico", "Argentina", "Turkey", "Iran", "Saudi Arabia", "Indonesia"
            ]
            
            # Return only the common countries that are actually in the database
            return [country for country in common_countries if country in all_countries]
        except Exception as e:
            logger.error(f"Error getting common countries: {e}")
            return []
    
    def _get_topic_salience_data(self, topics: List[str], year_range: Tuple[int, int], 
                                regions: List[str]) -> pd.DataFrame:
        """Get topic salience data for visualization."""
        try:
            # Build SQL query to get topic mentions
            topic_conditions = []
            for topic in topics:
                # Create keyword patterns for each topic
                if topic.lower() == "climate change":
                    keywords = ["climate", "global warming", "greenhouse", "carbon", "emissions", "environment"]
                elif topic.lower() == "peace & security":
                    keywords = ["peace", "security", "conflict", "war", "terrorism", "military"]
                elif topic.lower() == "development":
                    keywords = ["development", "poverty", "economic", "growth", "sustainable development"]
                elif topic.lower() == "human rights":
                    keywords = ["human rights", "rights", "freedom", "democracy", "justice"]
                elif topic.lower() == "gender equality":
                    keywords = ["gender", "women", "girls", "equality", "empowerment", "feminist"]
                elif topic.lower() == "trade":
                    keywords = ["trade", "commerce", "economic", "market", "business"]
                elif topic.lower() == "health":
                    keywords = ["health", "medical", "disease", "pandemic", "healthcare"]
                elif topic.lower() == "education":
                    keywords = ["education", "school", "learning", "knowledge", "training"]
                elif topic.lower() == "migration":
                    keywords = ["migration", "refugee", "immigration", "displacement"]
                elif topic.lower() == "technology":
                    keywords = ["technology", "digital", "innovation", "tech"]
                elif topic.lower() == "ai":
                    keywords = ["artificial intelligence", "ai", "machine learning", "automation"]
                elif topic.lower() == "palestine":
                    keywords = ["palestine", "palestinian", "israel", "gaza", "west bank"]
                elif topic.lower() == "ukraine":
                    keywords = ["ukraine", "ukrainian", "russia", "russian"]
                elif topic.lower() == "debt":
                    keywords = ["debt", "debt relief", "financial", "borrowing"]
                elif topic.lower() == "multilateralism":
                    keywords = ["multilateral", "cooperation", "international", "united nations"]
                else:
                    keywords = [topic.lower()]
                
                # Create SQL condition for topic
                topic_condition = " OR ".join([f"LOWER(speech_text) LIKE '%{kw}%'" for kw in keywords])
                topic_conditions.append(f"({topic_condition})")
            
            # Build the main query
            where_conditions = [
                f"year BETWEEN {year_range[0]} AND {year_range[1]}",
                f"({' OR '.join(topic_conditions)})"
            ]
            
            if regions:
                region_conditions = " OR ".join([f"region = '{region}'" for region in regions])
                where_conditions.append(f"({region_conditions})")
            
            query = f"""
                SELECT 
                    year,
                    country_name,
                    region,
                    speech_text,
                    word_count,
                    CASE 
                        {' '.join([f"WHEN ({topic_conditions[i]}) THEN '{topics[i]}'" for i in range(len(topics))])}
                        ELSE 'Other'
                    END as topic
                FROM speeches 
                WHERE {' AND '.join(where_conditions)}
                AND speech_text IS NOT NULL
                AND word_count > 0
            """
            
            result = self.db_manager.conn.execute(query).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=['year', 'country_name', 'region', 'speech_text', 'word_count', 'topic'])
            
            # Calculate mentions per 1000 words for each topic
            topic_data = []
            for topic in topics:
                topic_df = df[df['topic'] == topic]
                if not topic_df.empty:
                    # Group by year and region to preserve region information
                    yearly_stats = topic_df.groupby(['year', 'region']).agg({
                        'word_count': 'sum',
                        'country_name': 'count'
                    }).reset_index()
                    yearly_stats.columns = ['year', 'region', 'total_words', 'speech_count']
                    
                    # Calculate mentions per 1000 words (simplified - using speech count as proxy)
                    yearly_stats['mentions_per_1000_words'] = (yearly_stats['speech_count'] / yearly_stats['total_words']) * 1000
                    yearly_stats['topic'] = topic
                    topic_data.append(yearly_stats)
            
            if topic_data:
                return pd.concat(topic_data, ignore_index=True)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting topic salience data: {e}")
            return pd.DataFrame()
    
    def _get_country_embeddings(self, year: int) -> pd.DataFrame:
        """Get country embeddings for position mapping."""
        try:
            # First, check what years are available
            available_years = self.db_manager.conn.execute("SELECT DISTINCT year FROM speeches ORDER BY year").fetchall()
            available_years_list = [row[0] for row in available_years]
            
            if year not in available_years_list:
                st.warning(f"Year {year} not found in database. Available years: {min(available_years_list)}-{max(available_years_list)}")
                return pd.DataFrame()
            
            # Get speeches for the specified year
            query = """
                SELECT 
                    country_name,
                    region,
                    speech_text,
                    word_count,
                    COUNT(*) as speech_count
                FROM speeches 
                WHERE year = ? 
                AND speech_text IS NOT NULL 
                AND word_count > 100
                GROUP BY country_name, region
                HAVING COUNT(*) >= 1
                ORDER BY speech_count DESC
                LIMIT 50
            """
            
            result = self.db_manager.conn.execute(query, (year,)).fetchall()
            
            if not result:
                st.warning(f"No speeches found for year {year} with sufficient word count (>100 words).")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=['country', 'region', 'speech_text', 'word_count', 'speech_count'])
            
            # Create mock 2D coordinates based on speech characteristics
            # In a real implementation, you would use actual embeddings
            np.random.seed(42)  # For reproducible results
            
            # Create mock dimensions based on speech content
            df['dimension_1'] = np.random.normal(0, 1, len(df))  # Mock first dimension
            df['dimension_2'] = np.random.normal(0, 1, len(df))  # Mock second dimension
            
            # Add some structure based on region
            region_offsets = {
                'Africa': (0.5, 0.3),
                'Asia': (-0.3, 0.8),
                'Europe': (-0.8, -0.2),
                'Americas': (0.2, -0.6),
                'Oceania': (0.1, 0.1)
            }
            
            for region, (offset_x, offset_y) in region_offsets.items():
                mask = df['region'] == region
                df.loc[mask, 'dimension_1'] += offset_x
                df.loc[mask, 'dimension_2'] += offset_y
            
            return df[['country', 'region', 'speech_count', 'dimension_1', 'dimension_2']]
            
        except Exception as e:
            logger.error(f"Error getting country embeddings: {e}")
            return pd.DataFrame()
    
    def _find_similar_speeches(self, reference_country: str, reference_year: int, 
                             similarity_threshold: float) -> pd.DataFrame:
        """Find speeches similar to a reference speech."""
        try:
            # Get reference speech
            ref_query = """
                SELECT speech_text, word_count
                FROM speeches 
                WHERE country_name = ? AND year = ?
                AND speech_text IS NOT NULL
                LIMIT 1
            """
            
            ref_result = self.db_manager.conn.execute(ref_query, (reference_country, reference_year)).fetchone()
            
            if not ref_result:
                return pd.DataFrame()
            
            ref_text = ref_result[0]
            ref_word_count = ref_result[1]
            
            # Get other speeches for comparison
            comp_query = """
                SELECT 
                    country_name,
                    year,
                    region,
                    speech_text,
                    word_count
                FROM speeches 
                WHERE country_name != ? 
                AND year BETWEEN ? AND ?
                AND speech_text IS NOT NULL
                AND word_count > 100
                ORDER BY year DESC
                LIMIT 100
            """
            
            comp_result = self.db_manager.conn.execute(
                comp_query, 
                (reference_country, reference_year - 2, reference_year + 2)
            ).fetchall()
            
            if not comp_result:
                return pd.DataFrame()
            
            # Calculate similarity scores (simplified - using word overlap)
            similar_speeches = []
            ref_words = set(ref_text.lower().split())
            
            for row in comp_result:
                country, year, region, speech_text, word_count = row
                comp_words = set(speech_text.lower().split())
                
                # Calculate Jaccard similarity
                intersection = len(ref_words.intersection(comp_words))
                union = len(ref_words.union(comp_words))
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= similarity_threshold:
                    similar_speeches.append({
                        'country': country,
                        'year': year,
                'region': region,
                        'similarity_score': similarity,
                        'speech_length': word_count
                    })
            
            if similar_speeches:
                df = pd.DataFrame(similar_speeches)
                return df.sort_values('similarity_score', ascending=False)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error finding similar speeches: {e}")
            return pd.DataFrame()
    
    def _get_topic_composition_data(self, country: str, year: int) -> pd.DataFrame:
        """Get topic composition data for a country and year."""
        try:
            # Get speeches for the country and year
            query = """
                SELECT speech_text, word_count
                FROM speeches 
                WHERE country_name = ? AND year = ?
                AND speech_text IS NOT NULL
                AND word_count > 100
            """
            
            result = self.db_manager.conn.execute(query, (country, year)).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Combine all speeches for the country/year
            combined_text = " ".join([row[0] for row in result])
            total_words = sum([row[1] for row in result])
            
            # Define topic keywords and calculate percentages
            topics = {
                'Peace & Security': ['peace', 'security', 'conflict', 'war', 'terrorism', 'military', 'defense'],
                'Development': ['development', 'poverty', 'economic', 'growth', 'sustainable development', 'aid'],
                'Climate Change': ['climate', 'environment', 'global warming', 'carbon', 'emissions', 'green'],
                'Human Rights': ['human rights', 'rights', 'freedom', 'democracy', 'justice', 'equality'],
                'Gender Equality': ['gender', 'women', 'girls', 'empowerment', 'feminist', 'equality'],
                'Health': ['health', 'medical', 'disease', 'pandemic', 'healthcare', 'medicine'],
                'Education': ['education', 'school', 'learning', 'knowledge', 'training', 'university'],
                'Trade': ['trade', 'commerce', 'economic', 'market', 'business', 'investment'],
                'Technology': ['technology', 'digital', 'innovation', 'tech', 'artificial intelligence', 'ai'],
                'Migration': ['migration', 'refugee', 'immigration', 'displacement', 'asylum']
            }
            
            topic_data = []
            text_lower = combined_text.lower()
            
            for topic, keywords in topics.items():
                # Count keyword mentions
                mentions = sum([text_lower.count(keyword) for keyword in keywords])
                percentage = (mentions / total_words) * 100 if total_words > 0 else 0
                
                if percentage > 0.1:  # Only include topics with meaningful presence
                    topic_data.append({
                        'topic': topic,
                        'percentage': round(percentage, 2),
                        'mentions': mentions
                    })
            
            if topic_data:
                df = pd.DataFrame(topic_data)
                # Sort by percentage descending
                df = df.sort_values('percentage', ascending=False)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting topic composition data: {e}")
            return pd.DataFrame()
    
    def _get_country_dossier_data(self, country: str) -> Dict[str, Any]:
        """Get comprehensive country dossier data."""
        # This is a placeholder - implement comprehensive country analysis
        return {}
    
    def _get_keyword_trajectory_data(self, keywords: List[str], year_range: Tuple[int, int]) -> pd.DataFrame:
        """Get keyword trajectory data."""
        try:
            keyword_data = []
            
            for keyword in keywords:
                if not keyword.strip():
                    continue
                    
                # Search for keyword mentions in speeches
                query = """
                    SELECT 
                        year,
                        COUNT(*) as speech_count,
                        SUM(word_count) as total_words
                    FROM speeches 
                    WHERE year BETWEEN ? AND ?
                    AND LOWER(speech_text) LIKE ?
                    AND speech_text IS NOT NULL
                    AND word_count > 0
                    GROUP BY year
                    ORDER BY year
                """
                
                keyword_pattern = f"%{keyword.lower()}%"
                result = self.db_manager.conn.execute(query, (year_range[0], year_range[1], keyword_pattern)).fetchall()
                
                for row in result:
                    year, speech_count, total_words = row
                    mentions_per_1000 = (speech_count / total_words) * 1000 if total_words > 0 else 0
                    
                    keyword_data.append({
                        'year': year,
                        'keyword': keyword,
                        'mentions_per_1000_words': mentions_per_1000,
                        'speech_count': speech_count,
                        'total_words': total_words
                    })
            
            if keyword_data:
                return pd.DataFrame(keyword_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting keyword trajectory data: {e}")
            return pd.DataFrame()
    
    def _detect_keyword_bursts(self, keyword_data: pd.DataFrame) -> pd.DataFrame:
        """Detect keyword bursts in the data."""
        # This is a placeholder - implement burst detection algorithm
        return pd.DataFrame()
    
    def _get_sentiment_data(self, countries: List[str], year_range: Tuple[int, int]) -> pd.DataFrame:
        """Get sentiment data for countries and years."""
        try:
            sentiment_data = []
            
            for country in countries:
                # Get speeches for the country in the year range
                query = """
                    SELECT 
                        year,
                        speech_text,
                        word_count
                    FROM speeches 
                    WHERE country_name = ?
                    AND year BETWEEN ? AND ?
                    AND speech_text IS NOT NULL
                    AND word_count > 100
                    ORDER BY year
                """
                
                result = self.db_manager.conn.execute(query, (country, year_range[0], year_range[1])).fetchall()
                
                # Simple sentiment analysis based on positive/negative word counts
                positive_words = ['peace', 'hope', 'progress', 'development', 'cooperation', 'unity', 'freedom', 'justice', 'prosperity', 'success']
                negative_words = ['war', 'conflict', 'crisis', 'poverty', 'violence', 'threat', 'danger', 'failure', 'destruction', 'suffering']
                
                yearly_sentiment = {}
                
                for row in result:
                    year, speech_text, word_count = row
                    text_lower = speech_text.lower()
                    
                    positive_count = sum(1 for word in positive_words if word in text_lower)
                    negative_count = sum(1 for word in negative_words if word in text_lower)
                    
                    # Calculate sentiment score (-1 to 1)
                    total_sentiment_words = positive_count + negative_count
                    if total_sentiment_words > 0:
                        sentiment_score = (positive_count - negative_count) / total_sentiment_words
                    else:
                        sentiment_score = 0
                    
                    if year not in yearly_sentiment:
                        yearly_sentiment[year] = {'scores': [], 'word_counts': []}
                    
                    yearly_sentiment[year]['scores'].append(sentiment_score)
                    yearly_sentiment[year]['word_counts'].append(word_count)
                
                # Calculate weighted average sentiment by year
                for year, data in yearly_sentiment.items():
                    if data['scores']:
                        # Weight by word count
                        total_words = sum(data['word_counts'])
                        weighted_sentiment = sum(score * word_count for score, word_count in zip(data['scores'], data['word_counts'])) / total_words
                        
                        sentiment_data.append({
                            'year': year,
                            'country': country,
                            'sentiment_score': weighted_sentiment,
                            'speech_count': len(data['scores'])
                        })
            
            if sentiment_data:
                return pd.DataFrame(sentiment_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting sentiment data: {e}")
            return pd.DataFrame()
    
    def _get_event_timeline_data(self, events: List[str]) -> pd.DataFrame:
        """Get event timeline data."""
        try:
            event_data = []
            
            # Define event years and keywords
            event_info = {
                "Cold War End (1991)": {"year": 1991, "keywords": ["cold war", "berlin wall", "soviet union", "glasnost", "perestroika"]},
                "9/11 (2001)": {"year": 2001, "keywords": ["terrorism", "9/11", "september 11", "terrorist", "security"]},
                "Financial Crisis (2008)": {"year": 2008, "keywords": ["financial crisis", "economic crisis", "recession", "banking", "economy"]},
                "Arab Spring (2011)": {"year": 2011, "keywords": ["arab spring", "democracy", "revolution", "protest", "uprising"]},
                "Paris Agreement (2015)": {"year": 2015, "keywords": ["paris agreement", "climate change", "emissions", "carbon", "global warming"]},
                "COVID-19 (2020)": {"year": 2020, "keywords": ["covid", "pandemic", "coronavirus", "health", "crisis"]},
                "Ukraine War (2022)": {"year": 2022, "keywords": ["ukraine", "russia", "war", "conflict", "invasion"]}
            }
            
            for event in events:
                if event not in event_info:
                    continue
                    
                event_year = event_info[event]["year"]
                keywords = event_info[event]["keywords"]
                
                # Get data for 3 years before and after the event
                start_year = event_year - 3
                end_year = event_year + 3
                
                # Search for event-related keywords in speeches
                keyword_conditions = " OR ".join([f"LOWER(speech_text) LIKE '%{kw}%'" for kw in keywords])
                
                query = f"""
                    SELECT 
                        year,
                        COUNT(*) as speech_count,
                        SUM(word_count) as total_words
                    FROM speeches 
                    WHERE year BETWEEN ? AND ?
                    AND ({keyword_conditions})
                    AND speech_text IS NOT NULL
                    AND word_count > 0
                    GROUP BY year
                    ORDER BY year
                """
                
                result = self.db_manager.conn.execute(query, (start_year, end_year)).fetchall()
                
                for row in result:
                    year, speech_count, total_words = row
                    mentions_per_1000 = (speech_count / total_words) * 1000 if total_words > 0 else 0
                    
                    event_data.append({
                        'year': year,
                        'event': event,
                        'event_year': event_year,
                        'mentions_per_1000_words': mentions_per_1000,
                        'speech_count': speech_count,
                        'years_from_event': year - event_year
                    })
            
            if event_data:
                return pd.DataFrame(event_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting event timeline data: {e}")
            return pd.DataFrame()
    
    def _get_regional_comparison_data(self, regions: List[str], metric: str) -> pd.DataFrame:
        """Get regional comparison data."""
        try:
            if not regions:
                return pd.DataFrame()
            
            # Build region filter
            region_conditions = " OR ".join([f"region = '{region}'" for region in regions])
            
            if metric == "Topic Focus":
                # Compare topic focus across regions
                query = f"""
                    SELECT 
                        region,
                        year,
                        COUNT(*) as speech_count,
                        AVG(word_count) as avg_word_count
                    FROM speeches 
                    WHERE ({region_conditions})
                    AND speech_text IS NOT NULL
                    AND word_count > 100
                    GROUP BY region, year
                    ORDER BY region, year
                """
                
                result = self.db_manager.conn.execute(query).fetchall()
                
                data = []
                for row in result:
                    region, year, speech_count, avg_word_count = row
                    data.append({
                        'region': region,
                        'year': year,
                        'value': speech_count,
                        'metric': 'Speech Count',
                        'avg_word_count': avg_word_count
                    })
                
                return pd.DataFrame(data)
                
            elif metric == "Speech Length":
                # Compare average speech length
                query = f"""
                    SELECT 
                        region,
                        year,
                        AVG(word_count) as avg_word_count,
                        COUNT(*) as speech_count
                    FROM speeches 
                    WHERE ({region_conditions})
                    AND speech_text IS NOT NULL
                    AND word_count > 0
                    GROUP BY region, year
                    ORDER BY region, year
                """
                
                result = self.db_manager.conn.execute(query).fetchall()
                
                data = []
                for row in result:
                    region, year, avg_word_count, speech_count = row
                    data.append({
                        'region': region,
                        'year': year,
                        'value': avg_word_count,
                        'metric': 'Average Word Count',
                        'speech_count': speech_count
                    })
                
                return pd.DataFrame(data)
                
            elif metric == "Sentiment":
                # Compare sentiment across regions
                positive_words = ['peace', 'hope', 'progress', 'development', 'cooperation', 'unity']
                negative_words = ['war', 'conflict', 'crisis', 'poverty', 'violence', 'threat']
                
                query = f"""
                    SELECT 
                        region,
                        year,
                        speech_text,
                        word_count
                    FROM speeches 
                    WHERE ({region_conditions})
                    AND speech_text IS NOT NULL
                    AND word_count > 100
                    ORDER BY region, year
                """
                
                result = self.db_manager.conn.execute(query).fetchall()
                
                # Calculate sentiment by region and year
                regional_sentiment = {}
                
                for row in result:
                    region, year, speech_text, word_count = row
                    text_lower = speech_text.lower()
                    
                    positive_count = sum(1 for word in positive_words if word in text_lower)
                    negative_count = sum(1 for word in negative_words if word in text_lower)
                    
                    total_sentiment_words = positive_count + negative_count
                    if total_sentiment_words > 0:
                        sentiment_score = (positive_count - negative_count) / total_sentiment_words
                    else:
                        sentiment_score = 0
                    
                    key = (region, year)
                    if key not in regional_sentiment:
                        regional_sentiment[key] = {'scores': [], 'word_counts': []}
                    
                    regional_sentiment[key]['scores'].append(sentiment_score)
                    regional_sentiment[key]['word_counts'].append(word_count)
                
                data = []
                for (region, year), data_dict in regional_sentiment.items():
                    if data_dict['scores']:
                        total_words = sum(data_dict['word_counts'])
                        weighted_sentiment = sum(score * word_count for score, word_count in zip(data_dict['scores'], data_dict['word_counts'])) / total_words
                        
                        data.append({
                            'region': region,
                            'year': year,
                            'value': weighted_sentiment,
                            'metric': 'Sentiment Score',
                            'speech_count': len(data_dict['scores'])
                        })
                
                return pd.DataFrame(data)
                
            else:  # Keyword Usage
                # Compare keyword usage across regions
                common_keywords = ['development', 'peace', 'security', 'climate', 'human rights', 'cooperation']
                
                data = []
                for keyword in common_keywords:
                    query = f"""
                        SELECT 
                            region,
                            year,
                            COUNT(*) as speech_count,
                            SUM(word_count) as total_words
                        FROM speeches 
                        WHERE ({region_conditions})
                        AND LOWER(speech_text) LIKE ?
                        AND speech_text IS NOT NULL
                        AND word_count > 0
                        GROUP BY region, year
                        ORDER BY region, year
                    """
                    
                    result = self.db_manager.conn.execute(query, (f"%{keyword}%",)).fetchall()
                    
                    for row in result:
                        region, year, speech_count, total_words = row
                        mentions_per_1000 = (speech_count / total_words) * 1000 if total_words > 0 else 0
                        
                        data.append({
                            'region': region,
                            'year': year,
                            'value': mentions_per_1000,
                            'metric': f'"{keyword}" Mentions',
                            'keyword': keyword,
                            'speech_count': speech_count
                        })
                
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting regional comparison data: {e}")
            return pd.DataFrame()
    
    def _get_country_topic_network_data(self, year: int, min_mentions: int) -> Dict[str, Any]:
        """Get country-topic network data."""
        # This is a placeholder - implement network analysis
        return {}
    
    def _get_co_mention_data(self, year: int, min_co_mentions: int) -> pd.DataFrame:
        """Get co-mention data for network visualization."""
        # This is a placeholder - implement co-mention analysis
        return pd.DataFrame()
    
    def _get_speaker_pattern_data(self, year_range: Tuple[int, int]) -> Dict[str, pd.DataFrame]:
        """Get speaker pattern data."""
        # This is a placeholder - implement speaker analysis
        return {}
    
    def _get_alliance_data(self, year: int) -> pd.DataFrame:
        """Get alliance data for network visualization."""
        # This is a placeholder - implement alliance analysis
        return pd.DataFrame()


# Standalone functions for app.py compatibility
def create_region_distribution_chart(db_manager):
    """Create region distribution chart for the data explorer."""
    try:
        query = """
            SELECT region, COUNT(*) as count
            FROM speeches 
            WHERE region IS NOT NULL
            GROUP BY region
            ORDER BY count DESC
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['region', 'count'])
        
        fig = px.pie(
            df, 
            values='count', 
            names='region',
            title="Speech Distribution by Region"
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating region distribution chart: {e}")
        return None

def create_word_count_heatmap(db_manager):
    """Create word count heatmap for data explorer."""
    try:
        query = """
            SELECT 
                country_name,
                year,
                AVG(word_count) as avg_word_count
            FROM speeches 
            WHERE country_name IS NOT NULL 
            AND year IS NOT NULL
            AND word_count > 0
            GROUP BY country_name, year
            HAVING COUNT(*) > 0
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['country', 'year', 'avg_word_count'])
        
        # Create pivot table for heatmap
        pivot_df = df.pivot_table(
            index='country', 
            columns='year', 
            values='avg_word_count', 
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            title="Average Word Count by Country and Year",
            color_continuous_scale='Blues'
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating word count heatmap: {e}")
        return None

def create_au_members_chart(db_manager):
    """Create AU members chart for data explorer."""
    try:
        query = """
            SELECT 
                year,
                COUNT(DISTINCT country_name) as au_members
            FROM speeches 
            WHERE country_name IN (
                'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
                'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad',
                'Comoros', 'Congo', 'Democratic Republic of the Congo', 'Djibouti',
                'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia',
                'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast',
                'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
                'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique',
                'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe',
                'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa',
                'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda',
                'Zambia', 'Zimbabwe'
            )
            AND year IS NOT NULL
            GROUP BY year
            ORDER BY year
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['year', 'au_members'])
        
        fig = px.line(
            df, 
            x='year', 
            y='au_members',
            title="AU Members Speaking at UNGA Over Time"
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating AU members chart: {e}")
        return None

def create_word_count_distribution(db_manager):
    """Create word count distribution chart."""
    try:
        query = """
            SELECT word_count
            FROM speeches 
            WHERE word_count > 0
            AND word_count < 10000
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['word_count'])
        
        fig = px.histogram(
            df, 
            x='word_count',
            title="Distribution of Speech Word Counts",
            nbins=50
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating word count distribution: {e}")
        return None

def create_region_comparison_table(db_manager):
    """Create region comparison table."""
    try:
        query = """
            SELECT 
                region,
                COUNT(*) as total_speeches,
                COUNT(DISTINCT country_name) as unique_countries,
                AVG(word_count) as avg_word_count,
                MIN(year) as first_year,
                MAX(year) as last_year
            FROM speeches 
            WHERE region IS NOT NULL
            GROUP BY region
            ORDER BY total_speeches DESC
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=[
            'region', 'total_speeches', 'unique_countries', 
            'avg_word_count', 'first_year', 'last_year'
        ])
        
        # Round numeric columns
        df['avg_word_count'] = df['avg_word_count'].round(0)
        
        return df
    except Exception as e:
        logger.error(f"Error creating region comparison table: {e}")
        return None

def create_top_countries_chart(db_manager):
    """Create top countries chart."""
    try:
        query = """
            SELECT 
                country_name,
                COUNT(*) as speech_count,
                AVG(word_count) as avg_word_count
            FROM speeches 
            WHERE country_name IS NOT NULL
            GROUP BY country_name
            ORDER BY speech_count DESC
            LIMIT 20
        """
        result = db_manager.conn.execute(query).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['country', 'speech_count', 'avg_word_count'])
        
        fig = px.bar(
            df, 
            x='speech_count', 
            y='country',
            title="Top 20 Countries by Speech Count",
            orientation='h'
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating top countries chart: {e}")
        return None

def create_country_year_heatmap(db_manager, selected_countries=None, year_range=None):
    """Create country-year heatmap for data availability."""
    try:
        where_conditions = ["country_name IS NOT NULL", "year IS NOT NULL"]
        params = []
        
        if selected_countries:
            placeholders = ','.join(['?' for _ in selected_countries])
            where_conditions.append(f"country_name IN ({placeholders})")
            params.extend(selected_countries)
        
        if year_range:
            where_conditions.append("year BETWEEN ? AND ?")
            params.extend([year_range[0], year_range[1]])
        
        query = f"""
            SELECT 
                country_name,
                year,
                COUNT(*) as speech_count
            FROM speeches 
            WHERE {' AND '.join(where_conditions)}
            GROUP BY country_name, year
            ORDER BY country_name, year
        """
        
        result = db_manager.conn.execute(query, params).fetchall()
        
        if not result:
            return None
            
        df = pd.DataFrame(result, columns=['country', 'year', 'speech_count'])
        
        # Create pivot table
        pivot_df = df.pivot_table(
            index='country', 
            columns='year', 
            values='speech_count', 
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            title="Speech Availability by Country and Year",
            color_continuous_scale='RdYlGn',
            labels=dict(x="Year", y="Country", color="Speech Count")
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating country year heatmap: {e}")
        return None

def get_available_countries_for_filter(db_manager):
    """Get available countries for filter dropdown."""
    try:
        query = """
            SELECT DISTINCT country_name 
            FROM speeches 
            WHERE country_name IS NOT NULL 
            ORDER BY country_name
        """
        result = db_manager.conn.execute(query).fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f"Error getting available countries: {e}")
        return []

def get_available_years_for_filter(db_manager):
    """Get available years for filter dropdown."""
    try:
        query = """
            SELECT DISTINCT year 
            FROM speeches 
            WHERE year IS NOT NULL 
            ORDER BY year
        """
        result = db_manager.conn.execute(query).fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f"Error getting available years: {e}")
        return []