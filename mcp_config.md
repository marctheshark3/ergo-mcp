# Ergo Explorer MCP Setup for Cursor

This document explains how to set up and use the Ergo Explorer MCP server with Cursor.

## Quick Setup

1. Build the Docker image using the management script:
   ```bash
   ./manage_mcp.sh reload
   ```

2. Update your Cursor MCP configuration to use the managed container:

   ### Global Configuration
   Edit `~/.cursor/mcp.json` to include:

   ```json
   {
     "mcpServers": {
       "ergo": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "--add-host=host.docker.internal:host-gateway",
           "-e", "ERGO_NODE_API=http://host.docker.internal:9053",
           "-e", "ERGO_NODE_API_KEY=hashcream",
           "ergo-explorer-mcp:latest"
         ]
       }
     }
   }
   ```

   ### Project Configuration
   Or create a `.cursor/mcp.json` file in your project:

   ```json
   {
     "mcpServers": {
       "ergo": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "--add-host=host.docker.internal:host-gateway",
           "-e", "ERGO_NODE_API=http://host.docker.internal:9053",
           "-e", "ERGO_NODE_API_KEY=hashcream",
           "ergo-explorer-mcp:latest"
         ]
       }
     }
   }
   ```

## Container Management

The `manage_mcp.sh` script provides several commands for managing the MCP container:

- `./manage_mcp.sh start` - Start the container
- `./manage_mcp.sh stop` - Stop the container
- `./manage_mcp.sh restart` - Restart the container
- `./manage_mcp.sh status` - Show container status
- `./manage_mcp.sh logs` - Show container logs
- `./manage_mcp.sh reload` - Rebuild image and restart container
- `./manage_mcp.sh clean` - Remove all stopped containers
- `./manage_mcp.sh debug` - Run with interactive shell for debugging

## Development Workflow

When developing the MCP server:

1. Make changes to your code
2. Run `./manage_mcp.sh reload` to rebuild and restart the container
3. Test the changes in Cursor
4. Repeat

The `reload` command handles stopping, removing, rebuilding, and starting the container with a single command, which avoids creating multiple containers.

## Environment Variables

You can customize the MCP server with these environment variables:

- `ERGO_NODE_API` - URL of the Ergo node API (default: http://host.docker.internal:9053)
- `ERGO_NODE_API_KEY` - API key for the Ergo node (default: hashcream)
- `SERVER_PORT` - Port for the MCP server (default: 8000)

Example:
```bash
SERVER_PORT=3001 ./manage_mcp.sh reload
```

## Troubleshooting

If you encounter issues with multiple containers running:

1. Stop all containers: `docker stop $(docker ps -q --filter ancestor=ergo-explorer-mcp:latest)`
2. Clean up stopped containers: `./manage_mcp.sh clean`
3. Start a fresh container: `./manage_mcp.sh start`

If Cursor can't connect to the MCP server, check:
- Container status: `./manage_mcp.sh status`
- Container logs: `./manage_mcp.sh logs`
- Your MCP configuration in Cursor 