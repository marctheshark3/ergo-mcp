"""
Common test configuration and fixtures for Ergo Explorer MCP tests.
"""

import pytest
import os
import logging
from unittest.mock import AsyncMock, MagicMock, patch
# Import needed for the test_mcp fixture
from ergo_explorer.server_config import create_server
# Import needed for mock_context fixture
from mcp.server.fastmcp import Context

# Patch the logging configuration to prevent permission errors
@pytest.fixture(autouse=True, scope="session")
def mock_logging():
    """
    Mock logging to prevent permission errors during tests.
    This fixture runs automatically for all tests.
    """
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure basic logging to the test logs directory
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "test.log")),
            logging.StreamHandler()
        ]
    )
    
    # Patch get_logger to return a standard logger rather than setting up file handlers
    with patch("ergo_explorer.logging_config.get_logger", return_value=logging.getLogger("test")), \
         patch("ergo_explorer.logging_config.configure_logging", return_value=logging.getLogger("test")):
        yield

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
    return "9fE5o7913CKKe6wvNgM11vULjTuKiopPcvCaj7t2zcJWXM2gcLu"

@pytest.fixture
def sample_token_id():
    """Sample token ID for tests."""
    return "52f4544ce8a420d484ece16f9b984d81c23e46971ef5e37c29382ac50f80d5bd"

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
    return "9a35191fcb3e485e95f79cfa21364def40168b5c25b772be28926b6c7fc44fc6"

@pytest.fixture
def sample_block_id():
    """Sample Ergo block ID for testing."""
    return "b490c792336c962fd0ae57ea8e56da8f6a234e4a83f12e43901aa0eb66bb172e"

@pytest.fixture
def sample_block_height():
    """Sample Ergo block height for testing."""
    return 1200000

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