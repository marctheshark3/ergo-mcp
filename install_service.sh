#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define project root directory
PROJECT_ROOT="/home/ai-admin/ergo-mcp"
SERVICE_FILE="$PROJECT_ROOT/ergo-openwebui.service"
TARGET_PATH="/etc/systemd/system/ergo-openwebui.service"
LOG_DIR="$PROJECT_ROOT/logs"
LOGROTATE_CONF="/etc/logrotate.d/ergo-openwebui"

# Log function for install script
log() {
    local level=$1
    local message=$2
    local color=$YELLOW
    
    case $level in
        "INFO") color=$GREEN ;;
        "WARN") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}[$level] $message${NC}"
}

# Make sure we're in the project directory
cd "$PROJECT_ROOT" || { log "ERROR" "Failed to change to project directory"; exit 1; }

# Make log directory if it doesn't exist
mkdir -p "$LOG_DIR"
log "INFO" "Created log directory: $LOG_DIR"

# Make scripts executable
log "INFO" "Making scripts executable"
chmod +x "$PROJECT_ROOT/start_ergo_openwebui_prod.sh"
chmod +x "$PROJECT_ROOT/stop_ergo_openwebui_prod.sh"

# Verify the virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    log "INFO" "Virtual environment not found. Creating..."
    python3 -m venv "$PROJECT_ROOT/venv"
    
    # Activate and install dependencies
    source "$PROJECT_ROOT/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    deactivate
    
    log "INFO" "Virtual environment created and dependencies installed"
else
    log "INFO" "Virtual environment found"
fi

# Check if mcpo is installed in the virtual environment
if [ ! -f "$PROJECT_ROOT/venv/bin/mcpo" ]; then
    log "INFO" "MCPO not found in virtual environment. Installing..."
    source "$PROJECT_ROOT/venv/bin/activate"
    pip install mcpo>=0.0.12
    deactivate
    
    log "INFO" "MCPO installed"
fi

# Set up log rotation
log "INFO" "Setting up log rotation configuration"
sudo tee "$LOGROTATE_CONF" > /dev/null << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ai-admin ai-admin
    sharedscripts
    postrotate
        systemctl is-active --quiet ergo-openwebui.service && systemctl reload ergo-openwebui.service
    endscript
}
EOF

log "INFO" "Log rotation configured"

# Copy the service file to systemd directory
log "INFO" "Installing systemd service"
sudo cp "$SERVICE_FILE" "$TARGET_PATH" || { log "ERROR" "Failed to copy service file to $TARGET_PATH"; exit 1; }

# Reload systemd
log "INFO" "Reloading systemd daemon"
sudo systemctl daemon-reload || { log "ERROR" "Failed to reload systemd"; exit 1; }

# Enable and start the service
log "INFO" "Enabling and starting the service"
sudo systemctl enable ergo-openwebui.service || { log "ERROR" "Failed to enable service"; exit 1; }
sudo systemctl start ergo-openwebui.service || { log "ERROR" "Failed to start service"; exit 1; }

# Create a status utility script
log "INFO" "Creating status utility script"
cat > "$PROJECT_ROOT/service_status.sh" << EOF
#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

LOG_DIR="$LOG_DIR"
STATUS_LOG="\$LOG_DIR/service_status.log"

echo -e "\${YELLOW}=== Ergo OpenWebUI Service Status ===\${NC}"
echo -e "\${YELLOW}Systemd service status:\${NC}"
sudo systemctl status ergo-openwebui.service

echo -e "\n\${YELLOW}Recent log entries (last 20 lines):\${NC}"
if [ -f "\$STATUS_LOG" ]; then
    tail -n 20 "\$STATUS_LOG"
else
    echo -e "\${RED}Status log file not found\${NC}"
fi

echo -e "\n\${YELLOW}Process status:\${NC}"
pgrep -f "ergo_explorer" > /dev/null && echo -e "\${GREEN}Ergo Explorer is running\${NC}" || echo -e "\${RED}Ergo Explorer is NOT running\${NC}"
pgrep -f "mcpo" > /dev/null && echo -e "\${GREEN}MCPO is running\${NC}" || echo -e "\${RED}MCPO is NOT running\${NC}"

echo -e "\n\${YELLOW}To view full logs:\${NC}"
echo -e "MCPO log: cat \$LOG_DIR/mcpo.log"
echo -e "Ergo Explorer log: cat \$LOG_DIR/ergo_explorer.log"
echo -e "Service status log: cat \$LOG_DIR/service_status.log"
echo -e "Systemd logs: sudo journalctl -u ergo-openwebui.service"
EOF

chmod +x "$PROJECT_ROOT/service_status.sh"

log "INFO" "Service installation complete. Service is enabled and started"
log "INFO" "Check status with: ./service_status.sh"
log "INFO" "Or use: sudo systemctl status ergo-openwebui.service"
log "INFO" "View logs in: $LOG_DIR/" 