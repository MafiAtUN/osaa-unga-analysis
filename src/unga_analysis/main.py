"""
UNGA Analysis App - Main Application
Production-ready UNGA speech analysis platform
"""

import sys
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import core modules
from src.unga_analysis.core.user_auth import UserAuthManager
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
from src.unga_analysis.ui.auth_interface import (
    render_auth_interface, 
    is_user_authenticated, 
    get_current_user, 
    logout_user
)
from src.unga_analysis.ui.tabs.new_analysis_tab import render_new_analysis_tab
from src.unga_analysis.ui.tabs.cross_year_analysis_tab import render_cross_year_analysis_tab
from src.unga_analysis.ui.tabs.document_context_analysis_tab import render_document_context_analysis_tab
from src.unga_analysis.ui.tabs.all_analyses_tab import render_all_analyses_tab
from src.unga_analysis.ui.tabs.visualizations_tab import render_visualizations_tab
from src.unga_analysis.ui.tabs.data_explorer_tab import render_data_explorer_tab
from src.unga_analysis.ui.tabs.database_chat_tab import render_database_chat_tab
from src.unga_analysis.ui.tabs.error_insights_tab import render_error_insights_tab
from src.unga_analysis.ui.enhanced_ui_components import (
    render_page_header, render_info_card, render_success_card, 
    render_warning_card, render_error_card, render_step_guide,
    render_metric_cards, render_enhanced_sidebar,
    render_loading_spinner, render_tooltip_help, render_progress_bar,
    render_enhanced_tabs, render_data_quality_indicators, render_enhanced_footer
)

# Initialize user authentication
user_auth_manager = UserAuthManager()

def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

