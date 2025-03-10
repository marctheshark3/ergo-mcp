"""Unit tests for validation scripts."""
import pytest
import sys
import os
import importlib.util
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.fixture
def mock_get_token_price_info():
    """Mock get_token_price_info function."""
    return AsyncMock(return_value="Mock token price info")


@pytest.fixture
def mock_get_token_price_chart():
    """Mock get_token_price_chart function."""
    return AsyncMock(return_value="Mock token price chart")


@pytest.fixture
def mock_get_liquidity_pool_info():
    """Mock get_liquidity_pool_info function."""
    return AsyncMock(return_value="Mock liquidity pool info")


@pytest.fixture
def mock_get_token_swap_info():
    """Mock get_token_swap_info function."""
    return AsyncMock(return_value="Mock token swap info")


@pytest.fixture
def mock_analyze_smart_contract():
    """Mock analyze_smart_contract function."""
    return AsyncMock(return_value="Mock contract analysis")


@pytest.fixture
def mock_get_contract_statistics():
    """Mock get_contract_statistics function."""
    return AsyncMock(return_value="Mock contract statistics")


@pytest.fixture
def mock_simulate_contract_execution():
    """Mock simulate_contract_execution function."""
    return AsyncMock(return_value="Mock contract simulation")


@pytest.fixture
def mock_ergo_module():
    """Create a mock ergo module with tokenomics and contracts submodules."""
    mock_ergo = MagicMock()
    mock_ergo.tools = MagicMock()
    mock_ergo.tools.tokenomics = MagicMock()
    mock_ergo.tools.contracts = MagicMock()
    
    return mock_ergo


def test_validate_features_imports():
    """Test that validate_features.py can be imported without errors."""
    with patch.dict('sys.modules'):  
        # Remove existing imports to ensure clean import
        if 'ergo_explorer' in sys.modules:
            del sys.modules['ergo_explorer']
        if 'ergo_explorer.tools' in sys.modules:
            del sys.modules['ergo_explorer.tools']
            
        # Make all the imports we might need
        with patch('validate_features.get_token_price_info'), \
             patch('validate_features.get_token_price_chart'), \
             patch('validate_features.get_liquidity_pool_info'), \
             patch('validate_features.get_token_swap_info'), \
             patch('validate_features.analyze_smart_contract'), \
             patch('validate_features.get_contract_statistics'), \
             patch('validate_features.simulate_contract_execution'):
            
            # Load the validate_features module with our mocked dependencies
            spec = importlib.util.spec_from_file_location("validate_features", "validate_features.py")
            validate_features = importlib.util.module_from_spec(spec)
            sys.modules['validate_features'] = validate_features
            
            try:
                # Execute the module
                spec.loader.exec_module(validate_features)
                
                assert hasattr(validate_features, "main")
                assert hasattr(validate_features, "validate_tokenomics_features")
                assert hasattr(validate_features, "validate_contract_features")
                assert hasattr(validate_features, "generate_report")
            except Exception as e:
                pytest.fail(f"Failed to import validate_features.py: {str(e)}")
            finally:
                # Clean up
                if 'validate_features' in sys.modules:
                    del sys.modules['validate_features']


def test_quick_validate_imports():
    """Test that quick_validate.py can be imported without errors."""
    with patch.dict('sys.modules'):
        # Remove existing imports to ensure clean import
        if 'ergo_explorer' in sys.modules:
            del sys.modules['ergo_explorer']
        if 'ergo_explorer.tools' in sys.modules:
            del sys.modules['ergo_explorer.tools']
            
        # Make all the imports we might need 
        with patch('quick_validate.get_token_price_info'), \
             patch('quick_validate.get_token_price_chart'), \
             patch('quick_validate.get_liquidity_pool_info'), \
             patch('quick_validate.get_token_swap_info'), \
             patch('quick_validate.analyze_smart_contract'), \
             patch('quick_validate.get_contract_statistics'), \
             patch('quick_validate.simulate_contract_execution'):
            
            # Load the quick_validate module with our mocked dependencies
            spec = importlib.util.spec_from_file_location("quick_validate", "quick_validate.py")
            quick_validate = importlib.util.module_from_spec(spec)
            sys.modules['quick_validate'] = quick_validate
            
            try:
                # Execute the module
                spec.loader.exec_module(quick_validate)
                
                assert hasattr(quick_validate, "main")
                assert hasattr(quick_validate, "validate_token_price")
                assert hasattr(quick_validate, "validate_liquidity_pools")
                assert hasattr(quick_validate, "validate_token_swap")
                assert hasattr(quick_validate, "validate_contract_analysis")
                assert hasattr(quick_validate, "validate_contract_statistics")
                assert hasattr(quick_validate, "validate_contract_simulation")
            except Exception as e:
                pytest.fail(f"Failed to import quick_validate.py: {str(e)}")
            finally:
                # Clean up
                if 'quick_validate' in sys.modules:
                    del sys.modules['quick_validate']


