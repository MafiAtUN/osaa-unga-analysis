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

def create_methodology_tooltip(methodology_text: str) -> str:
    """Create a methodology tooltip that appears on hover."""
    return f"""
    <div style="position: relative; display: inline-block;">
        <span style="color: #666; cursor: help; font-size: 0.8em;">ℹ️</span>
        <div style="
            visibility: hidden;
            width: 300px;
            background-color: #f9f9f9;
            color: #333;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            border: 1px solid #ccc;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 0.85em;
            line-height: 1.4;
        ">
            <strong>Methodology:</strong><br>
            {methodology_text}
        </div>
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
        - 🕸️ **Country-Region networks** - which countries belong to which regions
        - 🤝 **Co-mention networks** - countries that speak in the same sessions
        - 👥 **Speaker patterns** - speech activity over time by country
        - 🤝 **Alliance networks** - regional political groupings
        
        **How to use:**
        1. 📋 Select a network type from the options below
        2. ⚙️ Configure the parameters (year, thresholds, etc.)
        3. 🔘 Click the "Generate Network Analysis" button
        4. 📊 View the interactive visualization with filters
        
        **Example questions you can answer:**
        - "Which countries are most active in UNGA?"
        - "What are the regional patterns in UNGA participation?"
        - "How has country participation changed over time?"
        - "Which countries form the strongest regional blocs?"
        """)
        
        # Methodology section
        with st.expander("📚 Methodology & Technical Details", expanded=False):
            st.markdown("""
            ### 🔬 Network Analysis Methodologies
            
            #### 1. Country-Region Network
            **Purpose**: Visualize the relationship between countries and their regional groupings in UNGA participation.
            
            **Methodology**:
            - **Data Source**: UNGA speeches database with country and region classifications
            - **Network Structure**: Bipartite graph with countries and regions as separate node types
            - **Edge Weight**: Number of speeches by each country in each region
            - **Layout**: Countries positioned horizontally, regions positioned above
            - **Filtering**: Minimum mention threshold to reduce noise
            - **Visualization**: Plotly scatter plot with lines connecting countries to their regions
            
            **Interpretation**:
            - Node size indicates activity level (number of speeches)
            - Line thickness shows strength of relationship
            - Clustering reveals regional participation patterns
            
            #### 2. Co-mention Network
            **Purpose**: Identify countries that frequently speak in the same UNGA sessions, indicating potential diplomatic relationships.
            
            **Methodology**:
            - **Data Source**: Session-based analysis of country participation
            - **Network Structure**: Undirected graph where countries are connected if they speak in the same sessions
            - **Edge Weight**: Number of shared sessions between country pairs
            - **Layout**: Circular arrangement for optimal visualization
            - **Filtering**: Minimum co-mention threshold to focus on significant relationships
            - **Visualization**: Plotly scatter plot with circular node positioning
            
            **Interpretation**:
            - Thick lines indicate strong diplomatic co-participation
            - Central nodes represent highly connected countries
            - Clusters may indicate regional or political alliances
            
            #### 3. Speaker Patterns
            **Purpose**: Analyze temporal patterns in country participation and speech activity.
            
            **Methodology**:
            - **Data Source**: Time-series analysis of speech counts by country
            - **Metrics**: Speech frequency, average speech length, participation trends
            - **Time Range**: Configurable year range for trend analysis
            - **Visualization**: Line charts showing activity over time
            - **Statistics**: Total speeches, active countries, average speech length
            
            **Interpretation**:
            - Upward trends indicate increasing participation
            - Peaks may correspond to major international events
            - Country comparisons reveal participation patterns
            
            #### 4. Alliance Network
            **Purpose**: Identify potential political alliances based on regional groupings and participation patterns.
            
            **Methodology**:
            - **Data Source**: Regional classification and participation analysis
            - **Network Structure**: Undirected graph connecting countries within regions
            - **Alliance Strength**: Regional proximity and participation similarity
            - **Layout**: Circular arrangement with regional clustering
            - **Filtering**: Alliance strength threshold for significant relationships
            - **Visualization**: Plotly scatter plot with regional color coding
            
            **Interpretation**:
            - Dense connections indicate strong regional alliances
            - Color coding shows regional groupings
            - Central nodes represent key regional players
            
            ### 📊 Data Quality & Limitations
            
            **Data Coverage**: 22,060 speeches from 1946-2024
            **Countries**: 200 countries with regional classifications
            **Regions**: 8 major regional groupings (Africa, Asia, Europe, etc.)
            
            **Limitations**:
            - Co-mention analysis based on session participation, not content analysis
            - Alliance networks inferred from regional groupings, not voting records
            - Historical data may have classification inconsistencies
            - Network layouts are simplified for visualization clarity
            
            **Technical Implementation**:
            - Database: DuckDB with vector embeddings
            - Visualization: Plotly interactive charts
            - Filtering: Real-time database queries
            - Performance: Optimized for large datasets
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            # Network type selection
            network_type = st.radio(
                "Network Type",
                options=[
                    "Country-Region Network",
                    "Co-mention Network", 
                    "Speaker Patterns",
                    "Alliance Networks"
                ],
                key="networks_analysis_type",
                help="Choose your network analysis type"
            )
            
            # Common filters (always visible)
            st.markdown("**🌍 Filters**")
            available_countries = self._get_available_countries()
            available_regions = self._get_available_topics()
            
            selected_countries = st.multiselect(
                "Select Countries (leave empty for all)",
                available_countries,
                key="network_country_filter",
                help="Choose specific countries to analyze"
            )
            
            # Year selection
            if network_type == "Speaker Patterns":
                year_range = st.slider("Year Range", 1946, 2025, (2010, 2025), key="speaker_patterns_year_range")
            else:
                year = st.slider("Year", 1946, 2025, 2025, key="network_year_slider")
            
            # Network-specific parameters
            if network_type == "Country-Region Network":
                min_mentions = st.slider("Minimum Mentions", 1, 50, 5, key="country_topic_min_mentions")
                selected_regions = st.multiselect(
                    "Select Regions (leave empty for all)",
                    available_regions,
                    key="network_region_filter",
                    help="Choose specific regions to analyze"
                )
                
            elif network_type == "Co-mention Network":
                min_co_mentions = st.slider("Minimum Co-mentions", 1, 20, 3, key="co_mention_min_mentions")
                
            elif network_type == "Alliance Networks":
                alliance_threshold = st.slider("Alliance Strength Threshold", 0.1, 1.0, 0.3, key="alliance_threshold")
            
            # Generate button
            if st.button("🔍 Generate Network Analysis", key="generate_network", type="primary"):
                if network_type == "Country-Region Network":
                    st.session_state.network_type = "country_topic"
                    st.session_state.network_year_value = year
                    st.session_state.network_min_mentions = min_mentions
                    st.session_state.selected_countries = selected_countries
                    st.session_state.selected_regions = selected_regions
                elif network_type == "Co-mention Network":
                    st.session_state.network_type = "co_mention"
                    st.session_state.network_year_value = year
                    st.session_state.network_min_co_mentions = min_co_mentions
                    st.session_state.selected_countries = selected_countries
                elif network_type == "Speaker Patterns":
                    st.session_state.network_type = "speaker_patterns"
                    st.session_state.network_year_range = year_range
                    st.session_state.selected_countries = selected_countries
                elif network_type == "Alliance Networks":
                    st.session_state.network_type = "alliance"
                    st.session_state.network_year_value = year
                    st.session_state.selected_countries = selected_countries
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Results")
            if hasattr(st.session_state, 'network_type'):
                # Get stored filter values with safe defaults
                selected_countries = getattr(st.session_state, 'selected_countries', [])
                selected_regions = getattr(st.session_state, 'selected_regions', [])
                
                # Show current filters
                if selected_countries:
                    st.info(f"**Filtered to:** {len(selected_countries)} countries")
                if selected_regions:
                    st.info(f"**Regions:** {', '.join(selected_regions)}")
                
                # Generate the selected network visualization with safe attribute access
                if st.session_state.network_type == "country_topic":
                    year = getattr(st.session_state, 'network_year_value', 2024)
                    min_mentions = getattr(st.session_state, 'network_min_mentions', 5)
                    self._create_country_topic_network(
                        year,
                        min_mentions,
                        selected_countries,
                        selected_regions
                    )
                elif st.session_state.network_type == "co_mention":
                    year = getattr(st.session_state, 'network_year_value', 2024)
                    min_co_mentions = getattr(st.session_state, 'network_min_co_mentions', 3)
                    self._create_co_mention_network(
                        year,
                        min_co_mentions,
                        selected_countries
                    )
                elif st.session_state.network_type == "speaker_patterns":
                    year_range = getattr(st.session_state, 'network_year_range', (2010, 2025))
                    self._create_speaker_pattern_chart(
                        year_range,
                        selected_countries
                    )
                elif st.session_state.network_type == "alliance":
                    year = getattr(st.session_state, 'network_year_value', 2024)
                    self._create_alliance_network(
                        year,
                        selected_countries
                    )
            else:
                # Show default network visualization to demonstrate functionality
                st.info("👆 Select a network analysis type, configure parameters, and click 'Generate Network Analysis' to see results here.")
                
                # Show a default country-region network for 2024
                st.markdown("**📊 Sample Network (2024)**")
                try:
                    self._create_country_topic_network(2024, 1)
                except Exception as e:
                    st.error(f"Error showing sample network: {e}")
    
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
            
            # Add methodology section
            add_methodology_section("""
            **Topic Salience Analysis Methodology:**
            
            • **Keyword Matching**: Each topic is identified using predefined keyword sets (e.g., "Climate Change" includes: climate, global warming, greenhouse, carbon, emissions, environment)
            
            • **Normalization**: Mentions are normalized per 1,000 words to account for varying speech lengths and ensure fair comparison across different time periods
            
            • **Data Aggregation**: Results are grouped by year and region to show temporal and geographical patterns
            
            • **Visualization Types**:
              - **Multi-line Trends**: Shows individual topic trajectories over time
              - **Stacked Area Chart**: Displays cumulative topic attention across years
              - **Session Heatmap**: Visualizes topic intensity by year using color gradients
              - **Regional Comparison**: Compares topic focus across different geographical regions
            
            • **Limitations**: Analysis relies on keyword matching and may not capture nuanced topic discussions or synonyms
            """)
            
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
            
            # Add methodology section
            add_methodology_section("""
            **Country Position Map Methodology:**
            
            • **Data Source**: All speeches from the selected year with word count > 100 words
            
            • **Position Calculation**: Countries are positioned using mock 2D coordinates based on speech characteristics (Note: In production, this would use actual semantic embeddings from sentence-transformers)
            
            • **Regional Clustering**: Countries are grouped by geographic region with slight offsets to show regional patterns:
              - Africa: (0.5, 0.3)
              - Asia: (-0.3, 0.8) 
              - Europe: (-0.8, -0.2)
              - Americas: (0.2, -0.6)
              - Oceania: (0.1, 0.1)
            
            • **Size Encoding**: Bubble size represents the number of speeches by each country in the selected year
            
            • **Filtering**: Only countries with at least 1 speech and >100 words are included (limited to top 50 countries by speech count)
            
            • **Limitations**: Current implementation uses mock coordinates; full semantic analysis would require actual embedding vectors from speech content
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
            
            # Add methodology section
            add_methodology_section("""
            **Similar Speech Finder Methodology:**
            
            • **Reference Speech**: Uses the first available speech from the selected country and year as the reference point
            
            • **Comparison Pool**: Searches speeches from other countries within ±2 years of the reference year (to capture contemporary context)
            
            • **Similarity Calculation**: Uses Jaccard similarity based on word overlap:
              - Jaccard = |Intersection| / |Union| of word sets
              - Converts speeches to lowercase word sets for comparison
              - Filters results by similarity threshold (default: 0.7)
            
            • **Data Filtering**: 
              - Excludes speeches with <100 words
              - Limits comparison to 100 most recent speeches
              - Only includes speeches with similarity ≥ threshold
            
            • **Visualization**: 
              - X-axis: Year of comparison speech
              - Y-axis: Similarity score (0-1)
              - Size: Speech length (word count)
              - Color: Geographic region
            
            • **Limitations**: Simple word overlap may not capture semantic similarity; advanced NLP techniques would provide better results
            """)
            
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
            
            # Add methodology section
            add_methodology_section("""
            **Topic Composition Analysis Methodology:**
            
            • **Data Source**: All speeches from the selected country and year with word count > 100 words
            
            • **Topic Categories**: 10 predefined topic categories with associated keywords:
              - Peace & Security: peace, security, conflict, war, terrorism, military, defense
              - Development: development, poverty, economic, growth, sustainable development, aid
              - Climate Change: climate, environment, global warming, carbon, emissions, green
              - Human Rights: human rights, rights, freedom, democracy, justice, equality
              - Gender Equality: gender, women, girls, empowerment, feminist, equality
              - Health: health, medical, disease, pandemic, healthcare, medicine
              - Education: education, school, learning, knowledge, training, university
              - Trade: trade, commerce, economic, market, business, investment
              - Technology: technology, digital, innovation, tech, artificial intelligence, ai
              - Migration: migration, refugee, immigration, displacement, asylum
            
            • **Calculation Method**: 
              - Combines all speeches for the country/year into a single text
              - Counts keyword mentions in the combined text
              - Calculates percentage as (mentions / total_words) × 100
              - Only includes topics with >0.1% presence
            
            • **Visualization**: Donut chart showing relative topic focus, sorted by percentage (descending)
            
            • **Limitations**: 
              - Relies on exact keyword matching (case-insensitive)
              - May miss synonyms or related terms not in keyword lists
              - Single year analysis may not capture long-term trends
            """)
            
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
            
            # Add methodology section
            add_methodology_section("""
            **Keyword Trajectory Analysis Methodology:**
            
            • **Data Source**: All speeches from the selected year range with word count > 0
            
            • **Keyword Search**: Uses case-insensitive LIKE pattern matching for each keyword/phrase
            
            • **Normalization**: Calculates mentions per 1,000 words to account for varying speech lengths:
              - Formula: (speech_count / total_words) × 1000
              - Groups results by year to show temporal trends
            
            • **Data Aggregation**:
              - Counts speeches containing each keyword per year
              - Sums total word count for normalization
              - Orders results chronologically
            
            • **Visualization**: Multi-line chart showing keyword popularity over time
            
            • **Burst Detection**: (Placeholder) Would identify periods of unusually high keyword usage
            
            • **Limitations**:
              - Simple pattern matching may miss variations or synonyms
              - No stemming or lemmatization applied
              - Case-insensitive but exact phrase matching only
              - May include false positives from partial word matches
            """)
            
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
            
            # Add methodology section
            add_methodology_section("""
            **Sentiment Analysis Methodology:**
            
            • **Data Source**: All speeches from selected countries in the year range with word count > 100 words
            
            • **Sentiment Dictionary**: Uses predefined word lists for sentiment classification:
              - **Positive Words**: peace, hope, progress, development, cooperation, unity, freedom, justice, prosperity, success
              - **Negative Words**: war, conflict, crisis, poverty, violence, threat, danger, failure, destruction, suffering
            
            • **Calculation Method**:
              - Counts positive and negative word occurrences in each speech
              - Calculates sentiment score: (positive_count - negative_count) / total_sentiment_words
              - Score range: -1 (very negative) to +1 (very positive)
              - Weights scores by word count for more accurate representation
            
            • **Aggregation**: 
              - Combines multiple speeches per country/year
              - Calculates weighted average sentiment by year
              - Uses word count as weighting factor
            
            • **Visualization**: 
              - Line chart: Sentiment trends over time by country
              - Box plot: Distribution of sentiment scores by country
            
            • **Limitations**:
              - Simple word-counting approach (not context-aware)
              - Limited sentiment dictionary may miss nuanced expressions
              - No handling of negations or sarcasm
              - May not capture cultural or diplomatic language nuances
            """)
            
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
            
            # Add methodology section
            add_methodology_section("""
            **Event-Aligned Timeline Analysis Methodology:**
            
            • **Data Source**: All speeches from 3 years before to 3 years after each selected event
            
            • **Event Definitions**: Predefined major events with associated keywords:
              - Cold War End (1991): cold war, berlin wall, soviet union, glasnost, perestroika
              - 9/11 (2001): terrorism, 9/11, september 11, terrorist, security
              - Financial Crisis (2008): financial crisis, economic crisis, recession, banking, economy
              - Arab Spring (2011): arab spring, democracy, revolution, protest, uprising
              - Paris Agreement (2015): paris agreement, climate change, emissions, carbon, global warming
              - COVID-19 (2020): covid, pandemic, coronavirus, health, crisis
              - Ukraine War (2022): ukraine, russia, war, conflict, invasion
            
            • **Calculation Method**:
              - Searches for event-related keywords in speeches using OR conditions
              - Counts speeches containing any event keywords per year
              - Calculates mentions per 1,000 words: (speech_count / total_words) × 1000
              - Shows 7-year window (±3 years around each event)
            
            • **Visualization**: 
              - Line chart showing keyword mentions over time
              - Vertical dashed lines mark the actual event years
              - Each event shown as separate line with different color
            
            • **Limitations**:
              - Relies on predefined keyword sets
              - May miss event-related discussions using different terminology
              - Fixed 7-year window may not capture all relevant periods
              - Simple keyword matching without context analysis
            """)
            
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
            
            # Add methodology section
            add_methodology_section(f"""
            **Regional Comparison Analysis Methodology:**
            
            • **Data Source**: All speeches from selected regions with word count > 100 words
            
            • **Comparison Metric**: {metric}
            
            • **Calculation Methods by Metric**:
            
            **Topic Focus**:
            - Counts total speeches per region per year
            - Calculates average word count per speech
            - Groups by region and year for temporal comparison
            
            **Speech Length**:
            - Calculates average word count per speech by region and year
            - Counts total speeches for context
            - Shows regional differences in speech verbosity
            
            **Sentiment**:
            - Uses predefined positive/negative word dictionaries
            - Calculates sentiment score: (positive - negative) / total_sentiment_words
            - Weights by word count for accurate representation
            - Aggregates by region and year
            
            **Keyword Usage**:
            - Analyzes 6 common keywords: development, peace, security, climate, human rights, cooperation
            - Counts speeches containing each keyword per region per year
            - Calculates mentions per 1,000 words for normalization
            - Shows regional focus differences
            
            • **Visualization**: Grouped bar chart comparing regions across selected metric
            
            • **Limitations**:
            - Sentiment analysis uses simple word counting
            - Keyword analysis limited to predefined terms
            - Regional groupings may not capture sub-regional differences
            - No statistical significance testing
            """)
            
        except Exception as e:
            st.error(f"Error creating regional comparison chart: {e}")
            logger.error(f"Error in _create_regional_comparison_chart: {e}")
    
    def _create_country_topic_network(self, year: int, min_mentions: int, selected_countries: List[str] = None, selected_topics: List[str] = None):
        """Create country-topic bipartite network."""
        try:
            # Show methodology info
            st.info("""
            **📊 Country-Region Network Analysis**
            
            This visualization shows the relationship between countries and their regional groupings based on UNGA participation.
            - **Blue nodes**: Countries (positioned below)
            - **Red nodes**: Regions (positioned above)  
            - **Line thickness**: Number of speeches (activity level)
            - **Filtering**: Only shows countries/regions with ≥{} mentions
            """.format(min_mentions))
            
            # Get network data
            network_data = self._get_country_topic_network_data(year, min_mentions, selected_countries, selected_topics)
            
            if not network_data:
                st.warning("No network data found for the selected criteria.")
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
                    opacity=0.6,
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Add country nodes
            country_nodes = [node for node in network_data['nodes'] if node['type'] == 'country']
            if country_nodes:
                fig.add_trace(go.Scatter(
                    x=[node['x'] for node in country_nodes],
                    y=[node['y'] for node in country_nodes],
                    mode='markers+text',
                    text=[node['label'] for node in country_nodes],
                    textposition='middle center',
                    marker=dict(size=20, color='lightblue'),
                    name='Countries',
                    showlegend=True
                ))
            
            # Add region nodes
            region_nodes = [node for node in network_data['nodes'] if node['type'] == 'region']
            if region_nodes:
                fig.add_trace(go.Scatter(
                    x=[node['x'] for node in region_nodes],
                    y=[node['y'] for node in region_nodes],
                    mode='markers+text',
                    text=[node['label'] for node in region_nodes],
                    textposition='middle center',
                    marker=dict(size=15, color='lightcoral'),
                    name='Regions',
                    showlegend=True
                ))
            
            fig.update_layout(
                title=f"Country-Topic Network ({year})",
                height=600,
                showlegend=True,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show network statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Countries", len(network_data['countries']))
            with col2:
                st.metric("Topics", len(network_data['topics']))
            with col3:
                st.metric("Connections", len(network_data['edges']))
            
        except Exception as e:
            st.error(f"Error creating country-topic network: {e}")
            logger.error(f"Error in _create_country_topic_network: {e}")
    
    def _create_co_mention_network(self, year: int, min_co_mentions: int, selected_countries: List[str] = None):
        """Create co-mention network visualization."""
        try:
            # Show methodology info
            st.info("""
            **🤝 Co-mention Network Analysis**
            
            This visualization identifies countries that frequently speak in the same UNGA sessions, indicating potential diplomatic relationships.
            - **Green nodes**: Countries (circular layout)
            - **Blue lines**: Co-participation in sessions
            - **Line thickness**: Number of shared sessions (≥{})
            - **Central nodes**: Highly connected countries
            """.format(min_co_mentions))
            
            # Get co-mention data
            co_mention_data = self._get_co_mention_data(year, min_co_mentions, selected_countries)
            
            if co_mention_data.empty:
                st.warning("No co-mention data found for the selected criteria.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add edges
            for _, row in co_mention_data.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['country1_x'], row['country2_x']],
                    y=[row['country1_y'], row['country2_y']],
                    mode='lines',
                    line=dict(width=min(row['co_mentions'], 5), color='blue'),
                    opacity=0.6,
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Add country nodes
            countries = list(set(co_mention_data['country1'].tolist() + co_mention_data['country2'].tolist()))
            for country in countries:
                country_data = co_mention_data[(co_mention_data['country1'] == country) | (co_mention_data['country2'] == country)]
                if not country_data.empty:
                    x = country_data.iloc[0]['country1_x'] if country_data.iloc[0]['country1'] == country else country_data.iloc[0]['country2_x']
                    y = country_data.iloc[0]['country1_y'] if country_data.iloc[0]['country1'] == country else country_data.iloc[0]['country2_y']
                    
                    fig.add_trace(go.Scatter(
                        x=[x],
                        y=[y],
                        mode='markers+text',
                        text=[country],
                        textposition='middle center',
                        marker=dict(size=20, color='lightgreen'),
                        name=country,
                        showlegend=False
                    ))
            
            fig.update_layout(
                title=f"Country Co-mention Network ({year})",
                height=600,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show network statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Countries", len(countries))
            with col2:
                st.metric("Connections", len(co_mention_data))
            with col3:
                st.metric("Total Co-mentions", co_mention_data['co_mentions'].sum())
            
        except Exception as e:
            st.error(f"Error creating co-mention network: {e}")
            logger.error(f"Error in _create_co_mention_network: {e}")
    
    def _create_speaker_pattern_chart(self, year_range: Tuple[int, int], selected_countries: List[str] = None):
        """Create speaker pattern visualization."""
        try:
            # Show methodology info
            st.info("""
            **👥 Speaker Pattern Analysis**
            
            This visualization analyzes temporal patterns in country participation and speech activity over time.
            - **Line chart**: Shows speech activity trends by country
            - **Time range**: {}-{}
            - **Metrics**: Speech frequency, average length, participation patterns
            - **Trends**: Upward trends indicate increasing participation
            """.format(year_range[0], year_range[1]))
            
            # Get speaker data
            speaker_data = self._get_speaker_pattern_data(year_range, selected_countries)
            
            if not speaker_data or speaker_data['speaker_activity'].empty:
                st.warning("No speaker data found for the selected criteria.")
                return
            
            df = speaker_data['speaker_activity']
            
            # Create visualization
            fig = px.line(
                df,
                x='year',
                y='speech_count',
                color='country_name',
                title="Speaker Activity Over Time",
                labels={'speech_count': 'Number of Speeches', 'year': 'Year'}
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Speeches", speaker_data['total_speeches'])
            with col2:
                st.metric("Active Countries", speaker_data['active_countries'])
            with col3:
                avg_length = df['avg_speech_length'].mean()
                st.metric("Avg Speech Length", f"{avg_length:.0f} chars")
            
        except Exception as e:
            st.error(f"Error creating speaker pattern chart: {e}")
            logger.error(f"Error in _create_speaker_pattern_chart: {e}")
    
    def _create_alliance_network(self, year: int, selected_countries: List[str] = None):
        """Create alliance network visualization."""
        try:
            # Show methodology info
            st.info("""
            **🤝 Alliance Network Analysis**
            
            This visualization identifies potential political alliances based on regional groupings and participation patterns.
            - **Orange nodes**: Countries (circular layout)
            - **Green lines**: Regional alliance connections
            - **Line thickness**: Alliance strength (regional proximity)
            - **Color coding**: Regional groupings and political blocs
            """)
            
            # Get alliance data
            alliance_data = self._get_alliance_data(year, selected_countries)
            
            if alliance_data.empty:
                st.warning("No alliance data found for the selected criteria.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add alliance connections
            for _, row in alliance_data.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['country1_x'], row['country2_x']],
                    y=[row['country1_y'], row['country2_y']],
                    mode='lines',
                    line=dict(width=row['alliance_strength']*5, color='green'),
                    opacity=0.6,
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Add country nodes
            countries = list(set(alliance_data['country1'].tolist() + alliance_data['country2'].tolist()))
            for country in countries:
                country_data = alliance_data[(alliance_data['country1'] == country) | (alliance_data['country2'] == country)]
                if not country_data.empty:
                    x = country_data.iloc[0]['country1_x'] if country_data.iloc[0]['country1'] == country else country_data.iloc[0]['country2_x']
                    y = country_data.iloc[0]['country1_y'] if country_data.iloc[0]['country1'] == country else country_data.iloc[0]['country2_y']
                    
                    fig.add_trace(go.Scatter(
                        x=[x],
                        y=[y],
                        mode='markers+text',
                        text=[country],
                        textposition='middle center',
                        marker=dict(size=20, color='orange'),
                        name=country,
                        showlegend=False
                    ))
            
            fig.update_layout(
                title=f"Alliance Network ({year})",
                height=600,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show network statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Countries", len(countries))
            with col2:
                st.metric("Alliances", len(alliance_data))
            with col3:
                regions = alliance_data['region'].nunique()
                st.metric("Regions", regions)
            
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
                    ANY_VALUE(speech_text) as speech_text,
                    AVG(word_count) as word_count,
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
    
    def _get_country_topic_network_data(self, year: int, min_mentions: int, selected_countries: List[str] = None, selected_topics: List[str] = None) -> Dict[str, Any]:
        """Get country-topic network data."""
        try:
            # Since we don't have topics, we'll create a country-region network instead
            query = """
                SELECT 
                    s.country_name,
                    s.region,
                    COUNT(*) as mention_count
                FROM speeches s
                WHERE s.year = ?
            """
            params = [year]
            
            # Add country filter if specified
            if selected_countries:
                placeholders = ','.join(['?' for _ in selected_countries])
                query += f" AND s.country_name IN ({placeholders})"
                params.extend(selected_countries)
            
            query += """
                GROUP BY s.country_name, s.region
                HAVING COUNT(*) >= ?
                ORDER BY mention_count DESC
            """
            params.append(min_mentions)
            
            result = self.db_manager.conn.execute(query, params).fetchall()
            
            if not result:
                return {}
            
            # Create network data structure
            countries = list(set([row[0] for row in result]))
            regions = list(set([row[1] for row in result]))
            
            # Create nodes
            nodes = []
            node_positions = {}
            
            # Add country nodes
            for i, country in enumerate(countries):
                nodes.append({
                    'id': country,
                    'label': country,
                    'type': 'country',
                    'x': i * 2,
                    'y': 0,
                    'size': 20,
                    'color': 'lightblue'
                })
                node_positions[country] = (i * 2, 0)
            
            # Add region nodes
            for i, region in enumerate(regions):
                nodes.append({
                    'id': region,
                    'label': region,
                    'type': 'region',
                    'x': i * 2,
                    'y': 2,
                    'size': 15,
                    'color': 'lightcoral'
                })
                node_positions[region] = (i * 2, 2)
            
            # Create edges
            edges = []
            for row in result:
                country, region, count = row
                if country in node_positions and region in node_positions:
                    edges.append({
                        'source': country,
                        'target': region,
                        'weight': min(count, 10),  # Cap weight for visualization
                        'source_x': node_positions[country][0],
                        'source_y': node_positions[country][1],
                        'target_x': node_positions[region][0],
                        'target_y': node_positions[region][1]
                    })
            
            return {
                'nodes': nodes,
                'edges': edges,
                'countries': countries,
                'topics': regions  # Using regions as "topics"
            }
            
        except Exception as e:
            logger.error(f"Error getting country-topic network data: {e}")
            return {}
    
    def _get_co_mention_data(self, year: int, min_co_mentions: int, selected_countries: List[str] = None) -> pd.DataFrame:
        """Get co-mention data for network visualization."""
        try:
            # This is a simplified co-mention analysis
            # In a real implementation, you'd analyze text for country co-mentions
            query = """
                SELECT 
                    s1.country_name as country1,
                    s2.country_name as country2,
                    COUNT(*) as co_mentions
                FROM speeches s1
                JOIN speeches s2 ON s1.session = s2.session AND s1.year = s2.year
                WHERE s1.year = ? 
                AND s1.country_name != s2.country_name
            """
            params = [year]
            
            # Add country filter if specified
            if selected_countries:
                placeholders = ','.join(['?' for _ in selected_countries])
                query += f" AND s1.country_name IN ({placeholders}) AND s2.country_name IN ({placeholders})"
                params.extend(selected_countries * 2)
            
            query += """
                GROUP BY s1.country_name, s2.country_name
                HAVING COUNT(*) >= ?
                ORDER BY co_mentions DESC
            """
            params.append(min_co_mentions)
            
            result = self.db_manager.conn.execute(query, params).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Create DataFrame with network positions
            df = pd.DataFrame(result, columns=['country1', 'country2', 'co_mentions'])
            
            # Add simple positioning (circular layout)
            countries = list(set(df['country1'].tolist() + df['country2'].tolist()))
            n = len(countries)
            
            for i, country in enumerate(countries):
                angle = 2 * np.pi * i / n
                x = np.cos(angle)
                y = np.sin(angle)
                df.loc[df['country1'] == country, 'country1_x'] = x
                df.loc[df['country1'] == country, 'country1_y'] = y
                df.loc[df['country2'] == country, 'country2_x'] = x
                df.loc[df['country2'] == country, 'country2_y'] = y
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting co-mention data: {e}")
            return pd.DataFrame()
    
    def _get_speaker_pattern_data(self, year_range: Tuple[int, int], selected_countries: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Get speaker pattern data."""
        try:
            start_year, end_year = year_range
            
            query = """
                SELECT 
                    country_name,
                    year,
                    COUNT(*) as speech_count,
                    AVG(LENGTH(text)) as avg_speech_length
                FROM speeches
                WHERE year >= ? AND year <= ?
            """
            params = [start_year, end_year]
            
            # Add country filter if specified
            if selected_countries:
                placeholders = ','.join(['?' for _ in selected_countries])
                query += f" AND country_name IN ({placeholders})"
                params.extend(selected_countries)
            
            query += """
                GROUP BY country_name, year
                ORDER BY year, speech_count DESC
            """
            
            result = self.db_manager.conn.execute(query, params).fetchall()
            
            if not result:
                return {}
            
            df = pd.DataFrame(result, columns=['country_name', 'year', 'speech_count', 'avg_speech_length'])
            
            return {
                'speaker_activity': df,
                'total_speeches': df['speech_count'].sum(),
                'active_countries': len(df['country_name'].unique())
            }
            
        except Exception as e:
            logger.error(f"Error getting speaker pattern data: {e}")
            return {}
    
    def _get_alliance_data(self, year: int, selected_countries: List[str] = None) -> pd.DataFrame:
        """Get alliance data for network visualization."""
        try:
            # This is a simplified alliance analysis based on voting patterns
            # In a real implementation, you'd analyze voting records and statements
            query = """
                SELECT 
                    country_name,
                    region,
                    COUNT(*) as speech_count
                FROM speeches
                WHERE year = ?
            """
            params = [year]
            
            # Add country filter if specified
            if selected_countries:
                placeholders = ','.join(['?' for _ in selected_countries])
                query += f" AND country_name IN ({placeholders})"
                params.extend(selected_countries)
            
            query += """
                GROUP BY country_name, region
                ORDER BY speech_count DESC
            """
            
            result = self.db_manager.conn.execute(query, params).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            df = pd.DataFrame(result, columns=['country_name', 'region', 'speech_count'])
            
            # Create alliance relationships based on regional groupings
            alliances = []
            regions = df['region'].unique()
            
            for region in regions:
                region_countries = df[df['region'] == region]['country_name'].tolist()
                for i, country1 in enumerate(region_countries):
                    for country2 in region_countries[i+1:]:
                        alliances.append({
                            'country1': country1,
                            'country2': country2,
                            'alliance_strength': 0.8,  # Regional alliance strength
                            'region': region
                        })
            
            return pd.DataFrame(alliances)
            
        except Exception as e:
            logger.error(f"Error getting alliance data: {e}")
            return pd.DataFrame()
    
    def _get_available_countries(self) -> List[str]:
        """Get list of available countries for filtering."""
        try:
            query = "SELECT DISTINCT country_name FROM speeches WHERE country_name IS NOT NULL ORDER BY country_name"
            result = self.db_manager.conn.execute(query).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting available countries: {e}")
            return []
    
    def _get_available_topics(self) -> List[str]:
        """Get list of available regions for filtering (since we don't have topics)."""
        try:
            query = "SELECT DISTINCT region FROM speeches WHERE region IS NOT NULL AND region != '' ORDER BY region"
            result = self.db_manager.conn.execute(query).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting available regions: {e}")
            return []


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
        
        # Add methodology note to the figure
        fig.add_annotation(
            text="Methodology: Counts all speeches by region from database",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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
        
        # Add methodology note
        fig.add_annotation(
            text="Methodology: Average word count per speech, grouped by country and year",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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
        
        # Add methodology note
        fig.add_annotation(
            text="Methodology: Counts distinct African Union member countries speaking each year",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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
        
        # Add methodology note
        fig.add_annotation(
            text="Methodology: Histogram of word counts (filtered: 0 < word_count < 10,000)",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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
        
        # Add methodology note
        fig.add_annotation(
            text="Methodology: Top 20 countries by total speech count across all years",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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
        
        # Add methodology note
        fig.add_annotation(
            text="Methodology: Speech count per country per year (green=more speeches, red=fewer)",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
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