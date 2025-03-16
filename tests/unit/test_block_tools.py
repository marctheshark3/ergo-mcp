"""
Tests for block-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.block import (
    get_block_by_height,
    get_block_by_hash,
    get_latest_blocks,
    get_block_transactions
)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_block_by_height(mock_client, mock_httpx_client, sample_block_height):
    """Test get_block_by_height tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "block": {
            "header": {
                "id": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "parentId": "parent_block_id",
                "version": 1,
                "height": sample_block_height,
                "timestamp": 1630000000000,
                "difficulty": "difficulty_value",
                "adProofsRoot": "adproof_root",
                "transactionsRoot": "tx_root",
                "stateRoot": "state_root",
                "extensionHash": "extension_hash"
            },
            "transactions": [
                {
                    "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"
                }
            ],
            "extension": {
                "fields": []
            },
            "adProofs": "adproofs_value",
            "size": 1000
        }
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_block_by_height(sample_block_height)
    
    assert isinstance(result, dict)
    assert str(sample_block_height) in str(result)
    assert "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_block_by_hash(mock_client, mock_httpx_client, sample_block_id):
    """Test get_block_by_hash tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "block": {
            "header": {
                "id": sample_block_id,
                "parentId": "parent_block_id",
                "version": 1,
                "height": 1000000,
                "timestamp": 1630000000000,
                "difficulty": "difficulty_value",
                "adProofsRoot": "adproof_root",
                "transactionsRoot": "tx_root",
                "stateRoot": "state_root",
                "extensionHash": "extension_hash"
            },
            "transactions": [
                {
                    "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"
                }
            ],
            "extension": {
                "fields": []
            },
            "adProofs": "adproofs_value",
            "size": 1000
        }
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_block_by_hash(sample_block_id)
    
    assert isinstance(result, dict)
    assert sample_block_id in str(result)
    assert "1000000" in str(result)  # block height


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_latest_blocks(mock_client, mock_httpx_client):
    """Test get_latest_blocks tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                "height": 1000000,
                "timestamp": 1630000000000,
                "transactionsCount": 5,
                "miner": "miner_address",
                "size": 1000,
                "difficulty": 1000000000
            },
            {
                "id": "second_block_id",
                "height": 999999,
                "timestamp": 1629999900000,
                "transactionsCount": 3,
                "miner": "miner_address",
                "size": 900,
                "difficulty": 1000000000
            }
        ],
        "total": 2
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_latest_blocks(limit=2)
    
    assert isinstance(result, dict)
    assert "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7" in str(result)
    assert "second_block_id" in str(result)
    assert "1000000" in str(result)
    assert "999999" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_block_transactions(mock_client, mock_httpx_client, sample_block_id):
    """Test get_block_transactions tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9",
                "blockId": sample_block_id,
                "inclusionHeight": 1000000,
                "timestamp": 1630000000000,
                "inputs": [{"id": "input1"}],
                "outputs": [{"id": "output1"}]
            },
            {
                "id": "second_tx_id",
                "blockId": sample_block_id,
                "inclusionHeight": 1000000,
                "timestamp": 1630000000000,
                "inputs": [{"id": "input2"}],
                "outputs": [{"id": "output2"}]
            }
        ],
        "total": 2
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await get_block_transactions(sample_block_id, limit=10)
    
    assert isinstance(result, dict)
    assert sample_block_id in str(result)
    assert "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9" in str(result)
    assert "second_tx_id" in str(result) 