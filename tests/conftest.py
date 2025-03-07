"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import patch
import os

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'ERGO_EXPLORER_API': 'https://api.ergoplatform.com/api/v1',
        'ERGO_NODE_API': 'http://localhost:9053',
        'ERGO_NODE_API_KEY': 'test_api_key',
        'TOKENJAY_API_URL': 'https://api.tokenjay.app',
        'ERGOWATCH_API_URL': 'https://api.ergo.watch',
        'SERVER_PORT': '3001'
    }):
        yield

@pytest.fixture
def mock_http_response():
    """Mock HTTP response for API calls."""
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
        
        async def json(self):
            return self.json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    return MockResponse

@pytest.fixture
def mock_error_response():
    """Mock error response for API calls."""
    class MockErrorResponse:
        def __init__(self, status_code=500):
            self.status_code = status_code
        
        def raise_for_status(self):
            raise Exception(f"HTTP {self.status_code}")
    
    return MockErrorResponse 