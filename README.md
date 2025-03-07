# Ergo Explorer MCP Server

An MCP (Model Control Protocol) server for exploring and analyzing the Ergo blockchain.

## Description

This server provides a set of tools for interacting with the Ergo blockchain through the MCP protocol, allowing AI assistants to:

- Check address balances
- Analyze transactions
- View transaction history
- Perform forensic analysis of addresses
- Search for tokens
- Monitor network status

## Requirements

- Python 3.8+
- FastMCP package
- httpx
- python-dotenv

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ergo-explorer-mcp.git
cd ergo-explorer-mcp
```

2. Install dependencies:
```bash
pip install "mcp>=0.5.0" httpx python-dotenv
```

3. Configure your environment:
```bash
cp .env.example .env
```
Then edit the `.env` file with your specific settings.

## Configuration

The server can be configured through environment variables in the `.env` file:

- `ERGO_EXPLORER_API`: URL of the Ergo Explorer API (default: https://api.ergoplatform.com/api/v1)
- `ERGO_NODE_API`: URL of your Ergo Node API (default: http://localhost:9053)
- `ERGO_NODE_API_KEY`: Your Ergo Node API key, if required
- `SERVER_PORT`: Port to run the MCP server on (default: 3001)

## Usage

Start the server using the run script:

```bash
python run_server.py
```

The server will run on port 3001 by default.

## Project Structure

The project is organized into the following structure:

```
ergo_explorer/
├── __init__.py         # Package initialization
├── api/                # API clients
│   ├── __init__.py     # API client functions
│   ├── explorer.py     # Ergo Explorer API client
│   └── node.py         # Ergo Node API client
├── config.py           # Configuration settings
├── prompts/            # MCP prompts
│   ├── __init__.py     # Prompts initialization
│   └── prompts.py      # Prompt templates
├── resources/          # MCP resources
│   ├── __init__.py     # Resources initialization
│   ├── address.py      # Address resource handlers
│   ├── transaction.py  # Transaction resource handlers
│   └── node_resources.py # Node-specific resource handlers
├── server.py           # Main MCP server setup
└── tools/              # MCP tools
    ├── __init__.py     # Tools initialization
    ├── address.py      # Address-related tools
    ├── misc.py         # Miscellaneous tools
    ├── transaction.py  # Transaction-related tools
    └── node.py         # Node-specific tools
```

## Available Tools

The server exposes the following tools:

### Explorer API Tools

These tools use the public Ergo Explorer API:

#### `get_address_balance`
Get the confirmed balance for an Ergo address.

**Parameters:**
- `address`: Ergo blockchain address

#### `analyze_transaction`
Analyze a transaction on the Ergo blockchain.

**Parameters:**
- `tx_id`: Transaction ID (hash)

#### `get_transaction_history`
Get the transaction history for an Ergo address.

**Parameters:**
- `address`: Ergo blockchain address
- `limit`: Maximum number of transactions to retrieve (default: 20)

#### `analyze_address`
Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.

**Parameters:**
- `address`: Ergo blockchain address to analyze
- `depth`: How many layers of transactions to analyze (1-4, default: 2)
- `tx_limit`: Maximum transactions per address to analyze (default: 5)

#### `search_for_token`
Search for tokens on the Ergo blockchain by name or ID.

**Parameters:**
- `query`: Token name or ID (minimum 3 characters)

#### `get_network_status`
Get the current status of the Ergo blockchain network.

### Node API Tools

These tools use a direct connection to an Ergo Node:

#### `get_address_balance_from_node`
Get the confirmed and unconfirmed balance for an Ergo address from a direct node connection.

**Parameters:**
- `address`: Ergo blockchain address

#### `analyze_transaction_from_node`
Analyze a transaction on the Ergo blockchain using a direct node connection.

**Parameters:**
- `tx_id`: Transaction ID (hash)

#### `get_transaction_history_from_node`
Get the transaction history for an Ergo address using a direct node connection.

**Parameters:**
- `address`: Ergo blockchain address
- `limit`: Maximum number of transactions to retrieve (default: 20)

#### `get_network_status_from_node`
Get the current status of the Ergo blockchain network from a direct node connection.

#### `search_for_token_from_node`
Search for tokens on the Ergo blockchain by name or ID using a direct node connection.

**Parameters:**
- `query`: Token name or ID (minimum 3 characters)

## Resource Endpoints

The server provides the following resource endpoints:

### Explorer API Resources
- `ergo://address/{address}/balance`: Get address balance
- `ergo://transaction/{tx_id}`: Get transaction details

### Node API Resources
- `ergo://node/address/{address}/balance`: Get address balance from node
- `ergo://node/transaction/{tx_id}`: Get transaction details from node

## API Reference

This server uses two APIs:
- Public Ergo Explorer API at `https://api.ergoplatform.com/api/v1`
- Direct Ergo Node API connection, typically at `http://localhost:9053`

The Ergo Node API integration is based on the [Ergo Node API OpenAPI specification](https://github.com/ergoplatform/ergo/blob/master/src/main/resources/api/openapi.yaml).

## License

See the [LICENSE](LICENSE) file for details.