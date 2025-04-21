# Integrating Ergo Explorer with Open WebUI

This guide explains how to integrate the Ergo Explorer MCP server with Open WebUI using MCPO (Model Context Protocol to OpenAPI proxy).

## Overview

The Ergo Explorer MCP server provides blockchain exploration tools for the Ergo ecosystem but doesn't have an OpenAI-compatible API interface by default. To make it compatible with Open WebUI, we'll use MCPO to proxy the MCP server and expose it as an OpenAPI-compatible HTTP server.

## Prerequisites

- Python 3.8+
- Ergo Explorer MCP server installed and configured
- Open WebUI instance up and running
- Basic knowledge of bash commands and API concepts

## Step 1: Install MCPO

MCPO (Model Context Protocol to OpenAPI) is a proxy that converts MCP tool servers to standard OpenAPI-compatible HTTP servers.

```bash
pip install mcpo
```

## Step 2: Set Up MCPO for Ergo Explorer

We've provided a setup script that automates the configuration of MCPO for Ergo Explorer. Run the script with:

```bash
./setup_mcpo.sh
```

You can customize the setup with the following options:

```bash
./setup_mcpo.sh --port 8000 --mcp-port 3001 --api-key your-custom-api-key
```

Options:
- `--port`: The port on which MCPO will listen (default: 8000)
- `--mcp-port`: The port on which your Ergo MCP server is running (default: 3001)
- `--api-key`: Custom API key for securing your MCPO proxy (if omitted, one will be generated)

The script will:
1. Install MCPO if it's not already installed
2. Create a configuration file for MCPO
3. Generate an API key for security (or use the one you provided)
4. Create a systemd service file for running MCPO as a system service
5. Create a simple script for running MCPO manually

## Step 3: Start MCPO Proxy

You can start the MCPO proxy in two ways:

**Option 1: Run manually**
```bash
./run_mcpo.sh
```

**Option 2: Install as a system service**
```bash
sudo cp /tmp/ergo-mcpo.service /etc/systemd/system/ergo-mcpo.service
sudo systemctl daemon-reload
sudo systemctl enable ergo-mcpo.service
sudo systemctl start ergo-mcpo.service
```

## Step 4: Verify MCPO Proxy

Once MCPO is running, you can verify that it's working by accessing the OpenAPI documentation:

```
http://your-server-ip:8001/docs
```

This should display an interactive Swagger UI with all the available Ergo Explorer API endpoints.

## Step 5: Configure Open WebUI

To add Ergo Explorer as a model provider in Open WebUI:

1. Go to Open WebUI's dashboard
2. Navigate to "Models" and click "Add New Model"
3. Select "API" as the model type
4. Configure with the following details:
   - **Name**: Ergo Explorer
   - **Endpoint URL**: `http://your-server-ip:8001`
   - **API Key**: The API key generated or specified during setup
   - **API Type**: OpenAI Compatible
5. Save the configuration

## Step 6: Test the Integration

Create a new chat in Open WebUI and select the "Ergo Explorer" model. Try asking about blockchain information, such as:

- "What is the current blockchain status?"
- "Get information about block #1000000"
- "Search for token with ID xyz..."
- "Show me the latest blocks"

## Available Endpoints

The Ergo Explorer MCP server provides various endpoints for blockchain exploration:

### Core Blockchain
- Blockchain status
- Mempool status

### Transactions
- Get transaction by ID
- Get transaction by index

### Boxes (UTXOs)
- Get box by ID
- Get box by index

### Tokens
- Get token information
- Get token holders
- Get collection holders
- Search tokens
- Search collections

### Blocks
- Get block by height
- Get block by hash
- Get latest blocks
- Get block transactions

### Address Book
- Get address book
- Get address book by type
- Search address book
- Get address details

### EIPs (Ergo Improvement Proposals)
- List EIPs
- Get EIP details

## Troubleshooting

**MCPO not starting:**
- Check if Python is installed and in your PATH
- Ensure you have the correct permissions to execute the scripts
- Verify that the Ergo Explorer MCP server is running

**Cannot connect to MCPO from Open WebUI:**
- Check firewall settings to ensure the MCPO port (default: 8000) is accessible
- Verify that the URL is correct with the proper protocol (http://)
- Make sure the API key is correct

**Errors in Open WebUI:**
- Check the browser console for any error messages
- Verify that Open WebUI is configured to use the OpenAI-compatible API format
- Ensure the Ergo Explorer MCP server is running and accessible by MCPO

## Advanced Configuration

For advanced configuration options, you can modify the MCPO configuration file directly:

```json
{
  "mcpServers": {
    "ergo": {
      "command": "python",
      "args": ["-m", "ergo_explorer", "--port", "3001"],
      "workingDir": "/path/to/ergo-explorer"
    }
  },
  "auth": {
    "apiKey": "your-api-key"
  },
  "port": 8000,
  "host": "0.0.0.0"
}
```

You can add additional authentication methods, configure CORS, and more by consulting the MCPO documentation. 