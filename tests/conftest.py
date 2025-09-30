# ScrAI Test Configuration
"""
Test configuration and fixtures for ScrAI testing.
"""

import pytest
import os
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "simulation": {
            "max_phases": 100,
            "default_scenario": "basic_test"
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 1000
        }
    }

@pytest.fixture
def temp_firestore_client():
    """Mock Firestore client for testing."""
    # This will be implemented when we create the data layer
    pass