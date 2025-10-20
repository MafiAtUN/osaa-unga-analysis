"""
Tests for core functionality
"""

import pytest
from src.unga_analysis.core.llm import get_available_models
from src.unga_analysis.core.classify import get_au_members


def test_get_au_members():
    """Test AU members retrieval."""
    members = get_au_members()
    assert isinstance(members, list)
    assert len(members) > 0
    assert "Nigeria" in members


def test_get_available_models():
    """Test model availability check."""
    models = get_available_models()
    assert isinstance(models, list)
