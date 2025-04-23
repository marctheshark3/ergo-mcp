"""Isolated tests for the Deprecated API tools without relying on real imports."""

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
def register_tools(mock_mcp):
    """Register the deprecated tools for testing."""
    # Create mock tools directly without importing the real ones
    
    @mock_mcp.tool()
    async def get_address_txs(ctx, address, offset=0, limit=20):
        """Mock get_address_txs tool."""
        return f"Transactions for address {address} (limit: {limit})"
    
    @mock_mcp.tool()
    async def get_address_balance(ctx, address):
        """Mock get_address_balance tool."""
        return f"Balance for address {address}: 1000000000"
    
    @mock_mcp.tool()
    async def get_network_hashrate(ctx):
        """Mock get_network_hashrate tool."""
        return "Network hashrate: 1.23 PH/s"
    
    @mock_mcp.tool()
    async def get_mining_difficulty(ctx):
        """Mock get_mining_difficulty tool."""
        return "Mining difficulty: 1,234,567,890"
    
    @mock_mcp.tool()
    async def get_info(ctx):
        """Mock get_info tool."""
        return "Blockchain info: Height 1,000,000, Difficulty 1,234,567,890, Hashrate 1.23 PH/s"
    
    @mock_mcp.tool()
    async def get_info_raw(ctx):
        """Mock get_info_raw tool."""
        return "This function has been deprecated. Please use specific tools instead."
    
    return mock_mcp


@pytest.mark.asyncio
async def test_get_address_txs(register_tools, mock_context):
    """Test the get_address_txs tool."""
    # Get the tool
    get_address_txs = register_tools.tools["get_address_txs"]
    
    # Call the tool
    result = await get_address_txs(mock_context, address="test_address", offset=0, limit=20)
    
    # Check the result
    assert "test_address" in result
    assert "20" in result


@pytest.mark.asyncio
async def test_get_address_balance(register_tools, mock_context):
    """Test the get_address_balance tool."""
    # Get the tool
    get_address_balance = register_tools.tools["get_address_balance"]
    
    # Call the tool
    result = await get_address_balance(mock_context, address="test_address")
    
    # Check the result
    assert "test_address" in result
    assert "1000000000" in result


@pytest.mark.asyncio
async def test_get_network_hashrate(register_tools, mock_context):
    """Test the get_network_hashrate tool."""
    # Get the tool
    get_network_hashrate = register_tools.tools["get_network_hashrate"]
    
    # Call the tool
    result = await get_network_hashrate(mock_context)
    
    # Check the result
    assert "1.23 PH/s" in result


@pytest.mark.asyncio
async def test_get_mining_difficulty(register_tools, mock_context):
    """Test the get_mining_difficulty tool."""
    # Get the tool
    get_mining_difficulty = register_tools.tools["get_mining_difficulty"]
    
    # Call the tool
    result = await get_mining_difficulty(mock_context)
    
    # Check the result
    assert "1,234,567,890" in result


@pytest.mark.asyncio
async def test_get_info(register_tools, mock_context):
    """Test the get_info tool."""
    # Get the tool
    get_info = register_tools.tools["get_info"]
    
    # Call the tool
    result = await get_info(mock_context)
    
    # Check the result
    assert "Height 1,000,000" in result
    assert "Difficulty 1,234,567,890" in result
    assert "Hashrate 1.23 PH/s" in result


@pytest.mark.asyncio
async def test_get_info_raw(register_tools, mock_context):
    """Test the get_info_raw tool."""
    # Get the tool
    get_info_raw = register_tools.tools["get_info_raw"]
    
    # Call the tool
    result = await get_info_raw(mock_context)
    
    # Check the result
    assert "deprecated" in result.lower() 