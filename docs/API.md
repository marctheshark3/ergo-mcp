# Ergo Explorer MCP API Documentation

This document describes the API endpoints provided by the Ergo Explorer MCP server.

## Architecture

The Ergo Explorer MCP server is organized into the following components:

- **API Routes**: Defined in `ergo_explorer/api/routes/`
  - Organized by domain (blockchain, transaction, block, etc.)
  - Each route module registers its endpoints with the MCP server
- **Tools**: Defined in `ergo_explorer/tools/`
  - Implementation of the functionality exposed by the API routes
- **Server Configuration**: Defined in `ergo_explorer/server_config.py`
  - Handles server setup and configuration
- **Logging**: Centralized in `ergo_explorer/logging_config.py`
  - Provides consistent logging across all components

## API Endpoints

### Blockchain Endpoints

#### `blockchain_status`

Get comprehensive blockchain status including height, difficulty metrics, network hashrate, and recent adjustments.

**Example Response:**
```markdown
# Ergo Blockchain Status

## Current State
Blockchain Height: 1,050,000
Last Block: 30 minutes ago

## Network Metrics
Current Difficulty: 5.32 PH
Difficulty Adjustment: +2.1% in last 24h

## Performance
Network Hashrate: 36.7 TH/s
Block Time (avg): 120 seconds
```

#### `mempool_status`

Get current mempool state including pending transactions, memory usage, and size statistics.

**Example Response:**
```markdown
# Ergo Mempool Status

Pending Transactions: 125
Memory Size: 4.2 MB
Fee Range: 0.001 ERG - 0.01 ERG
```

### Transaction Endpoints

#### `get_transaction`

Get detailed information about a transaction by its ID.

**Parameters:**
- `tx_id` (string): Transaction ID

#### `get_transaction_by_index`

Get detailed information about a transaction by its index.

**Parameters:**
- `index` (integer): Transaction index

### Box Endpoints

#### `get_box`

Get detailed information about a box by its ID.

**Parameters:**
- `box_id` (string): Box ID

#### `get_box_by_index`

Get detailed information about a box by its index.

**Parameters:**
- `index` (integer): Box index

### Token Endpoints

#### `get_token`

Get detailed information about a token.

**Parameters:**
- `token_id` (string): Token ID

#### `get_token_holders`

Get comprehensive token holder information.

**Parameters:**
- `token_id` (string): Token ID to analyze
- `include_raw` (boolean, optional): Include raw holder data (default: false)
- `include_analysis` (boolean, optional): Include holder analysis (default: true)

**Example Response:**
```markdown
# Token Holder Analysis: ErgoToken

## Overview
- Token ID: 03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04
- Name: ErgoToken
- Decimals: 2
- Total Supply: 1000000
- Total Holders: 245

## Top Holders
| Rank | Address | Amount | Percentage |
|------|---------|--------|------------|
| 1 | 9fRA...V5vA | 350000 | 35.0% |
| 2 | 3g1K...hK98 | 150000 | 15.0% |
...

## Distribution Analysis

### Concentration
- Top 10 holders control: 87.35% of supply
- Number of unique holders: 245
- Average holding per address: 4081.63 tokens
```

#### `search_token`

Search for tokens by ID or name.

**Parameters:**
- `query` (string): Search query (ID, name, or partial match)

### Block Endpoints

#### `get_block_by_height`

Get block data by height.

**Parameters:**
- `height` (integer): Block height

#### `get_block_by_hash`

Get block data by hash.

**Parameters:**
- `block_hash` (string): Block hash

#### `get_latest_blocks`

Get most recent blocks.

**Parameters:**
- `limit` (integer, optional): Number of blocks to return (default: 10)

#### `get_block_transactions`

Get transactions in a block.

**Parameters:**
- `block_id` (string): Block ID
- `limit` (integer, optional): Maximum number of transactions to return (default: 100)

### Node Endpoints

#### `get_node_wallet`

Get information about the connected node's wallet.

## Token Holder Export Tools

The Ergo Explorer MCP also includes tools for exporting token holder data to JSON files:

### Single Token Export

```bash
python -m ergo_explorer.tools.export_token_holders <token_id> [output_dir]
```

### Batch Token Export

```bash
python -m ergo_explorer.tools.batch_export_token_holders -t <token_id1> <token_id2> -o output_dir
```

or

```bash
python -m ergo_explorer.tools.batch_export_token_holders -f tokens.txt -o output_dir
```

where `tokens.txt` contains one token ID per line.

## Deprecated Endpoints

The following endpoints are deprecated and will be removed in a future version:

| Deprecated Endpoint | Replacement |
|---------------------|-------------|
| `get_address_txs` | `get_block_transactions` |
| `get_address_balance` | `get_token_holders` |
| `get_network_hashrate` | `blockchain_status` |
| `get_mining_difficulty` | `blockchain_status` |
| `get_info` | `blockchain_status` |
| `get_info_raw` | Use specific endpoints instead |

## Future Integration

The Ergo Explorer MCP server can be integrated with OpenAPI using [mcpo](https://github.com/open-webui/mcpo) to expose the MCP tools via a standard RESTful API. This will enable easier integration with clients and LLM agents that expect OpenAPI-compatible endpoints. 