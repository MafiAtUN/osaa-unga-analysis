"""
SDG Analysis Tab Module
Comprehensive SDG (Sustainable Development Goals) tracking and analysis across UNGA speeches.
Creative features for tracking SDG discourse, trends, and country commitments.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
import numpy as np

from ...data.simple_vector_storage import simple_vector_storage as db_manager
from ...data.data_ingestion import (
    get_country_region_lookup,
    get_all_region_labels,
)
from ...utils.region_utils import (
    extract_regions_and_countries,
)
from ...core.llm import run_analysis, get_available_models
from ...core.openai_client import get_openai_client
from ...utils.sdg_visualizations import SDG_KEYWORDS

# Official SDG Colors and Icons
SDG_INFO = {
    "SDG 1: No Poverty": {"color": "#E5243B", "icon": "🏚️"},
    "SDG 2: Zero Hunger": {"color": "#DDA63A", "icon": "🌾"},
    "SDG 3: Good Health": {"color": "#4C9F38", "icon": "⚕️"},
    "SDG 4: Quality Education": {"color": "#C5192D", "icon": "📚"},
    "SDG 5: Gender Equality": {"color": "#FF3A21", "icon": "⚖️"},
    "SDG 6: Clean Water": {"color": "#26BDE2", "icon": "💧"},
    "SDG 7: Clean Energy": {"color": "#FCC30B", "icon": "⚡"},
    "SDG 8: Decent Work": {"color": "#A21942", "icon": "💼"},
    "SDG 9: Industry & Innovation": {"color": "#FD6925", "icon": "🏭"},
    "SDG 10: Reduced Inequalities": {"color": "#DD1367", "icon": "⚖️"},
    "SDG 11: Sustainable Cities": {"color": "#FD9D24", "icon": "🏙️"},
    "SDG 12: Responsible Consumption": {"color": "#BF8B2E", "icon": "♻️"},
    "SDG 13: Climate Action": {"color": "#3F7E44", "icon": "🌍"},
    "SDG 14: Life Below Water": {"color": "#0A97D9", "icon": "🌊"},
    "SDG 15: Life on Land": {"color": "#56C02B", "icon": "🌳"},
    "SDG 16: Peace & Justice": {"color": "#00689D", "icon": "🕊️"},
    "SDG 17: Partnerships": {"color": "#19486A", "icon": "🤝"}
}


def get_sdg_analysis_questions() -> Dict[str, List[str]]:
    """Get SDG-specific analysis questions organized by category."""
    return {
        "📈 SDG Trend Tracking": [
            "How has attention to SDGs evolved from 2015 (when they were launched) to 2025?",
            "Which SDGs have seen the biggest increase in mentions since 2015?",
            "Compare SDG 13 (Climate Action) mentions in 2015 vs 2024.",
            "Which SDGs are mentioned most frequently by African countries?",
            "Track the evolution of SDG 5 (Gender Equality) discourse from 2015-2025.",
            "Which decade shows the most balanced SDG coverage across all 17 goals?",
            "How did COVID-19 impact SDG 3 (Good Health) mentions in speeches?",
            "Compare SDG prioritization before and after the 2030 Agenda adoption.",
            "Which SDGs show declining attention over time?",
            "What's the trend for SDG 17 (Partnerships) across regions?"
        ],
        
        "🌍 Country & Regional SDG Focus": [
            "Which countries mention SDG 13 (Climate Action) most frequently?",
            "Compare SDG priorities between developed and developing countries.",
            "What are the top 5 SDGs for African Member States vs Development Partners?",
            "Which small island states focus most on SDG 14 (Life Below Water)?",
            "How do G7 countries prioritize SDGs differently from G77?",
            "Which countries mention the most SDGs in their speeches?",
            "Compare SDG 4 (Education) focus between Asian and Latin American countries.",
            "What SDGs do Least Developed Countries (LDCs) emphasize most?",
            "Which region shows the highest SDG discourse integration?",
            "How do African countries' SDG priorities differ from each other?"
        ],
        
        "🔗 SDG Interconnections": [
            "Which SDGs are most commonly mentioned together in speeches?",
            "Analyze the relationship between SDG 1 (No Poverty) and SDG 8 (Decent Work).",
            "How do countries link SDG 13 (Climate) with SDG 7 (Energy)?",
            "Which SDG pairs show the strongest correlation in speeches?",
            "Examine connections between SDG 5 (Gender) and SDG 4 (Education).",
            "How are SDG 14 (Oceans) and SDG 15 (Land) discussed together?",
            "Which countries mention multiple SDGs in integrated ways?",
            "Track how SDG interconnections have evolved over time.",
            "What's the relationship between SDG 16 (Peace) and development SDGs?",
            "Analyze SDG 17 (Partnerships) as a cross-cutting theme."
        ],
        
        "📊 SDG Progress & Commitments": [
            "Which countries have made the strongest commitments to SDG 13 (Climate)?",
            "Track mentions of 'SDG implementation' vs 'SDG achievement' over time.",
            "Compare SDG commitment language between 2015 and 2024.",
            "Which regions emphasize SDG accountability and monitoring most?",
            "How do countries discuss SDG financing and resources?",
            "Which SDGs receive the most concrete action commitments?",
            "Track the evolution of SDG reporting and review mechanisms.",
            "Compare pledges vs actual SDG discourse patterns.",
            "Which countries link SDGs to national development plans?",
            "Analyze how SDG 'leave no one behind' appears in speeches."
        ],
        
        "🎯 Custom SDG Analysis": [
            "Analyze how a specific country discusses SDGs over time.",
            "Compare how different regions interpret SDG targets.",
            "Which SDGs are mentioned in connection with specific global events?",
            "How do annual SDG themes correspond to speech content?",
            "Track SDG mentions in relation to UN conferences and summits.",
            "Which countries show the most comprehensive SDG integration?",
            "Analyze SDG discourse quality and depth vs quantity.",
            "How do development partners discuss SDG support?",
            "Compare SDG priorities in pre-COVID vs post-COVID speeches.",
            "Which SDGs need more attention based on current discourse?"
        ]
    }


def get_sdg_data(year_range: tuple = (2015, 2025), countries: Optional[List[str]] = None, regions: Optional[List[str]] = None) -> pd.DataFrame:
    """Get SDG-related speech data from database."""
    try:
        countries = countries or []
        regions = regions or []

        country_region_lookup = get_country_region_lookup()

        selected_countries: Set[str] = set(countries)

        if regions:
            for country_name, labels in country_region_lookup.items():
                if any(region in labels for region in regions):
                    selected_countries.add(country_name)

        where_conditions = ["year >= ?", "year <= ?", "speech_text IS NOT NULL"]
        params = [year_range[0], year_range[1]]
        
        if selected_countries:
            placeholders = ','.join(['?' for _ in selected_countries])
            where_conditions.append(f"country_name IN ({placeholders})")
            params.extend(sorted(selected_countries))
        
        query = f"""
            SELECT country_name, year, speech_text, region, word_count
            FROM speeches
            WHERE {' AND '.join(where_conditions)}
            ORDER BY year DESC, country_name
        """
        
        results = db_manager.conn.execute(query, params).fetchall()
        
        data = []
        for row in results:
            country, year, text, region, word_count = row
            if text:
                # Count SDG mentions for each goal
                sdg_counts = {}
                for sdg_name, sdg_data in SDG_KEYWORDS.items():
                    keywords = sdg_data["keywords"]
                    count = sum(1 for keyword in keywords if keyword.lower() in text.lower())
                    sdg_counts[sdg_name] = count
                
                regions_for_country = country_region_lookup.get(country, [])
                primary_region = regions_for_country[0] if regions_for_country else (region or 'Unknown')
                data.append({
                    'country': country,
                    'year': year,
                    'region': primary_region,
                    'regions': regions_for_country,
                    'word_count': word_count or 0,
                    **sdg_counts
                })

        df = pd.DataFrame(data)

        if not df.empty and regions:
            df = df[df['regions'].apply(lambda labels: any(region in labels for region in regions))]
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching SDG data: {e}")
        return pd.DataFrame()


def render_sdg_analysis_tab():
    """Main function to render the SDG Analysis tab."""
    st.header("🌍 SDG Analysis Dashboard")
    st.markdown("**Track Sustainable Development Goals discourse across UNGA speeches (2015-2025) • 17 Goals • 2030 Agenda Progress**")
    
    # SDG Overview Banner
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Years Analyzed", "2015-2025")
    with col2:
        st.metric("🎯 SDGs Tracked", "17 Goals")
    with col3:
        st.metric("🌍 Countries", "200+")
    with col4:
        st.metric("📊 Data Points", "5,000+")
    
    st.markdown("---")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Quick SDG Analysis",
        "📈 Advanced SDG Trends",
        "🌍 Country SDG Profiles",
        "🔍 Custom SDG Query"
    ])
    
    with tab1:
        render_quick_sdg_analysis()
    
    with tab2:
        render_advanced_sdg_trends()
    
    with tab3:
        render_country_sdg_profiles()
    
    with tab4:
        render_custom_sdg_query()


def render_quick_sdg_analysis():
    """Quick analysis interface with predefined questions."""
    st.subheader("🎯 Quick SDG Analysis")
    
    st.info("💡 Select a question category and specific question to analyze SDG trends, country focus, and progress commitments.")
    
    # Step 1: Question Category
    questions_dict = get_sdg_analysis_questions()
    category = st.selectbox(
        "📋 Select Question Category:",
        options=list(questions_dict.keys()),
        key="sdg_quick_category"
    )
    
    # Step 2: Specific Question
    if category:
        selected_question = st.selectbox(
            "❓ Choose Question:",
            options=questions_dict[category],
            key="sdg_quick_question"
        )
        
        # Step 3: Analysis Options
        col1, col2 = st.columns(2)
        with col1:
            year_range = st.slider(
                "📅 Year Range:",
                2015, 2025, (2015, 2025),
                key="sdg_quick_years"
            )
        
        with col2:
            regions_filter = st.multiselect(
                "🌍 Regions:",
                [label for label in get_all_region_labels() if label and label != "Unknown"],
                key="sdg_quick_regions",
                help="Choose any region grouping (including sub-regions) to focus the analysis."
            )
        
        # Step 4: Analyze Button
        if st.button("🔍 Analyze SDGs", type="primary", use_container_width=True, key="sdg_quick_analyze"):
            if selected_question:
                with st.spinner("🔍 Analyzing SDG discourse..."):
                    perform_sdg_analysis(selected_question, year_range, regions_filter)


def render_advanced_sdg_trends():
    """Advanced trend visualization interface."""
    st.subheader("📈 Advanced SDG Trends")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_sdgs = st.multiselect(
            "🎯 Select SDGs to Compare:",
            options=list(SDG_INFO.keys()),
            default=["SDG 13: Climate Action", "SDG 5: Gender Equality", "SDG 1: No Poverty"],
            key="sdg_advanced_selection"
        )
    
    with col2:
        year_range = st.slider(
            "📅 Year Range:",
            2015, 2025, (2015, 2025),
            key="sdg_advanced_years"
        )

    with col3:
        regions_filter = st.multiselect(
            "🌍 Regions:",
            [label for label in get_all_region_labels() if label and label != "Unknown"],
            key="sdg_advanced_regions",
            help="Optional: restrict the visualization to selected regions."
        )
    
    if selected_sdgs and st.button("📊 Generate Trend Analysis", type="primary", key="sdg_advanced_generate"):
        with st.spinner("Generating SDG trend visualizations..."):
            create_sdg_trend_visualizations(selected_sdgs, year_range, regions_filter)


def render_country_sdg_profiles():
    """Country-specific SDG profile analysis."""
    st.subheader("🌍 Country SDG Profiles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get available countries
        countries_query = db_manager.conn.execute(
            "SELECT DISTINCT country_name FROM speeches ORDER BY country_name"
        ).fetchall()
        available_countries = [c[0] for c in countries_query]
        
        # Set default countries only if they exist in the list
        default_countries = []
        for country in ["Kenya", "Nigeria", "South Africa"]:
            if country in available_countries[:100]:
                default_countries.append(country)
        
        selected_countries = st.multiselect(
            "🌍 Select Countries:",
            options=available_countries[:100],  # Limit for performance
            default=default_countries,
            key="sdg_country_selection"
        )
    
    with col2:
        year_range = st.slider(
            "📅 Year Range:",
            2015, 2025, (2015, 2025),
            key="sdg_country_years"
        )
    
    if selected_countries and st.button("📊 Generate Country Profiles", type="primary", key="sdg_country_analyze"):
        with st.spinner("Analyzing country SDG profiles..."):
            create_country_sdg_profiles(selected_countries, year_range)


def render_custom_sdg_query():
    """Custom SDG analysis with AI."""
    st.subheader("🔍 Custom SDG Query")
    
    st.info("💡 Ask any question about SDGs in UNGA speeches. Use AI-powered analysis with visualizations.")
    
    # Custom prompt
    custom_prompt = st.text_area(
        "Ask your SDG question:",
        placeholder="e.g., 'How has SDG 13 (Climate Action) been discussed by African countries compared to European countries from 2015-2024?'",
        height=150,
        key="sdg_custom_prompt"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        year_range = st.slider(
            "📅 Year Range:",
            2015, 2025, (2015, 2025),
            key="sdg_custom_years"
        )
    
    with col2:
        model = st.selectbox(
            "🤖 AI Model:",
            options=get_available_models() or ["model-router"],
            key="sdg_custom_model"
        )

    regions_filter = st.multiselect(
        "🌍 Regions:",
        [label for label in get_all_region_labels() if label and label != "Unknown"],
        key="sdg_custom_regions",
        help="Select regions to focus the analysis. Leave empty to analyze all regions."
    )

    countries_query = db_manager.conn.execute(
        "SELECT DISTINCT country_name FROM speeches ORDER BY country_name"
    ).fetchall()
    available_countries = [row[0] for row in countries_query]

    countries_filter = st.multiselect(
        "🌐 Countries:",
        options=available_countries,
        key="sdg_custom_countries",
        help="Optionally restrict the analysis to specific countries."
    )
 
    if st.button("🚀 Run Custom Analysis", type="primary", use_container_width=True, key="sdg_custom_run"):
        if custom_prompt.strip():
            perform_custom_sdg_analysis(custom_prompt, year_range, model, regions_filter, countries_filter)
        else:
            st.warning("Please enter a question")


def perform_sdg_analysis(question: str, year_range: tuple, regions: List[str] = None):
    """Perform SDG analysis using AI."""
    try:
        detected_regions, detected_countries = extract_regions_and_countries(question)
        merged_regions = sorted(set(regions or []) | set(detected_regions))
        merged_countries = sorted(set(detected_countries))

        if detected_regions or detected_countries:
            st.caption(
                f"🧭 Detected entities → Regions: {', '.join(detected_regions) if detected_regions else 'None'} | "
                f"Countries: {', '.join(detected_countries) if detected_countries else 'None'}"
            )

        # Get SDG data
        df = get_sdg_data(year_range, countries=merged_countries, regions=merged_regions)
        
        if df.empty:
            st.warning("No data found for the selected criteria.")
            return
        
        # Prepare context for AI
        context = f"""
        SDG Analysis Context:
        - Year Range: {year_range[0]}-{year_range[1]}
        - Regions: {merged_regions if merged_regions else 'All'}
        - Countries: {merged_countries if merged_countries else 'Derived from regions'}
        - Total Speeches Analyzed: {len(df)}
        - Countries: {df['country'].nunique()}
        
        SDG Summary Data:
        {df[list(SDG_INFO.keys())].sum().to_dict()}
        
        Top SDGs by Total Mentions:
        {df[list(SDG_INFO.keys())].sum().sort_values(ascending=False).head(10).to_dict()}
        """
        
        # AI System Message
        system_msg = """You are an expert SDG analyst for UN General Assembly speeches.
        Analyze SDG discourse patterns, trends, and commitments.
        Provide comprehensive insights with:
        - Key findings about SDG mentions and trends
        - Regional and country comparisons
        - Time-based evolution of SDG focus
        - Actionable insights for policy makers
        Use tables, charts descriptions, and structured analysis."""
        
        user_msg = f"""Question: {question}
        
        Context: {context}
        
        Please provide a comprehensive SDG analysis answering the question with:
        1. Executive summary
        2. Key findings with specific data points
        3. Trends and patterns (with table format)
        4. Regional/country comparisons
        5. Recommendations"""
        
        # Run AI analysis
        client = get_openai_client()
        if client:
            response = run_analysis(system_msg, user_msg, model="model-router", client=client)
            st.markdown("### 🤖 AI Analysis Results")
            st.markdown(response)
        else:
            st.warning("AI client not available. Showing data summary instead.")
            st.dataframe(df.groupby('year')[list(SDG_INFO.keys())].sum())
    
    except Exception as e:
        st.error(f"Analysis error: {e}")
        import traceback
        st.code(traceback.format_exc())


def create_sdg_trend_visualizations(selected_sdgs: List[str], year_range: tuple, regions: Optional[List[str]] = None):
    """Create advanced SDG trend visualizations."""
    try:
        df = get_sdg_data(year_range, regions=regions)
        
        if df.empty:
            st.warning("No data available for visualization.")
            return
        
        # Aggregate by year
        yearly_data = df.groupby('year')[selected_sdgs].sum().reset_index()
        
        # Create multi-line trend chart
        fig = go.Figure()
        
        for sdg in selected_sdgs:
            color = SDG_INFO[sdg]["color"]
            icon = SDG_INFO[sdg]["icon"]
            fig.add_trace(go.Scatter(
                x=yearly_data['year'],
                y=yearly_data[sdg],
                mode='lines+markers',
                name=f"{icon} {sdg}",
                line=dict(color=color, width=3),
                marker=dict(size=10)
            ))
        
        fig.update_layout(
            title="📈 SDG Trend Analysis Over Time",
            xaxis_title="Year",
            yaxis_title="Total Mentions",
            hovermode='x unified',
            height=600,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap of SDG mentions by year
        st.subheader("🔥 SDG Heatmap by Year")
        heatmap_data = df.groupby('year')[selected_sdgs].sum().T
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Year", y="SDG", color="Mentions"),
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        total_mentions = df[selected_sdgs].sum().sum()
        avg_per_year = total_mentions / len(yearly_data)
        top_sdg = df[selected_sdgs].sum().idxmax()
        
        with col1:
            st.metric("Total Mentions", f"{total_mentions:,}")
        with col2:
            st.metric("Avg per Year", f"{avg_per_year:.0f}")
        with col3:
            st.metric("Top SDG", top_sdg.split(':')[1] if ':' in top_sdg else top_sdg)
        
    except Exception as e:
        st.error(f"Visualization error: {e}")


def create_country_sdg_profiles(selected_countries: List[str], year_range: tuple):
    """Create country-specific SDG profiles."""
    try:
        df = get_sdg_data(year_range, countries=selected_countries)
        
        if df.empty:
            st.warning("No data available for selected countries.")
            return
        
        # Calculate SDG focus for each country
        country_sdg_focus = df.groupby('country')[list(SDG_INFO.keys())].sum()
        country_totals = country_sdg_focus.sum(axis=1)
        country_percentages = (country_sdg_focus.div(country_totals, axis=0) * 100).round(2)
        
        # Top 5 SDGs per country
        st.subheader("🏆 Top 5 SDGs by Country")
        
        for country in selected_countries[:5]:  # Show first 5
            if country in country_percentages.index:
                top_sdgs = country_percentages.loc[country].nlargest(5)
                
                st.markdown(f"#### {country}")
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=top_sdgs.values,
                        y=[f"{SDG_INFO[sdg]['icon']} {sdg.split(':')[1].strip()}" for sdg in top_sdgs.index],
                        orientation='h',
                        marker_color=[SDG_INFO[sdg]['color'] for sdg in top_sdgs.index]
                    )
                ])
                
                fig.update_layout(
                    title=f"{country} - Top 5 SDG Focus (%)",
                    xaxis_title="Percentage of SDG Mentions",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Comparison radar chart
        if len(selected_countries) >= 2:
            st.subheader("🔍 SDG Focus Comparison")
            
            # Select top SDGs for comparison
            top_5_sdgs = country_sdg_focus.sum().nlargest(5).index.tolist()
            
            fig = go.Figure()
            
            for country in selected_countries[:3]:  # Max 3 for readability
                if country in country_percentages.index:
                    values = country_percentages.loc[country, top_5_sdgs].values
                    fig.add_trace(go.Scatterpolar(
                        r=list(values) + [values[0]],  # Close the radar
                        theta=[sdg.split(':')[1].strip() for sdg in top_5_sdgs] + [top_5_sdgs[0].split(':')[1].strip()],
                        fill='toself',
                        name=country
                    ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(country_percentages[top_5_sdgs].max())])
                ),
                showlegend=True,
                title="SDG Focus Comparison (Radar Chart)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Profile generation error: {e}")


def perform_custom_sdg_analysis(prompt: str, year_range: tuple, model: str, regions: Optional[List[str]] = None, countries: Optional[List[str]] = None):
    """Perform custom SDG analysis with AI and visualizations."""
    try:
        detected_regions, detected_countries = extract_regions_and_countries(prompt)
        merged_regions = sorted(set(regions or []) | set(detected_regions))
        merged_countries = sorted(set(countries or []) | set(detected_countries))

        if detected_regions or detected_countries:
            st.caption(
                f"🧭 Detected entities → Regions: {', '.join(detected_regions) if detected_regions else 'None'} | "
                f"Countries: {', '.join(detected_countries) if detected_countries else 'None'}"
            )

        # Get data
        df = get_sdg_data(year_range, countries=merged_countries, regions=merged_regions)

        if df.empty:
            st.warning("No data available for the selected filters.")
            return

        # Prepare comprehensive context
        context = f"""
        SDG Analysis Request: {prompt}
        
        Data Summary:
        - Year Range: {year_range[0]}-{year_range[1]}
        - Total Speeches: {len(df)}
        - Countries: {df['country'].nunique()}
        - Regions Filtered: {merged_regions if merged_regions else 'All'}
        - Countries Filtered: {merged_countries if merged_countries else 'Derived from regions'}
        
        SDG Statistics:
        {df[list(SDG_INFO.keys())].sum().sort_values(ascending=False).to_dict()}
        
        Regional Breakdown:
        {df.groupby('region')[list(SDG_INFO.keys())].sum().to_dict()}
        
        Temporal Trends:
        {df.groupby('year')[list(SDG_INFO.keys())].sum().tail(10).to_dict()}
        """
        
        system_msg = """You are an expert SDG policy analyst.
        Provide comprehensive analysis with:
        - Executive summary
        - Data-driven insights with specific numbers
        - Visual description (tables, trends, comparisons)
        - Policy implications
        - Recommendations
        
        Format with clear sections, tables, and actionable insights."""
        
        user_msg = f"{context}\n\nAnalyze this SDG data and answer: {prompt}"
        
        # Run AI analysis
        client = get_openai_client()
        if client:
            with st.spinner("🤖 AI is analyzing SDG data..."):
                response = run_analysis(system_msg, user_msg, model=model, client=client)
            
            st.markdown("### 🤖 AI Analysis")
            st.markdown(response)
            
            # Add quick visualization
            st.markdown("### 📊 Quick Data Overview")
            top_sdgs = df[list(SDG_INFO.keys())].sum().nlargest(10)
            
            fig = px.bar(
                x=top_sdgs.values,
                y=[sdg.split(':')[1].strip() for sdg in top_sdgs.index],
                orientation='h',
                title="Top 10 SDGs by Total Mentions",
                labels={'x': 'Total Mentions', 'y': 'SDG'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("AI client not available.")
    
    except Exception as e:
        st.error(f"Custom analysis error: {e}")

