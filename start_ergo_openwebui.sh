#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment
VENV_PATH="/home/ai-admin/ergo-mcp/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install required packages if not already installed
if ! command -v mcpo &> /dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip install mcpo ergo-explorer
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading configuration from .env file...${NC}"
    set -o allexport
    source .env
    set +o allexport
fi

# Check for python3 or python
PYTHON_CMD="python3"
echo -e "${GREEN}Using Python command: ${PYTHON_CMD}${NC}"

# Map .env variables to script variables and set defaults
# Note the variable names in the .env file vs what the script expects
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
sudo pkill -f "mcpo" || true
sudo pkill -f "ergo_explorer" || true

# Wait a moment
sleep 1

# Start Ergo Explorer MCP server
echo -e "${YELLOW}Starting Ergo Explorer MCP server on port ${MCP_PORT}...${NC}"

${PYTHON_CMD} -m ergo_explorer --port ${MCP_PORT} > ergo_explorer.log 2>&1 &
ERGO_PID=$!

# Wait for Ergo Explorer to start
sleep 3

# Start MCPO with subprocess configuration
echo -e "${YELLOW}Starting MCPO on port ${MCPO_PORT}...${NC}"
# Use the current directory instead of trying to cd to a non-existent path

mcpo --port ${MCPO_PORT} --api-key "${MCPO_API_KEY}" -- ${PYTHON_CMD} -m ergo_explorer --port ${MCPO_SUBPROCESS_PORT} > mcpo.log 2>&1 &
MCPO_PID=$!

# Create a script to stop MCPO and Ergo Explorer
STOP_SCRIPT="stop_ergo_openwebui.sh"
cat > "$STOP_SCRIPT" << EOF
#!/bin/bash
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true
echo "Stopped Ergo Explorer MCP and MCPO services."
# Deactivate virtual environment if it's activated
if [ -n "\$VIRTUAL_ENV" ]; then
    deactivate
fi
EOF

chmod +x "$STOP_SCRIPT"

echo -e "${GREEN}Started Ergo Explorer MCP server (PID: $ERGO_PID) and MCPO (PID: $MCPO_PID)${NC}"
echo -e "${GREEN}OpenAPI at http://localhost:${MCPO_PORT}/openapi.json${NC}"
echo -e "${GREEN}Docs at http://localhost:${MCPO_PORT}/docs${NC}"
echo -e "${GREEN}Created script to stop services: $STOP_SCRIPT${NC}"

# Keep the script running (prevents systemd from thinking the service has stopped)
wait $MCPO_PID 