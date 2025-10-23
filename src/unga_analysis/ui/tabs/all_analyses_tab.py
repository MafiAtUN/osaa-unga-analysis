"""
All Analyses Tab
Displays all previous analyses with filtering and search capabilities
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from ...utils.sdg_utils import format_sdgs
from ...data.simple_vector_storage import simple_vector_storage as db_manager


def render_all_analyses_tab():
    """Render the All Analyses tab."""
    st.header("📚 All Analyses")
    st.markdown("**View and manage all previous speech analyses**")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        country_filter = st.text_input("Filter by Country", placeholder="Enter country name")
    
    with col2:
        classification_filter = st.selectbox(
            "Filter by Classification",
            ["All", "African Member State", "Development Partner"],
            key="all_analyses_classification_filter"
        )
    
    with col3:
        africa_filter = st.selectbox(
            "Africa Mentioned (Partners only)",
            ["All", "Yes", "No"],
            key="all_analyses_africa_filter"
        )
    
    with col4:
        search_text = st.text_input("Search in content", placeholder="Search text")
    
    # Build filters
    filters = {}
    if country_filter:
        filters['country'] = country_filter
    if classification_filter != "All":
        filters['classification'] = classification_filter
    if africa_filter != "All":
        filters['africa_mentioned'] = africa_filter == "Yes"
    if search_text:
        filters['search_text'] = search_text
    
    # Get analyses
    try:
        analyses = db_manager.list_analyses(filters)
        
        if analyses:
            st.subheader(f"Found {len(analyses)} analyses")
            
            # Display analyses in a table
            for analysis in analyses:
                with st.expander(f"📄 {analysis['country']} - {analysis['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Classification:** {analysis['classification']}")
                        st.write(f"**SDGs:** {format_sdgs(analysis['sdgs'])}")
                        if analysis['africa_mentioned'] is not None:
                            africa_status = "✅ Yes" if analysis['africa_mentioned'] else "❌ No"
                            st.write(f"**Africa Mentioned:** {africa_status}")
                    
                    with col2:
                        st.write(f"**Date:** {analysis['speech_date']}")
                        st.write(f"**Source:** {analysis['source_filename']}")
                        st.write(f"**Created:** {analysis['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col3:
                        # Action buttons
                        if st.button("📄 View Analysis", key=f"view_{analysis['id']}"):
                            st.session_state.selected_analysis = analysis['id']
                            st.rerun()
                        
                        if st.button("📥 Download", key=f"download_{analysis['id']}"):
                            # Download functionality would be implemented here
                            st.info("Download functionality would be implemented here")
                        
                        if st.button("🗑️ Delete", key=f"delete_{analysis['id']}"):
                            if db_manager.delete_analysis(analysis['id']):
                                st.success("Analysis deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete analysis")
                    
                    # Show analysis content if selected
                    if st.session_state.get('selected_analysis') == analysis['id']:
                        st.markdown("---")
                        st.markdown("### Analysis Content")
                        st.markdown(analysis['output_markdown'])
        else:
            st.info("📊 No analyses found. Create your first analysis in the 'New Analysis' tab.")
            
    except Exception as e:
        st.error(f"Error loading analyses: {e}")
        st.info("This might be because the database is not properly initialized.")
