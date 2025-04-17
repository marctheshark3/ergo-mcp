# Ergo MCP

A Model Context Protocol (MCP) server for interacting with the Ergo blockchain. This package provides a set of tools for exploring blocks, transactions, addresses, and other aspects of the Ergo blockchain.

## Features

- Block exploration: retrieve blocks by height or hash, get latest blocks, etc.
- Network statistics: blockchain stats, hashrate, mining difficulty, etc.
- Mempool information: pending transactions status and statistics
- Token price information: get token prices from DEXes

## Installation

### Using a Virtual Environment (Recommended)

We strongly recommend using a virtual environment to isolate dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install the package
pip install ergo-mcp
```

### Using pip (System-wide)

```bash
pip install ergo-mcp
```

### From Source

```bash
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install .
```

### Using Docker

The project provides a Docker image for easy deployment:

```bash
# Build the Docker image
./build_docker.sh
# or manually
docker build -t mcp/ergo-explorer .

# Run the container
docker run -p 3001:3001 \
  -e ERGO_NODE_API=http://your-node-url:9053 \
  -e ERGO_NODE_API_KEY=your-api-key \
  mcp/ergo-explorer
```

To use with Cursor, update your MCP configuration:

```json
"mcpServers": {
  "ergo-explorer": {
    "command": "docker",
    "args": [
      "run", 
      "-i", 
      "--rm", 
      "-p", "3001:3001",
      "-e", "ERGO_NODE_API=http://your-node-url:9053",
      "-e", "ERGO_NODE_API_KEY=your-api-key", 
      "mcp/ergo-explorer"
    ]
  }
}
```

## Usage

### As a Module

Run the MCP server as a Python module from your virtual environment:

```bash
# Make sure your virtual environment is activated, or use the full path to Python
# Using the full path (recommended to ensure the correct Python is used):
/path/to/your/project/.venv/bin/python -m ergo_explorer

# Or with activated virtual environment:
python -m ergo_explorer
```

With custom configuration:

```bash
/path/to/your/project/.venv/bin/python -m ergo_explorer --port 3002 --env-file .env.local --debug
```

### Using the Consolidated Run Script

We provide a consolidated run script that handles environment setup, dependency installation, and server startup:

```bash
# Run with default settings
./run_server_consolidated.sh

# Run with custom arguments
./run_server_consolidated.sh --port 3002 --debug
```

The script automatically:
- Creates and activates a virtual environment if needed
- Installs dependencies if not already installed
- Sets up the logging directory
- Configures environment variables
- Starts the server

### As a Command-line Tool

After installation, you can run the server directly from the command line:

```bash
# Using the full path to the virtual environment:
/path/to/your/project/.venv/bin/ergo-mcp

# Or with activated virtual environment:
ergo-mcp
```

With custom configuration:

```bash
/path/to/your/project/.venv/bin/ergo-mcp --port 3002 --env-file .env.local --debug
```

### Environment Variables

The server can be configured using environment variables in a `.env` file:

- `SERVER_HOST`: Host to bind the server to (default: 0.0.0.0)
- `SERVER_PORT`: Port to run the server on (default: 3001)
- `SERVER_WORKERS`: Number of worker processes (default: 4)
- `ERGO_NODE_API`: URL of the Ergo node API (for node-specific features)
- `ERGO_NODE_API_KEY`: API key for the Ergo node (if required)

### Configure for Claude.app

Add to your Claude settings, making sure to use the full path to your virtual environment's Python:

```json
"mcpServers": {
  "ergo": {
    "command": "/path/to/your/project/.venv/bin/python",
    "args": ["-m", "ergo_explorer"]
  }
}
```

Or if installed via pip in your virtual environment:

```json
"mcpServers": {
  "ergo": {
    "command": "/path/to/your/project/.venv/bin/ergo-mcp",
    "args": []
  }
}
```

## API Documentation

Once the server is running, you can access the API documentation at:

```
http://localhost:3001/docs
```

## Recent Changes

### Token Holder Analysis

We've enhanced the token holder analysis functionality:

- Improved token holder data retrieval using the Node API
- Added comprehensive distribution analysis 
- Created batch export tools for processing multiple tokens

### Export Tools

New tools for exporting token holder data are available:

```bash
# Single token export
python -m ergo_explorer.tools.export_token_holders <token_id> [output_dir]

