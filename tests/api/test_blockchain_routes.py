"""Tests for the Blockchain API tools."""

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
def mock_blockchain_tools():
    """Mock blockchain tools for testing."""
    with patch("ergo_explorer.tools.blockchain.get_blockchain_height") as mock_height, \
         patch("ergo_explorer.tools.network.get_mempool_info") as mock_mempool, \
         patch("ergo_explorer.tools.node.get_network_status_from_node") as mock_network:
        
        # Mock the get_blockchain_height function
        mock_height.return_value = asyncio.Future()
        mock_height.return_value.set_result("Current Height: 1,000,000")
        
        # Mock the get_mempool_info function
        mock_mempool.return_value = asyncio.Future()
        mock_mempool.return_value.set_result({
            "size": 10,
            "memPoolSize": 1024 * 1024,
            "transactions": [{"id": "tx1"}, {"id": "tx2"}]
        })
        
        # Mock the get_network_status_from_node function
        mock_network.return_value = asyncio.Future()
        mock_network.return_value.set_result({
            "difficulty": 1234567890,
            "hashRate": "1.23 PH/s"
        })
        
        yield {
            "height": mock_height,
            "mempool": mock_mempool,
            "network": mock_network
        }


@pytest.fixture
def register_tools(mock_mcp, mock_blockchain_tools):
    """Register the blockchain tools for testing."""
    with patch("ergo_explorer.api.routes.blockchain.format_network_hashrate") as mock_format_hashrate, \
         patch("ergo_explorer.api.routes.blockchain.format_mining_difficulty") as mock_format_difficulty, \
         patch("ergo_explorer.api.routes.blockchain.format_mempool_info") as mock_format_mempool:
        
        # Mock the format functions
        mock_format_hashrate.return_value = asyncio.Future()
        mock_format_hashrate.return_value.set_result("Network Hashrate: 1.23 PH/s")
        
        mock_format_difficulty.return_value = asyncio.Future()
        mock_format_difficulty.return_value.set_result("Mining Difficulty: 1,234,567,890")
        
        mock_format_mempool.return_value = asyncio.Future()
        mock_format_mempool.return_value.set_result("Mempool Size: 10 transactions (1.0 MB)")
        
        from ergo_explorer.api.routes.blockchain import register_blockchain_routes
        register_blockchain_routes(mock_mcp)
        
        return mock_mcp


@pytest.mark.asyncio
async def test_blockchain_status(register_tools, mock_context, mock_blockchain_tools):
    """Test the blockchain_status tool."""
    # Get the tool
    blockchain_status = register_tools.tools["blockchain_status"]
    
    # Call the tool
    result = await blockchain_status(mock_context)
    
    # Check the result
    assert "Ergo Blockchain Status" in result
    assert "Current State" in result
    assert "Network Metrics" in result
    assert "Performance" in result
    
    # Verify the mocks were called
    mock_blockchain_tools["height"].assert_called_once()
    mock_blockchain_tools["network"].assert_called()


@pytest.mark.asyncio
async def test_mempool_status(register_tools, mock_context, mock_blockchain_tools):
    """Test the mempool_status tool."""
    # Get the tool
    mempool_status = register_tools.tools["mempool_status"]
    
    # Call the tool
    result = await mempool_status(mock_context)
    
    # Check the result
    assert "Mempool Size: 10 transactions" in result
    
    # Verify the mock was called
    mock_blockchain_tools["mempool"].assert_called_once() 