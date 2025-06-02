#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Define project root directory
PROJECT_ROOT="/home/ai-admin/ergo-mcp"
PID_FILE="$PROJECT_ROOT/ergo_openwebui.pid"
STATUS_LOG="./logs/service_status.log"

# Log function
log() {
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
    echo "[$timestamp] [$level] $message" >> "$STATUS_LOG" 2>/dev/null
}

log "INFO" "=== Stopping Ergo Explorer MCP and MCPO Services ==="

# First try to use the PID file if it exists
if [ -f "$PID_FILE" ]; then
    read -r ERGO_PID MCPO_PID < "$PID_FILE"
    
    # Kill the processes by PID if they exist
    if ps -p "$MCPO_PID" > /dev/null; then
        kill "$MCPO_PID" 
        log "INFO" "Stopped MCPO (PID: $MCPO_PID)"
    else
        log "WARN" "MCPO process (PID: $MCPO_PID) not found"
    fi
    
    if ps -p "$ERGO_PID" > /dev/null; then
        kill "$ERGO_PID" 
        log "INFO" "Stopped Ergo Explorer (PID: $ERGO_PID)"
    else
        log "WARN" "Ergo Explorer process (PID: $ERGO_PID) not found"
    fi
    
    # Remove the PID file
    rm -f "$PID_FILE"
    log "INFO" "Removed PID file"
fi

# As a fallback, try to kill by process name
pkill -f "mcpo" && log "INFO" "Stopped any remaining MCPO processes" || log "INFO" "No remaining MCPO processes found"
pkill -f "ergo_explorer" && log "INFO" "Stopped any remaining Ergo Explorer processes" || log "INFO" "No remaining Ergo Explorer processes found"

log "INFO" "All Ergo Explorer MCP and MCPO services stopped."
