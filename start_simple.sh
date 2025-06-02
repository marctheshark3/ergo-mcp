#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to project directory
cd /home/ai-admin/ergo-mcp || { echo "Failed to change to project directory"; exit 1; }

# Define log paths
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading configuration from .env file${NC}"
    set -o allexport
    source .env
    set +o allexport
fi

# Map .env variables to script variables and set defaults
MCP_PATH=${MCP_PATH:-"$(pwd)"}  # Default to current directory
MCPO_API_KEY=${MCPO_API_KEY:-"dbfa27c6aaca0eb2f15c2da35dc7f60d"}
MCP_PORT=${ERGO_MCP_PORT:-3100}  # Use ERGO_MCP_PORT from .env
MCPO_PORT=${SERVER_PORT:-8000}  # Use SERVER_PORT from .env
MCPO_SUBPROCESS_PORT=${MCPO_SUBPROCESS_PORT:-3101}

echo -e "${YELLOW}Starting Ergo Explorer MCP and MCPO...${NC}"
echo -e "${YELLOW}MCP_PATH: ${MCP_PATH}${NC}"
echo -e "${YELLOW}MCP_PORT: ${MCP_PORT}${NC}"
echo -e "${YELLOW}MCPO_PORT: ${MCPO_PORT}${NC}"

# Kill any existing processes
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true

# Wait a moment
sleep 1

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source ./venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }

# Run MCPO directly (without daemonizing)
echo -e "${GREEN}Starting MCPO on port ${MCPO_PORT}${NC}"
./venv/bin/mcpo --port ${MCPO_PORT} --api-key "${MCPO_API_KEY}" -- python -m ergo_explorer --port ${MCP_PORT} 