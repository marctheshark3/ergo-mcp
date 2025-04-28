# MCPO Response Format Analysis

## Problem Statement

We're encountering issues with the standardized response format expected by our test suite. The tests expect JSON responses with a structured format containing `status`, `data`, and `metadata` fields. However, the MCPO proxy appears to be returning raw markdown text or other non-standard response formats.

## Analysis Approach

To better understand the issue, we've created an analysis script (`analyze_mcpo_response.py`) that:

1. Makes requests to several key endpoints with the proper API key
2. Analyzes the response format (JSON vs. text, structure, fields)
3. Generates a summary report to help us understand the current behavior

## Analysis Results

We ran the analysis script against several key endpoints. Here are our findings:

### Response Format Summary

| Endpoint | Response Type | Is JSON | Has Standard Fields | Notes |
|----------|--------------|---------|---------------------|-------|
| blockchain_status | str | No | No | Returns markdown-formatted text starting with "# Ergo Blockchain Status" |
| get_block_by_height | N/A | N/A | N/A | Returns 500 error - internal server error |
| get_token | str | No | No | Returns error message text |
| list_eips | str | No | No | Returns markdown-formatted list of EIPs |
| blockchain_address_info | str | No | No | Returns markdown-formatted address information |

### Key Observations

1. **All responses are strings, not JSON**: Every successful response is returned as plain text or markdown, not JSON
2. **Markdown formatting**: Most successful responses use markdown formatting with headers and bullet points
3. **No standard fields**: None of the responses contain the expected fields (status, data, metadata)
4. **Errors in some endpoints**: The get_block_by_height endpoint returns a 500 internal server error

### Raw Response Examples

1. **blockchain_status**:
   ```
   # Ergo Blockchain Status

       ## Current State
       Blockchain Height Information:
   • Indexed Height: [...]
   ```

2. **list_eips**:
   ```
   # Ergo Improvement Proposals (EIPs)

   ## EIP-22: Auction contract
   Status: Unknown

   ## EIP-19: Cold Wallet: an interaction protocol [...]
   ```

3. **blockchain_address_info**:
   ```
   Balance for 9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K:
   • 9.901479000 ERG

   Tokens:
   • 2000 Mi Goreng [...]
   ```

## Current Architecture

Based on our investigation:

1. The Ergo Explorer MCP server provides blockchain data through MCP endpoints
2. MCPO acts as a proxy to expose these endpoints via an OpenAPI-compatible interface
3. The MCPO configuration (mcpo_config.json) points to the MCP server at http://ergo-mcp:3001/mcp
4. Our test suite expects standardized JSON responses but is receiving non-standard formats

```
Tests <---> MCPO Proxy <---> MCP Server
         (Expected JSON)   (Markdown/Text)
```

## Root Cause Analysis

The issue stems from how MCPO and MCP interact:

1. **MCPO Proxy Behavior**: The MCPO proxy is forwarding the raw response from the MCP server directly to clients
2. **MCP Response Format**: The MCP server is returning markdown/text responses rather than JSON objects
3. **Test Expectations**: Our test suite expects a standardized JSON format with specific fields

## Recommended Solution

Based on our analysis, we recommend pursuing **Option A: Modify MCP Server**. This involves:

1. **Updating Tool Implementations**: Modify the MCP server tool implementations to return proper JSON objects instead of markdown text
2. **Standardize Response Format**: Ensure all endpoints return responses with the standard fields (status, data, metadata)
3. **Error Handling**: Implement consistent error formats

This approach is preferred because:
- It addresses the root cause directly
- It makes our API more consistent and standards-compliant
- It avoids adding additional layers/complexity

## Implementation Steps

1. **Identify Core Response Formatter**: Look for a central location in the MCP server code that formats responses
2. **Update Formatter**: Modify the formatter to wrap the current markdown output in a standard JSON structure
3. **Add Metadata Generation**: Implement metadata generation (timing, size metrics, etc.)
4. **Update Individual Tools**: If needed, modify specific tool implementations to return standardized data
5. **Test Integration**: Verify that MCPO correctly proxies the updated JSON responses

## Alternative Solutions

### Option B: Create an Adapter Layer

This would involve creating a middleware that sits between MCPO and the tests to transform responses. While feasible, this adds complexity and doesn't solve the underlying design issue.

### Option C: Update Test Suite

We could modify the tests to accept the current format, but this would result in non-standard API behavior and could lead to issues with other clients in the future.

## Next Steps

1. Locate the response formatting code in the MCP server
2. Create a standardized response formatting function
3. Implement the formatter in all tool responses
4. Run the tests to verify the fix works

## Conclusion

The MCPO proxy is correctly passing through the MCP server responses, but those responses are not in the expected JSON format. By updating the MCP server to return standardized JSON responses with the required fields, we can make our API more consistent and ensure compatibility with our test suite and other clients. 