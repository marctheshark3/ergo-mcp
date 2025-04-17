"""Tests for the EIP API tools."""

import asyncio
from unittest.mock import patch, MagicMock

import pytest

from ergo_explorer.eip_manager.eip_manager import EIPDetail, EIPSummary


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
def mock_eip_manager():
    """Mock EIP manager for testing."""
    with patch("ergo_explorer.api.routes.eip.eip_manager") as mock_manager:
        # Mock the get_all_eips method
        mock_manager.get_all_eips.return_value = [
            EIPSummary(number=1, title="EIP 1", status="Final"),
            EIPSummary(number=2, title="EIP 2", status="Draft"),
        ]
        
        # Mock the get_eip_details method
        def mock_get_eip_details(eip_number):
            if eip_number == 1:
                return EIPDetail(
                    number=1,
                    title="EIP 1",
                    status="Final",
                    content="Content for EIP 1"
                )
            elif eip_number == 2:
                return EIPDetail(
                    number=2,
                    title="EIP 2",
                    status="Draft",
                    content="Content for EIP 2"
                )
            return None
        
        mock_manager.get_eip_details.side_effect = mock_get_eip_details
        
        # Mock the eip_cache
        mock_manager.eip_cache = {1: "dummy"}
        
        yield mock_manager


@pytest.fixture
def register_tools(mock_mcp, mock_eip_manager):
    """Register the EIP tools for testing."""
    from ergo_explorer.api.routes.eip import register_eip_routes
    register_eip_routes(mock_mcp)
    return mock_mcp


@pytest.mark.asyncio
async def test_list_eips(register_tools, mock_context, mock_eip_manager):
    """Test the list_eips tool."""
    # Get the tool
    list_eips = register_tools.tools["list_eips"]
    
    # Call the tool
    result = await list_eips(mock_context)
    
    # Check the result
    assert "Ergo Improvement Proposals (EIPs)" in result
    assert "EIP-1: EIP 1" in result
    assert "Status: Final" in result
    assert "EIP-2: EIP 2" in result
    assert "Status: Draft" in result
    
    # Verify the mock was called
    mock_eip_manager.get_all_eips.assert_called_once()


@pytest.mark.asyncio
async def test_get_eip_existing(register_tools, mock_context, mock_eip_manager):
    """Test the get_eip tool with an existing EIP."""
    # Get the tool
    get_eip = register_tools.tools["get_eip"]
    
    # Call the tool
    result = await get_eip(mock_context, eip_number=1)
    
    # Check the result
    assert result == "Content for EIP 1"
    
    # Verify the mock was called
    mock_eip_manager.get_eip_details.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_eip_nonexistent(register_tools, mock_context, mock_eip_manager):
    """Test the get_eip tool with a nonexistent EIP."""
    # Get the tool
    get_eip = register_tools.tools["get_eip"]
    
    # Call the tool
    result = await get_eip(mock_context, eip_number=999)
    
    # Check the result
    assert "Error: EIP-999 not found" in result
    
    # Verify the mock was called
    mock_eip_manager.get_eip_details.assert_called_once_with(999) 