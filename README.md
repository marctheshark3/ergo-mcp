# Ergo MCP Server

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
- Block information retrieval 
- Mining statistics
- Mempool monitoring
- Token price information

## Prerequisites

- Python 3.8+
- FastMCP package
- httpx
- python-dotenv

## Installation

### Option 1: Quick Installation from Source

The fastest way to install is using our installation script:

```bash
# Clone the repository
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp

# Run the installation script
python install.py

# Or with a virtual environment
python install.py --venv
```

### Option 2: Manual Installation from Source

1. Clone this repository:
```bash
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp
```

2. Install the package in development mode:
```bash
pip install -e .
```

### Option 3: Install via PyPI (Coming Soon)

```bash
pip install ergo_mcp
```

**Note:** This option will be available once the package is published to PyPI.

## Usage

### Running as a module

```bash
python -m ergo_explorer
```

### Running as a command-line application

```bash
ergo-mcp
```

### Command-line options

```bash
# Display help
ergo-mcp --help

# Use a specific .env file
ergo-mcp --env-file /path/to/.env

# Set a custom port
ergo-mcp --port 5000

# Run in debug mode
ergo-mcp --debug
```

## Environment Configuration

Create a `.env` file with your configuration:

```
# Node API Settings
ERGO_NODE_API=http://localhost:9053
ERGO_NODE_API_KEY=your_api_key_here

# ErgoWatch API Settings
ERGOWATCH_API_URL=https://api.ergo.watch

# Server Settings
SERVER_PORT=3001
SERVER_HOST=0.0.0.0
```

You can specify the path to your .env file using the `--env-file` command-line option:

```bash
ergo-mcp --env-file /path/to/your/.env
```

## Configure for Claude.app

Add to your Claude settings:

```json
"mcpServers": {
  "ergo": {
    "command": "python",
    "args": ["-m", "ergo_explorer"]
  }
}
```

Alternatively:

```json
"mcpServers": {
  "ergo": {
    "command": "ergo-mcp",
    "args": []
  }
}
```

## Troubleshooting

### Installation Issues

If you encounter issues with installation:

1. Make sure you're in the project directory when running `pip install -e .`
2. Try running the install script with the `--venv` option to create a fresh virtual environment
3. Check that you have the required Python version (3.8+)
4. If importing fails, ensure the package is installed and accessible in your Python path

### Running Issues

If the server fails to start:

1. Check that MCP and its dependencies are properly installed
2. Verify that required environment variables are set (either in `.env` file or directly)
3. Check for port conflicts and try specifying a different port with `--port`
4. Run with `--debug` flag for more detailed logging

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