# Batch token export from file
python -m ergo_explorer.tools.batch_export_token_holders -f token_list.txt -o output_dir

# Batch token export with direct token IDs
python -m ergo_explorer.tools.batch_export_token_holders -t token1 token2 token3 -o output_dir
```

### Code Cleanup

We've performed extensive code cleanup:
- Removed redundant and deprecated files
- Consolidated server startup scripts
- Improved Docker support
- Enhanced logging configuration

## Tool Reference

### MCP Tool Naming Convention

All tools are now consistently named with the `mcp_ergo_explorer_` prefix for clarity and to avoid conflicts with other MCPs. 

For backward compatibility, all tools are also available with their original non-prefixed names (e.g., `get_height` is an alias for `mcp_ergo_explorer_get_height`), but these aliases are deprecated and may be removed in a future version.

### Primary Tools

#### Blockchain Information
- `mcp_ergo_explorer_get_height`: Get the current blockchain height and indexing status
- `mcp_ergo_explorer_get_difficulty_info`: Get comprehensive information about blockchain difficulty and network hashrate

#### Transactions
- `mcp_ergo_explorer_get_transaction`: Get transaction details by ID
- `mcp_ergo_explorer_get_transaction_by_index`: Get transaction details by index
- `mcp_ergo_explorer_analyze_transaction`: Detailed analysis of a transaction
- `mcp_ergo_explorer_get_transaction_history`: Get transaction history for an address

#### Addresses
- `mcp_ergo_explorer_get_balance`: Get detailed balance information for an address
- `mcp_ergo_explorer_analyze_address`: Deep analysis of an address with transaction patterns and holdings

#### Boxes (UTXOs)
- `mcp_ergo_explorer_get_box`: Get box details by ID
- `mcp_ergo_explorer_get_box_by_index`: Get box details by index

#### Tokens
- `mcp_ergo_explorer_get_token`: Get token information
- `mcp_ergo_explorer_get_token_price`: Get token price information
- `mcp_ergo_explorer_get_token_holders`: Get address distribution analysis for a token
- `mcp_ergo_explorer_get_token_holders_raw`: Get raw token holder data
- `mcp_ergo_explorer_get_token_holders_json`: Get comprehensive token holder information
- `mcp_ergo_explorer_search_token`: Search for tokens by ID or name

#### Blocks
- `mcp_ergo_explorer_get_block_by_height`: Get block by height
- `mcp_ergo_explorer_get_block_by_hash`: Get block by hash
- `mcp_ergo_explorer_get_latest_blocks`: Get most recent blocks
- `mcp_ergo_explorer_get_block_transactions`: Get transactions in a block

#### Node
- `mcp_ergo_explorer_get_node_wallet`: Get information about the connected node's wallet
- `mcp_ergo_explorer_get_mempool_info`: Get current mempool status

### Deprecated Tools

The following tools have been removed or replaced:

- `get_address_txs`: Redundant with `mcp_ergo_explorer_get_transaction_history`
- `get_address_balance`: Redundant with `mcp_ergo_explorer_get_balance`
- `get_network_hashrate`: Functionality merged into `mcp_ergo_explorer_get_difficulty_info`
- `get_mining_difficulty`: Functionality merged into `mcp_ergo_explorer_get_difficulty_info`
- `get_info` and `get_info_raw`: Too vague, replaced by more specific tools

## Development

### Setting Up a Development Environment

```bash
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

The project includes a comprehensive test suite to ensure all MCP tools work as expected. To run the tests:

