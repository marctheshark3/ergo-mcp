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

### Option 1: Simple One-Step Installation (Recommended)

Use our simple installer that automatically handles common installation issues:

```bash
# Clone the repository
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp

# Run the simple installer
python simple_install.py
```

This script will:
- Create a fresh virtual environment
- Install pip if it's missing
- Install all dependencies
- Install the package in development mode
- Verify the installation

### Option 2: Installation with Options

For more control over the installation process:

```bash
# Clone the repository
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp

# Run the installer with options
python install.py --venv  # Install in a virtual environment
python install.py --venv --force  # Overwrite existing virtual environment
python install.py --no-interactive  # Run without prompts
```

### Option 3: Manual Installation

For direct installation:

```bash
# Clone the repository
git clone https://github.com/marctheshark3/ergo-mcp.git
cd ergo-mcp

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Option 4: Install via PyPI (Coming Soon)

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

1. **Missing pip in virtual environment**: 
   - Use the `simple_install.py` script which handles pip installation automatically
   - Or manually install pip: `curl https://bootstrap.pypa.io/get-pip.py | python`

2. **Permission issues**:
   - On Unix/Linux: `sudo pip install -e .`
   - On Windows: Run as administrator

3. **Python path issues**:
   - Ensure you're using the correct Python: `which python` or `where python`
   - Check Python version: `python --version`

4. **Package not found after installation**:
   - Verify installation in the right environment: `pip list | grep ergo`
   - Try installing with absolute path: `pip install -e /full/path/to/ergo-mcp`

5. **Dependency issues**:
   - Install dependencies manually: `pip install mcp httpx python-dotenv`

### Running Issues

If the server fails to start:

1. Check that MCP and its dependencies are properly installed
2. Verify that required environment variables are set (either in `.env` file or directly)
3. Check for port conflicts and try specifying a different port with `--port`
4. Run with `--debug` flag for more detailed logging

## Testing Installation

To verify if your installation is working correctly, run:

```bash
python test_install.py
```

This will check for proper module imports and command availability.

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