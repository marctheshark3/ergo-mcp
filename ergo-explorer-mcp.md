# Ergo Explorer MCP Response Format Standardization

## Project Overview

This project aims to standardize the response format of the Ergo Explorer MCP API endpoints. The MCP API currently returns responses in various formats (Markdown, JSON, tables), which can make it difficult for developers to consume the API programmatically.

## Current Issues

Based on our analysis with the MCP Response Analyzer, we've identified several inconsistencies:

1. **Mixed Response Formats**: Some endpoints return Markdown text, others return JSON, and many mix formats.
2. **Inconsistent Structure**: JSON structures vary between endpoints with no standard envelope.
3. **Table Formatting**: Many responses use ASCII tables, which are readable for humans but difficult to parse.
4. **Error Handling**: Error responses don't follow a consistent format.

## Goals

1. Standardize all API response formats to use a consistent structure
2. Maintain human-readable output while enabling machine parsing
3. Implement proper error handling and status codes
4. Document the standardized format for developers

## Implementation Plan

### Phase 1: Analysis (Current)

- ✅ Create MCP Response Analyzer tool
- ✅ Analyze response formats from various endpoints
- ✅ Document findings and patterns

### Phase 2: Design

- Define a standard response envelope format
- Create format conversion utilities
- Document the standardization approach
- Create test cases for validation

### Phase 3: Implementation

- Update endpoint response handlers
- Implement format conversion for all endpoints
- Add response validation
- Ensure backward compatibility where needed

### Phase 4: Testing & Documentation

- Test all endpoints for format compliance
- Update API documentation with format specifications
- Create developer guides for working with the standardized format

## Standardized Response Format

We propose the following standard format for all API responses:

```json
{
  "status": "success",           // "success" or "error"
  "request": {                   // Request metadata
    "endpoint": "endpoint_name", 
    "parameters": {},            // Request parameters 
    "timestamp": "ISO8601"       // When the request was processed
  },
  "data": {                     // The actual response data (varies by endpoint)
    // Endpoint-specific data
  },
  "metadata": {                 // Optional additional information
    "format_version": "1.0",
    "execution_time": 0.123,    // Time to process in seconds
    "data_source": "node",      // Where the data came from
    // Other metadata
  },
  "error": null                 // Only present for error responses
}
```

For errors:

```json
{
  "status": "error",
  "request": {
    "endpoint": "endpoint_name",
    "parameters": {},
    "timestamp": "ISO8601" 
  },
  "data": null,
  "metadata": {
    "format_version": "1.0",
    "execution_time": 0.123
  },
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    }
  }
}
```

## Database Schema

*Not applicable for this project as we're not using a database.*

## Migration Notes

*Not applicable as there are no database migrations for this project.* 