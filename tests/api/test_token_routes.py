"""Tests for the Token API tools."""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json

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
def sample_token_data():
    """Sample token data for testing."""
    return {
        "id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
        "boxId": "b51a34d3a1e184599137aa25139d282144dab328f0afa1afdeb5f0b6d2ed0923",
        "emissionAmount": 1000,
        "name": "Test Token",
        "description": "A test token for unit testing",
        "type": "EIP-004",
        "decimals": 2
    }


@pytest.fixture
def sample_token_holders():
    """Sample token holders data for testing."""
    return {
        "token": {
            "id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
            "name": "Test Token"
        },
        "holders": [
            {"address": "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA", "amount": 500},
            {"address": "9g1b69CQYaJKSY9ycjYJJnQxCJL8VEPn5kiVKQKDgkrQKGPRVf9", "amount": 500}
        ]
    }


@pytest.fixture
def sample_collection_data():
    """Sample NFT collection data for testing."""
    return {
        "collection": {
            "id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
            "name": "Test Collection",
            "description": "A test NFT collection",
            "tokenCount": 10
        },
        "nfts": [
            {"id": "nft1", "name": "NFT #1", "owner": "address1"},
            {"id": "nft2", "name": "NFT #2", "owner": "address2"}
        ]
    }


@pytest.fixture
def mock_token_api():
    """Mock token API for testing."""
    with patch("ergo_explorer.tools.token.get_token_by_id") as mock_get_token, \
         patch("ergo_explorer.tools.token.search_token") as mock_search_token, \
         patch("ergo_explorer.tools.token.get_token_holders") as mock_get_holders, \
         patch("ergo_explorer.tools.token.get_collection_holders") as mock_get_collection:
        
        # Mock get_token_by_id
        mock_get_token.return_value = asyncio.Future()
        mock_get_token.return_value.set_result({"token": {"id": "token1", "name": "Test Token"}})
        
        # Mock search_token
        mock_search_token.return_value = asyncio.Future()
        mock_search_token.return_value.set_result([
            {"id": "token1", "name": "Test Token A"},
            {"id": "token2", "name": "Test Token B"}
        ])
        
        # Mock get_token_holders
        mock_get_holders.return_value = asyncio.Future()
        mock_get_holders.return_value.set_result({
            "token": {"id": "token1", "name": "Test Token"},
            "holders": [
                {"address": "addr1", "amount": 500},
                {"address": "addr2", "amount": 500}
            ]
        })
        
        # Mock get_collection_holders
        mock_get_collection.return_value = asyncio.Future()
        mock_get_collection.return_value.set_result({
            "collection": {"id": "coll1", "name": "Test Collection"},
            "nfts": [
                {"id": "nft1", "name": "NFT #1", "owner": "addr1"},
                {"id": "nft2", "name": "NFT #2", "owner": "addr2"}
            ]
        })
        
        yield {
            "get_token": mock_get_token,
            "search_token": mock_search_token,
            "get_holders": mock_get_holders,
            "get_collection": mock_get_collection
        }


@pytest.fixture
def register_tools(mock_mcp, mock_token_api):
    """Register the token tools for testing."""
    from ergo_explorer.api.routes.token import register_token_routes
    register_token_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_token(register_tools, mock_context, mock_token_api):
    """Test the get_token tool."""
    # Get the tool
    get_token = register_tools.tools["get_token"]
    
    # Call the tool
    result = await get_token(mock_context, token_id="03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04")
    
    # Check the result (actual format will depend on your implementation)
    assert "Test Token" in result or "token1" in result
    
    # Verify the mock was called with correct parameters
    mock_token_api["get_token"].assert_called_once_with("03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04")


@pytest.mark.asyncio
async def test_search_token(register_tools, mock_context, mock_token_api):
    """Test the search_token tool."""
    # Get the tool
    search_token = register_tools.tools["search_token"]
    
    # Call the tool
    result = await search_token(mock_context, query="Test")
    
    # Check the result
    assert "Test Token A" in result or "token1" in result
    assert "Test Token B" in result or "token2" in result
    
    # Verify the mock was called with correct parameters
    mock_token_api["search_token"].assert_called_once_with("Test")


@pytest.mark.asyncio
async def test_get_token_holders(register_tools, mock_context, mock_token_api):
    """Test the get_token_holders tool."""
    # Get the tool
    get_token_holders = register_tools.tools["get_token_holders"]
    
    # Call the tool
    result = await get_token_holders(mock_context, token_id="token1", include_raw=False, include_analysis=True)
    
    # Check the result
    assert "Test Token" in result or "token1" in result
    assert "addr1" in result or "500" in result
    
    # Verify the mock was called with correct parameters
    mock_token_api["get_holders"].assert_called_once()


@pytest.mark.asyncio
async def test_get_collection_holders(register_tools, mock_context, mock_token_api):
    """Test the get_collection_holders tool."""
    # Get the tool
    get_collection_holders = register_tools.tools["get_collection_holders"]
    
    # Call the tool
    result = await get_collection_holders(mock_context, token_id="coll1", include_raw=False, include_analysis=True)
    
    # Check the result
    assert "Test Collection" in result or "coll1" in result
    assert "NFT #1" in result or "nft1" in result
    assert "NFT #2" in result or "nft2" in result
    
    # Verify the mock was called with correct parameters
    mock_token_api["get_collection"].assert_called_once()


@pytest.mark.asyncio
async def test_search_collections(register_tools, mock_context, mock_token_api):
    """Test the search_collections tool."""
    # Setup a specific mock for search_collections
    with patch("ergo_explorer.tools.collection.search_collections") as mock_search_collections:
        mock_search_collections.return_value = asyncio.Future()
        mock_search_collections.return_value.set_result([
            {"id": "coll1", "name": "Test Collection A"},
            {"id": "coll2", "name": "Test Collection B"}
        ])
        
        # Get the tool
        search_collections = register_tools.tools["search_collections"]
        
        # Call the tool
        result = await search_collections(mock_context, query="Test", limit=10)
        
        # Check the result
        assert "Test Collection A" in result or "coll1" in result
        assert "Test Collection B" in result or "coll2" in result
        
        # Verify the mock was called with correct parameters
        mock_search_collections.assert_called_once_with("Test", 10) 