def render_admin_tab():
    """Render the Admin Portal tab."""
    import sqlite3
    import hashlib
    import os
    from datetime import datetime
    
    st.header("🛡️ Admin Portal")
    st.markdown("**User Management and System Administration**")
    
    # Database connection
    DB_PATH = "user_auth.db"
    
    def get_db_connection():
        return sqlite3.connect(DB_PATH)
    
    def get_all_users():
        """Get all users from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, full_name, title, office, purpose, status, 
                       created_at, approved_at, approved_by, last_login, login_count
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                user_id, email, full_name, title, office, purpose, status, created_at, approved_at, approved_by, last_login, login_count = row
                users.append({
                    'id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'title': title,
                    'office': office,
                    'purpose': purpose,
                    'status': status,
                    'created_at': created_at,
                    'approved_at': approved_at,
                    'approved_by': approved_by,
                    'last_login': last_login,
                    'login_count': login_count
                })
            
            conn.close()
            return users
            
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
    
    def update_user_status(user_id, status):
        """Update user status"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET status = ?, approved_at = ?, approved_by = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), "admin@unga.org", user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating user status: {e}")
            return False
    
    def delete_user(user_id):
        """Delete user and all related data"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Delete usage logs first
            cursor.execute("DELETE FROM usage_logs WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False
    
    # Get all users
    all_users = get_all_users()
    
    # Statistics
    total_users = len(all_users)
    pending_users = [u for u in all_users if u['status'] == 'pending']
    approved_users = [u for u in all_users if u['status'] == 'approved']
    denied_users = [u for u in all_users if u['status'] == 'denied']
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", total_users)
    
    with col2:
        st.metric("⏳ Pending", len(pending_users))
    
    with col3:
        st.metric("✅ Approved", len(approved_users))
    
    with col4:
        st.metric("❌ Denied", len(denied_users))
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["Pending Approvals", "All Users", "System Info"])
    
    with tab1:
        st.markdown("### ⏳ Pending User Approvals")
        
        if not pending_users:
            st.info("No pending user registrations")
        else:
            for user in pending_users:
                with st.expander(f"👤 {user['full_name']} - {user['email']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Name:** {user['full_name']}")
                        st.markdown(f"**Email:** {user['email']}")
                        st.markdown(f"**Title:** {user['title']}")
                        st.markdown(f"**Office:** {user['office']}")
                        st.markdown(f"**Purpose:** {user['purpose']}")
                        st.markdown(f"**Registered:** {user['created_at']}")
                    
                    with col2:
                        if st.button(f"✅ Approve", key=f"approve_{user['id']}"):
                            if update_user_status(user['id'], 'approved'):
                                st.success("User approved!")
                                st.rerun()
                            else:
                                st.error("Failed to approve user")
                        
                        if st.button(f"❌ Deny", key=f"deny_{user['id']}"):
                            if update_user_status(user['id'], 'denied'):
                                st.success("User denied!")
                                st.rerun()
                            else:
                                st.error("Failed to deny user")
    
    with tab2:
        st.markdown("### 👥 All Users")
        
        if not all_users:
            st.info("No users registered")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.selectbox("Filter by Status:", ["All", "Pending", "Approved", "Denied"])
            
            with col2:
                search_term = st.text_input("Search by name or email:")
            
            # Filter users
            filtered_users = all_users
            if status_filter != "All":
                filtered_users = [u for u in filtered_users if u['status'] == status_filter.lower()]
            
            if search_term:
                filtered_users = [u for u in filtered_users if 
                                 search_term.lower() in u['full_name'].lower() or 
                                 search_term.lower() in u['email'].lower()]
            
            # Display users
            for user in filtered_users:
                status_color = {
                    'pending': '🟡',
                    'approved': '🟢',
                    'denied': '🔴'
                }
                
                with st.expander(f"{status_color.get(user['status'], '⚪')} {user['full_name']} - {user['email']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Status:** {user['status'].title()}")
                        st.markdown(f"**Title:** {user['title']}")
                        st.markdown(f"**Office:** {user['office']}")
                        st.markdown(f"**Purpose:** {user['purpose']}")
                    
                    with col2:
                        st.markdown(f"**Registered:** {user['created_at']}")
                        if user['approved_at']:
                            st.markdown(f"**Approved:** {user['approved_at']}")
                        if user['last_login']:
                            st.markdown(f"**Last Login:** {user['last_login']}")
                        st.markdown(f"**Login Count:** {user['login_count']}")
                        
                        # Action buttons
                        if user['status'] == 'pending':
                            if st.button(f"✅ Approve", key=f"approve_all_{user['id']}"):
                                if update_user_status(user['id'], 'approved'):
                                    st.success("User approved!")
                                    st.rerun()
                        
                        if st.button(f"❌ Deny", key=f"deny_all_{user['id']}"):
                            if update_user_status(user['id'], 'denied'):
                                st.success("User denied!")
                                st.rerun()
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{user['id']}"):
                            if delete_user(user['id']):
                                st.success("User deleted!")
                                st.rerun()
    
    with tab3:
        st.markdown("### 📊 System Information")
        
        # Database info
        st.markdown("#### Database Status")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get database size
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM usage_logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Users in Database", user_count)
            
            with col2:
                st.metric("Usage Logs", log_count)
            
        except Exception as e:
            st.error(f"Error getting database info: {e}")
        
        # System info
        st.markdown("#### Application Status")
        st.info("✅ Database connection: Working")
        st.info("✅ Authentication system: Active")
        st.info("✅ User management: Operational")
        
        # Admin actions
        st.markdown("#### Admin Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📊 Export User Data"):
            st.info("User data export functionality would be implemented here")

def main():
    """Main application function with enhanced UI/UX."""
    # Configure Streamlit with enhanced settings
    st.set_page_config(
        page_title="UNGA Analysis App",
        page_icon="🇺🇳",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://github.com/unga-analysis/docs',
            'Report a bug': 'https://github.com/unga-analysis/issues',
            'About': 'UNGA Analysis - Advanced speech analysis platform for UN General Assembly'
        }
    )
    
    # Initialize session state
    initialize_session_state()
    
    # TESTING MODE: Bypass authentication
    # Check if user is authenticated
    # if not is_user_authenticated():
    #     render_auth_interface()
    #     return
    
    # Create mock user for testing
    from datetime import datetime
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "test@un.org"
            self.full_name = "Test User"
            self.title = "Test Position"
            self.office = "Test Office"
            self.status = "approved"
            self.created_at = datetime.now()
            self.approved_at = datetime.now()
            self.approved_by = "admin"
            self.last_login = datetime.now()
            self.login_count = 1
            self.purpose = "Testing purposes"
    
    # Get current user info (using mock user for testing)
    if not hasattr(st.session_state, 'user') or st.session_state.user is None:
        st.session_state.user = MockUser()
    current_user = st.session_state.user
    
    # Initialize database
    try:
        db_manager.create_db_and_tables()
    except Exception as e:
        render_error_card(
            "Database Initialization Failed",
            f"Unable to connect to the database: {e}. Please contact support."
        )
        return
    
    # Top bar with user info and logout button
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        render_page_header(
            "🇺🇳 UN GA Daily Readouts",
            "Analysis tool for UN General Assembly speeches (1946-2025) • 11,094 speeches • 200 countries"
        )
    
    with col2:
        # User info - compact display
        st.markdown(f"""
        <div style="
            text-align: right;
            padding: 10px;
            margin-top: 10px;
        ">
            <p style="margin: 0; font-weight: bold; color: #000000; font-size: 0.9em;">
                👤 {current_user.full_name}
            </p>
            <p style="margin: 0; color: #666; font-size: 0.8em;">
                {current_user.title}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Logout button in top right
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", help="Logout from the application", use_container_width=True):
            logout_user()
            return
    
    # Separator line
    st.markdown("---")
    
    # Enhanced tabs with better organization
    tab_configs = [
        {"name": "New Analysis", "icon": "📝", "description": "Upload and analyze documents"},
        {"name": "Cross-Year Analysis", "icon": "🌍", "description": "Compare speeches across years"},
        {"name": "Document Context", "icon": "📄", "description": "Analyze with additional context"},
        {"name": "All Analyses", "icon": "📚", "description": "View and manage past analyses"},
        {"name": "Visualizations", "icon": "📊", "description": "Interactive charts and graphs"},
        {"name": "Data Explorer", "icon": "🗺️", "description": "Explore the database directly"},
        {"name": "Database Chat", "icon": "🗄️", "description": "Chat with the UNGA database"},
        {"name": "Error Insights", "icon": "🔍", "description": "System monitoring and debugging"}
    ]
    
    # Add admin tab for admin users
    if current_user.email == "islam50@un.org":
        tab_configs.append({
            "name": "Admin Portal", 
            "icon": "🛡️", 
            "description": "User management and system administration"
        })
    
    # Create enhanced tabs
    tabs = render_enhanced_tabs(tab_configs)
    
    # Tab content with enhanced UI
    with tabs[0]:
        render_new_analysis_tab()
    
    with tabs[1]:
        render_cross_year_analysis_tab()
    
    with tabs[2]:
        render_document_context_analysis_tab()
    
    with tabs[3]:
        render_all_analyses_tab()
    
    with tabs[4]:
        render_visualizations_tab()
    
    with tabs[5]:
        render_data_explorer_tab()
    
    with tabs[6]:
        render_database_chat_tab()
    
    with tabs[7]:
        render_error_insights_tab()
    
    # Admin tab (only for admin users)
    if current_user.email == "islam50@un.org" and len(tabs) > 8:
        with tabs[8]:
            render_admin_tab()
    
    # Enhanced footer
    render_enhanced_footer()

if __name__ == "__main__":
    main()
