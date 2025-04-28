# Ergo Explorer MCP Response Format Standardization

## Overview

This document outlines the approach for standardizing response formats across all Ergo Explorer MCP endpoints. The goal is to convert endpoints that return markdown text to a consistent JSON structure with appropriate metadata.

## Current Status

As identified by our testing:
- Most endpoints technically return JSON responses
- However, many return markdown-formatted text inside the JSON response
- Some newer endpoints already use the standardized format
- The codebase has inconsistent implementation patterns

## Technical Infrastructure

The existing response format infrastructure includes:

1. **Response Format Classes**
   - `ResponseMetadata` class for tracking timing and sizing information
   - `MCPResponse` class for standardized response format
   - `standardize_response` decorator for consistent formatting
   - Smart result limiting utilities

2. **Response Standardization Utilities**
   - `response_standardizer.py` contains utilities to parse markdown responses
   - Provides conversion from markdown to structured JSON data
   - Supports multiple data types (balance, transaction, box, token, etc.)

## Standardization System Analysis

The response standardization system works through several key components:

1. **Format Detection and Conversion**
   - `standardize_response()` function automatically detects content type and format
   - Content detection identifies data type (balance, transaction, box, token, EIP)
   - Format conversion uses specialized parsers for each data type
   - Robust error handling is implemented throughout the system

2. **Parser Functions**
   - `parse_balance_string()`: Extracts address, ERG balance, and token information
   - `parse_transaction_string()`: Extracts transaction details, inputs, outputs, and token transfers
   - `parse_box_string()`: Extracts box details including ID, value, creation height, and tokens
   - `parse_token_string()`: Extracts token information including ID, name, price, and liquidity
   - `parse_eip_string()`: Extracts EIP details or compiles lists of EIPs

3. **Decorator Pattern**
   - Functions can be decorated with `@standardize_response` for automatic standardization
   - This pattern handles format conversion without duplicating code
   - Example: `@standardize_response async def get_transaction_info_json()`

4. **Direct Format Control**
   - Some endpoints like `blockchain_status()` directly control formatting
   - These endpoints check the `response_format` parameter and return appropriate structure
   - They still use `standardize_response()` for the markdown format option

5. **Error Handling**
   - Parsers include comprehensive try-except blocks
   - Errors are properly logged with details
   - Error messages are returned in the appropriate format (JSON or markdown)
   - JSON responses include an "error" key with details when errors occur

## Standardized Response Format

All endpoints will follow this standard JSON structure:

```json
{
  "status": "success",  // or "error"
  "data": {
    // Endpoint-specific structured data
  },
  "metadata": {
    "execution_time_ms": 123,
    "result_size_bytes": 456,
    "is_truncated": false,
    "token_estimate": 789
  }
}
```

## Implementation Approach

### Step 1: Update Existing Endpoints Gradually

1. **Keep Legacy Endpoints for Backward Compatibility**
   ```python
   # Original function kept for backward compatibility
   async def get_address_balance(address: str) -> str:
       # Returns markdown formatted string
   ```

2. **Add New JSON-Formatted Endpoints**
   ```python
   @standardize_response
   async def get_address_balance_json(address: str) -> Dict[str, Any]:
       # Returns structured JSON data
   ```

3. **Use Response Format Utilities**
   - Apply the `@standardize_response` decorator to new endpoints
   - Return structured data instead of formatted strings
   - Implement proper error handling with try/except

### Step 2: Create New Main Functions and Update the API

1. **Update API Routes**
   - Point API routes to the new standardized endpoints
   - Ensure error responses follow the standardized format

2. **Update Documentation**
   - Document the new response format
   - Update endpoint documentation with response schemas

### Step 3: Testing and Validation

1. **Use Existing Test Infrastructure**
   - Update `tests/response_format_checker.py` to validate standardized responses
   - Add test cases for each endpoint in `tests/endpoint_tests/test_response_format.py`

2. **Manual Testing**
   - Use `test_standardizer.py` to check conversion from markdown to JSON
   - Validate response structures match the expected format

## Example Implementation

### Original Endpoint:
```python
async def get_address_balance(address: str) -> str:
    try:
        balance = await fetch_balance(address)
        
        # Format ERG amount
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        result = f"Balance for {address}:\n"
        result += f"• {erg_amount:.9f} ERG\n"
        
        # More formatting...
        
        return result
    except Exception as e:
        return f"Error fetching balance: {str(e)}"
```

### Standardized Endpoint:
```python
@standardize_response
async def get_address_balance_json(address: str) -> Dict[str, Any]:
    try:
        balance = await fetch_balance(address)
        
        # Create structured data
        return {
            "address": address,
            "balance": {
                "nanoErgs": balance.get("nanoErgs", 0),
                "erg": balance.get("nanoErgs", 0) / 1_000_000_000
            },
            "tokens": [
                {
                    "id": token.get("tokenId", ""),
                    "name": token.get("name", "Unknown Token"),
                    "amount": token.get("amount", 0)
                }
                for token in balance.get("tokens", [])
            ]
        }
    except Exception as e:
        raise Exception(f"Error retrieving address balance: {str(e)}")
```

## Real-World Example: Blockchain Status Endpoint

The `blockchain_status()` function is a good example of a dual-format endpoint implementation:

