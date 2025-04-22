"""
Tests for token holder functionality.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Imports for new package structure
from ergo_explorer.tools.token_holders import (
    get_token_holders,
    get_token_by_id,
    get_unspent_boxes_by_token_id
)

# Path updates for imports in the test file
TOKENS_MODULE_PATH = 'ergo_explorer.tools.token_holders.tokens'
BOXES_MODULE_PATH = 'ergo_explorer.tools.token_holders.boxes'
HOLDERS_MODULE_PATH = 'ergo_explorer.tools.token_holders.holders'
API_MODULE_PATH = 'ergo_explorer.tools.token_holders.api'


@pytest.mark.asyncio
@patch(f'{TOKENS_MODULE_PATH}.fetch_node_api')
async def test_get_token_by_id(mock_fetch_node_api, sample_token_id):
    """Test get_token_by_id function."""
    # Mock response
    mock_response = {
        "id": sample_token_id,
        "name": "Test Token",
        "decimals": 2,
        "description": "Test token description",
        "emissionAmount": 1000000
    }
    mock_fetch_node_api.return_value = mock_response
    
    # Call the function
    result = await get_token_by_id(sample_token_id)
    
    # Verify the result
    assert result == mock_response
    mock_fetch_node_api.assert_called_once_with(f"blockchain/token/byId/{sample_token_id}")


@pytest.mark.asyncio
@patch(f'{BOXES_MODULE_PATH}.fetch_node_api')
async def test_get_unspent_boxes_by_token_id(mock_fetch_node_api, sample_token_id):
    """Test get_unspent_boxes_by_token_id function."""
    # Mock response
    mock_boxes = [
        {
            "boxId": "box1",
            "address": "address1",
            "assets": [
                {
                    "tokenId": sample_token_id,
                    "amount": 100
                }
            ]
        },
        {
            "boxId": "box2",
            "address": "address2",
            "assets": [
                {
                    "tokenId": sample_token_id,
                    "amount": 200
                }
            ]
        }
    ]
    mock_fetch_node_api.return_value = mock_boxes
    
    # Call the function
    result = await get_unspent_boxes_by_token_id(sample_token_id, 0, 100)
    
    # Verify the result
    assert result == mock_boxes
    mock_fetch_node_api.assert_called_once_with(
        f"blockchain/box/unspent/byTokenId/{sample_token_id}",
        params={"offset": 0, "limit": 100}
    )


@pytest.mark.asyncio
@patch(f'{BOXES_MODULE_PATH}.fetch_node_api')
async def test_get_unspent_boxes_by_token_id_error(mock_fetch_node_api, sample_token_id):
    """Test get_unspent_boxes_by_token_id function with error response."""
    # Mock error response
    mock_error = {"error": "Not found"}
    mock_fetch_node_api.return_value = mock_error
    
    # Call the function
    result = await get_unspent_boxes_by_token_id(sample_token_id, 0, 100)
    
    # Verify the result
    assert result == []


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_token_holders_success(
    mock_async_client_class, test_mcp, sample_token_id, mock_context
):
    """Test get_token_holders tool via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the expected formatted string result
    expected_output = (
        f"# Token Holder Analysis: Test Token\n\n"
        f"## Overview\n"
        f"- Token ID: {sample_token_id}\n"
        # ... other formatted lines ...
        f"| 1 | address1 | 800 | 80.0% |\n"
        f"| 2 | address2 | 200 | 20.0% |\n"
        # ... include analysis section if expected ...
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    tool_args = {"token_id": sample_token_id}
    invoke_payload = {"tool": "token_holders", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert f"Token Holder Analysis: Test Token" in result_data["result"]
    assert f"Token ID: {sample_token_id}" in result_data["result"]
    assert "| address1 | 800 | 80.0% |" in result_data["result"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_token_holders_raw(
    mock_async_client_class, test_mcp, sample_token_id, mock_context
):
    """Test get_token_holders tool with raw output via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the expected dictionary result (raw output)
    expected_dict = {
        "token_id": sample_token_id,
        "token_name": "Test Token",
        "decimals": 2,
        "total_supply": 1000,
        "total_holders": 2,
        "holders": [
            {"address": "address1", "amount": 600, "percentage": 60.0},
            {"address": "address2", "amount": 400, "percentage": 40.0}
        ]
    }
    mock_response.json.return_value = {"result": expected_dict}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    
    tool_args = {"token_id": sample_token_id, "include_raw": True}
    invoke_payload = {"tool": "token_holders", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert isinstance(result_data["result"], dict)
    assert result_data["result"]["token_id"] == sample_token_id
    assert result_data["result"]["total_holders"] == 2


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_token_holders_token_error(mock_async_client_class, test_mcp, sample_token_id, mock_context):
    """Test get_token_holders tool with token fetch error via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_error_msg = "Error fetching token info: Token not found"
    mock_response.json.return_value = {"result": expected_error_msg}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    
    tool_args = {"token_id": sample_token_id}
    invoke_payload = {"tool": "token_holders", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert result_data["result"] == expected_error_msg


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock) 
async def test_get_token_holders_no_analysis(
    mock_async_client_class, test_mcp, sample_token_id, mock_context
):
    """Test get_token_holders tool without analysis via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    expected_output = (
        f"# Token Holder Analysis: Test Token\n\n"
        # ... overview and top holders table ...
        f"| 1 | address1 | 1000 | 100.0% |\n"
        # No Distribution Analysis section
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    
    tool_args = {"token_id": sample_token_id, "include_analysis": False}
    invoke_payload = {"tool": "token_holders", "args": tool_args}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert "Token Holder Analysis: Test Token" in result_data["result"]
    assert "Distribution Analysis" not in result_data["result"] 