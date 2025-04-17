"""
Tests for token export functionality.
"""

import pytest
import os
import json
import tempfile
from unittest.mock import AsyncMock, patch, MagicMock, mock_open

from ergo_explorer.tools.export_token_holders import export_token_holders
from ergo_explorer.tools.batch_export_token_holders import (
    batch_export_token_holders, 
    read_token_ids_from_file,
    main_async
)


@pytest.mark.asyncio
@patch('ergo_explorer.tools.export_token_holders.get_token_holders')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
async def test_export_token_holders(mock_makedirs, mock_file, mock_get_token_holders, sample_token_id):
    """Test export_token_holders function."""
    # Mock token holders data
    mock_token_data = {
        "token_id": sample_token_id,
        "token_name": "Test Token",
        "decimals": 2,
        "total_supply": 1000,
        "total_holders": 2,
        "holders": [
            {"address": "address1", "amount": 600, "percentage": 60.0},
            {"address": "address2", "amount": 400, "percentage": 40.0}
        ]
    }
    mock_get_token_holders.return_value = mock_token_data
    
    # Call export function
    output_dir = "test_output"
    result = await export_token_holders(sample_token_id, output_dir)
    
    # Verify function calls
    mock_makedirs.assert_called_once_with(output_dir)
    mock_get_token_holders.assert_called_once_with(
        sample_token_id, include_raw=True, include_analysis=False
    )
    
    # Verify file was opened and data was written
    assert mock_file.call_count == 1
    call_args = mock_file.call_args[0][0]
    assert call_args.startswith(output_dir)
    assert call_args.endswith(".json")
    assert sample_token_id[:8] in call_args
    
    # Verify json.dump was called with the correct data
    handle = mock_file()
    handle.write.assert_called()
    
    # Verify result
    assert result is True


@pytest.mark.asyncio
@patch('ergo_explorer.tools.export_token_holders.get_token_holders')
async def test_export_token_holders_error(mock_get_token_holders, sample_token_id):
    """Test export_token_holders function with error."""
    # Mock get_token_holders to raise exception
    mock_get_token_holders.side_effect = Exception("Test error")
    
    # Call export function
    result = await export_token_holders(sample_token_id)
    
    # Verify result
    assert result is False


@pytest.mark.asyncio
@patch('ergo_explorer.tools.batch_export_token_holders.export_token_holders')
async def test_batch_export_token_holders(mock_export, sample_token_id):
    """Test batch_export_token_holders function."""
    # Mock export_token_holders to return success
    mock_export.return_value = True
    
    # Create test token IDs
    token_ids = [sample_token_id, sample_token_id + "1", sample_token_id + "2"]
    
    # Call batch export function
    with tempfile.TemporaryDirectory() as temp_dir:
        success, errors = await batch_export_token_holders(token_ids, temp_dir)
    
    # Verify function was called for each token
    assert mock_export.call_count == len(token_ids)
    for i, token_id in enumerate(token_ids):
        args, kwargs = mock_export.call_args_list[i]
        assert args[0] == token_id
    
    # Verify result counts
    assert success == len(token_ids)
    assert errors == 0


@pytest.mark.asyncio
@patch('ergo_explorer.tools.batch_export_token_holders.export_token_holders')
async def test_batch_export_with_errors(mock_export, sample_token_id):
    """Test batch_export_token_holders function with some errors."""
    # Mock export_token_holders to alternate success and failure
    mock_export.side_effect = [True, False, True]
    
    # Create test token IDs
    token_ids = [sample_token_id, sample_token_id + "1", sample_token_id + "2"]
    
    # Call batch export function
    with tempfile.TemporaryDirectory() as temp_dir:
        success, errors = await batch_export_token_holders(token_ids, temp_dir)
    
    # Verify result counts
    assert success == 2
    assert errors == 1


@patch('builtins.open', new_callable=mock_open, read_data="token1\ntoken2\n# Comment\n\ntoken3")
def test_read_token_ids_from_file(mock_file):
    """Test read_token_ids_from_file function."""
    # Call function
    token_ids = read_token_ids_from_file("test_file.txt")
    
    # Verify file was opened
    mock_file.assert_called_once_with("test_file.txt", 'r')
    
    # Verify result
    assert token_ids == ["token1", "token2", "token3"]
    assert len(token_ids) == 3  # Comments and empty lines should be skipped


@patch('builtins.open', side_effect=Exception("File not found"))
def test_read_token_ids_from_file_error(mock_file):
    """Test read_token_ids_from_file function with error."""
    # Call function
    token_ids = read_token_ids_from_file("nonexistent_file.txt")
    
    # Verify result is empty list
    assert token_ids == []


@pytest.mark.asyncio
@patch('ergo_explorer.tools.batch_export_token_holders.batch_export_token_holders')
@patch('ergo_explorer.tools.batch_export_token_holders.read_token_ids_from_file')
async def test_main_async_with_file(mock_read_file, mock_batch_export):
    """Test main_async function with token IDs from file."""
    # Mock arguments
    args = MagicMock()
    args.file = "tokens.txt"
    args.tokens = None
    args.output_dir = "output"
    
    # Mock read_token_ids_from_file
    mock_read_file.return_value = ["token1", "token2"]
    
    # Mock batch_export_token_holders
    mock_batch_export.return_value = (2, 0)
    
    # Call function
    result = await main_async(args)
    
    # Verify function calls
    mock_read_file.assert_called_once_with("tokens.txt")
    mock_batch_export.assert_called_once_with(["token1", "token2"], "output")
    
    # Verify result
    assert result is True


@pytest.mark.asyncio
@patch('ergo_explorer.tools.batch_export_token_holders.batch_export_token_holders')
async def test_main_async_with_tokens(mock_batch_export):
    """Test main_async function with token IDs from arguments."""
    # Mock arguments
    args = MagicMock()
    args.file = None
    args.tokens = ["token1", "token2"]
    args.output_dir = "output"
    
    # Mock batch_export_token_holders
    mock_batch_export.return_value = (2, 0)
    
    # Call function
    result = await main_async(args)
    
    # Verify function calls
    mock_batch_export.assert_called_once_with(["token1", "token2"], "output")
    
    # Verify result
    assert result is True


@pytest.mark.asyncio
@patch('ergo_explorer.tools.batch_export_token_holders.batch_export_token_holders')
async def test_main_async_no_tokens(mock_batch_export):
    """Test main_async function with no token IDs."""
    # Mock arguments
    args = MagicMock()
    args.file = None
    args.tokens = None
    
    # Call function
    result = await main_async(args)
    
    # Verify result
    assert result is False
    mock_batch_export.assert_not_called() 