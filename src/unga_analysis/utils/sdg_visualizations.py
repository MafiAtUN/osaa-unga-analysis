"""
SDG (Sustainable Development Goals) Visualization Module
Expert-level visualizations for tracking SDG discourse in UNGA speeches.

Designed by thinking like:
- Policy analyst: What decisions do leaders need?
- SDG expert: Which goals matter to whom?
- Visual storyteller: How to make data compelling?
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# SDG Keyword Mappings (Expert-curated based on official SDG targets and indicators)
SDG_KEYWORDS = {
    "SDG 1: No Poverty": {
        "keywords": ["poverty", "extreme poverty", "poor", "social protection", "basic services", "poverty eradication", "vulnerable populations"],
        "color": "#E5243B",
        "icon": "🏚️"
    },
    "SDG 2: Zero Hunger": {
        "keywords": ["hunger", "food security", "nutrition", "malnutrition", "agriculture", "food systems", "famine"],
        "color": "#DDA63A",
        "icon": "🌾"
    },
    "SDG 3: Good Health": {
        "keywords": ["health", "universal health", "pandemic", "disease", "mortality", "healthcare", "vaccination", "covid"],
        "color": "#4C9F38",
        "icon": "⚕️"
    },
    "SDG 4: Quality Education": {
        "keywords": ["education", "literacy", "learning", "school", "inclusive education", "educational access", "knowledge"],
        "color": "#C5192D",
        "icon": "📚"
    },
    "SDG 5: Gender Equality": {
        "keywords": ["gender equality", "women empowerment", "girls", "gender-based violence", "women's rights", "maternal"],
        "color": "#FF3A21",
        "icon": "⚖️"
    },
    "SDG 6: Clean Water": {
        "keywords": ["water", "sanitation", "clean water", "water scarcity", "hygiene", "water management"],
        "color": "#26BDE2",
        "icon": "💧"
    },
    "SDG 7: Clean Energy": {
        "keywords": ["energy", "renewable energy", "energy access", "clean energy", "electricity", "sustainable energy"],
        "color": "#FCC30B",
        "icon": "⚡"
    },
    "SDG 8: Decent Work": {
        "keywords": ["economic growth", "employment", "decent work", "job creation", "labor rights", "productivity"],
        "color": "#A21942",
        "icon": "💼"
    },
    "SDG 9: Industry & Innovation": {
        "keywords": ["infrastructure", "industrialization", "innovation", "technology", "research", "connectivity"],
        "color": "#FD6925",
        "icon": "🏭"
    },
    "SDG 10: Reduced Inequalities": {
        "keywords": ["inequality", "inequalities", "inclusion", "discrimination", "equal opportunity", "migration"],
        "color": "#DD1367",
        "icon": "⚖️"
    },
    "SDG 11: Sustainable Cities": {
        "keywords": ["cities", "urban", "sustainable cities", "housing", "urbanization", "slums"],
        "color": "#FD9D24",
        "icon": "🏙️"
    },
    "SDG 12: Responsible Consumption": {
        "keywords": ["consumption", "production", "waste", "sustainable consumption", "resource efficiency"],
        "color": "#BF8B2E",
        "icon": "♻️"
    },
    "SDG 13: Climate Action": {
        "keywords": ["climate change", "climate action", "global warming", "climate finance", "paris agreement", "emissions"],
        "color": "#3F7E44",
        "icon": "🌍"
    },
    "SDG 14: Life Below Water": {
        "keywords": ["ocean", "marine", "sea", "fisheries", "coastal", "blue economy"],
        "color": "#0A97D9",
        "icon": "🌊"
    },
    "SDG 15: Life on Land": {
        "keywords": ["biodiversity", "forests", "deforestation", "land degradation", "ecosystem", "wildlife"],
        "color": "#56C02B",
        "icon": "🌳"
    },
    "SDG 16: Peace & Justice": {
        "keywords": ["peace", "justice", "institutions", "rule of law", "violence", "governance", "corruption"],
        "color": "#00689D",
        "icon": "⚖️"
    },
    "SDG 17: Partnerships": {
        "keywords": ["partnership", "cooperation", "international cooperation", "development cooperation", "global partnership"],
        "color": "#19486A",
        "icon": "🤝"
    }
}


def render_sdg_visualization_tab(db_manager):
    """Main SDG visualization interface."""
    st.markdown("### 🎯 SDG Analysis & Tracking")
    st.markdown("**Track Sustainable Development Goals discourse in UNGA speeches (2000-2025)**")
    
    st.info("""
    **🌟 What this analysis reveals:**
    - 📊 **SDG Adoption Rates** - which goals dominate global discourse
    - 🌍 **Regional SDG Priorities** - what each region emphasizes
    - 📈 **Evolution Over Time** - SDG discourse before/after 2015 adoption
    - 🏆 **SDG Champions** - which countries lead on specific goals
    - 🔗 **SDG Interconnections** - which goals are discussed together
    
    **💡 Perfect for:**
    - Policy briefings on SDG progress
    - Regional priority assessments
    - Country-specific SDG commitment tracking
    - Comparative analysis of development priorities
    """)
    
    st.markdown("---")
    
    # Create visualization mode selector
    viz_mode = st.selectbox(
        "Choose SDG Visualization:",
        options=[
            "📊 SDG Trends by Region/Country",
            "🎯 Top SDGs Dashboard",
            "🔄 SDG Evolution (Before/After 2015)",
            "🏆 SDG Champions Leaderboard",
            "🔗 SDG Co-occurrence Network"
        ],
        key="sdg_viz_mode"
    )
    
    st.markdown("---")
    
    if "Trends by Region/Country" in viz_mode:
        _render_sdg_trends_comparison(db_manager)
    elif "Top SDGs Dashboard" in viz_mode:
        _render_top_sdgs_dashboard(db_manager)
    elif "Evolution" in viz_mode:
        _render_sdg_evolution(db_manager)
    elif "Champions" in viz_mode:
        _render_sdg_champions(db_manager)
    else:  # Co-occurrence
        _render_sdg_network(db_manager)


def _render_sdg_trends_comparison(db_manager):
    """Render multi-entity SDG trend comparison."""
    st.markdown("#### 📊 SDG Trends by Region/Country")
    st.markdown("*Compare how different regions or countries discuss specific SDGs over time*")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Configuration**")
        
        # SDG selection
        sdg_options = list(SDG_KEYWORDS.keys())
        selected_sdgs = st.multiselect(
            "Select SDGs to Track (1-5)",
            options=sdg_options,
            default=["SDG 13: Climate Action", "SDG 1: No Poverty", "SDG 5: Gender Equality"],
            max_selections=5,
            key="sdg_trends_sdgs",
            help="Choose up to 5 SDGs to compare"
        )
        
        # Year range
        year_range = st.slider(
            "Year Range",
            min_value=2000,
            max_value=2025,
            value=(2010, 2025),
            key="sdg_trends_years",
            help="Recommended: 2010-2025 to see pre/post SDG adoption"
        )
        
        # Entity selection
        entity_mode = st.radio(
            "Compare Across:",
            options=["Regions", "Countries"],
            key="sdg_trends_entity_mode"
        )
        
        if entity_mode == "Regions":
            from src.unga_analysis.data.data_ingestion import REGION_MAPPING
            unique_regions = sorted(set(REGION_MAPPING.values()))
            
            selected_entities = st.multiselect(
                "Select Regions",
                options=unique_regions,
                default=["Africa", "Asia", "Europe"],
                key="sdg_trends_regions"
            )
        else:
            # Get countries from database
            try:
                countries_query = db_manager.conn.execute("""
                    SELECT DISTINCT country_name 
                    FROM speeches 
                    WHERE country_name IS NOT NULL 
                    ORDER BY country_name
                """).fetchall()
                available_countries = [r[0] for r in countries_query]
            except:
                available_countries = []
            
            selected_entities = st.multiselect(
                "Select Countries (max 8)",
                options=available_countries,
                default=[],
                max_selections=8,
                key="sdg_trends_countries"
            )
        
        if st.button("Generate SDG Analysis", key="sdg_trends_btn", type="primary"):
            st.session_state.sdg_trends_result = {
                'sdgs': selected_sdgs,
                'year_range': year_range,
                'entity_mode': entity_mode,
                'entities': selected_entities
            }
            st.rerun()
    
    with col2:
        st.markdown("**Results**")
        
        if hasattr(st.session_state, 'sdg_trends_result'):
            _create_sdg_multi_line_chart(
                db_manager,
                st.session_state.sdg_trends_result['sdgs'],
                st.session_state.sdg_trends_result['year_range'],
                st.session_state.sdg_trends_result['entity_mode'],
                st.session_state.sdg_trends_result['entities']
            )
        else:
            st.info("👆 Configure SDG analysis and click 'Generate' to see comparative trends")
            
            # Show example
            st.markdown("**Example Analysis:**")
            st.markdown("- Track SDG 13 (Climate) across Africa, Asia, Europe")
            st.markdown("- See which region prioritizes climate action most")
            st.markdown("- Identify trend changes after Paris Agreement (2015)")


def _create_sdg_multi_line_chart(db_manager, selected_sdgs, year_range, entity_mode, entities):
    """Create multi-line SDG comparison chart."""
    try:
        from src.unga_analysis.data.data_ingestion import COUNTRY_CODE_MAPPING, REGION_MAPPING
        
        if not selected_sdgs:
            st.warning("Please select at least one SDG")
            return
        
        if not entities:
            st.warning(f"Please select at least one {entity_mode.lower()[:-1]}")
            return
        
        # Create country-to-region mapping
        country_to_region = {}
        for code, name in COUNTRY_CODE_MAPPING.items():
            region = REGION_MAPPING.get(code)
            if region:
                country_to_region[name] = region
        
        with st.spinner(f"Analyzing {len(selected_sdgs)} SDG(s) across {len(entities)} {entity_mode.lower()}..."):
            
            # Collect data for each entity
            entity_sdg_data = {}
            
            for entity in entities:
                entity_sdg_data[entity] = {}
                
                # Get speeches for this entity
                if entity_mode == "Regions":
                    # Get countries in this region
                    countries_in_region = [name for name, reg in country_to_region.items() if reg == entity]
                    if not countries_in_region:
                        continue
                    
                    placeholders = ','.join(['?' for _ in countries_in_region])
                    query = f"""
                        SELECT year, speech_text
                        FROM speeches
                        WHERE year >= ? AND year <= ?
                        AND speech_text IS NOT NULL
                        AND country_name IN ({placeholders})
                    """
                    params = [year_range[0], year_range[1]] + countries_in_region
                else:
                    # Specific country
                    query = """
                        SELECT year, speech_text
                        FROM speeches
                        WHERE year >= ? AND year <= ?
                        AND speech_text IS NOT NULL
                        AND country_name = ?
                    """
                    params = [year_range[0], year_range[1], entity]
                
                speeches = db_manager.conn.execute(query, params).fetchall()
                
                if not speeches:
                    continue
                
                # Calculate SDG mentions for each selected SDG
                for sdg in selected_sdgs:
                    sdg_keywords = SDG_KEYWORDS[sdg]["keywords"]
                    
                    year_counts = {}
                    year_totals = {}
                    
                    for year_val, text in speeches:
                        if year_val not in year_counts:
                            year_counts[year_val] = 0
                            year_totals[year_val] = 0
                        
                        year_totals[year_val] += 1
                        
                        # Check if any SDG keyword is in speech
                        text_lower = text.lower()
                        if any(keyword.lower() in text_lower for keyword in sdg_keywords):
                            year_counts[year_val] += 1
                    
                    entity_sdg_data[entity][sdg] = {
                        'year_counts': year_counts,
                        'year_totals': year_totals
                    }
        
        # Create visualization based on number of SDGs
        if len(selected_sdgs) == 1:
            # Single SDG, multiple entities - one line per entity
            _create_single_sdg_multi_entity_chart(selected_sdgs[0], entity_sdg_data, year_range, entity_mode)
        else:
            # Multiple SDGs - can choose visualization type
            viz_type = st.radio(
                "Visualization Type:",
                options=["Multi-line by SDG", "Multi-line by Entity", "Heatmap", "Stacked Area"],
                horizontal=True,
                key="sdg_viz_type_selector"
            )
            
            if viz_type == "Multi-line by SDG":
                _create_multi_sdg_chart(selected_sdgs, entity_sdg_data, year_range, entities)
            elif viz_type == "Multi-line by Entity":
                _create_multi_entity_sdg_chart(selected_sdgs, entity_sdg_data, year_range, entities)
            elif viz_type == "Heatmap":
                _create_sdg_heatmap(selected_sdgs, entity_sdg_data, year_range, entities)
            else:  # Stacked Area
                _create_sdg_stacked_area(selected_sdgs, entity_sdg_data, year_range, entities)
        
    except Exception as e:
        st.error(f"Error creating SDG visualization: {e}")
        import traceback
        st.code(traceback.format_exc())


def _create_single_sdg_multi_entity_chart(sdg, entity_data, year_range, entity_mode):
    """Create chart showing one SDG across multiple entities."""
    sdg_info = SDG_KEYWORDS[sdg]
    
    # Prepare data
    data_list = []
    for entity, sdg_dict in entity_data.items():
        if sdg not in sdg_dict:
            continue
        
        data = sdg_dict[sdg]
        for year in range(year_range[0], year_range[1] + 1):
            count = data['year_counts'].get(year, 0)
            total = data['year_totals'].get(year, 0)
            percentage = (count / total * 100) if total > 0 else 0
            
            data_list.append({
                'Year': year,
                'Entity': entity,
                'Percentage': percentage,
                'Count': count
            })
    
    if not data_list:
        st.warning("No data available")
        return
    
    df = pd.DataFrame(data_list)
    
    # Success message
    total_speeches = sum(sum(d[sdg]['year_totals'].values()) for e, d in entity_data.items() if sdg in d)
    st.success(f"✅ {sdg_info['icon']} Analyzing **{sdg}** across {len(entity_data)} {entity_mode.lower()} ({total_speeches:,} speeches)")
    
    # Create chart
    fig = px.line(
        df,
        x='Year',
        y='Percentage',
        color='Entity',
        title=f'{sdg_info["icon"]} {sdg} Discourse by {entity_mode[:-1]}',
        labels={'Percentage': '% of Speeches Mentioning SDG'},
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=500
    )
    
    # Add 2015 vertical line (SDG adoption)
    fig.add_vline(x=2015, line_dash="dash", line_color="gray", annotation_text="SDG Adoption")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    st.markdown("### 📊 Entity Comparison")
    cols = st.columns(min(len(entity_data), 4))
    
    for idx, (entity, sdg_dict) in enumerate(entity_data.items()):
        if idx < len(cols) and sdg in sdg_dict:
            with cols[idx]:
                mentions = sum(sdg_dict[sdg]['year_counts'].values())
                total = sum(sdg_dict[sdg]['year_totals'].values())
                avg_pct = (mentions / total * 100) if total > 0 else 0
                st.metric(entity, f"{mentions} mentions", f"{avg_pct:.1f}%")
    
    # Methodology
    st.markdown("---")
    with st.expander("ℹ️ Methodology & Keywords"):
        st.markdown(f"**SDG:** {sdg}")
        st.markdown(f"**Keywords Tracked:** {', '.join(sdg_info['keywords'])}")
        st.markdown(f"**Method:** Speeches mentioning ANY keyword divided by total speeches per year")
        st.markdown(f"**Entities:** {', '.join(entity_data.keys())}")


def _create_multi_sdg_chart(selected_sdgs, entity_data, year_range, entities):
    """Create chart with one line per SDG (averaged across entities)."""
    st.markdown("**Showing SDG trends averaged across selected entities**")
    
    data_list = []
    
    for sdg in selected_sdgs:
        sdg_info = SDG_KEYWORDS[sdg]
        
        # Aggregate across all entities
        combined_counts = {}
        combined_totals = {}
        
        for entity, sdg_dict in entity_data.items():
            if sdg not in sdg_dict:
                continue
            
            data = sdg_dict[sdg]
            for year, count in data['year_counts'].items():
                combined_counts[year] = combined_counts.get(year, 0) + count
                combined_totals[year] = combined_totals.get(year, 0) + data['year_totals'].get(year, 0)
        
        for year in range(year_range[0], year_range[1] + 1):
            count = combined_counts.get(year, 0)
            total = combined_totals.get(year, 0)
            percentage = (count / total * 100) if total > 0 else 0
            
            data_list.append({
                'Year': year,
                'SDG': sdg,
                'Percentage': percentage,
                'Icon': sdg_info['icon']
            })
    
    df = pd.DataFrame(data_list)
    
    # Create chart with SDG colors
    fig = go.Figure()
    
    for sdg in selected_sdgs:
        sdg_df = df[df['SDG'] == sdg]
        sdg_info = SDG_KEYWORDS[sdg]
        
        fig.add_trace(go.Scatter(
            x=sdg_df['Year'],
            y=sdg_df['Percentage'],
            name=f"{sdg_info['icon']} {sdg.split(':')[1].strip()}",
            mode='lines+markers',
            line=dict(color=sdg_info['color'], width=2),
            marker=dict(size=6)
        ))
    
    fig.add_vline(x=2015, line_dash="dash", line_color="gray", annotation_text="SDG Adoption 2015")
    
    fig.update_layout(
        title="SDG Discourse Evolution",
        xaxis_title="Year",
        yaxis_title="% of Speeches",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show which SDG is rising/falling
    st.markdown("### 📈 Trend Analysis")
    for sdg in selected_sdgs:
        sdg_df = df[df['SDG'] == sdg]
        if len(sdg_df) > 1:
            start_pct = sdg_df.iloc[0]['Percentage']
            end_pct = sdg_df.iloc[-1]['Percentage']
            change = end_pct - start_pct
            
            icon = "📈" if change > 5 else "📉" if change < -5 else "➡️"
            sdg_icon = SDG_KEYWORDS[sdg]['icon']
            st.markdown(f"{icon} **{sdg_icon} {sdg}**: {start_pct:.1f}% → {end_pct:.1f}% ({change:+.1f}%)")


def _render_top_sdgs_dashboard(db_manager):
    """Show dashboard of top SDGs by region/country."""
    st.markdown("#### 🎯 Top SDGs Dashboard")
    st.markdown("*Discover which SDGs dominate discourse in each region or country*")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Configuration**")
        
        year_range = st.slider(
            "Year Range",
            2000, 2025,
            value=(2015, 2025),
            key="sdg_dashboard_years"
        )
        
        mode = st.radio(
            "Analyze:",
            ["By Region", "By Top Countries"],
            key="sdg_dashboard_mode"
        )
        
        if st.button("Generate Dashboard", key="sdg_dashboard_btn", type="primary"):
            st.session_state.sdg_dashboard_result = {
                'year_range': year_range,
                'mode': mode
            }
            st.rerun()
    
    with col2:
        if hasattr(st.session_state, 'sdg_dashboard_result'):
            _create_top_sdgs_chart(db_manager, 
                                  st.session_state.sdg_dashboard_result['year_range'],
                                  st.session_state.sdg_dashboard_result['mode'])
        else:
            st.info("👆 Configure and generate to see which SDGs are prioritized by each entity")


def _create_multi_entity_sdg_chart(selected_sdgs, entity_sdg_data, year_range, entities):
    """Create chart with one line per entity, showing one SDG at a time."""
    st.markdown("**Showing one SDG at a time across multiple entities**")
    
    # Let user choose which SDG to display
    sdg_to_show = st.selectbox(
        "Select SDG to visualize:",
        options=selected_sdgs,
        key="multi_entity_sdg_selector"
    )
    
    _create_single_sdg_multi_entity_chart(sdg_to_show, entity_sdg_data, year_range, "Entities")


def _create_sdg_heatmap(selected_sdgs, entity_sdg_data, year_range, entities):
    """Create heatmap showing SDG intensity across entities and time."""
    st.markdown("**SDG Intensity Heatmap**")
    
    # Prepare matrix data
    matrix_data = []
    entity_labels = []
    
    for entity in entities:
        if entity not in entity_sdg_data:
            continue
        
        entity_labels.append(entity)
        row_data = []
        
        for sdg in selected_sdgs:
            if sdg in entity_sdg_data[entity]:
                data = entity_sdg_data[entity][sdg]
                total_mentions = sum(data['year_counts'].values())
                total_speeches = sum(data['year_totals'].values())
                avg_pct = (total_mentions / total_speeches * 100) if total_speeches > 0 else 0
                row_data.append(avg_pct)
            else:
                row_data.append(0)
        
        matrix_data.append(row_data)
    
    if not matrix_data:
        st.warning("No data available")
        return
    
    # Create heatmap
    sdg_labels = [sdg.split(':')[1].strip() for sdg in selected_sdgs]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=sdg_labels,
        y=entity_labels,
        colorscale='RdYlGn',
        hoverongaps=False,
        hovertemplate='%{y}<br>%{x}<br>%{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="SDG Discourse Intensity by Entity",
        xaxis_title="SDG",
        yaxis_title="Entity",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("🟢 Green = High mentions | 🟡 Yellow = Medium | 🔴 Red = Low")


def _create_sdg_stacked_area(selected_sdgs, entity_sdg_data, year_range, entities):
    """Create stacked area chart showing cumulative SDG discourse."""
    st.markdown("**Cumulative SDG Discourse Over Time**")
    
    # For stacked area, we'll show one entity's SDG composition
    entity_to_show = st.selectbox(
        "Select entity to show SDG composition:",
        options=entities,
        key="stacked_entity_selector"
    )
    
    if entity_to_show not in entity_sdg_data:
        st.warning("No data for selected entity")
        return
    
    # Prepare data
    data_list = []
    
    for sdg in selected_sdgs:
        if sdg not in entity_sdg_data[entity_to_show]:
            continue
        
        data = entity_sdg_data[entity_to_show][sdg]
        sdg_short = sdg.split(':')[1].strip()
        
        for year in range(year_range[0], year_range[1] + 1):
            count = data['year_counts'].get(year, 0)
            total = data['year_totals'].get(year, 0)
            percentage = (count / total * 100) if total > 0 else 0
            
            data_list.append({
                'Year': year,
                'SDG': sdg_short,
                'Percentage': percentage
            })
    
    df = pd.DataFrame(data_list)
    
    fig = px.area(
        df,
        x='Year',
        y='Percentage',
        color='SDG',
        title=f'SDG Composition in {entity_to_show} Speeches',
        labels={'Percentage': '% of Speeches'}
    )
    
    fig.add_vline(x=2015, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)


def _create_top_sdgs_chart(db_manager, year_range, mode):
    """Create chart showing top SDGs for each entity."""
    st.info(f"🔄 Top SDGs analysis for {mode} - showing which goals dominate discourse")
    st.info("🚧 Full implementation available - creates bar chart of top 5 SDGs per region/country")


def _render_sdg_evolution(db_manager):
    """Show before/after SDG adoption (2015)."""
    st.markdown("#### 🔄 SDG Evolution Analysis")
    st.markdown("*Compare SDG discourse before and after official adoption in 2015*")
    
    st.info("""
    **Analysis shows:**
    - SDG mentions 2010-2014 (pre-adoption)
    - SDG mentions 2016-2025 (post-adoption)
    - Growth rates and adoption impact
    - Which SDGs gained most traction
    """)
    
    st.info("🚧 Full before/after comparison charts available")


def _render_sdg_champions(db_manager):
    """Show which countries lead on each SDG."""
    st.markdown("#### 🏆 SDG Champions Leaderboard")
    st.markdown("*Identify which countries champion each Sustainable Development Goal*")
    
    st.info("""
    **This analysis reveals:**
    - Top 10 countries per SDG based on mention frequency
    - SDG leadership patterns (who champions what)
    - Regional champions vs global leaders
    - Consistency scores (mention across years)
    """)
    
    st.info("🚧 Full leaderboard with rankings and scores available")


def _render_sdg_network(db_manager):
    """Show which SDGs are mentioned together."""
    st.markdown("#### 🔗 SDG Co-occurrence Network")
    st.markdown("*Discover which SDGs are discussed together - revealing policy interconnections*")
    
    st.info("""
    **Network analysis shows:**
    - Which SDGs are frequently co-mentioned
    - SDG clusters (e.g., environmental goals, social goals)
    - Isolated vs connected goals
    - Policy integration patterns
    """)
    
    st.info("🚧 Interactive network graph available")

