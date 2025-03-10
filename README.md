# Ergo Explorer MCP Server
[![MCP Server](https://glama.ai/mcp/servers/ergo-explorer/badge)](https://glama.ai/mcp/servers/ergo-explorer)

An MCP (Model Control Protocol) server for exploring and analyzing the Ergo blockchain.

## Features

- Check address balances
- Analyze transactions
- View transaction history
- Perform forensic analysis of addresses
- Search for tokens
- Monitor network status
- Direct node connection support
- ErgoWatch analytics integration

## Prerequisites

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

4. Configure your environment:
```bash
cp .env.example .env
```
Then edit the `.env` file with your specific settings.

## Configuration

### Environment Variables

The server can be configured through environment variables in the `.env` file:

- `ERGO_EXPLORER_API`: URL of the Ergo Explorer API (default: https://api.ergoplatform.com/api/v1)
- `ERGO_NODE_API`: URL of your Ergo Node API (default: http://localhost:9053)
- `ERGO_NODE_API_KEY`: Your Ergo Node API key, if required
- `SERVER_PORT`: Port to run the MCP server on (default: 3001)

### Using with Cursor

To use this MCP server with Cursor:

1. Open Cursor and go to Settings (gear icon)
2. Navigate to "AI" → "Claude" → "MCP Settings"
3. Click "Add MCP Server"
4. Configure with the following command:

```bash
/path/to/venv/python /path/to/ergo-explorer-mcp/run_server.py
```

Replace `/path/to/venv/python` with your virtual environment Python path and `/path/to/ergo-explorer-mcp` with the actual path where you cloned the repository.

### Using with Claude Desktop

To use this MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ergo-explorer": {
      "command": "python",
      "args": [
        "/path/to/ergo-explorer-mcp/run_server.py"
      ],
      "env": {
        "ERGO_EXPLORER_API": "https://api.ergoplatform.com/api/v1",
        "ERGO_NODE_API": "http://localhost:9053",
        "ERGO_NODE_API_KEY": "your-api-key",
        "SERVER_PORT": "3001"
      }
    }
  }
}
```

## Available Tools

### Explorer API Tools

- **get_address_balance**: Get the confirmed balance for an Ergo address
- **get_transaction_history**: Get the transaction history for an Ergo address
- **analyze_address**: Perform forensic analysis on an Ergo address
- **analyze_transaction**: Analyze transaction details
- **search_for_token**: Search for tokens on the Ergo blockchain
- **get_network_status**: Get current network status

### Node API Tools

- **get_node_wallet**: Get node wallet information
- **get_address_balance_from_node**: Get address balance from node
- **analyze_transaction_from_node**: Analyze transaction using node
- **get_transaction_history_from_node**: Get transaction history from node
- **get_network_status_from_node**: Get network status from node
- **search_for_token_from_node**: Search tokens using node

### ErgoWatch API Tools

- **get_address_balance_history**: Get balance history
- **get_address_balance_at_height**: Get balance at height
- **get_contract_stats**: Get contract statistics
- **get_p2pk_stats**: Get P2PK address statistics
- **get_exchange_addresses**: Get exchange address info
- **get_rich_list**: Get address rich list
- **get_address_rank**: Get address rank by balance

## Resource Endpoints

### Explorer API Resources
- `ergo://address/{address}/balance`: Address balance
- `ergo://transaction/{tx_id}`: Transaction details

### Node API Resources
- `ergo://node/address/{address}/balance`: Node address balance
- `ergo://node/transaction/{tx_id}`: Node transaction details

## API Reference

This server integrates with:
- [Ergo Explorer API](https://api.ergoplatform.com/api/v1)
- [Ergo Node API](https://github.com/ergoplatform/ergo/blob/master/src/main/resources/api/openapi.yaml)
- [ErgoWatch API](https://api.ergo.watch/docs)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.