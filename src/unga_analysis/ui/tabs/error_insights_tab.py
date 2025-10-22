"""
Error Insights Tab for UNGA Analysis Application.
Provides AI-readable error analysis and system health monitoring.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List

from ...utils.log_analyzer import LogAnalyzer, get_application_health, get_error_insights
from ...utils.logging_config import get_log_insights, analyze_recent_errors

def render_error_insights_tab():
    """Render the error insights and system health tab."""
    st.header("🔍 Error Insights & System Health")
    st.markdown("Monitor application health and understand error patterns for better AI assistance.")
    
    # Initialize analyzer
    analyzer = LogAnalyzer()
    
    # Create tabs for different insights
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Health Overview", 
        "🚨 Error Analysis", 
        "💡 AI Insights", 
        "📈 Performance"
    ])
    
    with tab1:
        render_health_overview(analyzer)
    
    with tab2:
        render_error_analysis(analyzer)
    
    with tab3:
        render_ai_insights(analyzer)
    
    with tab4:
        render_performance_metrics(analyzer)

def render_health_overview(analyzer: LogAnalyzer):
    """Render system health overview."""
    st.subheader("System Health Status")
    
    # Get health score
    health = analyzer.get_health_score()
    
    # Display health score with color coding
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Health Score", 
            f"{health['score']}/100",
            delta=None,
            help="Overall application health score"
        )
    
    with col2:
        st.metric(
            "Total Errors", 
            health['total_errors'],
            help="Total errors recorded in system"
        )
    
    with col3:
        st.metric(
            "Recent Errors (24h)", 
            health['recent_errors'],
            help="Errors in the last 24 hours"
        )
    
    with col4:
        st.metric(
            "Unique Error Types", 
            health['unique_errors'],
            help="Number of different error types"
        )
    
    # Health status indicator
    status_color = {
        "Excellent": "🟢",
        "Good": "🟡", 
        "Fair": "🟠",
        "Poor": "🔴",
        "Critical": "💀"
    }
    
    st.markdown(f"""
    **Status**: {status_color.get(health['status'], '❓')} {health['status']}
    
    **Last Updated**: {health['last_updated']}
    """)
    
    # Health trend (if we had historical data)
    st.subheader("Health Trend")
    st.info("Health trend analysis would show here with historical data collection.")

def render_error_analysis(analyzer: LogAnalyzer):
    """Render detailed error analysis."""
    st.subheader("Error Pattern Analysis")
    
    # Get error patterns
    patterns = analyzer.analyze_error_patterns()
    
    # Create error category chart
    error_categories = []
    error_counts = []
    
    for category, errors in patterns.items():
        if errors:
            error_categories.append(category.replace('_', ' ').title())
            error_counts.append(len(errors))
    
    if error_categories:
        # Create pie chart
        fig = px.pie(
            values=error_counts,
            names=error_categories,
            title="Error Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed breakdown
        st.subheader("Error Category Details")
        for category, errors in patterns.items():
            if errors:
                with st.expander(f"{category.replace('_', ' ').title()} ({len(errors)} errors)"):
                    for i, error in enumerate(errors[:5], 1):  # Show top 5
                        st.write(f"**{i}.** {error['error_message']}")
                        st.caption(f"Count: {error['count']} | Last seen: {error['last_seen']}")
    else:
        st.success("🎉 No errors detected in the system!")
    
    # Recent errors table
    st.subheader("Recent Error Activity")
    recent_errors = analyze_recent_errors(hours=24)
    
    if recent_errors['top_errors']:
        error_data = []
        for error_key, error_info in recent_errors['top_errors']:
            error_data.append({
                'Error Type': error_info['error_type'],
                'Message': error_info['error_message'][:100] + "..." if len(error_info['error_message']) > 100 else error_info['error_message'],
                'Count': error_info['count'],
                'Last Seen': error_info['last_seen']
            })
        
        df = pd.DataFrame(error_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("No recent errors in the last 24 hours!")

def render_ai_insights(analyzer: LogAnalyzer):
    """Render AI-readable insights."""
    st.subheader("AI Assistant Error Understanding")
    st.markdown("This section provides comprehensive error analysis for AI assistance.")
    
    # Get AI report
    ai_report = analyzer.generate_ai_report()
    
    # Display the report
    st.markdown(ai_report)
    
    # Quick insights
    st.subheader("Quick Error Insights")
    insights = get_log_insights()
    
    if insights['most_common_errors']:
        st.write("**Most Common Errors:**")
        for i, error in enumerate(insights['most_common_errors'][:3], 1):
            st.write(f"{i}. **{error['type']}**: {error['error']} (Count: {error['count']})")
    
    # Component breakdown
    if insights['component_breakdown']:
        st.write("**Error Distribution by Component:**")
        for component, count in insights['component_breakdown'].items():
            st.write(f"- {component}: {count} errors")
    
    # Suggested fixes
    st.subheader("Suggested Improvements")
    suggestions = analyzer.get_suggested_fixes()
    
    if suggestions:
        for suggestion in suggestions:
            with st.expander(f"🔧 {suggestion['category']}"):
                st.write(f"**Issue**: {suggestion['description']}")
                st.write("**Recommended Actions:**")
                for action in suggestion['suggestions']:
                    st.write(f"- {action}")
    else:
        st.success("No specific improvement suggestions at this time.")

def render_performance_metrics(analyzer: LogAnalyzer):
    """Render performance metrics."""
    st.subheader("Performance Monitoring")
    
    # Get recent logs
    recent_logs = analyzer.get_recent_logs(hours=24, log_type="performance")
    
    if recent_logs:
        # Extract performance data
        performance_data = []
        for log in recent_logs:
            if 'duration' in log:
                performance_data.append({
                    'Operation': log.get('operation', 'Unknown'),
                    'Component': log.get('component', 'Unknown'),
                    'Duration (s)': log.get('duration', 0),
                    'Timestamp': log.get('timestamp', ''),
                    'Message': log.get('message', '')
                })
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            
            # Performance summary
            st.subheader("Performance Summary")
            avg_duration = df['Duration (s)'].mean()
            max_duration = df['Duration (s)'].max()
            min_duration = df['Duration (s)'].min()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Duration", f"{avg_duration:.2f}s")
            with col2:
                st.metric("Max Duration", f"{max_duration:.2f}s")
            with col3:
                st.metric("Min Duration", f"{min_duration:.2f}s")
            
            # Performance chart
            fig = px.bar(
                df, 
                x='Operation', 
                y='Duration (s)',
                title="Operation Duration Analysis",
                color='Component'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance table
            st.subheader("Recent Performance Data")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No performance data available for the last 24 hours.")
    else:
        st.info("No performance logs found. Performance monitoring will start collecting data.")
    
    # System recommendations
    st.subheader("Performance Recommendations")
    st.markdown("""
    **For Better Performance:**
    - Monitor slow operations (>10s)
    - Implement caching for frequent operations
    - Consider async processing for heavy tasks
    - Add progress indicators for long operations
    """)

def render_error_context_search():
    """Render error context search functionality."""
    st.subheader("Error Context Search")
    
    search_term = st.text_input(
        "Search for specific error messages:",
        placeholder="Enter error message or keyword..."
    )
    
    if search_term:
        analyzer = LogAnalyzer()
        context_results = analyzer.find_error_context(search_term)
        
        if context_results:
            st.write(f"Found {len(context_results)} matching log entries:")
            
            for i, log_entry in enumerate(context_results[:10], 1):  # Show top 10
                with st.expander(f"Log Entry {i} - {log_entry.get('timestamp', 'Unknown time')}"):
                    st.json(log_entry)
        else:
            st.info("No matching log entries found.")
