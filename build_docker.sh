#!/usr/bin/env bash
# Build the Docker image for Ergo Explorer MCP

set -e

# Make sure logs directory exists
mkdir -p logs

echo "Building Ergo Explorer MCP Docker image..."
docker build -t mcp/ergo-explorer .

echo "Docker image built successfully."
echo "To use this with Cursor, update your mcp.json to use:"
echo '{
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
}'

echo "Done!" 