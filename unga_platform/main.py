"""
UN GA Daily Readouts - Enterprise Application Entry Point
Professional, enterprise-grade Streamlit application for UN General Assembly speech analysis

Architecture: Clean Architecture with Domain-Driven Design
Patterns: Repository, Use Case, Dependency Injection, Factory
Security: Comprehensive input validation, rate limiting, authentication
Monitoring: Enterprise logging, error handling, performance tracking

Developed by: SMU Data Team
Version: 2.1.0
"""

import streamlit as st
import logging
import sys
from pathlib import Path
from typing import Optional

# Add the platform to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('unga_platform.log')
    ]
)

logger = logging.getLogger(__name__)

def initialize_application():
    """Initialize the enterprise application."""
    try:
        # Import after path setup
        from infrastructure.config import ApplicationConfig
        from infrastructure.dependency_injection import Container
        from ui.streamlit_app import StreamlitApplication
        
        # Load configuration
        config = ApplicationConfig.from_env()
        
        # Validate configuration
        errors = config.validate()
        if errors:
            st.error("❌ Configuration Errors:")
            for error in errors:
                st.error(f"  - {error}")
            st.stop()
        
        # Initialize dependency injection container
        container = Container()
        container.configure(config)
        
        # Initialize application
        app = StreamlitApplication(container, config)
        
        logger.info("Enterprise application initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        st.error(f"❌ Application Initialization Error: {e}")
        st.error("Please check your configuration and try again.")
        st.stop()

def main():
    """Main application entry point."""
    try:
        # Initialize the enterprise application
        app = initialize_application()
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected application error: {e}")
        st.error(f"❌ Unexpected Error: {e}")
        st.error("Please refresh the page or contact support.")

if __name__ == "__main__":
    main()
