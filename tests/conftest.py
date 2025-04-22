"""
Common test configuration and fixtures for Ergo Explorer MCP tests.
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock
# Import needed for the test_mcp fixture
from ergo_explorer.server_config import create_server
# Import needed for mock_context fixture
from mcp.server.fastmcp import Context

# Skip these test files temporarily until we update the imports to match the new code structure
collect_ignore = [
    # "unit/test_server.py", # Removed as it has been updated
    # "unit/test_address_tools.py", # Removed as it has been updated
    # "unit/test_network_tools.py", # Removed as it has been updated
    # "unit/test_token_tools.py", # Removed as it has been updated
    # "unit/test_misc_tools.py", # Removed as the file is obsolete
    # "unit/test_block_tools.py", # Removed as redundant
    # "unit/test_node_tools.py", # Removed as redundant/needs rework
    # "unit/test_transaction_tools.py", # Removed as redundant
    # "unit/test_token_holders.py" # Removed as it's being updated
]

# Sample data for tests
@pytest.fixture
def sample_address():
    """Sample Ergo address for tests."""
    return "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"

@pytest.fixture
def sample_token_id():
    """Sample token ID for tests."""
    return "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"

@pytest.fixture
def mock_httpx_client():
    """Mock HTTPX client for API tests."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    return mock_client

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
def sample_transaction_id():
    """Sample Ergo transaction ID for testing."""
    return "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"

@pytest.fixture
def sample_block_id():
    """Sample Ergo block ID for testing."""
    return "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7"

@pytest.fixture
def sample_block_height():
    """Sample Ergo block height for testing."""
    return 1000000

# New fixture for the test MCP server
@pytest.fixture(scope="session") # Scope session might be better if server creation is slow
def test_mcp():
    """Create a test MCP server instance with all routes registered."""
    server = create_server()
    return server

# New fixture for mock context
@pytest.fixture
def mock_context():
    """Create a mock context object for MCP tool functions."""
    ctx = MagicMock(spec=Context)
    # Add attributes commonly used by tools if known, otherwise keep minimal
    ctx.path = "mock/tool/path"
    ctx.method = "POST" # Assuming tool calls are POSTs
    ctx.json = {}      # Mock JSON payload if needed
    ctx.headers = {}   # Mock headers if needed
    ctx.query_params = {} # Mock query params if needed
    # Add other attributes as necessary based on Context definition or tool usage
    # ctx.request = AsyncMock() 
    return ctx 