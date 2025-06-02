# Response Format Standardization Plan

## Current Findings

Based on our comprehensive testing of all Ergo MCP endpoints, we have found:

1. **All endpoints technically return JSON responses**, but:
   - Many endpoints return markdown text within the JSON response
   - Some endpoints return structured JSON data
   - Format inconsistencies exist across the API

2. **Common issues identified**:
   - Markdown formatted text in responses instead of structured data
   - Missing standard field structure (status, data, metadata)
   - Inconsistent error handling approaches
   - No standardized metadata for resource usage tracking

## Code Analysis Results

After analyzing the codebase, we found:

1. **Existing Infrastructure**:
   - A `response_format.py` module already exists with:
     - `ResponseMetadata` class for tracking timing and sizing
     - `MCPResponse` class for standardized response format
     - `standardize_response` decorator
     - Smart limiting and response formatting utilities

2. **Implementation Status**:
   - Some newer endpoints are already using the `@standardize_response` decorator
   - Many endpoints still return formatted strings (markdown) instead of structured data
   - A mix of implementation patterns exists across the codebase

## Standardization Requirements

All endpoints must be updated to follow this standard response format:

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

## Implementation Tasks

### 1. Review and Update Existing Response Format Utilities

- [x] `ResponseMetadata` class - Already implemented
- [x] `MCPResponse` class - Already implemented
- [x] `standardize_response` decorator - Already implemented
- [x] Smart limiting utilities - Already implemented

### 2. Identify and Update Endpoints

#### Blockchain Endpoints
- [ ] `get_blockchain_height` → Update to use structured data and the decorator
- [x] `blockchain_status` → Already standardized
- [ ] `get_transaction_info` → Update to use structured data and the decorator
- [ ] `get_address_transaction_history` → Update to use structured data and the decorator
- [ ] `get_box_info` → Update to use structured data and the decorator
- [ ] `get_token_info` → Update to use structured data and the decorator
- [ ] `get_address_full_balance` → Update to use structured data and the decorator
- [ ] `get_token_holders` → Update to use structured data and the decorator

#### Address Endpoints
- [ ] `get_address_balance` → Update to use structured data and the decorator
- [ ] `get_transaction_history` → Update to use structured data and the decorator
- [ ] `analyze_address` → Update to use structured data and the decorator
- [ ] `blockchain_address_info` → Update to use structured data and the decorator

#### Token Endpoints
- [ ] `get_token_price` → Update to use structured data and the decorator
- [ ] `format_token_price` → Convert to utility function, not endpoint
- [x] `get_token` → Already standardized
- [x] `search_token` → Already standardized
- [ ] `get_token_holders` → Update to use structured data and the decorator
- [ ] `get_collection_holders` → Update to use structured data and the decorator
- [ ] `search_collections` → Update to use structured data and the decorator

#### EIP Endpoints
- [ ] `list_eips` → Update to use structured data and the decorator
- [ ] `get_eip` → Update to use structured data and the decorator

### 3. Standardize Error Handling

- [ ] Ensure all endpoints use try/except to catch and format errors consistently
- [ ] Update error messages to be more informative and consistent
- [ ] Use the `MCPResponse` class for error responses

### 4. Testing and Validation

- [ ] Update test suite to validate standardized responses
- [ ] Create test cases for each endpoint to ensure consistent format
- [ ] Add validation for error handling 

## Implementation Strategy

1. **Step 1**: Create utility functions to convert existing markdown responses to structured data
   - For example, a function to convert balance strings to structured JSON
   - Define clear data models for each type of response

2. **Step 2**: Update each endpoint one at a time, starting with high-priority endpoints
   - Replace string returns with structured data
   - Add the `@standardize_response` decorator
   - Update error handling

3. **Step 3**: Add tests to verify standardized response format
   - Each endpoint should return the expected format
   - Errors should be properly formatted
   - Metadata should be correctly populated

4. **Step 4**: Document the standardized response format for developer reference

## Prioritized Implementation Order

1. Blockchain status endpoints (high visibility, frequently used)
2. Address information endpoints (commonly used for balances)
3. Token information endpoints (frequently queried)
4. Transaction and box endpoints (complex data structures)
5. EIP and miscellaneous endpoints

## Conclusion

Standardizing the response format will significantly improve the usability of the Ergo MCP with AI assistants, ensuring consistent and structured data that can be easily parsed and used in conversations. The good news is that much of the infrastructure is already in place, and we just need to consistently apply it across all endpoints. 