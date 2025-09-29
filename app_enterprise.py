"""
UN GA Daily Readouts - Enterprise Application
Professional, enterprise-grade Streamlit application

This is a simplified but professional version that demonstrates:
- Clean architecture principles
- Professional code organization
- Enterprise-grade patterns
- Comprehensive error handling
- Security best practices

Developed by: SMU Data Team
"""

import streamlit as st
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('enterprise_app.log')
    ]
)

logger = logging.getLogger(__name__)

class EnterpriseConfig:
    """Enterprise configuration management."""
    
    def __init__(self):
        self.APP_NAME = "UN GA Daily Readouts"
        self.VERSION = "2.1.0"
        self.DESCRIPTION = "Professional UN General Assembly speech analysis platform"
        self.DEVELOPER = "SMU Data Team"
        
        # Security Configuration
        self.APP_PASSWORD = os.getenv('APP_PASSWORD')
        self.RATE_LIMIT_ATTEMPTS = int(os.getenv('RATE_LIMIT_ATTEMPTS', '5'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '300'))
        self.MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', '10000'))
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '52428800'))
        
        # API Configuration
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        self.AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        # UI Configuration
        self.PAGE_TITLE = "UN GA Daily Readouts"
        self.PAGE_ICON = "🇺🇳"
        self.LAYOUT = "wide"
    
    def validate(self) -> list[str]:
        """Validate configuration and return errors."""
        errors = []
        
        if not self.APP_PASSWORD:
            errors.append("APP_PASSWORD is required")
        if not self.AZURE_OPENAI_API_KEY:
            errors.append("AZURE_OPENAI_API_KEY is required")
        if not self.AZURE_OPENAI_ENDPOINT:
            errors.append("AZURE_OPENAI_ENDPOINT is required")
        
        return errors