@pytest.mark.asyncio
async def test_quick_validate_token_price(monkeypatch):
    """Test validate_token_price function in quick_validate.py with monkeypatch."""
    mock_price = AsyncMock(return_value="Mock token price info")
    mock_chart = AsyncMock(return_value="Mock token price chart")
    
    # Import the module directly 
    from quick_validate import validate_token_price
    
    # Monkeypatch the imported functions
    monkeypatch.setattr('quick_validate.get_token_price_info', mock_price)
    monkeypatch.setattr('quick_validate.get_token_price_chart', mock_chart)
    
    # Test the function
    result = await validate_token_price("test_token")
    
    # Verify results
    assert result == 0
    mock_price.assert_called_once_with("test_token")
    mock_chart.assert_called_once_with("test_token", days=7)


@pytest.mark.asyncio
async def test_quick_validate_liquidity_pools(monkeypatch):
    """Test validate_liquidity_pools function in quick_validate.py with monkeypatch."""
    mock_pools = AsyncMock(return_value="Mock liquidity pool info")
    
    # Import the module directly
    from quick_validate import validate_liquidity_pools
    
    # Monkeypatch the imported function
    monkeypatch.setattr('quick_validate.get_liquidity_pool_info', mock_pools)
    
    # Test with token
    result = await validate_liquidity_pools("test_token")
    assert result == 0
    mock_pools.assert_called_with("test_token")
    
    # Test without token
    mock_pools.reset_mock()
    result = await validate_liquidity_pools()
    assert result == 0
    mock_pools.assert_called_with(None)


@pytest.mark.asyncio
async def test_quick_validate_token_swap(monkeypatch):
    """Test validate_token_swap function in quick_validate.py with monkeypatch."""
    mock_swap = AsyncMock(return_value="Mock token swap info")
    
    # Import the module directly
    from quick_validate import validate_token_swap
    
    # Monkeypatch the imported function
    monkeypatch.setattr('quick_validate.get_token_swap_info', mock_swap)
    
    # Test the function
    result = await validate_token_swap("from_token", "to_token", 10.0)
    
    # Verify results
    assert result == 0
    mock_swap.assert_called_once_with("from_token", "to_token", 10.0)


@pytest.mark.asyncio
async def test_quick_validate_contract_analysis(monkeypatch):
    """Test validate_contract_analysis function in quick_validate.py with monkeypatch."""
    mock_analyze = AsyncMock(return_value="Mock contract analysis")
    
    # Import the module directly
    from quick_validate import validate_contract_analysis
    
    # Monkeypatch the imported function
    monkeypatch.setattr('quick_validate.analyze_smart_contract', mock_analyze)
    
    # Test the function
    result = await validate_contract_analysis("test_address")
    
    # Verify results
    assert result == 0
    mock_analyze.assert_called_once_with("test_address")


@pytest.mark.asyncio
async def test_quick_validate_contract_statistics(monkeypatch):
    """Test validate_contract_statistics function in quick_validate.py with monkeypatch."""
    mock_stats = AsyncMock(return_value="Mock contract statistics")
    
    # Import the module directly
    from quick_validate import validate_contract_statistics
    
    # Monkeypatch the imported function
    monkeypatch.setattr('quick_validate.get_contract_statistics', mock_stats)
    
    # Test the function
    result = await validate_contract_statistics()
    
    # Verify results
    assert result == 0
    mock_stats.assert_called_once()


@pytest.mark.asyncio
async def test_quick_validate_contract_simulation(monkeypatch):
    """Test validate_contract_simulation function in quick_validate.py with monkeypatch."""
    mock_simulate = AsyncMock(return_value="Mock contract simulation")
    
    # Import the module directly
    from quick_validate import validate_contract_simulation
    
    # Monkeypatch the imported function
    monkeypatch.setattr('quick_validate.simulate_contract_execution', mock_simulate)
    
    # Test the function
    result = await validate_contract_simulation("test_address")
    
    # Verify results
    assert result == 0
    mock_simulate.assert_called_once()
    # Check that the address was passed correctly
    args, _ = mock_simulate.call_args
    assert args[0] == "test_address" 