"""Unit tests for Tokenomics functionality."""
import pytest
from unittest.mock import patch, AsyncMock
from ergo_explorer.tools import tokenomics
from ergo_explorer.api import ergodex

@pytest.fixture
def mock_token_search_result():
    return {
        "items": [
            {
                "id": "test_token_id_123456789",
                "name": "Test Token",
                "tokenType": {
                    "tokenId": "TEST"
                },
                "decimals": 2
            }
        ]
    }

@pytest.fixture
def mock_token_price():
    return {
        "price_in_erg": 0.01,
        "price_in_usd": 0.05,
        "liquidity": 1000.5,
        "volume_24h": 500.75,
        "pool_id": "test_pool_id",
        "source": "ErgoDEX"
    }

@pytest.fixture
def mock_price_history():
    return [
        {
            "timestamp": 1646092800000,
            "date": "2023-01-01",
            "price_in_erg": 0.01,
            "price_in_usd": 0.05
        },
        {
            "timestamp": 1646179200000,
            "date": "2023-01-02",
            "price_in_erg": 0.011,
            "price_in_usd": 0.055
        }
    ]

@pytest.fixture
def mock_liquidity_pools():
    return [
        {
            "pool_id": "pool_id_1",
            "base_token": {
                "id": "base_token_id_1",
                "name": "ERG",
                "decimals": 9,
                "reserves": 1000000000000
            },
            "quote_token": {
                "id": "quote_token_id_1",
                "name": "Test Token 1",
                "decimals": 2,
                "reserves": 5000000
            },
            "liquidity_erg": 1000.0,
            "tvl_usd": 5000.0,
            "volume_24h": {"base": 100.0, "quote": 200.0},
            "fee_percent": 0.3
        },
        {
            "pool_id": "pool_id_2",
            "base_token": {
                "id": "base_token_id_2",
                "name": "ERG",
                "decimals": 9,
                "reserves": 2000000000000
            },
            "quote_token": {
                "id": "quote_token_id_2",
                "name": "Test Token 2",
                "decimals": 0,
                "reserves": 1000000
            },
            "liquidity_erg": 2000.0,
            "tvl_usd": 10000.0,
            "volume_24h": {"base": 300.0, "quote": 400.0},
            "fee_percent": 0.3
        }
    ]

@pytest.mark.asyncio
async def test_get_token_price_info(mock_token_search_result, mock_token_price):
    """Test getting token price information."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        with patch('ergo_explorer.api.get_token_price', new_callable=AsyncMock) as mock_price:
            mock_search.return_value = mock_token_search_result
            mock_price.return_value = mock_token_price
            
            result = await tokenomics.get_token_price_info("test token")
            
            assert "Token Price Information for Test Token" in result
            assert "Current Price: 0.01000000 ERG ($0.0500)" in result
            assert "Liquidity: 1000.50 ERG" in result
            assert "24h Volume: 500.75 ERG" in result
            assert "Source: ErgoDEX" in result
            
            mock_search.assert_called_once_with("test token")
            mock_price.assert_called_once_with("test_token_id_123456789")

@pytest.mark.asyncio
async def test_get_token_price_info_not_found():
    """Test getting token price when token is not found."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"items": []}
        
        result = await tokenomics.get_token_price_info("nonexistent token")
        
        assert "No tokens found matching 'nonexistent token'" in result
        mock_search.assert_called_once_with("nonexistent token")

@pytest.mark.asyncio
async def test_get_token_price_info_no_liquidity(mock_token_search_result):
    """Test getting token price when there's no liquidity."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        with patch('ergo_explorer.api.get_token_price', new_callable=AsyncMock) as mock_price:
            mock_search.return_value = mock_token_search_result
            mock_price.return_value = {"error": "No liquidity pools found for token"}
            
            result = await tokenomics.get_token_price_info("test token")
            
            assert "Found token Test Token" in result
            assert "no liquidity pools found for token" in result
            
            mock_search.assert_called_once_with("test token")
            mock_price.assert_called_once_with("test_token_id_123456789")

@pytest.mark.asyncio
async def test_get_token_price_chart(mock_token_search_result, mock_price_history):
    """Test getting token price chart."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        with patch('ergo_explorer.api.get_price_history', new_callable=AsyncMock) as mock_history:
            mock_search.return_value = mock_token_search_result
            mock_history.return_value = mock_price_history
            
            result = await tokenomics.get_token_price_chart("test token", days=7)
            
            assert "Price History for Test Token (Last 7 days)" in result
            assert "2023-01-01" in result
            assert "2023-01-02" in result
            assert "0.01000000" in result
            assert "0.01100000" in result
            
            mock_search.assert_called_once_with("test token")
            mock_history.assert_called_once_with("test_token_id_123456789", 7)

