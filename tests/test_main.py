"""
Test suite for the main UNGA Analysis application
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all main imports work correctly."""
    try:
        from src.unga_analysis.main import main
        from src.unga_analysis.core.user_auth import UserAuthManager
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage
        from src.unga_analysis.ui.auth_interface import render_auth_interface
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_database_connection():
    """Test database connection."""
    try:
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
        # Test basic connection
        result = db_manager.conn.execute("SELECT 1").fetchone()
        assert result[0] == 1
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_country_manager():
    """Test country manager functionality."""
    try:
        from src.unga_analysis.utils.country_manager import country_manager
        countries = country_manager.get_all_countries()
        assert len(countries) > 0
        assert "United States" in countries
        assert "Algeria" in countries
    except Exception as e:
        pytest.fail(f"Country manager test failed: {e}")

def test_user_auth():
    """Test user authentication system."""
    try:
        from src.unga_analysis.core.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        # Test that the manager can be initialized
        assert auth_manager is not None
    except Exception as e:
        pytest.fail(f"User auth test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
