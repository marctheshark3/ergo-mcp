"""
Tests for the token_counter utilities in ergo_explorer.util.token_counter.

This file contains tests for the token counting utilities used
for estimating token usage in API responses.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from ergo_explorer.util.token_counter import (
    count_tokens,
    count_json_tokens,
    estimate_response_tokens,
    should_truncate,
    get_token_usage_tier,
    get_tokenizer,
    get_tokenizer_for_model,
    MODEL_TO_ENCODING,
    TIKTOKEN_AVAILABLE
)

# Sample test data
SAMPLE_TEXT = "This is a test string for token counting"
SAMPLE_JSON = {
    "status": "success",
    "data": {
        "id": 123,
        "name": "Test Item",
        "description": "This is a test description",
        "tags": ["test", "example", "sample"],
        "nested": {
            "field1": "value1",
            "field2": 42
        }
    },
    "metadata": {
        "execution_time_ms": 42,
        "result_count": 1
    }
}

SAMPLE_RESPONSE = {
    "status": "success",
    "data": {
        "address": "9hdcMw4eRpJPJGx8RJhvdRgFRsE1URpQCsAWM3wG547gQ9awZgi",
        "balance": 1000000000,
        "transactions": [
            {"id": "tx1", "value": 100},
            {"id": "tx2", "value": 200}
        ]
    },
    "metadata": {
        "execution_time_ms": 123,
        "result_count": 2
    }
}

# Test basic token counting functionality
def test_count_tokens():
    """Test the count_tokens function."""
    # Should return a positive integer for non-empty text
    assert count_tokens(SAMPLE_TEXT) > 0
    
    # Empty text should have zero tokens
    assert count_tokens("") == 0
    
    # None should have zero tokens
    assert count_tokens(None) == 0
    
    # Test different model types
    for model_type in ["claude", "gpt-4", "gpt-3.5", "gemini"]:
        token_count = count_tokens(SAMPLE_TEXT, model_type)
        assert isinstance(token_count, int)
        assert token_count > 0

# Test JSON token counting
def test_count_json_tokens():
    """Test the count_json_tokens function."""
    # Should return a positive integer for non-empty JSON
    token_count = count_json_tokens(SAMPLE_JSON)
    assert isinstance(token_count, int)
    assert token_count > 0
    
    # Empty dict should have minimal tokens (likely just 2 for {})
    assert count_json_tokens({}) < 5
    
    # None should have zero tokens
    assert count_json_tokens(None) == 0
    
    # Test different model types
    for model_type in ["claude", "gpt-4", "gpt-3.5", "gemini"]:
        token_count = count_json_tokens(SAMPLE_JSON, model_type)
        assert isinstance(token_count, int)
        assert token_count > 0

# Test response token estimation
def test_estimate_response_tokens():
    """Test the estimate_response_tokens function."""
    # Should return a tuple of (total_tokens, breakdown)
    total, breakdown = estimate_response_tokens(SAMPLE_RESPONSE)
    
    # Check total is positive
    assert isinstance(total, int)
    assert total > 0
    
    # Check breakdown contains expected keys
    assert "data" in breakdown
    assert "metadata" in breakdown
    assert "status" in breakdown
    
    # Check values are integers
    for key, value in breakdown.items():
        assert isinstance(value, int)
    
    # Total should be sum of breakdown values
    assert total == sum(breakdown.values())
    
    # Test with include_metadata=False
    total_no_meta, breakdown_no_meta = estimate_response_tokens(
        SAMPLE_RESPONSE, include_metadata=False
    )
    assert breakdown_no_meta["metadata"] == 0
    
    # Test different model types
    for model_type in ["claude", "gpt-4", "gpt-3.5", "gemini"]:
        total, breakdown = estimate_response_tokens(SAMPLE_RESPONSE, model_type=model_type)
        assert isinstance(total, int)
        assert total > 0

# Test truncation threshold logic
def test_should_truncate():
    """Test the should_truncate function."""
    # Below threshold should return False
    assert should_truncate(1000, threshold=2000) is False
    
    # Equal to threshold should return False
    assert should_truncate(2000, threshold=2000) is False
    
    # Above threshold should return True
    assert should_truncate(2500, threshold=2000) is True
    
    # Test model-specific adjustments
    # GPT-3.5 should have a lower threshold
    assert should_truncate(1700, threshold=2000, model_type="gpt-3.5") is True
    
    # GPT-4 should have a higher threshold
    assert should_truncate(2300, threshold=2000, model_type="gpt-4") is False

# Test token usage tier categorization 
def test_get_token_usage_tier():
    """Test the get_token_usage_tier function."""
    # Test boundaries and categories
    assert get_token_usage_tier(0) == "minimal"
    assert get_token_usage_tier(499) == "minimal"
    assert get_token_usage_tier(500) == "standard"
    assert get_token_usage_tier(1999) == "standard"
    assert get_token_usage_tier(2000) == "intensive"
    assert get_token_usage_tier(4999) == "intensive"
    assert get_token_usage_tier(5000) == "excessive"
    assert get_token_usage_tier(10000) == "excessive"

# Test tokenizer retrieval
def test_get_tokenizer():
    """Test the get_tokenizer function."""
    if not TIKTOKEN_AVAILABLE:
        pytest.skip("tiktoken not available")
    
    # Should return a tokenizer for valid encoding
    tokenizer = get_tokenizer("cl100k_base")
    assert tokenizer is not None
    
    # Should return None for invalid encoding
    with patch("tiktoken.get_encoding", side_effect=Exception("Invalid encoding")):
        tokenizer = get_tokenizer("invalid_encoding")
        assert tokenizer is None

# Test model-specific tokenizer retrieval
def test_get_tokenizer_for_model():
    """Test the get_tokenizer_for_model function."""
    if not TIKTOKEN_AVAILABLE:
        pytest.skip("tiktoken not available")
    
    # Should return a tokenizer for known models
    for model in MODEL_TO_ENCODING.keys():
        tokenizer = get_tokenizer_for_model(model)
        assert tokenizer is not None
    
    # Should use default encoding for unknown model
    tokenizer = get_tokenizer_for_model("unknown_model")
    assert tokenizer is not None

# Test fallback behavior when tiktoken is not available
def test_fallback_behavior():
    """Test the fallback behavior when tiktoken is not available."""
    # Mock tiktoken as unavailable
    with patch("ergo_explorer.util.token_counter.TIKTOKEN_AVAILABLE", False):
        # Should use character-based estimation
        token_count = count_tokens(SAMPLE_TEXT)
        # Just verify type and reasonable value, not exact calculation
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count <= len(SAMPLE_TEXT)
        
        # JSON tokens should also work with fallback
        token_count = count_json_tokens(SAMPLE_JSON)
        assert isinstance(token_count, int)
        
        # Response estimation should work with fallback
        total, breakdown = estimate_response_tokens(SAMPLE_RESPONSE)
        assert isinstance(total, int)
        assert isinstance(breakdown, dict)

# Test error handling in count_tokens
def test_error_handling():
    """Test error handling in token counting functions."""
    # Should handle exceptions in token counting
    with patch("ergo_explorer.util.token_counter.get_tokenizer_for_model", return_value=None):
        # Should fall back to character-based estimation
        token_count = count_tokens(SAMPLE_TEXT)
        # Just verify type and reasonable value, not exact calculation
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count <= len(SAMPLE_TEXT)
    
    # Should handle exceptions in JSON conversion
    with patch("json.dumps", side_effect=Exception("Test error")):
        # Should return 0 on error
        token_count = count_json_tokens(SAMPLE_JSON)
        assert token_count == 0

# Test with various data types and sizes
@pytest.mark.parametrize("data", [
    # Simple types
    "Short text",
    "A" * 1000,  # Long text
    123,
    True,
    None,
    
    # Collections
    [],
    ["item1", "item2", "item3"],
    {"key": "value"},
    
    # Nested structures
    {"data": {"nested": {"deeply": {"value": 42}}}},
    [{"item": 1}, {"item": 2}, [1, 2, 3]]
])
def test_various_data_types(data):
    """Test token counting with various data types."""
    # Should handle all data types without errors
    token_count = count_json_tokens(data)
    assert isinstance(token_count, int)
    
    # For None, should return 0
    if data is None:
        assert token_count == 0 