#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
MCPO_PORT=8000
ERGO_MCP_PORT=3001
API_KEY=""

# Banner
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║      Ergo Explorer MCP to OpenAPI Setup      ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Help function
function show_help {
    echo "Usage: ./setup_mcpo.sh [OPTIONS]"
    echo
    echo "Options:"
    echo "  -p, --port PORT       MCPO proxy port (default: 8000)"
    echo "  -m, --mcp-port PORT   Ergo MCP server port (default: 3001)"
    echo "  -k, --api-key KEY     API key for securing the MCPO proxy"
    echo "  -h, --help            Show this help message"
    echo
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port)
            MCPO_PORT="$2"
            shift 2
            ;;
        -m|--mcp-port)
            ERGO_MCP_PORT="$2"
            shift 2
            ;;
        -k|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Install MCPO if not already installed
echo -e "${YELLOW}Checking if MCPO is installed...${NC}"
if ! pip list | grep -q "mcpo"; then
    echo -e "${YELLOW}Installing MCPO...${NC}"
    pip install mcpo
else
    echo -e "${GREEN}MCPO is already installed.${NC}"
fi

# Create MCPO configuration directory if it doesn't exist
MCPO_CONFIG_DIR="$HOME/.mcpo"
if [ ! -d "$MCPO_CONFIG_DIR" ]; then
    echo -e "${YELLOW}Creating MCPO configuration directory...${NC}"
    mkdir -p "$MCPO_CONFIG_DIR"
fi

# Create MCPO configuration file
echo -e "${YELLOW}Creating MCPO configuration file...${NC}"
CONFIG_FILE="$MCPO_CONFIG_DIR/ergo_config.json"

# Generate API key if not provided
if [ -z "$API_KEY" ]; then
    API_KEY=$(openssl rand -hex 16)
    echo -e "${GREEN}Generated API key: ${YELLOW}$API_KEY${NC}"
    echo -e "${YELLOW}Please save this API key for configuring Open WebUI.${NC}"
fi

# Write configuration to file
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ergo": {
      "command": "python",
      "args": ["-m", "ergo_explorer", "--port", "$ERGO_MCP_PORT"],
      "workingDir": "$(pwd)"
    }
  },
  "auth": {
    "apiKey": "$API_KEY"
  },
  "port": $MCPO_PORT,
  "host": "0.0.0.0"
}
EOF

echo -e "${GREEN}MCPO configuration file created at $CONFIG_FILE${NC}"

# Create a service file for systemd
SERVICE_FILE="/tmp/ergo-mcpo.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Ergo Explorer MCPO Proxy
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(which mcpo) --config $CONFIG_FILE
Restart=on-failure
RestartSec=5s
Environment=PATH=$PATH

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Systemd service file created at $SERVICE_FILE${NC}"
echo -e "${YELLOW}To install as a system service, run:${NC}"
echo -e "${GREEN}sudo cp $SERVICE_FILE /etc/systemd/system/ergo-mcpo.service${NC}"
echo -e "${GREEN}sudo systemctl daemon-reload${NC}"
echo -e "${GREEN}sudo systemctl enable ergo-mcpo.service${NC}"
echo -e "${GREEN}sudo systemctl start ergo-mcpo.service${NC}"

# Create a script to run MCPO manually
RUN_SCRIPT="run_mcpo.sh"
cat > "$RUN_SCRIPT" << EOF
#!/bin/bash
mcpo --config $CONFIG_FILE
EOF

chmod +x "$RUN_SCRIPT"
echo -e "${GREEN}Created script to run MCPO manually: $RUN_SCRIPT${NC}"

# Instructions for Open WebUI integration
echo -e "${YELLOW}=====================================================${NC}"
echo -e "${GREEN}MCPO Setup Complete!${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "To configure Open WebUI for Ergo Explorer via MCPO:"
echo -e "1. Go to Open WebUI's Models section"
echo -e "2. Click 'Add New Model'"
echo -e "3. Select 'API' as the model type"
echo -e "4. Configure with the following details:"
echo -e "   - Name: ${GREEN}Ergo Explorer${NC}"
echo -e "   - Endpoint URL: ${GREEN}http://your-server-ip:$MCPO_PORT${NC}"
echo -e "   - API Key: ${GREEN}$API_KEY${NC}"
echo -e "   - API Type: ${GREEN}OpenAI Compatible${NC}"
echo -e "5. Save the configuration"
echo -e "${YELLOW}=====================================================${NC}"

echo -e "${GREEN}To start the proxy:${NC}"
echo -e "  ${YELLOW}./run_mcpo.sh${NC}"
echo -e "${YELLOW}=====================================================${NC}" 