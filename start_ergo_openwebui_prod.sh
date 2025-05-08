#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define project root directory
PROJECT_ROOT="/home/ai-admin/ergo-mcp"
VENV_PATH="$PROJECT_ROOT/venv"

# Change to project directory
cd "$PROJECT_ROOT" || { echo "Failed to change to project directory"; exit 1; }

# Define log paths
LOG_DIR="./logs"
MCPO_LOG="$LOG_DIR/mcpo.log"
ERGO_LOG="$LOG_DIR/ergo_explorer.log"
STATUS_LOG="$LOG_DIR/service_status.log"

# Create log directory with proper permissions
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Simple logging function that doesn't depend on log file
log_to_console() {
    local level=$1
    local message=$2
    local color=$YELLOW
    
    case $level in
        "INFO") color=$GREEN ;;
        "WARN") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${color}[$level] $message${NC}"
}

# Log function to both terminal and status log file
log() {
    local level=$1
    local message=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Always output to console
    log_to_console "$level" "$message"
    
    # Try to write to log file, ignore errors
    echo "[$timestamp] [$level] $message" >> "$STATUS_LOG" 2>/dev/null
}

# Log startup
log "INFO" "=== Ergo Explorer MCP and MCPO Service Starting ==="

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    log "INFO" "Loading configuration from .env file"
    set -o allexport
    source .env
    set +o allexport
fi

# Map .env variables to script variables and set defaults
# Note the variable names in the .env file vs what the script expects
MCP_PATH=${MCP_PATH:-"$PROJECT_ROOT"}  # Default to project root
MCPO_API_KEY=${MCPO_API_KEY:-"dbfa27c6aaca0eb2f15c2da35dc7f60d"}
MCP_PORT=${ERGO_MCP_PORT:-3100}  # Use ERGO_MCP_PORT from .env
MCPO_PORT=${SERVER_PORT:-8000}  # Use SERVER_PORT from .env
MCPO_SUBPROCESS_PORT=${MCPO_SUBPROCESS_PORT:-3101}

log "INFO" "Configuration:"
log "INFO" "MCP_PATH: ${MCP_PATH}"
log "INFO" "MCP_PORT: ${MCP_PORT}"
log "INFO" "MCPO_PORT: ${MCPO_PORT}"
log "INFO" "MCPO_SUBPROCESS_PORT: ${MCPO_SUBPROCESS_PORT}"

# Kill any existing processes
log "INFO" "Stopping any existing processes"
pkill -f "mcpo" && log "INFO" "Stopped existing MCPO processes" || log "INFO" "No existing MCPO processes found"
pkill -f "ergo_explorer" && log "INFO" "Stopped existing Ergo Explorer processes" || log "INFO" "No existing Ergo Explorer processes found"

# Wait a moment
sleep 1

# Activate virtual environment
log "INFO" "Activating virtual environment"
source "$VENV_PATH/bin/activate" || { 
    log "ERROR" "Failed to activate virtual environment"
    exit 1
}

# Check if required packages are installed
if ! command -v mcpo &> /dev/null; then
    log "WARN" "MCPO not found. Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to install required packages"
        exit 1
    else
        log "INFO" "Successfully installed required packages"
    fi
fi

# Start Ergo Explorer MCP server
log "INFO" "Starting Ergo Explorer MCP server on port ${MCP_PORT}"
python -m ergo_explorer --port ${MCP_PORT} > "$ERGO_LOG" 2>&1 &
ERGO_PID=$!

# Check if process started successfully
if ! ps -p $ERGO_PID > /dev/null; then
    log "ERROR" "Failed to start Ergo Explorer MCP server"
    exit 1
fi
log "INFO" "Ergo Explorer MCP server started successfully with PID: ${ERGO_PID}"

# Wait for Ergo Explorer to start
log "INFO" "Waiting for Ergo Explorer to initialize"
sleep 3

# Start MCPO with subprocess configuration
log "INFO" "Starting MCPO on port ${MCPO_PORT}"
# Use the absolute path to mcpo from the virtual environment
"$VENV_PATH/bin/mcpo" --port ${MCPO_PORT} --api-key "${MCPO_API_KEY}" -- python -m ergo_explorer --port ${MCPO_SUBPROCESS_PORT} > "$MCPO_LOG" 2>&1 &
MCPO_PID=$!

