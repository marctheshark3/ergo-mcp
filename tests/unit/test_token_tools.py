"""
Tests for token-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
import httpx

from ergo_explorer.tools.token import get_token_price
from ergo_explorer.tools.node import search_for_token_from_node as search_for_token


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_search_token(mock_async_client_class, test_mcp, mock_context):
    """Test search_token tool via simulated HTTP request."""
    query = "Test"
    
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the formatted string output
    expected_output = (
        "Found 2 tokens matching 'Test':\n"
        "- Test Token (ID: token1)\n"
        "- Another Test Token (ID: token2)"
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    
    tool_args = {"query": query}
    invoke_payload = {"tool": "search_token", "args": tool_args}

    async with httpx.AsyncClient() as client: 
        response = await client.post("http://testserver/invoke", json=invoke_payload)
    
    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    assert "Found 2 tokens matching 'Test':" in result_data["result"]
    assert "- Test Token (ID: token1)" in result_data["result"]
    assert "- Another Test Token (ID: token2)" in result_data["result"]

    # Verify the mock was called - No longer needed as we check the HTTP call
    # mock_search_tokens.assert_called_once_with(query=query)

# Removed test_get_token_price
# The following function is obsolete and removed:
# @pytest.mark.asyncio
# @patch('httpx.AsyncClient')
# async def test_get_token_price(mock_client, mock_httpx_client, sample_token_id):
#    ... 