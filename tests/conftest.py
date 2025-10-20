"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample UN General Assembly speech text for testing purposes.
    It contains multiple sentences and should be processed correctly by our
    analysis pipeline.
    """
