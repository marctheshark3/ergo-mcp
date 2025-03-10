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

2. Set up a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
   
   Or install dependencies manually:
```bash
pip install "mcp>=0.5.0" httpx python-dotenv
```

4. Configure your environment:
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

If you're using a virtual environment, make sure it's activated before running the server:

```bash
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
python run_server.py
```

The server will run on port 3001 by default.

## Using with Cursor and Claude Desktop

### Configuring in Cursor

To use this MCP server with Cursor:

#### Option 1: Command-based Setup (Recommended)

1. Open Cursor and go to Settings (gear icon in the bottom left)
2. Navigate to "AI" → "Claude" → "MCP Settings"
3. Click "Add MCP Server"
4. Configure with the following information:
   - Name: Ergo Explorer
   - Type: command (select from dropdown)
   - Command: [Path to your Python interpreter in the virtual environment] [Path to the run_server.py script]
   
   Example using virtual environment (recommended):
   ```
   /home/username/path/to/ergo-mcp/.venv/bin/python /home/username/path/to/ergo-mcp/run_server.py
   ```
   
   You can get the exact path to your Python interpreter in the virtual environment with:
   ```bash
   which python  # On Linux/Mac while the venv is activated
   # or
   where python  # On Windows while the venv is activated
   ```

5. Click Save

With this command-based approach, Cursor will automatically start the MCP server when needed and stop it when not in use.

#### Option 2: URL-based Setup

Alternatively, you can run the server separately and connect to it via URL:

1. Start the MCP server as described in the Usage section
2. Open Cursor Settings (gear icon)
3. Navigate to "AI" → "Claude" → "MCP Settings"
4. Add a new MCP provider with the following information:
   - Name: Ergo Explorer
   - Type: URL
   - URL: http://localhost:3001 (or the custom port you configured)
   - Authentication: None (unless you've configured authentication)
5. Save your settings
6. Make sure to keep the server running separately while using Cursor

### Using with Claude Desktop

To use this MCP server with Claude Desktop:

1. Start the MCP server as described in the Usage section
2. Open Claude Desktop settings
3. Navigate to the "Plugins" or "Extensions" section
4. Add a new MCP connection with:
   - Name: Ergo Explorer
   - URL: http://localhost:3001 (or your custom port)
   - No authentication required (unless configured)
5. Save settings
6. In your conversations with Claude, you can now use Ergo blockchain analysis tools

The MCP tools will be available to Claude when interacting with the Ergo blockchain, analyzing addresses, transactions, and exploring other blockchain data.

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

The server provides the following tools:

### Explorer API Tools

These tools use the public Ergo Explorer API:

- **get_address_balance**: Get the confirmed balance for an Ergo address.
- **get_transaction_history**: Get the transaction history for an Ergo address.
- **analyze_address**: Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.
- **analyze_transaction**: Analyze the details of a transaction on the Ergo blockchain.
- **search_for_token**: Search for tokens on the Ergo blockchain.
- **get_network_status**: Get the current status of the Ergo blockchain network.

### Node API Tools

These tools use a direct connection to an Ergo node:

- **get_node_wallet**: Get the node's own wallet information including addresses and balances.
- **get_address_balance_from_node**: Get the confirmed and unconfirmed balance for an Ergo address from a direct node connection.
- **analyze_transaction_from_node**: Analyze a transaction using direct node connection.
- **get_transaction_history_from_node**: Get the transaction history for an Ergo address using a direct node connection.
- **get_network_status_from_node**: Get the current status of the Ergo blockchain from direct node connection.
- **search_for_token_from_node**: Search for tokens using direct node connection.

### ErgoWatch API Tools

These tools use the ErgoWatch API for blockchain analytics:

- **get_address_balance_history**: Get balance history for an address
- **get_address_balance_at_height**: Get address balance at a specific block height
- **get_contract_stats**: Get statistics about contract addresses
- **get_p2pk_stats**: Get statistics about P2PK addresses
- **get_exchange_addresses**: Get information about exchange addresses
- **get_rich_list**: Get a list of addresses sorted by balance
- **get_address_rank**: Get the rank of a P2PK address by balance

## Resource Endpoints

The server provides the following resource endpoints:

### Explorer API Resources
- `ergo://address/{address}/balance`: Get address balance
- `ergo://transaction/{tx_id}`: Get transaction details

### Node API Resources
- `ergo://node/address/{address}/balance`: Get address balance from node
- `ergo://node/transaction/{tx_id}`: Get transaction details from node

## API Reference

This server uses three main APIs:
- Public Ergo Explorer API at `https://api.ergoplatform.com/api/v1`
- Direct Ergo Node API connection, typically at `http://localhost:9053`
- ErgoWatch API at `https://api.ergo.watch`

### API Documentation
- [Ergo Node API OpenAPI specification](https://github.com/ergoplatform/ergo/blob/master/src/main/resources/api/openapi.yaml)
- [ErgoWatch API Documentation](https://api.ergo.watch/docs)

## License

See the [LICENSE](LICENSE) file for details.