"""Tests for the Address Book API tools."""

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
def sample_address_book_data():
    """Sample address book data for testing."""
    return {
        "items": [
            {
                "name": "Test Exchange",
                "address": "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA",
                "type": "Exchange",
                "description": "A test exchange",
                "url": "https://testexchange.com"
            },
            {
                "name": "Test Mining Pool",
                "address": "9g1b69CQYaJKSY9ycjYJJnQxCJL8VEPn5kiVKQKDgkrQKGPRVf9",
                "type": "Mining pool",
                "description": "A test mining pool",
                "url": "https://testpool.com"
            },
            {
                "name": "Test Service",
                "address": "9h5R3USYAj7hRuJQY7yzQajkFdkso2t7HWVm4xUUD8uxswtJtd9",
                "type": "Service",
                "description": "A test service",
                "url": "https://testservice.com"
            }
        ]
    }


@pytest.fixture
def mock_address_book_api():
    """Mock address book API for testing."""
    with patch("ergo_explorer.tools.address_book.get_address_book") as mock_get_book, \
         patch("ergo_explorer.tools.address_book.filter_address_book_by_type") as mock_filter_type, \
         patch("ergo_explorer.tools.address_book.search_address_book") as mock_search, \
         patch("ergo_explorer.tools.address_book.get_address_details") as mock_get_details:
        
        # Mock get_address_book
        mock_get_book.return_value = asyncio.Future()
        mock_get_book.return_value.set_result({
            "items": [
                {"name": "Exchange A", "type": "Exchange", "address": "addr1"},
                {"name": "Mining Pool B", "type": "Mining pool", "address": "addr2"},
                {"name": "Service C", "type": "Service", "address": "addr3"}
            ]
        })
        
        # Mock filter_address_book_by_type
        mock_filter_type.return_value = asyncio.Future()
        mock_filter_type.return_value.set_result({
            "items": [
                {"name": "Exchange A", "type": "Exchange", "address": "addr1"},
                {"name": "Exchange D", "type": "Exchange", "address": "addr4"}
            ]
        })
        
        # Mock search_address_book
        mock_search.return_value = asyncio.Future()
        mock_search.return_value.set_result({
            "items": [
                {"name": "Mining Pool B", "type": "Mining pool", "address": "addr2"},
                {"name": "Mining Pool E", "type": "Mining pool", "address": "addr5"}
            ]
        })
        
        # Mock get_address_details
        mock_get_details.return_value = asyncio.Future()
        mock_get_details.return_value.set_result({
            "name": "Service C", 
            "type": "Service", 
            "address": "addr3",
            "description": "A service",
            "url": "https://service.com"
        })
        
        yield {
            "get_book": mock_get_book,
            "filter_type": mock_filter_type,
            "search": mock_search,
            "get_details": mock_get_details
        }


@pytest.fixture
def register_tools(mock_mcp, mock_address_book_api):
    """Register the address book tools for testing."""
    from ergo_explorer.api.routes.address_book import register_address_book_routes
    register_address_book_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_get_address_book(register_tools, mock_context, mock_address_book_api):
    """Test the get_address_book tool."""
    # Get the tool
    get_address_book = register_tools.tools["get_address_book"]
    
    # Call the tool
    result = await get_address_book(mock_context)
    
    # Check the result
    assert "Exchange A" in result
    assert "Mining Pool B" in result
    assert "Service C" in result
    
    # Verify the mock was called
    mock_address_book_api["get_book"].assert_called_once()


@pytest.mark.asyncio
async def test_get_address_book_by_type(register_tools, mock_context, mock_address_book_api):
    """Test the get_address_book_by_type tool."""
    # Get the tool
    get_address_book_by_type = register_tools.tools["get_address_book_by_type"]
    
    # Call the tool
    result = await get_address_book_by_type(mock_context, type_filter="Exchange")
    
    # Check the result
    assert "Exchange A" in result
    assert "Exchange D" in result
    
    # Verify the mock was called with correct parameters
    mock_address_book_api["filter_type"].assert_called_once_with("Exchange")


@pytest.mark.asyncio
async def test_search_address_book(register_tools, mock_context, mock_address_book_api):
    """Test the search_address_book tool."""
    # Get the tool
    search_address_book = register_tools.tools["search_address_book"]
    
    # Call the tool
    result = await search_address_book(mock_context, query="Mining")
    
    # Check the result
    assert "Mining Pool B" in result
    assert "Mining Pool E" in result
    
    # Verify the mock was called with correct parameters
    mock_address_book_api["search"].assert_called_once_with("Mining")


@pytest.mark.asyncio
async def test_get_address_details(register_tools, mock_context, mock_address_book_api):
    """Test the get_address_details tool."""
    # Get the tool
    get_address_details = register_tools.tools["get_address_details"]
    
    # Call the tool
    result = await get_address_details(mock_context, address="addr3")
    
    # Check the result
    assert "Service C" in result
    assert "A service" in result
    assert "https://service.com" in result
    
    # Verify the mock was called with correct parameters
    mock_address_book_api["get_details"].assert_called_once_with("addr3") 