```python
async def blockchain_status(response_format: str = "markdown", random_string: str = None) -> Union[str, Dict[str, Any]]:
    """
    Get comprehensive blockchain status including height, difficulty metrics,
    network hashrate, and recent adjustments.
    """
    try:
        # Fetch data from multiple sources
        height_data = await get_indexed_height()
        node_info = await fetch_node_api("info")
        network_state = await fetch_network_state()
        
        # Extract key information
        indexed_height = height_data.get("indexedHeight", 0)
        full_height = height_data.get("fullHeight", 0)
        blocks_behind = full_height - indexed_height
        
        # Calculate metrics
        difficulty = node_info.get("difficulty", 0)
        readable_difficulty = await format_difficulty(difficulty)
        hashrate = await calculate_hashrate(difficulty)
        hashrate_th = hashrate / 1_000_000_000_000  # Convert to TH/s
        
        # Create standardized data structure
        status_data = {
            "height": {
                "current": full_height,
                "indexed": indexed_height,
                "blocksBehind": blocks_behind,
                "isIndexingSynced": blocks_behind == 0,
                "lastBlockTimestamp": height_data.get("lastBlockTimestamp", 0)
            },
            "mining": {
                "difficulty": difficulty,
                "readableDifficulty": readable_difficulty,
                "estimatedHashrate": hashrate,
                "estimatedHashrateTh": hashrate_th,
                "blockTimeTarget": 120  # Ergo's target block time in seconds
            },
            "network": {
                "name": node_info.get("network", "mainnet"),
                "version": node_info.get("appVersion", "Unknown"),
                "stateType": node_info.get("stateType", "Unknown"),
                "headersHeight": node_info.get("headersHeight", 0),
                "peersCount": node_info.get("peersCount", 0),
                "unconfirmedCount": node_info.get("unconfirmedCount", 0)
            }
        }
        
        # Return JSON format directly if requested
        if response_format.lower() == "json":
            return status_data
        
        # Otherwise, format as markdown and standardize
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        markdown_output = f"""
# Ergo Blockchain Status
*Last updated: {timestamp}*

## Height Information
• **Current Height**: {full_height:,}
• **Indexed Height**: {indexed_height:,}
• **Blocks Behind**: {blocks_behind:,}
• **Status**: {"Fully Synced" if blocks_behind == 0 else f"Indexing ({blocks_behind:,} blocks remaining)"}

## Mining Information
• **Difficulty**: {difficulty:,}
• **Readable Difficulty**: {readable_difficulty}
• **Estimated Hashrate**: {hashrate_th:.2f} TH/s
• **Target Block Time**: 120 seconds

## Network Status
• **Network**: {node_info.get("network", "mainnet")}
• **Version**: {node_info.get("appVersion", "Unknown")}
• **State Type**: {node_info.get("stateType", "Unknown")}
• **Headers Height**: {node_info.get("headersHeight", 0):,}
• **Connected Peers**: {node_info.get("peersCount", 0)}
• **Unconfirmed Transactions**: {node_info.get("unconfirmedCount", 0):,}
"""
        
        # Standardize the markdown response
        return standardize_response(markdown_output, response_format)
    
    except Exception as e:
        error_msg = f"Error retrieving blockchain status: {str(e)}"
        
        if response_format.lower() == "json":
            return {"error": error_msg}
        return error_msg
```

## Benefits of the Standardization System

The response standardization system offers several key benefits:

1. **Backward Compatibility**: Legacy functions returning text can be maintained alongside newer JSON endpoints
2. **Consistent Interfaces**: All endpoints provide uniform responses regardless of underlying data sources
3. **Flexible Output Formats**: Clients can choose between markdown (human-readable) and JSON (machine-readable)
4. **Developer-Friendly**: Human-readable markdown for debugging and structured JSON for applications
5. **Progressive Enhancement**: Easy to add new formats without changing core functionality
6. **Reduced Duplication**: Standardization utilities handle common parsing and formatting tasks
7. **Consistent Error Handling**: Errors are formatted consistently across all endpoints

## Timeline

1. **Phase 1: Core Infrastructure and High-Priority Endpoints** ✅
   - Finalize response standardization utilities
   - Update high-visibility endpoints (blockchain status, address info)
   - Update API routes for converted endpoints

2. **Phase 2: Remaining Endpoints** 🔄
   - Update token information endpoints
   - Update transaction and box endpoints
   - Update EIP and miscellaneous endpoints

3. **Phase 3: Testing and Documentation** 📝
   - Complete test suite for all standardized endpoints
   - Update documentation with new response formats
   - Verify all endpoints meet the standardization requirements

## Next Steps

1. **Complete Token Analytics Endpoint Standardization**
   - Update `get_token_holders`, `get_collection_holders`, and other token-related endpoints
   - Ensure consistent structure across all token data responses

2. **Transaction and Box Endpoint Updates**
   - Standardize transaction history and details endpoints 
   - Update box information endpoints with common structure

3. **Integration Testing**
   - Create comprehensive tests for all standardized endpoints
   - Validate format consistency and error handling
   - Measure performance and token usage metrics

## Conclusion

Standardizing the response format across all Ergo Explorer MCP endpoints will significantly improve the usability of the API with AI assistants. This approach allows for a gradual transition while maintaining backward compatibility, ensuring a smooth upgrade process. 