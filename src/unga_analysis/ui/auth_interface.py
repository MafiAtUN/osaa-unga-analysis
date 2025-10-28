"""
User Authentication Interface
Handles user registration, login, and session management
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from ..core.user_auth import user_auth_manager, User
from .enhanced_ui_components import (
    render_page_header, render_info_card, render_success_card, 
    render_warning_card, render_error_card, render_step_guide,
    render_enhanced_footer
)


def render_auth_interface():
    """Render the main authentication interface."""
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    
    # Show appropriate page
    if st.session_state.auth_page == 'login':
        render_login_page()
    elif st.session_state.auth_page == 'register':
        render_registration_page()
    elif st.session_state.auth_page == 'admin':
        render_admin_portal()


def render_login_page():
    """Render the enhanced login page."""
    # Enhanced page header
    render_page_header(
        "🔐 UNGA Analysis Platform",
        "Sign in to access advanced speech analysis tools"
    )
    
    # Welcome information removed as requested
    
    # Login form with enhanced styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4 style="text-align: center; color: #000000; margin-bottom: 20px; font-size: 16px;">
                🔑 Sign In
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input(
                "Email Address:", 
                placeholder="your.email@un.org",
                help="Enter your UN email address"
            )
            password = st.text_input(
                "Password:", 
                type="password",
                help="Enter your password"
            )
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button(
                    "🔑 Login", 
                    use_container_width=True,
                    type="primary"
                )
            
            with col_register:
                register_clicked = st.form_submit_button(
                    "📝 New User? Register", 
                    use_container_width=True
                )
        
        if login_clicked:
            if email and password:
                user = user_auth_manager.authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    user_auth_manager.log_user_activity(user.id, "login")
                    render_success_card(
                        "Login Successful!",
                        f"Welcome back, {user.full_name}! You can now access all features of the UNGA Analysis platform."
                    )
                    st.rerun()
                else:
                    render_error_card(
                        "Login Failed",
                        "Invalid email or password. Please check your credentials and try again."
                    )
            else:
                render_warning_card(
                    "Missing Information",
                    "Please fill in both email and password fields."
                )
        
        if register_clicked:
            st.session_state.auth_page = 'register'
            st.rerun()
        
        # Show registration status if user was redirected
        if 'registration_status' in st.session_state:
            if st.session_state.registration_status['success']:
                render_success_card(
                    "Registration Successful!",
                    st.session_state.registration_status['message']
                )
            else:
                render_error_card(
                    "Registration Failed",
                    st.session_state.registration_status['message']
                )
            del st.session_state.registration_status
    
    # Enhanced footer
    st.markdown("---")
    render_enhanced_footer()


def render_registration_page():
    """Render the registration page."""
    st.title("📝 UNGA Analysis App - Registration")
    st.markdown("**Register for access to the UNGA Analysis Platform**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Create Account")
        st.info("🔒 **UN Official Email Required**: Please use your official UN email address for registration.")
        
        with st.form("registration_form"):
            # Personal Information
            st.markdown("#### Personal Information")
            full_name = st.text_input("Full Name:", placeholder="John Doe")
            email = st.text_input("UN Official Email:", placeholder="john.doe@un.org")
            title = st.text_input("Current Title:", placeholder="Senior Policy Advisor")
            office = st.text_input("Office/Department:", placeholder="Office of the Special Adviser on Africa")
            
            # Purpose of Use
            st.markdown("#### Purpose of Use")
            purpose = st.text_area(
                "Please describe the purpose of your use:",
                placeholder="I will use this platform to analyze UNGA speeches for research on African development policies...",
                height=100
            )
            
            # Password
            st.markdown("#### Security")
            password = st.text_input("Password:", type="password", help="Choose a strong password")
            confirm_password = st.text_input("Confirm Password:", type="password")
            
            # Terms and conditions
            st.markdown("#### Terms and Conditions")
            terms_accepted = st.checkbox(
                "I agree to the terms of use and understand that my registration requires admin approval",
                help="Your registration will be reviewed by an administrator before access is granted"
            )
            
            col_submit, col_back = st.columns(2)
            
            with col_submit:
                submit_clicked = st.form_submit_button("📝 Register", use_container_width=True)
            
            with col_back:
                back_clicked = st.form_submit_button("⬅️ Back to Login", use_container_width=True)
        
        if submit_clicked:
            if not all([full_name, email, title, office, purpose, password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif not terms_accepted:
                st.error("❌ Please accept the terms and conditions")
            elif not email.endswith(('.un.org', '.un.int', '@un.org', '@un.int')):
                st.warning("⚠️ Please use your official UN email address")
            else:
                result = user_auth_manager.register_user(
                    email=email,
                    password=password,
                    full_name=full_name,
                    title=title,
                    office=office,
                    purpose=purpose
                )
                
                if result['success']:
                    st.success("✅ Registration successful! Your account is pending admin approval.")
                    st.info("📧 You will receive an email notification once your account is approved.")
                    st.session_state.auth_page = 'login'
                    st.session_state.registration_status = result
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
        
        if back_clicked:
            st.session_state.auth_page = 'login'
            st.rerun()


def render_admin_portal():
    """Render the admin portal."""
    st.title("🛡️ Admin Portal")
    st.markdown("**User Management and System Administration**")
    
    # No password required for admin portal
    st.session_state.admin_authenticated = True
    
    # Admin dashboard
    st.markdown("### Dashboard")
    
    # Statistics
    all_users = user_auth_manager.get_all_users()
    pending_users = [u for u in all_users if u.status == 'pending']
    approved_users = [u for u in all_users if u.status == 'approved']
    denied_users = [u for u in all_users if u.status == 'denied']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", len(all_users))
    
    with col2:
        st.metric("⏳ Pending", len(pending_users))
    
    with col3:
        st.metric("✅ Approved", len(approved_users))
    
    with col4:
        st.metric("❌ Denied", len(denied_users))
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["Pending Approvals", "All Users", "Usage Analytics"])
    
    with tab1:
        render_pending_approvals(pending_users)
    
    with tab2:
        render_all_users_view(all_users)
    
    with tab3:
        render_usage_analytics(approved_users)
    
    # Logout button
    if st.button("🚪 Logout Admin"):
        st.session_state.admin_authenticated = False
        st.rerun()


def render_pending_approvals(pending_users):
    """Render pending user approvals."""
    st.markdown("### ⏳ Pending User Approvals")
    
    if not pending_users:
        st.info("No pending user registrations")
        return
    
    for user in pending_users:
        with st.expander(f"👤 {user.full_name} - {user.email}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Name:** {user.full_name}")
                st.markdown(f"**Email:** {user.email}")
                st.markdown(f"**Title:** {user.title}")
                st.markdown(f"**Office:** {user.office}")
                st.markdown(f"**Purpose:** {user.purpose}")
                st.markdown(f"**Registered:** {user.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                if st.button(f"✅ Approve", key=f"approve_{user.id}"):
                    if user_auth_manager.approve_user(user.id, "admin"):
                        st.success("User approved!")
                        st.rerun()
                    else:
                        st.error("Failed to approve user")
                
                if st.button(f"❌ Deny", key=f"deny_{user.id}"):
                    if user_auth_manager.deny_user(user.id, "admin"):
                        st.success("User denied!")
                        st.rerun()
                    else:
                        st.error("Failed to deny user")


def render_all_users_view(all_users):
    """Render all users view."""
    st.markdown("### 👥 All Users")
    
    if not all_users:
        st.info("No users registered")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox("Filter by Status:", ["All", "Pending", "Approved", "Denied"])
    
    with col2:
        search_term = st.text_input("Search by name or email:")
    
    # Filter users
    filtered_users = all_users
    if status_filter != "All":
        filtered_users = [u for u in filtered_users if u.status == status_filter.lower()]
    
    if search_term:
        filtered_users = [u for u in filtered_users if 
                         search_term.lower() in u.full_name.lower() or 
                         search_term.lower() in u.email.lower()]
    
    # Display users
    for user in filtered_users:
        status_color = {
            'pending': '🟡',
            'approved': '🟢',
            'denied': '🔴'
        }
        
        with st.expander(f"{status_color.get(user.status, '⚪')} {user.full_name} - {user.email}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Status:** {user.status.title()}")
                st.markdown(f"**Title:** {user.title}")
                st.markdown(f"**Office:** {user.office}")
                st.markdown(f"**Purpose:** {user.purpose}")
            
            with col2:
                st.markdown(f"**Registered:** {user.created_at.strftime('%Y-%m-%d %H:%M')}")
                if user.approved_at:
                    st.markdown(f"**Approved:** {user.approved_at.strftime('%Y-%m-%d %H:%M')}")
                if user.last_login:
                    st.markdown(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Login Count:** {user.login_count}")


def render_usage_analytics(approved_users):
    """Render usage analytics."""
    st.markdown("### 📊 Usage Analytics")
    
    if not approved_users:
        st.info("No approved users to analyze")
        return
    
    # User selection
    user_options = {f"{u.full_name} ({u.email})": u.id for u in approved_users}
    selected_user_name = st.selectbox("Select User:", list(user_options.keys()))
    
    if selected_user_name:
        user_id = user_options[selected_user_name]
        user = next(u for u in approved_users if u.id == user_id)
        
        # Get usage stats
        stats = user_auth_manager.get_user_usage_stats(user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Sessions", stats.get('total_sessions', 0))
        
        with col2:
            total_time = stats.get('total_time_minutes', 0)
            hours = total_time // 60
            minutes = total_time % 60
            st.metric("Total Time", f"{hours}h {minutes}m")
        
        with col3:
            last_login = stats.get('last_login', 'Never')
            st.metric("Last Login", last_login)
        
        # Recent activities
        st.markdown("#### Recent Activities")
        activities = stats.get('recent_activities', [])
        
        if activities:
            for activity in activities:
                action, timestamp, details = activity
                st.markdown(f"**{action}** - {timestamp} - {details}")
        else:
            st.info("No recent activities recorded")


def logout_user():
    """Logout the current user."""
    if st.session_state.user:
        user_auth_manager.log_user_activity(
            st.session_state.user.id, 
            "logout",
            details="User logged out"
        )
    st.session_state.user = None
    st.session_state.auth_page = 'login'
    st.rerun()


def is_user_authenticated() -> bool:
    """Check if user is authenticated."""
    return hasattr(st.session_state, 'user') and st.session_state.user is not None


def get_current_user() -> Optional[User]:
    """Get the current authenticated user."""
    return st.session_state.user if hasattr(st.session_state, 'user') else None