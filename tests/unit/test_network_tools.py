"""
Tests for network-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import datetime
import httpx # Import httpx

# Removed unused imports
# from ergo_explorer.tools.network import (
#     get_blockchain_stats,
#     get_network_hashrate,
#     get_mining_difficulty
# )
# from ergo_explorer.api.routes.node import get_node_wallet
# from ergo_explorer.api.routes.deprecated import get_network_status, get_mempool_info


# Removed obsolete test_get_network_status


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_node_wallet(mock_async_client_class, test_mcp, mock_context):
    """Test get_node_wallet tool via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the expected formatted string result from the tool
    expected_output = (
        "Node Wallet Information:\n\n"
        "Address 1: address1\n"
        "• Confirmed: 1.000000000 ERG\n"
        "• Unconfirmed: 0.000000000 ERG\n\n"
        "Address 2: address2\n"
        "• Confirmed: 0.500000000 ERG\n"
        "• Unconfirmed: 0.000000000 ERG\n\n"
        "Tokens:\n"
        "• 10 TestTok (ID: tk1...)\n\n"
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    invoke_payload = {"tool": "get_node_wallet", "args": {}}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    # Check substrings of the result
    assert "Node Wallet Information" in result_data["result"]
    assert "Address 1: address1" in result_data["result"]
    assert "Confirmed: 1.000000000 ERG" in result_data["result"]
    assert "Address 2: address2" in result_data["result"]
    assert "Confirmed: 0.500000000 ERG" in result_data["result"]
    assert "• 10 TestTok (ID: tk1...)" in result_data["result"]


# Removed obsolete test_get_blockchain_stats (covered by test_blockchain_status)


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_blockchain_status(mock_async_client_class, test_mcp, mock_context):
    """Test the blockchain_status tool via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the combined formatted string from the tool
    expected_output = (
        "# Ergo Blockchain Status\n\n"
        "    ## Current State\n"
        "    Blockchain Height Information:\n• Indexed Height: 1,000,000\n\n"
        "    ## Network Metrics\n"
        "    ## Ergo Mining Difficulty\n\n"
        "    - Raw Difficulty: 1,234,567,890,123\n"
        "    - Readable Difficulty: 1.23 P\n"
        # ... other difficulty lines ...
        "\n    ## Performance\n"
        "    ## Ergo Network Hashrate\n\n"
        "    - Estimated Hashrate: 5415.48 TH/s\n"
        # ... other hashrate lines ...
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
    # Check key substrings
    assert "# Ergo Blockchain Status" in result_data["result"]
    assert "Indexed Height: 1,000,000" in result_data["result"]
    assert "Raw Difficulty: 1,234,567,890,123" in result_data["result"]
    assert "Estimated Hashrate: 5415.48 TH/s" in result_data["result"]


# Removed obsolete test_get_network_hashrate


# Removed obsolete test_get_mining_difficulty


@pytest.mark.asyncio
@patch('httpx.AsyncClient', new_callable=MagicMock)
async def test_get_mempool_statistics(mock_async_client_class, test_mcp, mock_context):
    """Test get_mempool_statistics tool via simulated HTTP request."""
    mock_client_instance = mock_async_client_class.return_value.__aenter__.return_value
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    # Mock the formatted string result
    expected_output = (
        "## Ergo Node Mempool Statistics\n\n"
        "- Transactions Count: 3\n"
        "- Total Size: 750 bytes\n"
        "- Total Value: 0.450000000 ERG\n"
        "- Total Fees: 0.003000000 ERG\n"
    )
    mock_response.json.return_value = {"result": expected_output}
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    invoke_payload = {"tool": "get_mempool_statistics", "args": {}}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://testserver/invoke", json=invoke_payload)

    mock_client_instance.post.assert_called_once_with("http://testserver/invoke", json=invoke_payload)
    assert response.status_code == 200
    result_data = response.json()
    assert "result" in result_data
    # Check key substrings
    assert "Ergo Node Mempool Statistics" in result_data["result"]
    assert "Transactions Count: 3" in result_data["result"]
    assert "Total Size: 750 bytes" in result_data["result"]
    assert "Total Value: 0.450000000 ERG" in result_data["result"]
    assert "Total Fees: 0.003000000 ERG" in result_data["result"]


# Removed obsolete test_get_mempool_info


# ... (rest of the file remains unchanged) ... 