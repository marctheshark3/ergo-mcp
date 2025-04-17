"""
Tests for address-related MCP tools (originally deprecated).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
import httpx # Import httpx


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_address_balance(mock_async_client_class, test_mcp, sample_address, mock_context):
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

    # Simulate making the request using the patched client
    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert result_data["result"] == expected_error_msg


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_address_balance_api_error(mock_async_client_class, test_mcp, sample_address, mock_context):
    """Test get_address_balance tool with simulated HTTP 500 error."""
    address = sample_address

    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error during tool execution"} 
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"address": address}
    invoke_payload = {"tool": "get_address_balance", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 500
    assert "error" in response.json()


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_address_history(mock_async_client_class, test_mcp, sample_address, sample_transaction_id, mock_context):
    """Test the get_address_history tool via simulated HTTP request."""
    address = sample_address
    limit = 10
    offset = 0
    
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Tool returns a formatted string, need to mock the JSON response wrapper
    expected_output = (
        f"Transaction History for {address}\n"
        f"Found 1 transactions. Showing 1:\n\n"
        f"1. Transaction: {sample_transaction_id}\n"
        f"   Timestamp: 2021-08-26 18:06:40\n" # Example format, adjust if needed
        f"   Received: +0.499000000 ERG\n"
    )
    mock_response.json.return_value = {"result": expected_output} 
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"address": address, "offset": offset, "limit": limit}
    invoke_payload = {"tool": "get_address_history", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert f"Transaction History for {address}" in result_data["result"]
    assert f"1. Transaction: {sample_transaction_id}" in result_data["result"]
    assert "Received: +0.499000000 ERG" in result_data["result"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_address_history_error(mock_async_client_class, test_mcp, sample_address, mock_context):
    """Test get_address_history tool error handling via simulated HTTP request."""
    address = sample_address
    limit = 10
    offset = 0
    
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_error_msg = "Error fetching transaction history: API error"
    mock_response.json.return_value = {"result": expected_error_msg}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"address": address, "offset": offset, "limit": limit}
    invoke_payload = {"tool": "get_address_history", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert result_data["result"] == expected_error_msg