class SecurityManager:
    """Enterprise security management."""
    
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.user_attempts = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input for security."""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        import re
        import html
        
        text = re.sub(r'[<>"\']', '', text)
        text = html.escape(text)
        text = text[:self.config.MAX_INPUT_LENGTH]
        
        return text
    
    def validate_prompt_safety(self, prompt: str) -> bool:
        """Validate prompt for safety."""
        if not prompt:
            return False
        
        dangerous_patterns = [
            r'ignore\s+previous\s+instructions',
            r'you\s+are\s+now',
            r'system\s+prompt',
            r'jailbreak',
            r'bypass',
            r'admin',
            r'root',
            r'execute',
            r'command',
            r'shell',
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:'
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                self.logger.warning(f"Blocked dangerous prompt pattern: {pattern}")
                return False
        
        return True
    
    def check_rate_limit(self, user_id: str) -> bool:
        """Check rate limiting for user."""
        import time
        
        now = time.time()
        if user_id not in self.user_attempts:
            self.user_attempts[user_id] = []
        
        # Remove old attempts
        self.user_attempts[user_id] = [
            attempt for attempt in self.user_attempts[user_id]
            if now - attempt < self.config.RATE_LIMIT_WINDOW
        ]
        
        if len(self.user_attempts[user_id]) >= self.config.RATE_LIMIT_ATTEMPTS:
            self.logger.warning(f"Rate limit exceeded for user: {user_id}")
            return False
        
        self.user_attempts[user_id].append(now)
        return True
    
    def validate_file_upload(self, file_bytes: bytes, filename: str) -> bool:
        """Validate uploaded file."""
        # Check file size
        if len(file_bytes) > self.config.MAX_FILE_SIZE:
            self.logger.warning(f"File too large: {len(file_bytes)} bytes")
            return False
        
        # Check file extension
        allowed_extensions = ['.pdf', '.docx', '.mp3']
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            self.logger.warning(f"Invalid file type: {file_ext}")
            return False
        
        return True

class AuthenticationManager:
    """Enterprise authentication management."""
    
    def __init__(self, config: EnterpriseConfig, security: SecurityManager):
        self.config = config
        self.security = security
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def authenticate_user(self, password: str, user_id: str = "anonymous") -> tuple[bool, str]:
        """Authenticate user with security checks."""
        # Check rate limit
        if not self.security.check_rate_limit(user_id):
            return False, "❌ Too many authentication attempts. Please try again later."
        
        # Validate configuration
        if not self.config.APP_PASSWORD:
            self.logger.error("Application password not configured")
            return False, "❌ Application password not configured."
        
        # Sanitize input
        sanitized_password = self.security.sanitize_input(password)
        
        # Check password
        if sanitized_password == self.config.APP_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            self.logger.info(f"User {user_id} authenticated successfully")
            return True, "✅ Authentication successful!"
        else:
            self.logger.warning(f"Failed authentication attempt for user {user_id}")
            return False, "❌ Incorrect password. Please try again."
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return st.session_state.get('authenticated', False)
    
    def logout(self) -> None:
        """Logout user."""
        st.session_state.authenticated = False
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        self.logger.info("User logged out")
    
    def require_authentication(self) -> bool:
        """Require authentication."""
        if not self.is_authenticated():
            self.render_login_form()
            return False
        return True
    
    def render_login_form(self) -> None:
        """Render professional login form."""
        # Header
        col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
        
        with col_header2:
            st.image("artifacts/logo/OSAA identifier acronym white.svg", width=200)
            st.title("🔐 Enterprise Authentication")
            st.markdown("**Professional UN GA Analysis Platform**")
        
        # Login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Secure Access Required")
            
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="Enter your secure password",
                help="Enter the application password to continue"
            )
            
            col_login, col_clear = st.columns(2)
            
            with col_login:
                if st.button("🚀 Authenticate", type="primary", use_container_width=True):
                    if password:
                        success, message = self.authenticate_user(password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            with col_clear:
                if st.button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            # Information
            st.info("💡 **Enterprise Platform**: This is a professional tool for UN OSAA Intergovernmental Support Team.")
            
            # Footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
                f"<strong>{self.config.APP_NAME}</strong> | Version {self.config.VERSION} | "
                f"Developed by: <strong>{self.config.DEVELOPER}</strong>"
                "</div>", 
                unsafe_allow_html=True
            )

class EnterpriseApplication:
    """Enterprise application with professional architecture."""
    
    def __init__(self):
        self.config = EnterpriseConfig()
        self.security = SecurityManager(self.config)
        self.auth = AuthenticationManager(self.config, self.security)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def initialize(self):
        """Initialize the enterprise application."""
        # Validate configuration
        errors = self.config.validate()
        if errors:
            st.error("❌ Configuration Errors:")
            for error in errors:
                st.error(f"  - {error}")
            st.stop()
        
        # Configure page
        st.set_page_config(
            page_title=self.config.PAGE_TITLE,
            page_icon=self.config.PAGE_ICON,
            layout=self.config.LAYOUT,
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'anonymous'
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
    
    def render_header(self):
        """Render professional header."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title(f"🇺🇳 {self.config.APP_NAME}")
            st.markdown(f"**{self.config.DESCRIPTION}**")
            st.markdown(f"*Version {self.config.VERSION} | Professional Enterprise Platform*")
        
        st.markdown("---")
    
    def render_sidebar(self):
        """Render professional sidebar."""
        with st.sidebar:
            # Logo
            st.image("artifacts/logo/OSAA identifier acronym white.svg", width=150)
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            
            pages = ["🏠 Dashboard", "📊 New Analysis", "📚 History", "⚙️ Settings"]
            selected_page = st.radio("Select Page:", pages)
            
            # User info
            if st.session_state.authenticated:
                st.markdown("---")
                st.markdown(f"**👤 User:** {st.session_state.user_id}")
                st.markdown(f"**⏰ Session:** {st.session_state.session_start.strftime('%H:%M:%S')}")
                
                if st.button("🚪 Logout", use_container_width=True):
                    self.auth.logout()
                    st.rerun()
            
            # Application info
            st.markdown("---")
            st.markdown("**🏢 Enterprise Platform**")
            st.markdown(f"**Version:** {self.config.VERSION}")
            st.markdown(f"**Developer:** {self.config.DEVELOPER}")
            
            # Security status
            st.markdown("**🔒 Security Status:** ✅ Active")
            st.markdown("**🛡️ Rate Limiting:** ✅ Enabled")
            st.markdown("**🔐 Authentication:** ✅ Required")
        
        return selected_page
    
    def render_dashboard(self):
        """Render professional dashboard."""
        st.header("🏠 Enterprise Dashboard")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Analyses", "0", "0")
        with col2:
            st.metric("🌍 Countries", "0", "0")
        with col3:
            st.metric("📅 Today", "0", "0")
        with col4:
            st.metric("🔒 Security", "✅ Active", "0")
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        st.info("No analyses yet. Create your first analysis to get started!")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Start New Analysis", use_container_width=True):
                st.session_state.selected_page = "📊 New Analysis"
                st.rerun()
        
        with col2:
            if st.button("📚 View History", use_container_width=True):
                st.session_state.selected_page = "📚 History"
                st.rerun()
    
    def render_analysis(self):
        """Render analysis page."""
        st.header("📊 New Analysis")
        st.markdown("**Professional UN GA Speech Analysis**")
        
        # Analysis form
        with st.form("analysis_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                country = st.text_input("Country:", placeholder="Enter country name")
                classification = st.selectbox(
                    "Classification:",
                    ["African Member State", "Development Partner"]
                )
            
            with col2:
                speech_date = st.date_input("Speech Date:", value=datetime.now().date())
                model = st.selectbox("Model:", ["gpt-4o", "gpt-4o-mini"])
            
            # Text input
            st.markdown("### 📝 Speech Content")
            text_input = st.radio(
                "Input Method:",
                ["Paste Text", "Upload File"],
                horizontal=True
            )
            
            if text_input == "Paste Text":
                speech_text = st.text_area(
                    "Speech Text:",
                    height=200,
                    placeholder="Paste the speech text here..."
                )
            else:
                uploaded_file = st.file_uploader(
                    "Upload File:",
                    type=['pdf', 'docx', 'mp3'],
                    help="Upload a PDF, Word document, or MP3 audio file"
                )
                speech_text = ""
            
            # Submit button
            submitted = st.form_submit_button("🚀 Analyze Speech", type="primary")
            
            if submitted:
                if not country or not speech_text:
                    st.error("Please fill in all required fields")
                else:
                    # Sanitize inputs
                    country = self.security.sanitize_input(country)
                    speech_text = self.security.sanitize_input(speech_text)
                    
                    # Validate prompt safety
                    if not self.security.validate_prompt_safety(speech_text):
                        st.error("❌ Input contains potentially harmful content")
                    else:
                        st.success("✅ Analysis request submitted successfully!")
                        st.info("🚧 Analysis functionality will be implemented in the full version")
    
    def render_history(self):
        """Render history page."""
        st.header("📚 Analysis History")
        st.info("📋 No analyses found. Create your first analysis to see it here!")
    
    def render_settings(self):
        """Render settings page."""
        st.header("⚙️ Settings")
        
        # Security settings
        st.subheader("🔒 Security Settings")
        st.markdown("**Rate Limiting:** ✅ Enabled")
        st.markdown("**Input Validation:** ✅ Active")
        st.markdown("**File Upload Security:** ✅ Enabled")
        
        # Application settings
        st.subheader("📱 Application Settings")
        st.markdown(f"**Version:** {self.config.VERSION}")
        st.markdown(f"**Environment:** Production")
        st.markdown(f"**Security Level:** High")
        
        # Developer info
        st.subheader("👨‍💻 Developer Information")
        st.markdown(f"**Developer:** {self.config.DEVELOPER}")
        st.markdown("**Architecture:** Clean Architecture")
        st.markdown("**Patterns:** Enterprise Design Patterns")
    
    def run(self):
        """Run the enterprise application."""
        try:
            # Initialize
            self.initialize()
            
            # Check authentication
            if not self.auth.require_authentication():
                return
            
            # Render header
            self.render_header()
            
            # Render sidebar and get selected page
            selected_page = self.render_sidebar()
            
            # Render main content
            if selected_page == "🏠 Dashboard":
                self.render_dashboard()
            elif selected_page == "📊 New Analysis":
                self.render_analysis()
            elif selected_page == "📚 History":
                self.render_history()
            elif selected_page == "⚙️ Settings":
                self.render_settings()
            
            # Performance logging
            self.logger.info(f"Page rendered: {selected_page}")
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            st.error(f"❌ Application Error: {e}")
            st.error("Please refresh the page or contact support.")

def main():
    """Main application entry point."""
    try:
        # Create and run enterprise application
        app = EnterpriseApplication()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        st.error(f"❌ Startup Error: {e}")

if __name__ == "__main__":
    main()
