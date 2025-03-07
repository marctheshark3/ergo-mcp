"""Unit tests for ErgoWatch integration."""
import pytest
from unittest.mock import patch, AsyncMock
from ergo_explorer.tools import ergowatch
from ergo_explorer.api import ergowatch as ergowatch_api

@pytest.fixture
def mock_balance_history():
    return [
        {
            "timestamp": 1646092800000,
            "height": 100000,
            "balance": 1000000000  # 1 ERG
        },
        {
            "timestamp": 1646179200000,
            "height": 100100,
            "balance": 2000000000  # 2 ERG
        }
    ]

@pytest.fixture
def mock_balance_at_height():
    return {
        "amount": 1000000000,  # 1 ERG
        "token_name": "ERG",
        "height": 100000
    }

@pytest.fixture
def mock_contract_stats():
    return {
        "count": 1000,
        "amount": 100000000000,  # 100 ERG
        "percentage": 0.5
    }

@pytest.fixture
def mock_exchange_addresses():
    return [
        {
            "name": "Exchange 1",
            "address": "9test1address",
            "balance": 1000000000000  # 1000 ERG
        },
        {
            "name": "Exchange 2",
            "address": "9test2address",
            "balance": 2000000000000  # 2000 ERG
        }
    ]

@pytest.fixture
def mock_rich_list():
    return {
        "token_name": "ERG",
        "addresses": [
            {
                "address": "9rich1address",
                "balance": 10000000000000  # 10000 ERG
            },
            {
                "address": "9rich2address",
                "balance": 5000000000000   # 5000 ERG
            }
        ]
    }

@pytest.fixture
def mock_address_rank():
    return {
        "rank": 100,
        "total": 10000,
        "balance": 1000000000000  # 1000 ERG
    }

@pytest.mark.asyncio
async def test_get_address_balance_history(mock_balance_history):
    """Test getting address balance history."""
    with patch.object(ergowatch_api, 'get_address_balance_history', new_callable=AsyncMock) as mock_history:
        mock_history.return_value = mock_balance_history
        result = await ergowatch.get_address_balance_history("test_address")
        assert "Balance History for test_address:" in result
        assert "Height 100000" in result
        assert "Height 100100" in result
        mock_history.assert_called_once_with("test_address", None)

@pytest.mark.asyncio
async def test_get_address_balance_at_height(mock_balance_at_height):
    """Test getting address balance at specific height."""
    with patch.object(ergowatch_api, 'get_address_balance_at_height', new_callable=AsyncMock) as mock_balance:
        mock_balance.return_value = mock_balance_at_height
        result = await ergowatch.get_address_balance_at_height("test_address", 100000)
        assert "Balance for test_address at height 100000:" in result
        assert "1 ERG" in result
        mock_balance.assert_called_once_with("test_address", 100000, None)

@pytest.mark.asyncio
async def test_get_contract_stats(mock_contract_stats):
    """Test getting contract statistics."""
    with patch.object(ergowatch_api, 'get_contract_address_count', new_callable=AsyncMock) as mock_count:
        with patch.object(ergowatch_api, 'get_contracts_supply', new_callable=AsyncMock) as mock_supply:
            mock_count.return_value = {"count": mock_contract_stats["count"]}
            mock_supply.return_value = {
                "amount": mock_contract_stats["amount"],
                "percentage": mock_contract_stats["percentage"]
            }
            
            result = await ergowatch.get_contract_stats()
            assert "Contract Address Statistics:" in result
            assert "1000" in result  # count
            assert "100.00 ERG" in result  # amount
            assert "0.50%" in result  # percentage
            
            mock_count.assert_called_once()
            mock_supply.assert_called_once()

@pytest.mark.asyncio
async def test_get_exchange_addresses(mock_exchange_addresses):
    """Test getting exchange addresses."""
    with patch.object(ergowatch_api, 'get_exchange_addresses', new_callable=AsyncMock) as mock_exchanges:
        mock_exchanges.return_value = mock_exchange_addresses
        result = await ergowatch.get_exchange_addresses()
        assert "Tracked Exchange Addresses:" in result
        assert "Exchange 1" in result
        assert "Exchange 2" in result
        assert "1000.00 ERG" in result
        assert "2000.00 ERG" in result
        mock_exchanges.assert_called_once()

@pytest.mark.asyncio
async def test_get_rich_list(mock_rich_list):
    """Test getting rich list."""
    with patch.object(ergowatch_api, 'get_rich_list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_rich_list
        result = await ergowatch.get_rich_list(limit=2)
        assert "Top 2 Addresses by ERG Balance:" in result
        assert "9rich1address" in result
        assert "9rich2address" in result
        assert "10000.00 ERG" in result
        assert "5000.00 ERG" in result
        mock_list.assert_called_once_with(limit=2, token_id=None)

@pytest.mark.asyncio
async def test_get_address_rank(mock_address_rank):
    """Test getting address rank."""
    with patch.object(ergowatch_api, 'get_p2pk_address_rank', new_callable=AsyncMock) as mock_rank:
        mock_rank.return_value = mock_address_rank
        result = await ergowatch.get_address_rank("test_address")
        assert "Address Ranking for test_address:" in result
        assert "Rank: 100 of 10000" in result
        assert "1000.00 ERG" in result
        mock_rank.assert_called_once_with("test_address")

@pytest.mark.asyncio
async def test_empty_responses():
    """Test handling of empty responses."""
    with patch.object(ergowatch_api, 'get_address_balance_history', new_callable=AsyncMock) as mock_history:
        with patch.object(ergowatch_api, 'get_exchange_addresses', new_callable=AsyncMock) as mock_exchanges:
            with patch.object(ergowatch_api, 'get_rich_list', new_callable=AsyncMock) as mock_rich:
                mock_history.return_value = []
                mock_exchanges.return_value = []
                mock_rich.return_value = None
                
                assert "No balance history found" in await ergowatch.get_address_balance_history("test_address")
                assert "No exchange addresses found" in await ergowatch.get_exchange_addresses()
                assert "No addresses found" in await ergowatch.get_rich_list() 