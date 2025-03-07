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

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ergo-explorer-mcp.git
cd ergo-explorer-mcp
```

2. Install dependencies:
```bash
pip install "mcp>=0.5.0" httpx
```

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
├── api/                # API client for Ergo Explorer
│   └── __init__.py     # API client functions
├── config.py           # Configuration settings
├── prompts/            # MCP prompts
│   ├── __init__.py     # Prompts initialization
│   └── prompts.py      # Prompt templates
├── resources/          # MCP resources
│   ├── __init__.py     # Resources initialization
│   └── resources.py    # Resource handlers
├── server.py           # Main MCP server setup
└── tools/              # MCP tools
    ├── __init__.py     # Tools initialization
    ├── address.py      # Address-related tools
    ├── misc.py         # Miscellaneous tools
    └── transaction.py  # Transaction-related tools
```

## Available Tools

The server exposes the following tools:

### `get_address_balance`
Get the confirmed balance for an Ergo address.

**Parameters:**
- `address`: Ergo blockchain address

### `analyze_transaction`
Analyze a transaction on the Ergo blockchain.

**Parameters:**
- `tx_id`: Transaction ID (hash)

### `get_transaction_history`
Get the transaction history for an Ergo address.

**Parameters:**
- `address`: Ergo blockchain address
- `limit`: Maximum number of transactions to retrieve (default: 20)

### `analyze_address`
Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.

**Parameters:**
- `address`: Ergo blockchain address to analyze
- `depth`: How many layers of transactions to analyze (1-4, default: 2)
- `tx_limit`: Maximum transactions per address to analyze (default: 5)

### `search_for_token`
Search for tokens on the Ergo blockchain by name or ID.

**Parameters:**
- `query`: Token name or ID (minimum 3 characters)

### `get_network_status`
Get the current status of the Ergo blockchain network.

## Resource Endpoints

The server also provides the following resource endpoints:

- `ergo://address/{address}/balance`: Get address balance
- `ergo://transaction/{tx_id}`: Get transaction details

## API Reference

This server uses the public Ergo Explorer API at `https://api.ergoplatform.com/api/v1`.

## License

See the [LICENSE](LICENSE) file for details.