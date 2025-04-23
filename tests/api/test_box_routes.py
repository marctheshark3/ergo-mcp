"""Tests for the Box API tools."""

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
def sample_box_data():
    """Sample box data for testing."""
    return {
        "id": "b51a34d3a1e184599137aa25139d282144dab328f0afa1afdeb5f0b6d2ed0923",
        "value": 1000000000,
        "creationHeight": 100000,
        "assets": [
            {
                "tokenId": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
                "amount": 100
            }
        ],
        "additionalRegisters": {},
        "transactionId": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
        "index": 0
    }


@pytest.fixture
def mock_box_api():
    """Mock box API for testing."""
    with patch("ergo_explorer.tools.box.get_box_by_id") as mock_get_box, \
         patch("ergo_explorer.tools.box.get_box_by_index") as mock_get_box_by_index:
        
        # Mock get_box_by_id
        mock_get_box.return_value = asyncio.Future()
        mock_get_box.return_value.set_result({
            "id": "box1",
            "value": 1000000000,
            "creationHeight": 100000,
            "assets": [{"tokenId": "token1", "amount": 100}],
            "additionalRegisters": {},
            "transactionId": "tx1",
            "index": 0
        })
        
        # Mock get_box_by_index
        mock_get_box_by_index.return_value = asyncio.Future()
        mock_get_box_by_index.return_value.set_result({
            "id": "box2",
            "value": 5000000000,
            "creationHeight": 200000,
            "assets": [{"tokenId": "token2", "amount": 500}],
            "additionalRegisters": {},
            "transactionId": "tx2",
            "index": 1
        })
        
        yield {
            "get_box": mock_get_box,
            "get_box_by_index": mock_get_box_by_index
        }


@pytest.fixture
def register_tools(mock_mcp, mock_box_api):
    """Register the box tools for testing."""
    from ergo_explorer.api.routes.box import register_box_routes
    register_box_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_box(register_tools, mock_context, mock_box_api):
    """Test the get_box tool."""
    # Get the tool
    get_box = register_tools.tools["get_box"]
    
    # Call the tool
    result = await get_box(mock_context, box_id="box1")
    
    # Check the result
    assert "box1" in result
    assert "1000000000" in result
    assert "token1" in result
    assert "100" in result
    
    # Verify the mock was called with correct parameters
    mock_box_api["get_box"].assert_called_once_with("box1")


@pytest.mark.asyncio
async def test_get_box_by_index(register_tools, mock_context, mock_box_api):
    """Test the get_box_by_index tool."""
    # Get the tool
    get_box_by_index = register_tools.tools["get_box_by_index"]
    
    # Call the tool
    result = await get_box_by_index(mock_context, index=123)
    
    # Check the result
    assert "box2" in result
    assert "5000000000" in result
    assert "token2" in result
    assert "500" in result
    
    # Verify the mock was called with correct parameters
    mock_box_api["get_box_by_index"].assert_called_once_with(123) 