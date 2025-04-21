# Docker Deployment Guide for Ergo Explorer + MCPO

This guide explains how to deploy Ergo Explorer and MCPO using Docker, making it easy to integrate with Open WebUI.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Basic understanding of terminal/command line

## Quick Start

The easiest way to get started is to use the provided scripts:

```bash
# Start the services
./start_docker.sh

# Stop the services when needed
./stop_docker.sh
```

The `start_docker.sh` script will:
1. Check for Docker and Docker Compose installations
2. Create a `.env` file if it doesn't exist
3. Generate a random API key for MCPO if needed
4. Start the containers with Docker Compose
5. Display the URLs for accessing the services and configuration instructions for Open WebUI

## Manual Setup

If you prefer to set up manually:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set your configuration:
   ```bash
   # Edit the .env file with your preferred text editor
   nano .env
   ```

3. Start the containers:
   ```bash
   docker-compose up -d
   ```

4. Stop the containers when needed:
   ```bash
   docker-compose down
   ```

## Environment Variables

The key environment variables you may want to configure in the `.env` file:

- `ERGO_NODE_API`: URL to your Ergo node (default: http://localhost:9053)
- `ERGO_NODE_API_KEY`: Your Ergo node API key (default: hashcream)
- `SERVER_PORT`: Port for the Ergo Explorer service (default: 3001)
- `MCPO_API_KEY`: API key for securing the MCPO proxy

## Services

After deployment, the following services will be available:

- **Ergo Explorer MCP**: http://localhost:3001
- **MCPO Proxy (OpenAPI)**: http://localhost:8001
- **OpenAPI Documentation**: http://localhost:8001/docs

## Integrating with Open WebUI

To integrate with Open WebUI:

1. Go to Open WebUI's Models section
2. Click "Add New Model"
3. Select "API" as the model type
4. Configure with the following details:
   - Name: Ergo Explorer
   - Endpoint URL: http://your-server-ip:8001
   - API Key: [Your MCPO API key from .env]
   - API Type: OpenAI Compatible
5. Save the configuration

## Troubleshooting

- **Services not starting**: Check Docker logs with `docker-compose logs`
- **Connection issues**: Make sure ports are not being blocked by a firewall
- **Ergo node connectivity**: If using a remote Ergo node, ensure the URL and API key are correct

## Advanced Configuration

For advanced configuration, you can modify:

- `docker-compose.yml`: To change container configurations
- `mcpo_config.json`: To adjust MCPO settings
- `Dockerfile`: To customize the build process 