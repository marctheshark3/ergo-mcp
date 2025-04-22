"""Tests for the Block API tools."""

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
def sample_block_data():
    """Sample block data for testing."""
    return {
        "id": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
        "height": 1000000,
        "timestamp": 1620000000000,
        "transactionsCount": 10,
        "miner": {
            "address": "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"
        },
        "size": 5000,
        "difficulty": 1000000000
    }


@pytest.fixture
def sample_block_transactions():
    """Sample block transactions for testing."""
    return {
        "items": [
            {
                "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
                "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "timestamp": 1620000000000,
                "inputs": [{"boxId": "input1", "value": 1000000000}],
                "outputs": [{"boxId": "output1", "value": 990000000}, {"boxId": "output2", "value": 9000000}],
                "size": 500
            },
            {
                "id": "83a2cdc7b4d2fb994a2af970f6ea95145d43a4df2e47ac9add8e1cad20b655a7",
                "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "timestamp": 1620000000100,
                "inputs": [{"boxId": "input3", "value": 5000000000}],
                "outputs": [{"boxId": "output3", "value": 4950000000}, {"boxId": "output4", "value": 45000000}],
                "size": 700
            }
        ]
    }


@pytest.fixture
def mock_block_api():
    """Mock block API for testing."""
    with patch("ergo_explorer.tools.block.get_block_by_height") as mock_get_by_height, \
         patch("ergo_explorer.tools.block.get_block_by_hash") as mock_get_by_hash, \
         patch("ergo_explorer.tools.block.get_latest_blocks") as mock_get_latest, \
         patch("ergo_explorer.tools.block.get_block_transactions") as mock_get_txs:
        
        # Mock get_block_by_height
        mock_get_by_height.return_value = asyncio.Future()
        mock_get_by_height.return_value.set_result({
            "id": "block1",
            "height": 1000000,
            "timestamp": 1620000000000,
            "transactionsCount": 10,
            "miner": {"address": "address1"},
            "size": 5000,
            "difficulty": 1000000000
        })
        
        # Mock get_block_by_hash
        mock_get_by_hash.return_value = asyncio.Future()
        mock_get_by_hash.return_value.set_result({
            "id": "block2",
            "height": 1000001,
            "timestamp": 1620000060000,
            "transactionsCount": 15,
            "miner": {"address": "address2"},
            "size": 6000,
            "difficulty": 1000000000
        })
        
        # Mock get_latest_blocks
        mock_get_latest.return_value = asyncio.Future()
        mock_get_latest.return_value.set_result([
            {
                "id": "block3",
                "height": 1000002,
                "timestamp": 1620000120000,
                "transactionsCount": 12,
                "miner": {"address": "address3"},
                "size": 5500,
                "difficulty": 1000000000
            },
            {
                "id": "block4",
                "height": 1000003,
                "timestamp": 1620000180000,
                "transactionsCount": 8,
                "miner": {"address": "address4"},
                "size": 4800,
                "difficulty": 1000000000
            }
        ])
        
        # Mock get_block_transactions
        mock_get_txs.return_value = asyncio.Future()
        mock_get_txs.return_value.set_result({
            "items": [
                {
                    "id": "tx1",
                    "blockId": "block1",
                    "timestamp": 1620000000000,
                    "inputs": [{"boxId": "input1", "value": 1000000000}],
                    "outputs": [{"boxId": "output1", "value": 990000000}, {"boxId": "output2", "value": 9000000}],
                    "size": 500
                },
                {
                    "id": "tx2",
                    "blockId": "block1",
                    "timestamp": 1620000000100,
                    "inputs": [{"boxId": "input3", "value": 5000000000}],
                    "outputs": [{"boxId": "output3", "value": 4950000000}, {"boxId": "output4", "value": 45000000}],
                    "size": 700
                }
            ]
        })
        
        yield {
            "get_by_height": mock_get_by_height,
            "get_by_hash": mock_get_by_hash,
            "get_latest": mock_get_latest,
            "get_txs": mock_get_txs
        }


@pytest.fixture
def register_tools(mock_mcp, mock_block_api):
    """Register the block tools for testing."""
    from ergo_explorer.api.routes.block import register_block_routes
    register_block_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_block_by_height(register_tools, mock_context, mock_block_api):
    """Test the get_block_by_height tool."""
    # Get the tool
    get_block_by_height = register_tools.tools["get_block_by_height"]
    
    # Call the tool
    result = await get_block_by_height(mock_context, height=1000000)
    
    # Check the result
    assert "block1" in result
    assert "1000000" in result
    assert "10" in result
    assert "address1" in result
    
    # Verify the mock was called with correct parameters
    mock_block_api["get_by_height"].assert_called_once_with(1000000)


@pytest.mark.asyncio
async def test_get_block_by_hash(register_tools, mock_context, mock_block_api):
    """Test the get_block_by_hash tool."""
    # Get the tool
    get_block_by_hash = register_tools.tools["get_block_by_hash"]
    
    # Call the tool
    result = await get_block_by_hash(mock_context, block_hash="block2")
    
    # Check the result
    assert "block2" in result
    assert "1000001" in result
    assert "15" in result
    assert "address2" in result
    
    # Verify the mock was called with correct parameters
    mock_block_api["get_by_hash"].assert_called_once_with("block2")


@pytest.mark.asyncio
async def test_get_latest_blocks(register_tools, mock_context, mock_block_api):
    """Test the get_latest_blocks tool."""
    # Get the tool
    get_latest_blocks = register_tools.tools["get_latest_blocks"]
    
    # Call the tool
    result = await get_latest_blocks(mock_context, limit=10)
    
    # Check the result
    assert "block3" in result
    assert "block4" in result
    assert "1000002" in result
    assert "1000003" in result
    
    # Verify the mock was called with correct parameters
    mock_block_api["get_latest"].assert_called_once_with(10)


@pytest.mark.asyncio
async def test_get_block_transactions(register_tools, mock_context, mock_block_api):
    """Test the get_block_transactions tool."""
    # Get the tool
    get_block_transactions = register_tools.tools["get_block_transactions"]
    
    # Call the tool
    result = await get_block_transactions(mock_context, block_id="block1", limit=100)
    
    # Check the result
    assert "tx1" in result
    assert "tx2" in result
    assert "990000000" in result or "9000000" in result
    assert "4950000000" in result or "45000000" in result
    
    # Verify the mock was called with correct parameters
    mock_block_api["get_txs"].assert_called_once_with("block1", 100) 