@pytest.mark.asyncio
async def test_get_liquidity_pool_info(mock_liquidity_pools):
    """Test getting liquidity pool information."""
    with patch('ergo_explorer.api.get_liquidity_pools', new_callable=AsyncMock) as mock_pools:
        with patch('ergo_explorer.api.get_erg_price_usd', new_callable=AsyncMock) as mock_erg_price:
            mock_pools.return_value = mock_liquidity_pools
            mock_erg_price.return_value = 5.0
            
            result = await tokenomics.get_liquidity_pool_info()
            
            assert "Top Liquidity Pools on ErgoDEX" in result
            assert "ERG" in result
            assert "Test Token 1" in result
            assert "Test Token 2" in result
            assert "1,000.00" in result
            assert "2,000.00" in result
            
            mock_pools.assert_called_once_with(None)

@pytest.mark.asyncio
async def test_get_liquidity_pool_info_filtered(mock_token_search_result, mock_liquidity_pools):
    """Test getting filtered liquidity pool information."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        with patch('ergo_explorer.api.get_liquidity_pools', new_callable=AsyncMock) as mock_pools:
            with patch('ergo_explorer.api.get_erg_price_usd', new_callable=AsyncMock) as mock_erg_price:
                mock_search.return_value = mock_token_search_result
                mock_pools.return_value = mock_liquidity_pools
                mock_erg_price.return_value = 5.0
                
                result = await tokenomics.get_liquidity_pool_info("test token")
                
                assert "Liquidity Pools for Test Token" in result
                
                mock_search.assert_called_once_with("test token")
                mock_pools.assert_called_once_with("test_token_id_123456789")

@pytest.mark.asyncio
async def test_get_token_swap_info(mock_token_search_result, mock_liquidity_pools, mock_token_price):
    """Test getting token swap information."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        with patch('ergo_explorer.api.get_liquidity_pools', new_callable=AsyncMock) as mock_pools:
            with patch('ergo_explorer.api.get_token_price', new_callable=AsyncMock) as mock_price:
                # Setup mocks for two different tokens
                mock_search.side_effect = [
                    {"items": [{"id": "token1_id", "name": "Token 1", "decimals": 2}]},
                    {"items": [{"id": "token2_id", "name": "Token 2", "decimals": 2}]}
                ]
                mock_pools.return_value = [
                    {
                        "pool_id": "pool_direct",
                        "base_token": {"id": "token1_id", "name": "Token 1", "decimals": 2, "reserves": 1000000},
                        "quote_token": {"id": "token2_id", "name": "Token 2", "decimals": 2, "reserves": 2000000},
                        "liquidity_erg": 1000.0,
                        "fee_percent": 0.3
                    }
                ]
                
                result = await tokenomics.get_token_swap_info("token1", "token2", 100)
                
                assert "Swap Estimate:" in result
                assert "Token 1" in result
                assert "Token 2" in result
                assert "Direct swap via pool" in result
                
                assert mock_search.call_count == 2
                mock_pools.assert_called_once()

@pytest.mark.asyncio
async def test_token_swap_info_error_handling():
    """Test error handling in token swap info."""
    with patch('ergo_explorer.api.search_tokens', new_callable=AsyncMock) as mock_search:
        # Test invalid amount
        result = await tokenomics.get_token_swap_info("token1", "token2", -1)
        assert "Amount must be greater than 0" in result
        
        # Test token not found
        mock_search.return_value = {"items": []}
        result = await tokenomics.get_token_swap_info("nonexistent", "token2", 100)
        assert "No tokens found matching source token 'nonexistent'" in result 