#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Ergo Explorer MCP and MCPO...${NC}"

# Kill any existing processes
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true

# Wait a moment
sleep 1

# Start Ergo Explorer MCP server on port 3100
echo -e "${YELLOW}Starting Ergo Explorer MCP server...${NC}"
python -m ergo_explorer --port 3100 > ergo_explorer.log 2>&1 &
ERGO_PID=$!

# Wait for Ergo Explorer to start
sleep 3

# Start MCPO with subprocess configuration
echo -e "${YELLOW}Starting MCPO...${NC}"
cd ~/Documents/ergo/ergo-explorer-mcp && mcpo --port 8000 --api-key "dbfa27c6aaca0eb2f15c2da35dc7f60d" -- python -m ergo_explorer --port 3101 > mcpo.log 2>&1 &
MCPO_PID=$!

# Create a script to stop MCPO and Ergo Explorer
STOP_SCRIPT="stop_ergo_openwebui.sh"
cat > "$STOP_SCRIPT" << EOF
#!/bin/bash
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true
echo "Stopped Ergo Explorer MCP and MCPO services."
EOF

chmod +x "$STOP_SCRIPT"

echo -e "${GREEN}Started Ergo Explorer MCP server (PID: $ERGO_PID) and MCPO (PID: $MCPO_PID)${NC}"
echo -e "${GREEN}OpenAPI at http://localhost:8000/openapi.json${NC}"
echo -e "${GREEN}Docs at http://localhost:8000/docs${NC}"
echo -e "${GREEN}Created script to stop services: $STOP_SCRIPT${NC}" 