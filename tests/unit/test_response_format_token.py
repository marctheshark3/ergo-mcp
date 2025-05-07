"""
Tests for token estimation functionality in the response_format module.

This test file verifies that token estimation is correctly integrated
into the response standardization process.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from ergo_explorer.response_format import (
    ResponseMetadata,
    MCPResponse,
    standardize_response,
    format_response,
    TOKEN_COUNTER_AVAILABLE
)

# Sample test data
SAMPLE_DATA = {
    "address": "9hdcMw4eRpJPJGx8RJhvdRgFRsE1URpQCsAWM3wG547gQ9awZgi",
    "balance": 1000000000,
    "transactions": [
        {"id": "tx1", "value": 100},
        {"id": "tx2", "value": 200}
    ]
}

# Test response metadata token estimation
def test_response_metadata_token_estimation():
    """Test token estimation in ResponseMetadata."""
    metadata = ResponseMetadata()
    metadata.finish()
    
    # Set result metrics with token estimation
    metadata.set_result_metrics(SAMPLE_DATA, False, None, "claude")
    
    # Token estimate should be set
    assert metadata.token_estimate is not None
    assert isinstance(metadata.token_estimate, int)
    assert metadata.token_estimate > 0
    
    # Check dictionary representation
    metadata_dict = metadata.to_dict()
    assert "token_estimate" in metadata_dict
    assert metadata_dict["token_estimate"] == metadata.token_estimate

# Test token estimation in MCPResponse
def test_mcp_response_token_estimation():
    """Test token estimation in MCPResponse."""
    # Create a response with sample data
    response = MCPResponse(data=SAMPLE_DATA, model_type="claude")
    response.finish()
    
    # Convert to dict and check token estimation
    response_dict = response.to_dict()
    assert "metadata" in response_dict
    assert "token_estimate" in response_dict["metadata"]
    assert response_dict["metadata"]["token_estimate"] > 0
    
    # If token counter is available, breakdown should be set
    if TOKEN_COUNTER_AVAILABLE:
        assert "token_breakdown" in response_dict["metadata"]
        assert isinstance(response_dict["metadata"]["token_breakdown"], dict)

# Test token estimation with different model types
@pytest.mark.parametrize("model_type", [
    "claude",
    "gpt-4",
    "gpt-3.5",
    "gemini",
    "mistral",
    "llama"
])
def test_model_specific_token_estimation(model_type):
    """Test token estimation with different model types."""
    # Create a response with specific model type
    response = MCPResponse(data=SAMPLE_DATA, model_type=model_type)
    response.finish()
    
    # Convert to dict and check token estimation
    response_dict = response.to_dict()
    assert "token_estimate" in response_dict["metadata"]
    assert response_dict["metadata"]["token_estimate"] > 0

# Test standardize_response decorator
def test_standardize_response_decorator():
    """Test token estimation in standardize_response decorator."""
    # Create a test function with the decorator
    @standardize_response
    def test_func(data):
        return data
    
    # Call the function with sample data
    result = test_func(SAMPLE_DATA)
    
    # Result should be an MCPResponse
    assert isinstance(result, MCPResponse)
    
    # Convert to dict and check token estimation
    result_dict = result.to_dict()
    assert "metadata" in result_dict
    assert "token_estimate" in result_dict["metadata"]
    assert result_dict["metadata"]["token_estimate"] > 0

# Test format_response with token estimation
def test_format_response():
    """Test token estimation in format_response function."""
    # Format raw data
    formatted = format_response(SAMPLE_DATA, model_type="claude")
    
    # Check token estimation
    assert "metadata" in formatted
    assert "token_estimate" in formatted["metadata"]
    assert formatted["metadata"]["token_estimate"] > 0
    
    # Test with minimal format
    minimal = format_response(SAMPLE_DATA, verbose=False)
    assert "metadata" not in minimal

# Test token estimation when tiktoken is not available
def test_token_estimation_without_tiktoken():
    """Test token estimation when tiktoken is not available."""
    # Mock tiktoken as unavailable
    with patch("ergo_explorer.response_format.TOKEN_COUNTER_AVAILABLE", False), \
         patch("ergo_explorer.util.token_counter.TIKTOKEN_AVAILABLE", False):
        
        # Create a response with sample data
        response = MCPResponse(data=SAMPLE_DATA)
        response.finish()
        
        # Token estimate should still be set (fallback to character-based)
        response_dict = response.to_dict()
        assert "token_estimate" in response_dict["metadata"]
        assert response_dict["metadata"]["token_estimate"] > 0
        
        # No need to check breakdown, might be None when tiktoken is unavailable

# Test token estimation with various data types
@pytest.mark.parametrize("data", [
    # Simple types
    "Simple string response",
    123,
    True,
    None,
    
    # Collections
    [],
    ["item1", "item2", "item3"],
    {"key": "value"},
    
    # Nested structures
    {"data": {"nested": {"deeply": {"value": 42}}}},
    [{"item": 1}, {"item": 2}, {"item": 3}]
])
def test_token_estimation_various_types(data):
    """Test token estimation with various data types."""
    # Create a response with different data types
    response = MCPResponse(data=data)
    response.finish()
    
    # Convert to dict and check token estimation
    response_dict = response.to_dict()
    assert "token_estimate" in response_dict["metadata"]
    
    # Note: Even None data will have some token estimate in an MCPResponse
    # because the response wrapper itself has JSON structure that counts
    # All we need to check is it's a valid integer
    assert isinstance(response_dict["metadata"]["token_estimate"], int)
    assert response_dict["metadata"]["token_estimate"] >= 0

# Test model_type parameter in standardize_response decorator
def test_model_type_parameter_in_decorator():
    """Test the model_type parameter handling in standardize_response decorator."""
    
    @standardize_response
    def test_func(data, model_type="default_model"):
        # Shouldn't get the model_type parameter as it's pulled out by the decorator
        return data
    
    # Call with explicit model_type
    result = test_func(SAMPLE_DATA, model_type="gpt-4")
    assert isinstance(result, MCPResponse)
    assert result.model_type == "gpt-4"
    
    # Call with default model_type
    result = test_func(SAMPLE_DATA)
    assert isinstance(result, MCPResponse)
    assert result.model_type == "claude"  # Default in the wrapper 