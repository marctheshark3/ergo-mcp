"""
Tests for node-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.node import (
    get_address_balance_from_node,
    analyze_transaction_from_node,
    get_transaction_history_from_node,
    get_network_status_from_node,
    search_for_token_from_node,
    get_node_wallet_info
)


@pytest.mark.asyncio
async def test_get_address_balance_from_node(mock_httpx_client, sample_address):
    """Test get_address_balance_from_node tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "balance": 1000000000,  # in nanoERG
        "tokens": [
            {
                "tokenId": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
                "amount": 10,
                "decimals": 0,
                "name": "Test Token"
            }
        ]
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await get_address_balance_from_node(sample_address)
    
    assert isinstance(result, dict)
    assert "balance" in result
    assert result["balance"] == 1000000000
    assert "tokens" in result
    assert len(result["tokens"]) == 1
    assert result["tokens"][0]["tokenId"] == "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"


@pytest.mark.asyncio
async def test_analyze_transaction_from_node(mock_httpx_client, sample_transaction_id):
    """Test analyze_transaction_from_node tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": sample_transaction_id,
        "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
        "timestamp": 1630000000000,
        "inputs": [
            {
                "id": "input1",
                "value": 1000000000,
                "address": "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"
            }
        ],
        "outputs": [
            {
                "id": "output1",
                "value": 900000000,
                "address": "9f9q6Hs7vXZSQwhbrptQZLkTx15ApjbEkQwWXJqD2NpaouiigJQ"
            }
        ]
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await analyze_transaction_from_node(sample_transaction_id)
    
    assert isinstance(result, dict)
    assert "id" in result
    assert result["id"] == sample_transaction_id
    assert "inputs" in result
    assert "outputs" in result
    assert len(result["inputs"]) == 1
    assert len(result["outputs"]) == 1


@pytest.mark.asyncio
async def test_get_transaction_history_from_node(mock_httpx_client, sample_address):
    """Test get_transaction_history_from_node tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
                "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "timestamp": 1630000000000,
                "inputs": [{"id": "input1"}],
                "outputs": [{"id": "output1"}]
            }
        ],
        "total": 1
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await get_transaction_history_from_node(sample_address, limit=10)
    
    assert isinstance(result, dict)
    assert "items" in result
    assert "total" in result
    assert len(result["items"]) == 1
    assert result["items"][0]["id"] == "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"


@pytest.mark.asyncio
async def test_get_network_status_from_node(mock_httpx_client):
    """Test get_network_status_from_node tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "height": 1000000,
        "headerId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
        "difficulty": 1000000000,
        "bestFullHeight": 999990,
        "bestHeaderId": "header_id",
        "supplyAmount": 97000000000000000,  # in nanoERG
        "transactionsCount": 5000000,
        "peerCount": 100
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await get_network_status_from_node()
    
    assert isinstance(result, dict)
    assert "height" in result
    assert result["height"] == 1000000
    assert "difficulty" in result
    assert "supplyAmount" in result


@pytest.mark.asyncio
async def test_search_for_token_from_node(mock_httpx_client):
    """Test search_for_token_from_node tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",
                "name": "Test Token",
                "decimals": 2,
                "emissionAmount": 1000000
            }
        ],
        "total": 1
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await search_for_token_from_node("Test Token")
    
    assert isinstance(result, dict)
    assert "items" in result
    assert "total" in result
    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "Test Token"


@pytest.mark.asyncio
async def test_get_node_wallet_info(mock_httpx_client):
    """Test get_node_wallet_info tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "walletStatus": {
            "balance": 1000000000,  # in nanoERG
            "height": 1000000,
            "addresses": [
                "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"
            ],
            "transactions": []
        }
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await get_node_wallet_info()
    
    assert isinstance(result, dict)
    assert "walletStatus" in result
    assert "balance" in result["walletStatus"]
    assert "addresses" in result["walletStatus"]
    assert len(result["walletStatus"]["addresses"]) == 1 