# Check if process started successfully
if ! ps -p $MCPO_PID > /dev/null; then
    log "ERROR" "Failed to start MCPO"
    kill $ERGO_PID # Clean up ergo explorer
    exit 1
fi
log "INFO" "MCPO started successfully with PID: ${MCPO_PID}"

# Create a script to stop MCPO and Ergo Explorer
STOP_SCRIPT="$PROJECT_ROOT/stop_ergo_openwebui_prod.sh"
log "INFO" "Creating stop script at ${STOP_SCRIPT}"
cat > "$STOP_SCRIPT" << EOF
#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Define project root directory
PROJECT_ROOT="/home/ai-admin/ergo-mcp"
PID_FILE="\$PROJECT_ROOT/ergo_openwebui.pid"
STATUS_LOG="./logs/service_status.log"

# Log function
log() {
    local level=\$1
    local message=\$2
    local color=\$YELLOW
    
    case \$level in
        "INFO") color=\$GREEN ;;
        "WARN") color=\$YELLOW ;;
        "ERROR") color=\$RED ;;
    esac
    
    local timestamp=\$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "\${color}[\$level] \$message\${NC}"
    echo "[\$timestamp] [\$level] \$message" >> "\$STATUS_LOG" 2>/dev/null
}

log "INFO" "=== Stopping Ergo Explorer MCP and MCPO Services ==="

# First try to use the PID file if it exists
if [ -f "\$PID_FILE" ]; then
    read -r ERGO_PID MCPO_PID < "\$PID_FILE"
    
    # Kill the processes by PID if they exist
    if ps -p "\$MCPO_PID" > /dev/null; then
        kill "\$MCPO_PID" 
        log "INFO" "Stopped MCPO (PID: \$MCPO_PID)"
    else
        log "WARN" "MCPO process (PID: \$MCPO_PID) not found"
    fi
    
    if ps -p "\$ERGO_PID" > /dev/null; then
        kill "\$ERGO_PID" 
        log "INFO" "Stopped Ergo Explorer (PID: \$ERGO_PID)"
    else
        log "WARN" "Ergo Explorer process (PID: \$ERGO_PID) not found"
    fi
    
    # Remove the PID file
    rm -f "\$PID_FILE"
    log "INFO" "Removed PID file"
fi

# As a fallback, try to kill by process name
pkill -f "mcpo" && log "INFO" "Stopped any remaining MCPO processes" || log "INFO" "No remaining MCPO processes found"
pkill -f "ergo_explorer" && log "INFO" "Stopped any remaining Ergo Explorer processes" || log "INFO" "No remaining Ergo Explorer processes found"

log "INFO" "All Ergo Explorer MCP and MCPO services stopped."
EOF

chmod +x "$STOP_SCRIPT"

# Create a pid file with the process ids for the systemd service
echo "$ERGO_PID $MCPO_PID" > "$PROJECT_ROOT/ergo_openwebui.pid"
log "INFO" "Created PID file with PIDs: ERGO=$ERGO_PID, MCPO=$MCPO_PID"

log "INFO" "OpenAPI available at: http://localhost:${MCPO_PORT}/openapi.json"
log "INFO" "Documentation available at: http://localhost:${MCPO_PORT}/docs"
log "INFO" "Service startup completed successfully"

# Verify the services are actually running after a short delay
sleep 5
log "INFO" "Verifying services are running"

if ps -p $ERGO_PID > /dev/null; then
    log "INFO" "Ergo Explorer MCP server is running (PID: $ERGO_PID)"
else
    log "ERROR" "Ergo Explorer MCP server is not running!"
fi

if ps -p $MCPO_PID > /dev/null; then
    log "INFO" "MCPO is running (PID: $MCPO_PID)"
else
    log "ERROR" "MCPO is not running!"
fi

# Keep the script running to maintain the child processes (for non-daemon mode)
log "INFO" "Main process entering wait state to maintain child processes"
wait 