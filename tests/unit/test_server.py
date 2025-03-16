"""
Tests for MCP server implementation.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.server import (
    get_address_balance,
    analyze_transaction,
    get_transaction_history,
    analyze_address,
    search_for_token,
    get_network_status,
    get_node_wallet,
    get_block_by_height,
    get_block_by_hash,
    get_latest_blocks,
    get_block_transactions,
    get_blockchain_stats,
    get_network_hashrate,
    get_mining_difficulty,
    get_mempool_info,
    get_token_price
)


class MockContext:
    """Mock context for testing MCP tools."""
    def __init__(self):
        self.path = "mock/path"
        self.method = "GET"
        self.json = {}
        self.headers = {}
        self.query_params = {}
        self.request = AsyncMock()


@pytest.mark.asyncio
async def test_get_address_balance_server():
    """Test get_address_balance MCP tool implementation."""
    address = "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"
    
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
            "address": address,
            "confirmed": {
                "nanoErgs": 1000000000,
                "tokens": []
            },
            "unconfirmed": {
                "nanoErgs": 0,
                "tokens": []
            }
        }
        
        result = await get_address_balance(address)
        
    assert isinstance(result, str)
    assert address in result
    assert "ERG" in result


@pytest.mark.asyncio
async def test_analyze_transaction_server():
    """Test analyze_transaction MCP tool implementation."""
    tx_id = "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"
    
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
            "id": tx_id,
            "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
            "inclusionHeight": 1000000,
            "timestamp": 1630000000000,
            "inputs": [{"id": "input1"}],
            "outputs": [{"id": "output1"}]
        }
        
        result = await analyze_transaction(tx_id)
        
    assert isinstance(result, str)
    assert tx_id in result
    assert "transaction" in result.lower()


@pytest.mark.asyncio
async def test_get_transaction_history_server():
    """Test get_transaction_history MCP tool implementation."""
    address = "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA"
    
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
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
        }
        
        result = await get_transaction_history(address, limit=10)
        
    assert isinstance(result, str)
    assert address in result
    assert "transaction" in result.lower()


@pytest.mark.asyncio
async def test_get_block_by_height_server():
    """Test get_block_by_height MCP tool implementation."""
    height = 1000000
    
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
            "block": {
                "header": {
                    "id": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
                    "height": height,
                    "timestamp": 1630000000000,
                },
                "transactions": [{"id": "tx1"}]
            }
        }
        
        result = await get_block_by_height(height)
        
    assert isinstance(result, str)
    assert str(height) in result
    assert "block" in result.lower()


@pytest.mark.asyncio
async def test_get_blockchain_stats_server():
    """Test get_blockchain_stats MCP tool implementation."""
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
            "blockchainInfo": {
                "height": 1000000,
                "difficulty": 1000000000,
                "supply": 97000000000000000,
                "transactionCount": 5000000
            }
        }
        
        result = await get_blockchain_stats()
        
    assert isinstance(result, str)
    assert "1000000" in result  # height
    assert "blockchain" in result.lower()
    assert "statistics" in result.lower()


@pytest.mark.asyncio
async def test_get_token_price_server():
    """Test get_token_price MCP tool implementation."""
    token_id = "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"
    
    with patch('ergo_explorer.server.fetch_api', new_callable=AsyncMock) as mock_fetch_api:
        mock_fetch_api.return_value = {
            "tokenInfo": {
                "id": token_id,
                "name": "Test Token",
                "decimals": 2,
                "price": {
                    "erg": 0.01,
                    "usd": 0.05
                }
            }
        }
        
        result = await get_token_price(token_id)
        
    assert isinstance(result, str)
    assert token_id in result
    assert "price" in result.lower()
    assert "Test Token" in result 