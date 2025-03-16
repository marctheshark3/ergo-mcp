"""
Tests for address-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.address import (
    get_address_balance,
    get_transaction_history,
    analyze_address
)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_address_balance(mock_client, mock_httpx_client, sample_address):
    """Test get_address_balance tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "address": sample_address,
        "confirmed": {
            "nanoErgs": 1000000000,
            "tokens": [
                {
                    "tokenId": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
                    "amount": 10,
                    "decimals": 0,
                    "name": "Test Token"
                }
            ]
        },
        "unconfirmed": {
            "nanoErgs": 0,
            "tokens": []
        }
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_address_balance(sample_address)
    
    assert isinstance(result, dict)
    assert sample_address in str(result)
    assert "ERG" in str(result)
    assert "1.0" in str(result)  # 1 ERG = 1,000,000,000 nanoERG
    assert "Test Token" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_address_balance_error(mock_client, mock_httpx_client, sample_address):
    """Test get_address_balance error handling."""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.json = AsyncMock(return_value={"error": "Address not found"})
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_address_balance(sample_address)
    
    assert isinstance(result, dict)
    assert "error" in result
    assert "404" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_transaction_history(mock_client, mock_httpx_client, sample_address):
    """Test get_transaction_history tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
                "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "inclusionHeight": 1000000,
                "timestamp": 1630000000000,
                "inputs": [{"id": "input1"}],
                "outputs": [{"id": "output1"}]
            }
        ],
        "total": 1
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_transaction_history(sample_address, limit=10)
    
    assert isinstance(result, dict)
    assert sample_address in str(result)
    assert "transaction" in str(result).lower()
    assert "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_transaction_history_error(mock_client, mock_httpx_client, sample_address):
    """Test get_transaction_history error handling."""
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.json = AsyncMock(return_value={"error": "Internal server error"})
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_transaction_history(sample_address, limit=10)
    
    assert isinstance(result, dict)
    assert "error" in result
    assert "500" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_analyze_address(mock_client, mock_httpx_client, sample_address):
    """Test analyze_address tool."""
    # Mock responses for different API calls
    transaction_response = AsyncMock()
    transaction_response.status_code = 200
    transaction_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
                "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "inclusionHeight": 1000000,
                "timestamp": 1630000000000,
                "inputs": [{"id": "input1", "address": "addr1"}],
                "outputs": [{"id": "output1", "address": "addr2"}]
            }
        ],
        "total": 1
    })
    
    balance_response = AsyncMock()
    balance_response.status_code = 200
    balance_response.json = AsyncMock(return_value={
        "address": sample_address,
        "confirmed": {
            "nanoErgs": 1000000000,
            "tokens": [
                {
                    "tokenId": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
                    "amount": 10,
                    "decimals": 0,
                    "name": "Test Token"
                }
            ]
        },
        "unconfirmed": {
            "nanoErgs": 0,
            "tokens": []
        }
    })
    
    # Set up different responses for different API calls
    async def mock_get(url, *args, **kwargs):
        if "addresses" in url and "transactions" in url:
            return transaction_response
        elif "addresses" in url and "balance" in url:
            return balance_response
        return AsyncMock(status_code=404)
        
    mock_httpx_client.get = AsyncMock(side_effect=mock_get)
    mock_client.return_value = mock_httpx_client
    
    result = await analyze_address(sample_address, depth=1, tx_limit=2)
    
    assert isinstance(result, dict)
    assert sample_address in str(result)
    assert "ERG" in str(result)
    assert "Test Token" in str(result)
    assert "transaction" in str(result).lower()
    assert "Related addresses" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_analyze_address_error(mock_client, mock_httpx_client, sample_address):
    """Test analyze_address error handling."""
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.json = AsyncMock(return_value={"error": "Internal server error"})
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await analyze_address(sample_address, depth=1, tx_limit=2)
    
    assert isinstance(result, dict)
    assert "error" in result
    assert "500" in str(result)