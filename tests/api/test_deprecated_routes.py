"""Tests for the Deprecated API tools."""

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
def mock_routes():
    """Mock the routes that deprecated functions redirect to."""
    with patch("ergo_explorer.api.routes.block.get_block_transactions") as mock_block_transactions, \
         patch("ergo_explorer.api.routes.token.get_token_holders") as mock_token_holders, \
         patch("ergo_explorer.api.routes.blockchain.blockchain_status") as mock_blockchain_status:
            
        # Mock get_block_transactions
        mock_block_transactions.return_value = asyncio.Future()
        mock_block_transactions.return_value.set_result("Block transactions result")
        
        # Mock get_token_holders
        mock_token_holders.return_value = asyncio.Future()
        mock_token_holders.return_value.set_result("Token holders result")
        
        # Mock blockchain_status
        mock_blockchain_status.return_value = asyncio.Future()
        mock_blockchain_status.return_value.set_result("Blockchain status result")
        
        yield {
            "block_transactions": mock_block_transactions,
            "token_holders": mock_token_holders,
            "blockchain_status": mock_blockchain_status
        }


@pytest.fixture
def register_tools(mock_mcp, mock_routes):
    """Register the deprecated tools for testing."""
    from ergo_explorer.api.routes.deprecated import register_deprecated_routes
    register_deprecated_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_address_txs(register_tools, mock_context, mock_routes):
    """Test the get_address_txs tool."""
    # Get the tool
    get_address_txs = register_tools.tools["get_address_txs"]
    
    # Call the tool
    result = await get_address_txs(mock_context, address="test_address", offset=0, limit=20)
    
    # Check the result
    assert result == "Block transactions result"
    
    # Verify the mock was called with correct parameters
    mock_routes["block_transactions"].assert_called_once_with(mock_context, "test_address", 20)


@pytest.mark.asyncio
async def test_get_address_balance(register_tools, mock_context, mock_routes):
    """Test the get_address_balance tool."""
    # Get the tool
    get_address_balance = register_tools.tools["get_address_balance"]
    
    # Call the tool
    result = await get_address_balance(mock_context, address="test_address")
    
    # Check the result
    assert result == "Token holders result"
    
    # Verify the mock was called with correct parameters
    mock_routes["token_holders"].assert_called_once_with(mock_context, "test_address", False, True)


@pytest.mark.asyncio
async def test_get_network_hashrate(register_tools, mock_context, mock_routes):
    """Test the get_network_hashrate tool."""
    # Get the tool
    get_network_hashrate = register_tools.tools["get_network_hashrate"]
    
    # Call the tool
    result = await get_network_hashrate(mock_context)
    
    # Check the result
    assert result == "Blockchain status result"
    
    # Verify the mock was called
    mock_routes["blockchain_status"].assert_called_once_with(mock_context)


@pytest.mark.asyncio
async def test_get_mining_difficulty(register_tools, mock_context, mock_routes):
    """Test the get_mining_difficulty tool."""
    # Get the tool
    get_mining_difficulty = register_tools.tools["get_mining_difficulty"]
    
    # Call the tool
    result = await get_mining_difficulty(mock_context)
    
    # Check the result
    assert result == "Blockchain status result"
    
    # Verify the mock was called
    mock_routes["blockchain_status"].assert_called_once_with(mock_context)


@pytest.mark.asyncio
async def test_get_info(register_tools, mock_context, mock_routes):
    """Test the get_info tool."""
    # Get the tool
    get_info = register_tools.tools["get_info"]
    
    # Call the tool
    result = await get_info(mock_context)
    
    # Check the result
    assert result == "Blockchain status result"
    
    # Verify the mock was called
    mock_routes["blockchain_status"].assert_called_once_with(mock_context)


@pytest.mark.asyncio
async def test_get_info_raw(register_tools, mock_context):
    """Test the get_info_raw tool."""
    # Get the tool
    get_info_raw = register_tools.tools["get_info_raw"]
    
    # Call the tool
    result = await get_info_raw(mock_context)
    
    # Check the result
    assert "deprecated" in result.lower() 