1. Make sure you have all the test dependencies installed:
   ```bash
   pip install -e ".[test]"
   # or
   pip install -r requirements.txt
   ```

2. Run the tests using pytest:
   ```bash
   # Run all tests
   python -m pytest
   
   # Run tests with coverage report
   python -m pytest --cov=ergo_explorer
   
   # Run specific test files
   python -m pytest tests/unit/test_address_tools.py
   ```

3. Alternatively, use the provided test runner script:
   ```bash
   python tests/run_tests.py
   ```

The test suite includes unit tests for all MCP tools, including:
- Address tools
- Transaction tools
- Block tools
- Network tools
- Token tools
- Node tools
- Server implementation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Ergo Explorer MCP - NFT Collection Analysis

This module extends the Ergo Explorer MCP to support detailed analysis of NFT collections following the EIP-34 standard on the Ergo blockchain.

## Features

- **Collection Metadata Retrieval**: Get comprehensive metadata about NFT collections
- **Collection NFT Discovery**: Find all NFTs belonging to a specific collection
- **Holder Analysis**: Analyze NFT ownership distribution across collections
- **Distribution Metrics**: Get insights into collection concentration and uniqueness

## Usage

### Collection Analysis

```python
from ergo_explorer.tools.token_holders import get_collection_holders

# Get comprehensive collection holder analysis
collection_id = "your_collection_token_id_here"
analysis = await get_collection_holders(collection_id)
print(analysis)

# Get raw data for further processing
raw_data = await get_collection_holders(collection_id, include_raw=True)
```

### Collection Metadata

```python
from ergo_explorer.tools.token_holders import get_collection_metadata

# Get collection metadata based on EIP-34 standard
collection_id = "your_collection_token_id_here"
metadata = await get_collection_metadata(collection_id)
print(metadata)
```

### Discovering Collection NFTs

```python
from ergo_explorer.tools.token_holders import get_collection_nfts

# Find all NFTs in a collection
collection_id = "your_collection_token_id_here"
nfts = await get_collection_nfts(collection_id)
print(f"Found {len(nfts)} NFTs in collection")

# Limit the number of NFTs returned
limited_nfts = await get_collection_nfts(collection_id, limit=50)
```

## Command Line Interface

```bash
# Get collection holder analysis
python -m ergo_explorer collection_holders --collection-id <COLLECTION_ID>

# Get detailed analysis with raw data
python -m ergo_explorer collection_holders --collection-id <COLLECTION_ID> --raw

# Get collection metadata
python -m ergo_explorer collection_metadata --collection-id <COLLECTION_ID>
```

## Understanding EIP-34 NFT Collections

The NFT Collection Standard (EIP-34) defines how NFT collections are structured on the Ergo blockchain. Key concepts:

1. **Collection Token**: A token representing the collection itself
2. **Issuer Box**: The box that issues the collection token (contains collection metadata)
3. **NFT Association**: NFTs are linked to collections via the R7 register
4. **Metadata Registers**:
   - R4: Collection standard version
   - R5: Collection information (logo, images, category)
   - R6: Social media links
   - R7: Minting expiry timestamp
   - R8: Additional information

## Implementation Details

The collection analysis functionality is built on top of the existing token holder analysis module. It uses:

1. **Ergo Node API**: For retrieving box and token data
2. **Explorer API**: For searching and discovering NFTs

For large collections, the analysis might take some time due to API rate limits and the need to check each NFT's register values.

## Requirements

- Ergo Node API access
- Ergo Explorer API access
- Python 3.7+
- httpx library

## Configuration

The module uses the following environment variables:

- `ERGO_NODE_API`: URL of the Ergo Node API (default: http://localhost:9053)
- `ERGO_NODE_API_KEY`: API key for the Ergo Node
- `ERGO_EXPLORER_API`: URL of the Ergo Explorer API (default: https://api.ergoplatform.com/api/v1)