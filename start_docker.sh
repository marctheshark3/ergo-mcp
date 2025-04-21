#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║      Ergo Explorer + MCPO Docker Deployment          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is required but not installed. Please install Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is installed (either standalone or as plugin)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "${RED}Docker Compose is required but not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Using Docker Compose command: ${DOCKER_COMPOSE_CMD}${NC}"

# Check if .env file exists, if not create it from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
        cp .env.example .env
        # Generate a random API key for MCPO
        API_KEY=$(openssl rand -hex 16)
        # Replace the placeholder with the generated key
        sed -i "s/your_mcpo_api_key_here/$API_KEY/g" .env
        echo -e "${GREEN}Generated MCPO API key: ${YELLOW}$API_KEY${NC}"
        echo -e "${YELLOW}Please save this API key for configuring Open WebUI.${NC}"
    else
        echo -e "${RED}.env file not found and no .env.example to create from. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Start the Docker containers
echo -e "${YELLOW}Starting Ergo Explorer and MCPO with Docker Compose...${NC}"
$DOCKER_COMPOSE_CMD up -d

# Get the MCPO API key from the .env file
MCPO_API_KEY=$(grep MCPO_API_KEY .env | cut -d'=' -f2)
SERVER_PORT=$(grep SERVER_PORT .env | cut -d'=' -f2)

echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "To configure Open WebUI for Ergo Explorer via MCPO:"
echo -e "1. Go to Open WebUI's Models section"
echo -e "2. Click 'Add New Model'"
echo -e "3. Select 'API' as the model type"
echo -e "4. Configure with the following details:"
echo -e "   - Name: ${GREEN}Ergo Explorer${NC}"
echo -e "   - Endpoint URL: ${GREEN}http://your-server-ip:8001${NC}"
echo -e "   - API Key: ${GREEN}$MCPO_API_KEY${NC}"
echo -e "   - API Type: ${GREEN}OpenAI Compatible${NC}"
echo -e "5. Save the configuration"
echo -e "${YELLOW}=====================================================${NC}"

echo -e "${YELLOW}Ergo Explorer MCP server:${NC} http://localhost:${SERVER_PORT}"
echo -e "${YELLOW}MCPO proxy (OpenAPI):${NC} http://localhost:8001"
echo -e "${YELLOW}OpenAPI documentation:${NC} http://localhost:8001/docs" 