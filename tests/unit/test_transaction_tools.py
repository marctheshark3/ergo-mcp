"""
Tests for transaction-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.transaction import analyze_transaction


@pytest.mark.asyncio
async def test_analyze_transaction(mock_httpx_client, sample_transaction_id):
    """Test analyze_transaction tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "id": sample_transaction_id,
        "blockId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
        "inclusionHeight": 1000000,
        "timestamp": 1630000000000,
        "index": 1,
        "confirmationsCount": 1000,
        "inputs": [
            {
                "id": "input1",
                "value": 1000000000,
                "address": "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA",
                "spendingProof": "proof1"
            }
        ],
        "outputs": [
            {
                "id": "output1",
                "value": 900000000,
                "address": "9f9q6Hs7vXZSQwhbrptQZLkTx15ApjbEkQwWXJqD2NpaouiigJQ",
                "assets": [],
                "creationHeight": 1000000,
                "ergoTree": "ergo_tree_hash",
                "additionalRegisters": {}
            }
        ],
        "size": 300
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    
    async with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        result = await analyze_transaction(sample_transaction_id)
    
    assert isinstance(result, dict)
    assert sample_transaction_id in str(result)
    assert "inputs" in str(result).lower()
    assert "outputs" in str(result).lower()
    assert "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA" in str(result) 