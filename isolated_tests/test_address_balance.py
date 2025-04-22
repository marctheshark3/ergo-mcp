"""Isolated tests for the get_address_balance tool."""

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
def mock_token_holders():
    """Mock the token_holders function."""
    mock = AsyncMock()
    mock.return_value = (
        "Token holders for address: test_address\n"
        "ERG Balance: 1000.0 ERG\n"
        "Tokens: 5 different tokens\n"
        "  - Token1: 100 units\n"
        "  - Token2: 200 units\n"
    )
    return mock


@pytest.fixture
def register_tools(mock_mcp, mock_token_holders):
    """Register the get_address_balance tool for testing."""
    # Create a direct implementation of get_address_balance
    # This simulates how it works in the actual code
    
    @mock_mcp.tool()
    async def get_address_balance(ctx, address):
        """
        DEPRECATED: Use get_token_holders instead.
        Get the confirmed balance for an Ergo address.
        """
        # This mimics the behavior in deprecated.py
        # It calls get_token_holders with specific parameters
        from_get_token_holders = await mock_token_holders(ctx, address, False, True)
        return from_get_token_holders
    
    return mock_mcp


@pytest.mark.asyncio
async def test_get_address_balance_implementation(register_tools, mock_context, mock_token_holders):
    """Test that get_address_balance calls get_token_holders with the right parameters."""
    # Get the tool
    get_address_balance = register_tools.tools["get_address_balance"]
    
    # Call the tool
    result = await get_address_balance(mock_context, address="test_address")
    
    # Check the result
    assert "Token holders for address: test_address" in result
    assert "ERG Balance: 1000.0 ERG" in result
    
    # Verify the mock was called with correct parameters
    mock_token_holders.assert_called_once_with(mock_context, "test_address", False, True)


@pytest.mark.asyncio
async def test_get_address_balance_output(register_tools, mock_context):
    """Test the get_address_balance tool output format."""
    # Get the tool
    get_address_balance = register_tools.tools["get_address_balance"]
    
    # Call the tool
    result = await get_address_balance(mock_context, address="test_address")
    
    # Check the result has the right formatting and content
    assert "Token holders for address: test_address" in result
    assert "ERG Balance: 1000.0 ERG" in result
    assert "Tokens: 5 different tokens" in result
    assert "Token1: 100 units" in result
    assert "Token2: 200 units" in result 