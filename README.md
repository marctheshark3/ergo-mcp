# MCP Response Standardizer

A standardization tool for Ergo MCP API responses that transforms various output formats (JSON, Markdown, plaintext) into a consistent JSON structure for improved integration and usability.

## Problem

The MCP API returns responses in inconsistent formats:
- Some endpoints return JSON
- Some return Markdown
- Some return plain text
- Some return mixed formats (Markdown with embedded JSON)

This inconsistency makes it difficult to integrate with other systems and requires custom handling for each endpoint.

## Solution

The `MCPResponseStandardizer` transforms all responses into a consistent JSON structure:

```json
{
  "success": true,
  "data": {
    // Standardized response data extracted from the original
  },
  "meta": {
    "format": "json|markdown|text|mixed",
    "endpoint": "endpoint_name",
    "timestamp": "ISO-timestamp"
  }
}
```

For error responses:

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Error message"
  },
  "meta": {
    "format": "json|markdown|text|mixed",
    "endpoint": "endpoint_name",
    "timestamp": "ISO-timestamp"
  }
}
```

## Features

- Automatically detects response format (JSON, Markdown, plaintext)
- Extracts structured data from Markdown responses
- Preserves original data structure for JSON responses
- Extracts embedded JSON from mixed-format responses
- Provides consistent error handling
- Includes metadata about original format and processing timestamp

## Usage

### Basic Usage

```python
from mcp_response_standardizer import MCPResponseStandardizer

# Initialize the standardizer
standardizer = MCPResponseStandardizer()

# Standardize a response
endpoint_name = "blockchain_status"
response_content = "..."  # Content from the MCP API
status_code = 200  # HTTP status code from the API call

# Get standardized response
standardized = standardizer.standardize_response(
    endpoint_name, 
    response_content, 
    status_code
)

# Access the standardized data
if standardized["success"]:
    data = standardized["data"]
    # Use the standardized data...
else:
    error = standardized["error"]
    print(f"Error {error['code']}: {error['message']}")
```

### Command Line Usage

You can also use the standardizer from the command line:

```bash
python mcp_response_standardizer.py blockchain_status response.txt
```

Where:
- `blockchain_status` is the endpoint name
- `response.txt` is a file containing the response content

## Testing

A test script `test_standardizer.py` is provided to demonstrate the standardizer with sample responses:

```bash
python test_standardizer.py
```

This script:
1. Creates sample responses in different formats
2. Saves them to the `sample_responses` directory
3. Processes each sample using the standardizer
4. Saves the standardized output for comparison

## Implementation Details

The standardizer uses the following approach:

1. Check if response is an error based on HTTP status code
2. Determine the original format (JSON, Markdown, text)
3. Process the response according to its format:
   - JSON: Parse and preserve the structure
   - Markdown: Extract structured data (headers, lists, tables, code blocks)
   - Text: Convert to key-value pairs when possible
   - Mixed: Extract embedded JSON and combine with other extracted data
4. Format the result in the standardized structure
5. Include metadata about the original format and processing

## Requirements

- Python 3.6+
- No external dependencies required

# Ergo Explorer MCP

Ergo Explorer Model Context Protocol (MCP) is a comprehensive server that provides AI assistants with direct access to Ergo blockchain data through a standardized interface.

## Overview

This project bridges the gap between AI assistants and the Ergo blockchain ecosystem by:

- Providing structured blockchain data in AI-friendly formats
- Enabling complex blockchain analysis through simple natural language queries
- Supporting token analytics, address intelligence, and ecosystem monitoring
- Standardizing blockchain data access patterns for AI models

## Features

- **Blockchain Exploration**: Retrieve blocks, transactions, and network statistics
- **Address Analysis**: Query balances, transaction history, and perform forensic analysis
- **Token Intelligence**: View token information, holder distributions, and collection data
- **Ecosystem Integration**: Access EIP information, oracle pool data, and address book
- **Advanced Analytics**: Analyze blockchain patterns, token metrics, and transaction flows

## Response Standardization

All endpoints in the Ergo Explorer MCP implement a standardized response format system that:

- Supports both human-readable (markdown) and machine-readable (JSON) formats
- Provides consistent structure across all endpoints
- Maintains backward compatibility through dual-format support
- Implements comprehensive error handling
- Uses the `@standardize_response` decorator for automatic format conversion

### Standard JSON Response Structure:

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

For more information on response standardization, see [RESPONSE_STANDARDIZATION.md](./RESPONSE_STANDARDIZATION.md).

## Installation

### Prerequisites

- Python 3.8+
- Access to Ergo Explorer API
- Optional: Access to Ergo Node API (for advanced features)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ergo-mcp/ergo-explorer-mcp.git
   cd ergo-explorer-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   # Set up environment variables
   export ERGO_EXPLORER_API="https://api.ergoplatform.com/api/v1"
   export ERGO_NODE_API="http://your-node-address:9053"  # Optional
   export ERGO_NODE_API_KEY="your-api-key"  # Optional
   ```

4. Run the MCP server:
   ```bash
   python -m ergo_explorer.server
   ```

### Docker Installation (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t ergo-explorer-mcp .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 \
     -e ERGO_EXPLORER_API="https://api.ergoplatform.com/api/v1" \
     -e ERGO_NODE_API="http://your-node-address:9053" \
     -e ERGO_NODE_API_KEY="your-api-key" \
     --name ergo-mcp ergo-explorer-mcp
   ```

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Set up a development environment:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.test.txt
   ```
4. Run tests:
   ```bash
   pytest
   ```
5. Submit a pull request

## Documentation

For comprehensive documentation, see:

- [API Reference](./docs/API_REFERENCE.md)
- [Feature Roadmap](./TODO_FEATURES.md)
- [Response Standardization](./RESPONSE_STANDARDIZATION.md)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
