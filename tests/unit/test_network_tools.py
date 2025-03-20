"""
Tests for network-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.network import (
    get_network_status,
    get_node_wallet,
    get_blockchain_stats,
    get_network_hashrate,
    get_mining_difficulty,
    get_mempool_info
)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_network_status(mock_client, mock_httpx_client):
    """Test get_network_status tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "height": 1000000,
        "headerId": "block_id",
        "lastBlockId": "last_block_id",
        "difficulty": 1000000000,
        "currentTime": 1630000000000,
        "networkType": "mainnet"
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_network_status()
    
    assert isinstance(result, dict)
    assert "1000000" in str(result)
    assert "block_id" in str(result)
    assert "mainnet" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_node_wallet(mock_client, mock_httpx_client):
    """Test get_node_wallet tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "walletStatus": "unlocked",
        "balance": 1000000000,
        "addresses": ["address1", "address2"],
        "transactions": ["tx1", "tx2"]
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_node_wallet()
    
    assert isinstance(result, dict)
    assert "unlocked" in str(result)
    assert "1000000000" in str(result)
    assert "address1" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_blockchain_stats(mock_client, mock_httpx_client):
    """Test get_blockchain_stats tool."""
    # Mock response data for network state
    mock_state_response = AsyncMock()
    mock_state_response.status_code = 200
    mock_state_response.json = AsyncMock(return_value={
        "height": 1000000,
        "headerId": "block_id",
        "lastBlockId": "last_block_id",
        "difficulty": 1000000000,
        "currentTime": 1630000000000,
        "networkType": "mainnet"
    })
    
    # Mock response data for additional info
    mock_info_response = AsyncMock()
    mock_info_response.status_code = 200
    mock_info_response.json = AsyncMock(return_value={
        "blockCount": 1000000,
        "totalTransactions": 5000000,
        "totalCoins": 97000000,
        "averageBlockTime": 120,
        "averageHashrate": "1.23 PH/s"
    })
    
    mock_httpx_client.get = AsyncMock(side_effect=[mock_state_response, mock_info_response])
    mock_client.return_value = mock_httpx_client
    
    result = await get_blockchain_stats()
    
    assert isinstance(result, dict)
    assert "networkState" in result
    assert "additionalInfo" in result
    assert "1000000" in str(result)
    assert "mainnet" in str(result)
    assert "1.23 PH/s" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_network_hashrate(mock_client, mock_httpx_client):
    """Test get_network_hashrate tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "hashrate": "1.23 PH/s",
        "timestamp": 1630000000000,
        "difficulty": 1000000000
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_network_hashrate()
    
    assert isinstance(result, dict)
    assert "1.23 PH/s" in str(result)
    assert "1000000000" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_mining_difficulty(mock_client, mock_httpx_client):
    """Test get_mining_difficulty tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "difficulty": 1000000000,
        "epoch": 500,
        "lastAdjustment": "2%",
        "expectedAdjustment": "1%",
        "targetBlockTime": 120
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_mining_difficulty()
    
    assert isinstance(result, dict)
    assert "1000000000" in str(result)
    assert "120" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_mempool_info(mock_client, mock_httpx_client):
    """Test get_mempool_info tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "size": 100,
        "transactions": ["tx1", "tx2", "tx3"],
        "totalFees": 1000000,
        "avgWaitTime": 300
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_mempool_info()
    
    assert isinstance(result, dict)
    assert "100" in str(result)
    assert "tx1" in str(result)
    assert "1000000" in str(result) 