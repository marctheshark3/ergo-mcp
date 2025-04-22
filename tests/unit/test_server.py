"""
Tests for MCP server tool invocations (originally test_server.py).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import datetime
import httpx # Import httpx

# Note: Direct tool function imports are no longer needed


# MockContext class might not be needed anymore with HTTP testing
# class MockContext: ...


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_address_balance_server(mock_async_client_class, test_mcp, sample_address):
    """Test get_address_balance tool via simulated HTTP request."""
    address = sample_address
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_error_msg = f"Error fetching token info: Token not found for ID: {address}"
    mock_response.json.return_value = {"result": expected_error_msg}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"address": address}
    invoke_payload = {"tool": "get_address_balance", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert result_data["result"] == expected_error_msg


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_transaction_server(mock_async_client_class, test_mcp, sample_transaction_id):
    """Test get_transaction tool via simulated HTTP request."""
    tx_id = sample_transaction_id
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the expected formatted string result
    expected_output = (
        f"Transaction Details for {tx_id}:\n"
        f"• Size: 500 bytes\n"
        f"• Inputs: 1\n"
        f"• Outputs: 2\n\n"
        # ... (add formatted input/output details if needed for assertion) ...
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"tx_id": tx_id}
    invoke_payload = {"tool": "get_transaction", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)
        
    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert f"Transaction Details for {tx_id}" in result_data["result"]
    assert "Size: 500 bytes" in result_data["result"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_address_history_server(mock_async_client_class, test_mcp, sample_address, sample_transaction_id):
    """Test get_address_history tool via simulated HTTP request."""
    address = sample_address
    limit = 10
    offset = 0
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_output = (
        f"Transaction History for {address}\n"
        f"Found 1 transactions. Showing 1:\n\n"
        f"1. Transaction: {sample_transaction_id}\n"
        # ... other formatted lines ...
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
        
    tool_args = {"address": address, "offset": 0, "limit": limit}
    invoke_payload = {"tool": "get_address_history", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)
        
    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert f"Transaction History for {address}" in result_data["result"]
    assert f"1. Transaction: {sample_transaction_id}" in result_data["result"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_block_by_height_server(mock_async_client_class, test_mcp, sample_block_height, sample_block_id):
    """Test get_block_by_height tool via simulated HTTP request."""
    height = sample_block_height
    block_id = sample_block_id # Needed for assertion checks
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the formatted string from format_block_data
    expected_output = (
        f"## Block Details\n\n"
        f"- **Height**: {height}\n"
        f"- **ID**: {block_id}\n"
        # ... other formatted lines ...
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
        
    tool_args = {"height": height}
    invoke_payload = {"tool": "get_block_by_height", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)
        
    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert f"Height**: {height}" in result_data["result"]
    assert f"ID**: {block_id}" in result_data["result"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_blockchain_status_server(mock_async_client_class, test_mcp):
    """Test the blockchain_status tool via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_output = (
        "# Ergo Blockchain Status\n\n"
        "    ## Current State\n"
        # ... other formatted sections ...
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
        
    invoke_payload = {"tool": "blockchain_status", "args": {}}
    
    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)
        
    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert "# Ergo Blockchain Status" in result_data["result"] 