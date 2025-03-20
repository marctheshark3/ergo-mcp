"""
Tests for token-related MCP tools.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ergo_explorer.tools.token import (
    search_for_token,
    get_token_price
)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_search_for_token(mock_client, mock_httpx_client):
    """Test search_for_token tool."""
    # Mock response data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "token1",
                "name": "Test Token",
                "decimals": 2,
                "supply": 1000000,
                "description": "Test token description"
            },
            {
                "id": "token2",
                "name": "Another Token",
                "decimals": 4,
                "supply": 500000,
                "description": "Another test token"
            }
        ],
        "total": 2
    })
    
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    mock_client.return_value = mock_httpx_client
    
    result = await search_for_token("Test")
    
    assert isinstance(result, dict)
    assert "token1" in str(result)
    assert "token2" in str(result)
    assert "Test Token" in str(result)
    assert "Another Token" in str(result)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_token_price(mock_client, mock_httpx_client, sample_token_id):
    """Test get_token_price tool."""
    # Mock response data for token price
    mock_token_response = AsyncMock()
    mock_token_response.status_code = 200
    mock_token_response.json = AsyncMock(return_value={
        "priceInErg": 0.001,
        "tokenId": sample_token_id,
        "tokenName": "Test Token",
        "liquidity": {
            "totalLiquidityErg": 1000000000  # in nanoERG
        }
    })
    
    # Mock response data for ERG price
    mock_erg_response = AsyncMock()
    mock_erg_response.status_code = 200
    mock_erg_response.json = AsyncMock(return_value={
        "price": 50.0  # USD per ERG
    })
    
    mock_httpx_client.get = AsyncMock(side_effect=[mock_token_response, mock_erg_response])
    mock_client.return_value = mock_httpx_client
    
    result = await get_token_price(sample_token_id)
    
    assert isinstance(result, dict)
    assert sample_token_id in str(result)
    assert "Test Token" in str(result)
    assert "0.001" in str(result)  # ERG price
    assert "50.0" in str(result)  # ERG/USD price
    assert "0.05" in str(result)  # Token USD price (0.001 * 50.0) 