"""
Configuration and fixtures for pytest.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_httpx_client():
    """Mock for httpx client."""
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance
        client_instance.get.return_value = AsyncMock()
        client_instance.post.return_value = AsyncMock()
        yield client_instance

@pytest.fixture
def mock_node_response():
    """Mock response from Ergo node API."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "result": "success",
        "data": {
            "balance": 1000000000,
            "transactions": []
        }
    }
    mock_response.status_code = 200
    return mock_response

@pytest.fixture
def mock_explorer_response():
    """Mock response from Ergo Explorer API."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "items": [],
        "total": 0
    }
    mock_response.status_code = 200
    return mock_response

@pytest.fixture
def sample_address():
    """Sample Ergo address for testing."""
    return "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"

@pytest.fixture
def sample_transaction_id():
    """Sample Ergo transaction ID for testing."""
    return "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"

@pytest.fixture
def sample_block_id():
    """Sample Ergo block ID for testing."""
    return "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7"

@pytest.fixture
def sample_token_id():
    """Sample Ergo token ID for testing."""
    return "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"

@pytest.fixture
def sample_block_height():
    """Sample Ergo block height for testing."""
    return 1000000 