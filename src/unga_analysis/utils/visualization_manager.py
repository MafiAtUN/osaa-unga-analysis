"""
Main visualization manager for UNGA Analysis.
Simplified interface that imports from specialized modules.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

# Import from specialized modules
from .chart_helpers import (
    create_methodology_tooltip, 
    add_methodology_section,
    get_color_palette,
    create_theme_colors,
    format_number,
    create_plotly_layout,
    add_watermark
)

from .trend_visualizations import (
    create_trend_analysis_chart,
    create_cross_year_comparison,
    create_temporal_heatmap,
    create_trend_decomposition
)

from .geographic_visualizations import (
    create_geographic_distribution,
    create_regional_analysis,
    create_africa_vs_development_chart,
    create_country_ranking,
    create_geographic_heatmap
)

logger = logging.getLogger(__name__)

class UNGAVisualizationManager:
    """Main visualization manager for UNGA Analysis."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.colors = create_theme_colors()
    
    def render_visualization_menu(self):
        """Render the main visualization menu."""
        st.header("📊 Advanced Visualizations")
        st.markdown("**Interactive visualizations for UNGA speech analysis and exploration**")
        
        # Visualization options
        viz_options = [
            "📈 Trend Analysis",
            "🌍 Geographic Distribution", 
            "🔄 Cross-Year Comparison",
            "📊 Regional Analysis",
            "🏆 Country Rankings",
            "🌡️ Temporal Heatmap"
        ]
        
        selected_viz = st.selectbox(
            "Choose Visualization Type:",
            viz_options,
            key="viz_type_select"
        )
        
        if selected_viz == "📈 Trend Analysis":
            self._render_trend_analysis()
        elif selected_viz == "🌍 Geographic Distribution":
            self._render_geographic_distribution()
        elif selected_viz == "🔄 Cross-Year Comparison":
            self._render_cross_year_comparison()
        elif selected_viz == "📊 Regional Analysis":
            self._render_regional_analysis()
        elif selected_viz == "🏆 Country Rankings":
            self._render_country_rankings()
        elif selected_viz == "🌡️ Temporal Heatmap":
            self._render_temporal_heatmap()
    
    def _render_trend_analysis(self):
        """Render trend analysis visualizations."""
        st.subheader("📈 Trend Analysis")
        
        # Get data
        try:
            data = self._get_analysis_data()
            if data.empty:
                st.warning("No data available for trend analysis")
                return
            
            # Create trend chart
            fig = create_trend_analysis_chart(
                data, 'year', 'word_count', 
                "Speech Volume Trends Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating trend analysis: {e}")
    
    def _render_geographic_distribution(self):
        """Render geographic distribution visualizations."""
        st.subheader("🌍 Geographic Distribution")
        
        try:
            data = self._get_analysis_data()
            if data.empty:
                st.warning("No data available for geographic analysis")
                return
            
            # Create geographic chart
            fig = create_geographic_distribution(
                data, 'word_count',
                "Speech Volume by Country"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating geographic distribution: {e}")
    
    def _render_cross_year_comparison(self):
        """Render cross-year comparison visualizations."""
        st.subheader("🔄 Cross-Year Comparison")
        
        # Country selection
        countries = st.multiselect(
            "Select Countries:",
            options=self._get_available_countries(),
            default=self._get_available_countries()[:5],
            key="cross_year_countries"
        )
        
        # Year selection
        years = st.multiselect(
            "Select Years:",
            options=self._get_available_years(),
            default=self._get_available_years()[-5:],
            key="cross_year_years"
        )
        
        if countries and years:
            try:
                data = self._get_analysis_data()
                filtered_data = data[
                    (data['country_name'].isin(countries)) & 
                    (data['year'].isin(years))
                ]
                
                if not filtered_data.empty:
                    fig = create_cross_year_comparison(
                        filtered_data, countries, years, 'word_count'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for selected criteria")
                    
            except Exception as e:
                st.error(f"Error creating cross-year comparison: {e}")
    
    def _render_regional_analysis(self):
        """Render regional analysis visualizations."""
        st.subheader("📊 Regional Analysis")
        
        try:
            data = self._get_analysis_data()
            if data.empty:
                st.warning("No data available for regional analysis")
                return
            
            # Define regions
            regions = {
                "Africa": self._get_african_countries(),
                "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain"],
                "Asia": ["China", "India", "Japan", "South Korea", "Indonesia"],
                "Americas": ["United States", "Brazil", "Canada", "Mexico", "Argentina"]
            }
            
            fig = create_regional_analysis(data, regions, 'word_count')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating regional analysis: {e}")
    
    def _render_country_rankings(self):
        """Render country ranking visualizations."""
        st.subheader("🏆 Country Rankings")
        
        top_n = st.slider("Number of Top Countries:", 5, 25, 15)
        
        try:
            data = self._get_analysis_data()
            if data.empty:
                st.warning("No data available for country rankings")
                return
            
            fig = create_country_ranking(data, 'word_count', top_n)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating country rankings: {e}")
    
    def _render_temporal_heatmap(self):
        """Render temporal heatmap visualizations."""
        st.subheader("🌡️ Temporal Heatmap")
        
        # Country selection
        countries = st.multiselect(
            "Select Countries:",
            options=self._get_available_countries(),
            default=self._get_available_countries()[:10],
            key="heatmap_countries"
        )
        
        # Year selection
        years = st.multiselect(
            "Select Years:",
            options=self._get_available_years(),
            default=self._get_available_years()[-10:],
            key="heatmap_years"
        )
        
        if countries and years:
            try:
                data = self._get_analysis_data()
                filtered_data = data[
                    (data['country_name'].isin(countries)) & 
                    (data['year'].isin(years))
                ]
                
                if not filtered_data.empty:
                    fig = create_temporal_heatmap(
                        filtered_data, countries, years, 'word_count'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for selected criteria")
                    
            except Exception as e:
                st.error(f"Error creating temporal heatmap: {e}")
    
    def _get_analysis_data(self) -> pd.DataFrame:
        """Get analysis data from database."""
        try:
            # Get speeches data
            results = self.db_manager.search_speeches(limit=1000)
            if not results:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = pd.DataFrame(results)
            return data
            
        except Exception as e:
            logger.error(f"Error getting analysis data: {e}")
            return pd.DataFrame()
    
    def _get_available_countries(self) -> List[str]:
        """Get available countries from database."""
        try:
            from .country_manager import country_manager
            return country_manager.get_all_countries()
        except:
            return ["United States", "China", "Germany", "France", "United Kingdom"]
    
    def _get_available_years(self) -> List[int]:
        """Get available years from database."""
        try:
            # Get years from database
            cursor = self.db_manager.conn.execute("SELECT DISTINCT year FROM speeches ORDER BY year")
            years = [row[0] for row in cursor.fetchall()]
            return years
        except:
            return list(range(2020, 2025))
    
    def _get_african_countries(self) -> List[str]:
        """Get African countries list."""
        try:
            from .country_manager import country_manager
            return country_manager.get_african_countries()
        except:
            return ["Nigeria", "South Africa", "Kenya", "Ghana", "Ethiopia"]
