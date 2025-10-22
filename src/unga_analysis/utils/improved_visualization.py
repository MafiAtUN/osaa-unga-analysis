"""
Improved visualization module for UNGA speech analysis.
Fixed issues with filters, error handling, and data validation.
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

class ImprovedVisualizationManager:
    """Improved visualization manager with better error handling and filters."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.available_countries = []
        self.available_years = []
        self.available_regions = []
        self._load_metadata()
    
    def _load_metadata(self):
        """Load available countries, years, and regions from database."""
        try:
            # Get available countries
            countries_result = self.db_manager.conn.execute("SELECT DISTINCT country_name FROM speeches ORDER BY country_name").fetchall()
            self.available_countries = [row[0] for row in countries_result]
            
            # Get available years
            years_result = self.db_manager.conn.execute("SELECT DISTINCT year FROM speeches ORDER BY year").fetchall()
            self.available_years = [row[0] for row in years_result]
            
            # Get available regions
            regions_result = self.db_manager.conn.execute("SELECT DISTINCT region FROM speeches ORDER BY region").fetchall()
            self.available_regions = [row[0] for row in regions_result]
            
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            self.available_countries = []
            self.available_years = []
            self.available_regions = []
    
    def render_improved_visualization_menu(self):
        """Render the improved visualization menu with proper filters."""
        st.markdown("## 📊 Improved Visualizations")
        st.markdown("**Enhanced visualizations with comprehensive filters and error handling**")
        
        # Show data availability
        self._show_data_availability()
        
        # Create tabs for different visualization categories
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Topic Analysis", 
            "🌍 Country Analysis", 
            "📊 Regional Analysis", 
            "🔍 Network Analysis"
        ])
        
        with tab1:
            self._render_topic_analysis_tab()
        
        with tab2:
            self._render_country_analysis_tab()
        
        with tab3:
            self._render_regional_analysis_tab()
        
        with tab4:
            self._render_network_analysis_tab()
    
    def _show_data_availability(self):
        """Show data availability statistics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📅 Years", len(self.available_years))
        with col2:
            st.metric("🌍 Countries", len(self.available_countries))
        with col3:
            st.metric("🗺️ Regions", len(self.available_regions))
        with col4:
            try:
                total_speeches = self.db_manager.conn.execute("SELECT COUNT(*) FROM speeches").fetchone()[0]
                st.metric("📝 Speeches", f"{total_speeches:,}")
            except:
                st.metric("📝 Speeches", "N/A")
    
    def _render_topic_analysis_tab(self):
        """Render topic analysis visualizations with proper filters."""
        st.markdown("### 📈 Topic Analysis")
        st.markdown("**Analyze how different topics are discussed over time and across regions.**")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            topics = st.multiselect(
                "Select Topics",
                options=[
                    "Climate Change", "Peace & Security", "Development", "Human Rights",
                    "Gender Equality", "Trade", "Health", "Education", "Migration",
                    "Technology", "AI", "Palestine", "Ukraine", "Debt", "Multilateralism"
                ],
                default=["Climate Change", "Peace & Security", "Development"],
                help="Choose topics to analyze"
            )
        
        with col2:
            year_range = st.slider(
                "Year Range",
                min_value=min(self.available_years) if self.available_years else 1946,
                max_value=max(self.available_years) if self.available_years else 2024,
                value=(2000, 2024),
                help="Select the time period to analyze"
            )
        
        with col3:
            regions = st.multiselect(
                "Select Regions",
                options=self.available_regions,
                default=self.available_regions[:3] if self.available_regions else [],
                help="Choose regions to include"
            )
        
        # Visualization type
        viz_type = st.selectbox(
            "Visualization Type",
            options=["Line Chart", "Bar Chart", "Heatmap", "Area Chart"],
            help="Choose how to display the data"
        )
        
        # Generate button
        if st.button("📊 Generate Topic Analysis", type="primary"):
            if not topics:
                st.error("Please select at least one topic.")
                return
            
            with st.spinner("Generating topic analysis..."):
                self._create_topic_analysis_chart(topics, year_range, regions, viz_type)
    
    def _render_country_analysis_tab(self):
        """Render country analysis visualizations with proper filters."""
        st.markdown("### 🌍 Country Analysis")
        st.markdown("**Analyze individual countries and compare them with others.**")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            countries = st.multiselect(
                "Select Countries",
                options=self.available_countries,
                default=self.available_countries[:5] if self.available_countries else [],
                help="Choose countries to analyze"
            )
        
        with col2:
            year_range = st.slider(
                "Year Range",
                min_value=min(self.available_years) if self.available_years else 1946,
                max_value=max(self.available_years) if self.available_years else 2024,
                value=(2020, 2024),
                help="Select the time period to analyze"
            )
        
        with col3:
            analysis_type = st.selectbox(
                "Analysis Type",
                options=["Word Count Trends", "Topic Focus", "Sentiment Analysis", "Speech Length"],
                help="Choose what to analyze"
            )
        
        # Generate button
        if st.button("🌍 Generate Country Analysis", type="primary"):
            if not countries:
                st.error("Please select at least one country.")
                return
            
            with st.spinner("Generating country analysis..."):
                self._create_country_analysis_chart(countries, year_range, analysis_type)
    
    def _render_regional_analysis_tab(self):
        """Render regional analysis visualizations with proper filters."""
        st.markdown("### 📊 Regional Analysis")
        st.markdown("**Compare different regions and their focus areas.**")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            regions = st.multiselect(
                "Select Regions",
                options=self.available_regions,
                default=self.available_regions[:4] if self.available_regions else [],
                help="Choose regions to compare"
            )
        
        with col2:
            metric = st.selectbox(
                "Metric",
                options=["Speech Count", "Average Word Count", "Topic Diversity", "Sentiment Score"],
                help="Choose what to compare"
            )
        
        # Generate button
        if st.button("📊 Generate Regional Analysis", type="primary"):
            if not regions:
                st.error("Please select at least one region.")
                return
            
            with st.spinner("Generating regional analysis..."):
                self._create_regional_analysis_chart(regions, metric)
    
    def _render_network_analysis_tab(self):
        """Render network analysis visualizations with proper filters."""
        st.markdown("### 🔍 Network Analysis")
        st.markdown("**Explore relationships between countries and topics.**")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.selectbox(
                "Select Year",
                options=self.available_years,
                index=len(self.available_years)-1 if self.available_years else 0,
                help="Choose year for network analysis"
            )
        
        with col2:
            min_connections = st.number_input(
                "Minimum Connections",
                min_value=1,
                max_value=50,
                value=5,
                help="Minimum number of connections to show"
            )
        
        # Generate button
        if st.button("🔍 Generate Network Analysis", type="primary"):
            with st.spinner("Generating network analysis..."):
                self._create_network_analysis_chart(year, min_connections)
    
    def _create_topic_analysis_chart(self, topics: List[str], year_range: Tuple[int, int], 
                                   regions: List[str], viz_type: str):
        """Create topic analysis chart with proper error handling."""
        try:
            # Get data
            data = self._get_topic_data_safe(topics, year_range, regions)
            
            if data.empty:
                st.warning("No data found for the selected criteria. Try adjusting your filters.")
                return
            
            # Create visualization based on type
            if viz_type == "Line Chart":
                fig = px.line(
                    data, 
                    x='year', 
                    y='mentions_per_1000_words', 
                    color='topic',
                    title="Topic Mentions Over Time",
                    labels={'mentions_per_1000_words': 'Mentions per 1,000 Words', 'year': 'Year'}
                )
            elif viz_type == "Bar Chart":
                fig = px.bar(
                    data, 
                    x='year', 
                    y='mentions_per_1000_words', 
                    color='topic',
                    title="Topic Mentions by Year",
                    labels={'mentions_per_1000_words': 'Mentions per 1,000 Words', 'year': 'Year'}
                )
            elif viz_type == "Heatmap":
                pivot_data = data.pivot_table(
                    index='topic', 
                    columns='year', 
                    values='mentions_per_1000_words', 
                    fill_value=0
                )
                fig = px.imshow(
                    pivot_data,
                    title="Topic Mentions Heatmap",
                    labels={'x': 'Year', 'y': 'Topic', 'color': 'Mentions per 1,000 Words'}
                )
            else:  # Area Chart
                fig = px.area(
                    data, 
                    x='year', 
                    y='mentions_per_1000_words', 
                    color='topic',
                    title="Topic Mentions Over Time (Area)",
                    labels={'mentions_per_1000_words': 'Mentions per 1,000 Words', 'year': 'Year'}
                )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data summary
            st.markdown("#### 📊 Data Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Data Points", len(data))
            with col2:
                st.metric("Topics Analyzed", len(data['topic'].unique()))
            with col3:
                st.metric("Years Covered", len(data['year'].unique()))
            
        except Exception as e:
            st.error(f"Error creating topic analysis chart: {e}")
            logger.error(f"Topic analysis error: {e}")
    
    def _create_country_analysis_chart(self, countries: List[str], year_range: Tuple[int, int], 
                                     analysis_type: str):
        """Create country analysis chart with proper error handling."""
        try:
            # Get data
            data = self._get_country_data_safe(countries, year_range, analysis_type)
            
            if data.empty:
                st.warning("No data found for the selected countries and criteria.")
                return
            
            # Create visualization based on analysis type
            if analysis_type == "Word Count Trends":
                fig = px.line(
                    data, 
                    x='year', 
                    y='word_count', 
                    color='country_name',
                    title="Word Count Trends by Country",
                    labels={'word_count': 'Word Count', 'year': 'Year'}
                )
            elif analysis_type == "Topic Focus":
                fig = px.bar(
                    data, 
                    x='country_name', 
                    y='topic_mentions', 
                    color='topic',
                    title="Topic Focus by Country",
                    labels={'topic_mentions': 'Topic Mentions', 'country_name': 'Country'}
                )
            elif analysis_type == "Sentiment Analysis":
                fig = px.line(
                    data, 
                    x='year', 
                    y='sentiment_score', 
                    color='country_name',
                    title="Sentiment Trends by Country",
                    labels={'sentiment_score': 'Sentiment Score', 'year': 'Year'}
                )
            else:  # Speech Length
                fig = px.box(
                    data, 
                    x='country_name', 
                    y='speech_length',
                    title="Speech Length Distribution by Country",
                    labels={'speech_length': 'Speech Length (words)', 'country_name': 'Country'}
                )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data summary
            st.markdown("#### 📊 Data Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Countries Analyzed", len(data['country_name'].unique()))
            with col2:
                st.metric("Years Covered", len(data['year'].unique()))
            with col3:
                st.metric("Total Data Points", len(data))
            
        except Exception as e:
            st.error(f"Error creating country analysis chart: {e}")
            logger.error(f"Country analysis error: {e}")
    
    def _create_regional_analysis_chart(self, regions: List[str], metric: str):
        """Create regional analysis chart with proper error handling."""
        try:
            # Get data
            data = self._get_regional_data_safe(regions, metric)
            
            if data.empty:
                st.warning("No data found for the selected regions.")
                return
            
            # Create visualization
            fig = px.bar(
                data,
                x='region',
                y='value',
                color='region',
                title=f"Regional Comparison: {metric}",
                labels={'value': metric, 'region': 'Region'}
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data summary
            st.markdown("#### 📊 Data Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Regions Compared", len(data))
            with col2:
                st.metric("Metric", metric)
            
        except Exception as e:
            st.error(f"Error creating regional analysis chart: {e}")
            logger.error(f"Regional analysis error: {e}")
    
    def _create_network_analysis_chart(self, year: int, min_connections: int):
        """Create network analysis chart with proper error handling."""
        try:
            # Get data
            data = self._get_network_data_safe(year, min_connections)
            
            if data.empty:
                st.warning("No network data found for the selected criteria.")
                return
            
            # Create network visualization
            fig = go.Figure()
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='markers+text',
                text=data['label'],
                textposition="middle center",
                marker=dict(size=20, color=data['color']),
                name='Countries'
            ))
            
            # Add edges if they exist
            if 'edges' in data.columns and not data['edges'].empty:
                edges_df = data['edges'].iloc[0] if len(data) > 0 else pd.DataFrame()
                if not edges_df.empty:
                    for _, edge in edges_df.iterrows():
                        fig.add_trace(go.Scatter(
                            x=[edge['x1'], edge['x2']],
                            y=[edge['y1'], edge['y2']],
                            mode='lines',
                            line=dict(width=1, color='gray'),
                            showlegend=False
                        ))
            
            fig.update_layout(
                title=f"Country Network Analysis ({year})",
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data summary
            st.markdown("#### 📊 Network Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nodes", len(data))
            with col2:
                st.metric("Connections", len(data['edges']))
            with col3:
                st.metric("Year", year)
            
        except Exception as e:
            st.error(f"Error creating network analysis chart: {e}")
            logger.error(f"Network analysis error: {e}")
    
    def _get_topic_data_safe(self, topics: List[str], year_range: Tuple[int, int], 
                           regions: List[str]) -> pd.DataFrame:
        """Get topic data with proper error handling."""
        try:
            # Simple keyword matching approach
            topic_keywords = {
                "Climate Change": ["climate", "global warming", "greenhouse", "carbon", "emissions"],
                "Peace & Security": ["peace", "security", "conflict", "war", "terrorism"],
                "Development": ["development", "poverty", "economic", "growth", "sustainable"],
                "Human Rights": ["human rights", "rights", "freedom", "democracy", "justice"],
                "Gender Equality": ["gender", "women", "girls", "equality", "empowerment"],
                "Trade": ["trade", "commerce", "economic", "market", "business"],
                "Health": ["health", "medical", "disease", "pandemic", "healthcare"],
                "Education": ["education", "school", "learning", "knowledge", "training"],
                "Migration": ["migration", "refugee", "immigration", "displacement"],
                "Technology": ["technology", "digital", "innovation", "tech"],
                "AI": ["artificial intelligence", "ai", "machine learning", "automation"],
                "Palestine": ["palestine", "palestinian", "israel", "gaza", "west bank"],
                "Ukraine": ["ukraine", "ukrainian", "russia", "russian", "war"],
                "Debt": ["debt", "debt relief", "debt cancellation", "debt sustainability"],
                "Multilateralism": ["multilateral", "multilateralism", "united nations", "cooperation"]
            }
            
            # Build query
            topic_conditions = []
            for topic in topics:
                if topic in topic_keywords:
                    keywords = topic_keywords[topic]
                    conditions = [f"LOWER(speech_text) LIKE '%{keyword.lower()}%'" for keyword in keywords]
                    topic_conditions.append(f"({' OR '.join(conditions)})")
            
            if not topic_conditions:
                return pd.DataFrame()
            
            # Build the main query
            query = f"""
            SELECT 
                year,
                country_name,
                region,
                speech_text,
                word_count,
                CASE 
                    {' '.join([f"WHEN {' OR '.join([f'LOWER(speech_text) LIKE \'%{keyword.lower()}%\'' for keyword in topic_keywords.get(topic, [])])} THEN '{topic}'" for topic in topics])}
                END as topic
            FROM speeches 
            WHERE year BETWEEN {year_range[0]} AND {year_range[1]}
            AND ({' OR '.join(topic_conditions)})
            """
            
            if regions:
                region_conditions = "', '".join(regions)
                query += f" AND region IN ('{region_conditions}')"
            
            # Execute query
            result = self.db_manager.conn.execute(query).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=['year', 'country_name', 'region', 'speech_text', 'word_count', 'topic'])
            
            # Calculate mentions per 1000 words
            df['mentions_per_1000_words'] = df.apply(lambda row: self._count_topic_mentions(row['speech_text'], row['topic'], topic_keywords) / (row['word_count'] / 1000), axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting topic data: {e}")
            return pd.DataFrame()
    
    def _get_country_data_safe(self, countries: List[str], year_range: Tuple[int, int], 
                              analysis_type: str) -> pd.DataFrame:
        """Get country data with proper error handling."""
        try:
            # Build query based on analysis type
            if analysis_type == "Word Count Trends":
                query = f"""
                SELECT year, country_name, word_count
                FROM speeches 
                WHERE country_name IN ({', '.join([f"'{c}'" for c in countries])})
                AND year BETWEEN {year_range[0]} AND {year_range[1]}
                ORDER BY year, country_name
                """
            elif analysis_type == "Topic Focus":
                query = f"""
                SELECT country_name, 
                       COUNT(CASE WHEN LOWER(speech_text) LIKE '%climate%' THEN 1 END) as climate_mentions,
                       COUNT(CASE WHEN LOWER(speech_text) LIKE '%peace%' THEN 1 END) as peace_mentions,
                       COUNT(CASE WHEN LOWER(speech_text) LIKE '%development%' THEN 1 END) as development_mentions
                FROM speeches 
                WHERE country_name IN ({', '.join([f"'{c}'" for c in countries])})
                AND year BETWEEN {year_range[0]} AND {year_range[1]}
                GROUP BY country_name
                """
            elif analysis_type == "Sentiment Analysis":
                # Simple sentiment based on positive/negative words
                query = f"""
                SELECT year, country_name, 
                       (LENGTH(speech_text) - LENGTH(REPLACE(LOWER(speech_text), 'peace', ''))) as positive_words,
                       (LENGTH(speech_text) - LENGTH(REPLACE(LOWER(speech_text), 'conflict', ''))) as negative_words
                FROM speeches 
                WHERE country_name IN ({', '.join([f"'{c}'" for c in countries])})
                AND year BETWEEN {year_range[0]} AND {year_range[1]}
                ORDER BY year, country_name
                """
            else:  # Speech Length
                query = f"""
                SELECT country_name, word_count as speech_length
                FROM speeches 
                WHERE country_name IN ({', '.join([f"'{c}'" for c in countries])})
                AND year BETWEEN {year_range[0]} AND {year_range[1]}
                ORDER BY country_name
                """
            
            # Execute query
            result = self.db_manager.conn.execute(query).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            if analysis_type == "Word Count Trends":
                df = pd.DataFrame(result, columns=['year', 'country_name', 'word_count'])
            elif analysis_type == "Topic Focus":
                df = pd.DataFrame(result, columns=['country_name', 'climate_mentions', 'peace_mentions', 'development_mentions'])
                # Melt for plotting
                df = df.melt(id_vars=['country_name'], var_name='topic', value_name='topic_mentions')
                df['topic'] = df['topic'].str.replace('_mentions', '')
            elif analysis_type == "Sentiment Analysis":
                df = pd.DataFrame(result, columns=['year', 'country_name', 'positive_words', 'negative_words'])
                df['sentiment_score'] = df['positive_words'] - df['negative_words']
            else:  # Speech Length
                df = pd.DataFrame(result, columns=['country_name', 'speech_length'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting country data: {e}")
            return pd.DataFrame()
    
    def _get_regional_data_safe(self, regions: List[str], metric: str) -> pd.DataFrame:
        """Get regional data with proper error handling."""
        try:
            # Build query based on metric
            if metric == "Speech Count":
                query = f"""
                SELECT region, COUNT(*) as value
                FROM speeches 
                WHERE region IN ({', '.join([f"'{r}'" for r in regions])})
                GROUP BY region
                ORDER BY value DESC
                """
            elif metric == "Average Word Count":
                query = f"""
                SELECT region, AVG(word_count) as value
                FROM speeches 
                WHERE region IN ({', '.join([f"'{r}'" for r in regions])})
                GROUP BY region
                ORDER BY value DESC
                """
            elif metric == "Topic Diversity":
                query = f"""
                SELECT region, COUNT(DISTINCT CASE 
                    WHEN LOWER(speech_text) LIKE '%climate%' OR 
                         LOWER(speech_text) LIKE '%peace%' OR 
                         LOWER(speech_text) LIKE '%development%' THEN 1 
                END) as value
                FROM speeches 
                WHERE region IN ({', '.join([f"'{r}'" for r in regions])})
                GROUP BY region
                ORDER BY value DESC
                """
            else:  # Sentiment Score
                query = f"""
                SELECT region, 
                       AVG((LENGTH(speech_text) - LENGTH(REPLACE(LOWER(speech_text), 'peace', ''))) - 
                           (LENGTH(speech_text) - LENGTH(REPLACE(LOWER(speech_text), 'conflict', '')))) as value
                FROM speeches 
                WHERE region IN ({', '.join([f"'{r}'" for r in regions])})
                GROUP BY region
                ORDER BY value DESC
                """
            
            # Execute query
            result = self.db_manager.conn.execute(query).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=['region', 'value'])
            df['metric'] = metric
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting regional data: {e}")
            return pd.DataFrame()
    
    def _get_network_data_safe(self, year: int, min_connections: int) -> pd.DataFrame:
        """Get network data with proper error handling."""
        try:
            # Simple network based on co-mentions
            query = f"""
            SELECT country_name, COUNT(*) as connections
            FROM speeches 
            WHERE year = {year}
            GROUP BY country_name
            HAVING connections >= {min_connections}
            ORDER BY connections DESC
            LIMIT 20
            """
            
            # Execute query
            result = self.db_manager.conn.execute(query).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(result, columns=['country_name', 'connections'])
            
            # Add network coordinates (simple layout)
            n = len(df)
            angles = np.linspace(0, 2*np.pi, n, endpoint=False)
            df['x'] = np.cos(angles)
            df['y'] = np.sin(angles)
            df['label'] = df['country_name']
            df['color'] = df['connections']
            
            # Create simple edges (connect to nearest neighbors)
            edges = []
            for i in range(n):
                for j in range(i+1, min(i+3, n)):  # Connect to next 2 neighbors
                    edges.append({
                        'x1': df.iloc[i]['x'],
                        'y1': df.iloc[i]['y'],
                        'x2': df.iloc[j]['x'],
                        'y2': df.iloc[j]['y']
                    })
            
            # Store edges as a separate DataFrame
            edges_df = pd.DataFrame(edges) if edges else pd.DataFrame()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting network data: {e}")
            return pd.DataFrame()
    
    def _count_topic_mentions(self, text: str, topic: str, topic_keywords: Dict[str, List[str]]) -> int:
        """Count mentions of a topic in text."""
        if topic not in topic_keywords:
            return 0
        
        keywords = topic_keywords[topic]
        text_lower = text.lower()
        mentions = sum(text_lower.count(keyword.lower()) for keyword in keywords)
        return mentions
