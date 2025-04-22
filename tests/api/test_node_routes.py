"""Tests for the Node API tools."""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


@pytest.fixture
def mock_mcp():
    """Mock MCP server for testing."""
    class MockMCP:
        def __init__(self):
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
    
    return MockMCP()


@pytest.fixture
def mock_context():
    """Mock Context for testing."""
    return MagicMock()


@pytest.fixture
def mock_node_api():
    """Mock node API for testing."""
    with patch("ergo_explorer.tools.node.get_node_wallet_status") as mock_wallet:
        
        # Mock get_node_wallet_status
        mock_wallet.return_value = asyncio.Future()
        mock_wallet.return_value.set_result({
            "height": 1000000,
            "balance": 100000000000,
            "unlocked_balance": 95000000000,
            "address_count": 5
        })
        
        yield {
            "wallet": mock_wallet
        }


@pytest.fixture
def register_tools(mock_mcp, mock_node_api):
    """Register the node tools for testing."""
    from ergo_explorer.api.routes.node import register_node_routes
    register_node_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_node_wallet(register_tools, mock_context, mock_node_api):
    """Test the get_node_wallet tool."""
    # Get the tool
    get_node_wallet = register_tools.tools["get_node_wallet"]
    
    # Call the tool
    result = await get_node_wallet(mock_context)
    
    # Check the result
    assert "100000000000" in result or "100 ERG" in result
    assert "95000000000" in result or "95 ERG" in result
    assert "1000000" in result
    assert "5" in result
    
    # Verify the mock was called
    mock_node_api["wallet"].assert_called_once() 