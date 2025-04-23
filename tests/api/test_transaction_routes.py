"""Tests for the Transaction API tools."""

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
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
        "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
        "timestamp": 1620000000000,
        "inputs": [
            {
                "boxId": "input1",
                "value": 1000000000
            }
        ],
        "outputs": [
            {
                "boxId": "output1",
                "value": 990000000
            },
            {
                "boxId": "output2",
                "value": 9000000
            }
        ],
        "size": 500
    }


@pytest.fixture
def mock_transaction_api():
    """Mock transaction API for testing."""
    with patch("ergo_explorer.tools.transaction.get_transaction") as mock_get_tx, \
         patch("ergo_explorer.tools.transaction.get_transaction_by_index") as mock_get_tx_by_index:
        
        # Mock get_transaction
        mock_get_tx.return_value = asyncio.Future()
        mock_get_tx.return_value.set_result({
            "id": "tx1",
            "blockId": "block1",
            "timestamp": 1620000000000,
            "inputs": [{"boxId": "input1", "value": 1000000000}],
            "outputs": [{"boxId": "output1", "value": 990000000}, {"boxId": "output2", "value": 9000000}],
            "size": 500
        })
        
        # Mock get_transaction_by_index
        mock_get_tx_by_index.return_value = asyncio.Future()
        mock_get_tx_by_index.return_value.set_result({
            "id": "tx2",
            "blockId": "block2",
            "timestamp": 1630000000000,
            "inputs": [{"boxId": "input3", "value": 5000000000}],
            "outputs": [{"boxId": "output3", "value": 4950000000}, {"boxId": "output4", "value": 45000000}],
            "size": 700
        })
        
        yield {
            "get_transaction": mock_get_tx,
            "get_transaction_by_index": mock_get_tx_by_index
        }


@pytest.fixture
def register_tools(mock_mcp, mock_transaction_api):
    """Register the transaction tools for testing."""
    from ergo_explorer.api.routes.transaction import register_transaction_routes
    register_transaction_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_transaction(register_tools, mock_context, mock_transaction_api):
    """Test the get_transaction tool."""
    # Get the tool
    get_transaction = register_tools.tools["get_transaction"]
    
    # Call the tool
    result = await get_transaction(mock_context, tx_id="tx1")
    
    # Check the result
    assert "tx1" in result
    assert "block1" in result
    assert "990000000" in result or "9000000" in result
    
    # Verify the mock was called with correct parameters
    mock_transaction_api["get_transaction"].assert_called_once_with("tx1")


@pytest.mark.asyncio
async def test_get_transaction_by_index(register_tools, mock_context, mock_transaction_api):
    """Test the get_transaction_by_index tool."""
    # Get the tool
    get_transaction_by_index = register_tools.tools["get_transaction_by_index"]
    
    # Call the tool
    result = await get_transaction_by_index(mock_context, index=123)
    
    # Check the result
    assert "tx2" in result
    assert "block2" in result
    assert "4950000000" in result or "45000000" in result
    
    # Verify the mock was called with correct parameters
    mock_transaction_api["get_transaction_by_index"].assert_called_once_with(123) 