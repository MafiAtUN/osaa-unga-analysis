"""
Data Explorer tab for visualizing UNGA speech data availability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Any
from src.unga_analysis.data.cross_year_analysis import cross_year_manager


def perform_speech_search(years=None, regions=None, country_search=None, au_members_only=False, query_text=None):
    """Perform a search for speeches based on criteria using semantic search."""
    try:
        # Use cross-year manager for semantic search
        search_results = cross_year_manager.search_speeches_by_criteria(
            query_text=query_text,
            countries=[country_search] if country_search else None,
            years=years,
            regions=regions,
            african_members_only=au_members_only,
            use_semantic_search=bool(query_text)  # Use semantic search if query provided
        )
        
        # Convert to expected format for compatibility
        results = []
        for speech in search_results:
                results.append({
                'country': speech.get('country_name', ''),
                'region': speech.get('region', ''),
                'year': speech.get('year', 0),
                'word_count': speech.get('word_count', 0),
                'is_african_member': speech.get('is_african_member', False),
                'session': speech.get('session', ''),
                'similarity': speech.get('similarity', 0),
                'speech_text': speech.get('speech_text', ''),
                'id': speech.get('id', 0)
                })
        
        return results
        
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []


def display_search_results(results):
    """Display search results in a clean table format."""
    if not results:
        st.info("No results found.")
        return
    
    # Create DataFrame for display
    df = pd.DataFrame(results)
    
    # Format the display
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "country": "Country",
            "region": "Region", 
            "year": "Year",
            "word_count": st.column_config.NumberColumn("Word Count", format="%d"),
            "is_african_member": "AU Member",
            "session": "Session"
        }
    )
    
    # Show summary
    st.info(f"Found {len(results)} speeches matching your criteria.")


def create_availability_heatmap(results, selected_years):
    """Create a heatmap showing speech availability."""
    if not results or not selected_years:
        return
    
    try:
        # Create a pivot table for the heatmap
        df = pd.DataFrame(results)
        pivot_data = df.pivot_table(
            values='word_count',
            index='country',
            columns='year',
            fill_value=0,
            aggfunc='sum'
        )
        
        # Create heatmap
        fig = px.imshow(
            pivot_data,
            title="Speech Availability Heatmap",
            labels=dict(x="Year", y="Country", color="Word Count"),
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            height=max(400, len(pivot_data.index) * 20),
            xaxis_title="Year",
            yaxis_title="Country"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Could not create heatmap: {e}")


def get_available_countries():
    """Get list of all available countries from the database."""
    try:
        # Get all speeches to extract unique countries
        all_speeches = cross_year_manager.db_manager.search_speeches(limit=10000)
        countries = list(set([speech.get('country_name', 'Unknown') for speech in all_speeches if speech.get('country_name')]))
        return sorted(countries)
    except Exception as e:
        st.error(f"Error getting countries: {e}")
        return []


def get_availability_data(countries, year_range):
    """Get data availability for selected countries and year range."""
    try:
        start_year, end_year = year_range
        years = list(range(start_year, end_year + 1))
        
        # Get all speeches for the selected countries and years
        all_speeches = cross_year_manager.db_manager.search_speeches(
            countries=countries,
            years=years,
            limit=10000
        )
        
        # Create availability matrix
        availability_data = []
        
        for country in countries:
            country_data = {'Country': country}
            
            # Get speeches for this country
            country_speeches = [s for s in all_speeches if s.get('country_name') == country]
            country_years = set([s.get('year') for s in country_speeches])
            
            for year in years:
                # 1 if speech exists, 0 if not
                country_data[year] = 1 if year in country_years else 0
            
            availability_data.append(country_data)
        
        return availability_data
        
    except Exception as e:
        st.error(f"Error getting availability data: {e}")
        return []


def display_availability_chart(availability_data, year_range):
    """Display the availability chart as a heatmap."""
    st.subheader("📊 Data Availability Heatmap")
    
    # Convert to DataFrame
    df = pd.DataFrame(availability_data)
    df = df.set_index('Country')
    
    # Create the heatmap
    fig = px.imshow(
        df,
        labels=dict(x="Year", y="Country", color="Data Available"),
        color_continuous_scale=['#ff4444', '#44ff44'],  # Red to Green
        aspect="auto",
        title=f"Speech Data Availability ({year_range[0]}-{year_range[1]})"
    )
    
    # Customize the layout
    fig.update_layout(
        height=max(400, len(availability_data) * 30),  # Dynamic height based on number of countries
        xaxis_title="Year",
        yaxis_title="Country",
        coloraxis_colorbar=dict(
            title="Data Available",
            tickvals=[0, 1],
            ticktext=["Not Available", "Available"]
        )
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Year: %{x}<br>Available: %{z}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add legend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🟢 **Green**: Speech data available")
    with col2:
        st.markdown("🔴 **Red**: No speech data")


def display_availability_stats(availability_data):
    """Display statistics about data availability."""
    st.subheader("📈 Availability Statistics")
    
    # Calculate statistics
    total_cells = len(availability_data) * (len(availability_data[0]) - 1)  # -1 for Country column
    available_cells = sum(sum(row[year] for year in row.keys() if year != 'Country') for row in availability_data)
    availability_percentage = (available_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Country-wise statistics
    country_stats = []
    for row in availability_data:
        country = row['Country']
        years_data = {k: v for k, v in row.items() if k != 'Country'}
        available_years = sum(years_data.values())
        total_years = len(years_data)
        percentage = (available_years / total_years * 100) if total_years > 0 else 0
        
        country_stats.append({
            'Country': country,
            'Available Years': available_years,
            'Total Years': total_years,
            'Percentage': f"{percentage:.1f}%"
        })
    
    # Display overall stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Overall Availability", f"{availability_percentage:.1f}%")
    with col2:
        st.metric("✅ Available Data Points", f"{available_cells:,}")
    with col3:
        st.metric("📅 Total Data Points", f"{total_cells:,}")
    
    # Display country-wise stats
    st.markdown("#### 📋 Country-wise Statistics")
    stats_df = pd.DataFrame(country_stats)
    st.dataframe(
        stats_df,
        use_container_width=True,
        column_config={
            "Percentage": st.column_config.TextColumn(
                "Availability %",
                help="Percentage of years with available data"
            )
        }
    )
    
    # Show countries with best and worst availability
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Best Coverage")
        best_countries = sorted(country_stats, key=lambda x: float(x['Percentage'].replace('%', '')), reverse=True)[:5]
        for i, country in enumerate(best_countries, 1):
            st.markdown(f"{i}. **{country['Country']}** - {country['Percentage']}")
    
    with col2:
        st.markdown("#### 📉 Needs More Data")
        worst_countries = sorted(country_stats, key=lambda x: float(x['Percentage'].replace('%', '')))[:5]
        for i, country in enumerate(worst_countries, 1):
            st.markdown(f"{i}. **{country['Country']}** - {country['Percentage']}")


def render_data_explorer_tab():
    """Render the data availability explorer tab."""
    st.header("📊 Data Availability Explorer")
    st.markdown("**Visualize speech data availability by country and year**")
    
    # Get data summary
    data_summary = cross_year_manager.get_data_summary()
    
    if not data_summary:
        st.info("📊 No data available yet. Upload speech files to see visualizations.")
        return
    
    # Quick stats at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🗣️ Total Countries", data_summary.get('total_countries', 0))
    with col2:
        st.metric("📝 Total Speeches", data_summary.get('total_speeches', 0))
    with col3:
        st.metric("📅 Available Years", data_summary.get('total_years', 0))
    with col4:
        # Count AU members from all years
        au_count = 0
        for year_stats in data_summary.get('year_statistics', {}).values():
            if isinstance(year_stats, dict) and 'au_members' in year_stats:
                au_count += year_stats['au_members']
        st.metric("🇦🇺 AU Members", au_count)
    
    st.markdown("---")
    
    # Year Range Selection
    st.subheader("📅 Select Year Range")
    
    available_years = sorted(data_summary.get('available_years', []))
    if not available_years:
        st.warning("No years available in the dataset.")
        return
    
    # Year range slider
    min_year = min(available_years)
    max_year = max(available_years)
    
    year_range = st.slider(
        "Select year range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        format="%d"
    )
    
    # Country Selection
    st.subheader("🏳️ Select Countries")
    
    # Get all available countries
    all_countries = get_available_countries()
    
    if not all_countries:
        st.warning("No countries available in the dataset.")
        return
    
    # Multi-select for countries
    selected_countries = st.multiselect(
        "Choose countries to visualize:",
        options=all_countries,
        default=all_countries[:10] if len(all_countries) > 10 else all_countries,  # Default to first 10
        help="Select multiple countries to see their data availability"
    )
    
    if not selected_countries:
        st.warning("Please select at least one country.")
        return
    
    # Generate and display availability data
    if st.button("📊 Generate Availability Chart", type="primary"):
        with st.spinner("Generating availability data..."):
            availability_data = get_availability_data(selected_countries, year_range)
            
            if availability_data:
                display_availability_chart(availability_data, year_range)
                display_availability_stats(availability_data)
            else:
                st.warning("No data found for the selected criteria.")
