#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
MODE="standalone"
MCPO_API_KEY=""
ERGO_NODE_API="http://localhost:9053"
ERGO_NODE_API_KEY="hashcream"

# Banner
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║      Ergo Explorer + MCPO for Open WebUI Starter      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Help function
function show_help {
    echo "Usage: ./start_ergo_openwebui.sh [OPTIONS]"
    echo
    echo "Options:"
    echo "  -m, --mode MODE        Deployment mode: 'docker' or 'standalone' (default: standalone)"
    echo "  -k, --api-key KEY      API key for securing the MCPO proxy"
    echo "  -n, --node-api URL     Ergo node API URL (default: $ERGO_NODE_API)"
    echo "  -a, --node-api-key KEY Ergo node API key (default: hashcream)"
    echo "  -h, --help             Show this help message"
    echo
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -k|--api-key)
            MCPO_API_KEY="$2"
            shift 2
            ;;
        -n|--node-api)
            ERGO_NODE_API="$2"
            shift 2
            ;;
        -a|--node-api-key)
            ERGO_NODE_API_KEY="$2"
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

# Validate mode
if [[ "$MODE" != "docker" && "$MODE" != "standalone" ]]; then
    echo -e "${RED}Invalid mode: $MODE. Must be 'docker' or 'standalone'.${NC}"
    show_help
fi

# Generate API key if not provided
if [ -z "$MCPO_API_KEY" ]; then
    MCPO_API_KEY=$(openssl rand -hex 16)
    echo -e "${GREEN}Generated API key: ${YELLOW}$MCPO_API_KEY${NC}"
    echo -e "${YELLOW}Please save this API key for configuring Open WebUI.${NC}"
fi

# Docker mode
if [ "$MODE" == "docker" ]; then
    echo -e "${YELLOW}Starting in Docker mode...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is required but not installed. Please install Docker and try again.${NC}"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is required but not installed. Please install Docker Compose and try again.${NC}"
        exit 1
    fi
    
    # Export environment variables for Docker Compose
    export MCPO_API_KEY="$MCPO_API_KEY"
    export ERGO_NODE_API="$ERGO_NODE_API"
    export ERGO_NODE_API_KEY="$ERGO_NODE_API_KEY"
    
    # Start with Docker Compose
    echo -e "${YELLOW}Starting Ergo Explorer and MCPO with Docker Compose...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}Services started successfully!${NC}"
    echo -e "${YELLOW}Ergo Explorer MCP server:${NC} http://localhost:3001"
    echo -e "${YELLOW}MCPO proxy (OpenAPI):${NC} http://localhost:8000"
    echo -e "${YELLOW}OpenAPI documentation:${NC} http://localhost:8000/docs"
    
# Standalone mode
else
    echo -e "${YELLOW}Starting in standalone mode...${NC}"
    
    # Check if Python is installed
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
    
    # Create MCPO configuration file
    echo -e "${YELLOW}Creating MCPO configuration file...${NC}"
    CONFIG_FILE="mcpo_config_standalone.json"
    
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ergo": {
      "command": "python",
      "args": ["-m", "ergo_explorer", "--port", "3001"],
      "workingDir": "$(pwd)"
    }
  },
  "auth": {
    "apiKey": "$MCPO_API_KEY"
  },
  "port": 8000,
  "host": "0.0.0.0",
  "cors": {
    "allowOrigins": ["*"],
    "allowMethods": ["GET", "POST"],
    "allowHeaders": ["*"]
  }
}
EOF
    
    echo -e "${GREEN}MCPO configuration file created at $CONFIG_FILE${NC}"
    
    # Set environment variables for Ergo Explorer
    export ERGO_NODE_API="$ERGO_NODE_API"
    export ERGO_NODE_API_KEY="$ERGO_NODE_API_KEY"
    
    # Start MCPO in the background
    echo -e "${YELLOW}Starting MCPO with Ergo Explorer...${NC}"
    nohup mcpo --config "$CONFIG_FILE" > mcpo.log 2>&1 &
    MCPO_PID=$!
    
    echo -e "${GREEN}Services started successfully!${NC}"
    echo -e "${YELLOW}MCPO proxy (OpenAPI):${NC} http://localhost:8000"
    echo -e "${YELLOW}OpenAPI documentation:${NC} http://localhost:8000/docs"
    echo -e "${YELLOW}MCPO process ID:${NC} $MCPO_PID"
    echo -e "${YELLOW}MCPO log file:${NC} mcpo.log"
    
    # Create a script to stop MCPO
    STOP_SCRIPT="stop_mcpo.sh"
    cat > "$STOP_SCRIPT" << EOF
#!/bin/bash
MCPO_PID=\$(ps aux | grep "mcpo --config $CONFIG_FILE" | grep -v grep | awk '{print \$2}')
if [ -n "\$MCPO_PID" ]; then
    echo "Stopping MCPO (PID: \$MCPO_PID)..."
    kill \$MCPO_PID
    echo "MCPO stopped successfully."
else
    echo "MCPO is not running."
fi
EOF
    
    chmod +x "$STOP_SCRIPT"
    echo -e "${GREEN}Created script to stop MCPO: $STOP_SCRIPT${NC}"
fi

# Instructions for Open WebUI integration
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