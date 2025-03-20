"""
Tests for miscellaneous MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.misc import get_network_status


@pytest.mark.asyncio
async def test_get_network_status(mock_httpx_client):
    """Test get_network_status tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "networkStatus": {
            "height": 1000000,
            "headerId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
            "difficulty": 1000000000,
            "bestFullHeight": 999990,
            "bestHeaderId": "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7",
            "supplyAmount": 97000000000000000,  # in nanoERG
            "transactionsCount": 5000000,
            "peerCount": 100
        }
    }
    
    mock_httpx_client.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=MagicMock()):
        result = await get_network_status()
    
    assert isinstance(result, str)
    assert "1000000" in result  # height
    assert "97,000,000" in result or "97000000" in result  # supply in ERG
    assert "5,000,000" in result or "5000000" in result  # transaction count
    assert "network" in result.lower() 