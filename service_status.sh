#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

LOG_DIR="/home/ai-admin/ergo-mcp/logs"
STATUS_LOG="$LOG_DIR/service_status.log"

echo -e "${YELLOW}=== Ergo OpenWebUI Service Status ===${NC}"
echo -e "${YELLOW}Systemd service status:${NC}"
sudo systemctl status ergo-openwebui.service

echo -e "\n${YELLOW}Recent log entries (last 20 lines):${NC}"
if [ -f "$STATUS_LOG" ]; then
    tail -n 20 "$STATUS_LOG"
else
    echo -e "${RED}Status log file not found${NC}"
fi

echo -e "\n${YELLOW}Process status:${NC}"
pgrep -f "ergo_explorer" > /dev/null && echo -e "${GREEN}Ergo Explorer is running${NC}" || echo -e "${RED}Ergo Explorer is NOT running${NC}"
pgrep -f "mcpo" > /dev/null && echo -e "${GREEN}MCPO is running${NC}" || echo -e "${RED}MCPO is NOT running${NC}"

echo -e "\n${YELLOW}To view full logs:${NC}"
echo -e "MCPO log: cat $LOG_DIR/mcpo.log"
echo -e "Ergo Explorer log: cat $LOG_DIR/ergo_explorer.log"
echo -e "Service status log: cat $LOG_DIR/service_status.log"
echo -e "Systemd logs: sudo journalctl -u ergo-openwebui.service"
