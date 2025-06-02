#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define project root directory
PROJECT_ROOT="/home/ai-admin/ergo-mcp"
LOG_DIR="$PROJECT_ROOT/logs"

# Check if log directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}Error: Log directory $LOG_DIR does not exist${NC}"
    exit 1
fi

# Function to display usage information
show_usage() {
    echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
    echo -e "View and monitor logs for the Ergo OpenWebUI service"
    echo -e ""
    echo -e "Options:"
    echo -e "  -h, --help              Show this help message"
    echo -e "  -s, --status            View the service status log"
    echo -e "  -m, --mcpo              View the MCPO log"
    echo -e "  -e, --ergo-explorer     View the Ergo Explorer log"
    echo -e "  -y, --systemd           View systemd service logs"
    echo -e "  -a, --all               View all logs side by side (requires tmux)"
    echo -e "  -f, --follow            Follow the log in real-time (add -f to any option)"
    echo -e "  -n, --lines [N]         Show the last N lines (default: 50)"
    echo -e ""
    echo -e "Examples:"
    echo -e "  $0 -s                   View the status log"
    echo -e "  $0 -m -f                View and follow the MCPO log"
    echo -e "  $0 -e -n 100            View the last 100 lines of the Ergo Explorer log"
    echo -e "  $0 -a                   View all logs side by side in tmux"
}

# Default options
FOLLOW=""
LINES="50"
LOG_TYPE=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -s|--status)
            LOG_TYPE="status"
            shift
            ;;
        -m|--mcpo)
            LOG_TYPE="mcpo"
            shift
            ;;
        -e|--ergo-explorer)
            LOG_TYPE="ergo"
            shift
            ;;
        -y|--systemd)
            LOG_TYPE="systemd"
            shift
            ;;
        -a|--all)
            LOG_TYPE="all"
            shift
            ;;
        -f|--follow)
            FOLLOW="-f"
            shift
            ;;
        -n|--lines)
            LINES="$2"
            shift
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# If no log type specified, show usage
if [ -z "$LOG_TYPE" ]; then
    show_usage
    exit 1
fi

# Function to check if file exists
check_file_exists() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: Log file $1 does not exist${NC}"
        return 1
    fi
    return 0
}

# View logs based on type
case $LOG_TYPE in
    "status")
        STATUS_LOG="$LOG_DIR/service_status.log"
        if check_file_exists "$STATUS_LOG"; then
            echo -e "${BLUE}Showing the last $LINES lines of the service status log:${NC}"
            tail $FOLLOW -n "$LINES" "$STATUS_LOG" | grep --color=auto -E 'ERROR|WARN|$'
        fi
        ;;
    "mcpo")
        MCPO_LOG="$LOG_DIR/mcpo.log"
        if check_file_exists "$MCPO_LOG"; then
            echo -e "${BLUE}Showing the last $LINES lines of the MCPO log:${NC}"
            tail $FOLLOW -n "$LINES" "$MCPO_LOG" | grep --color=auto -E 'error|warning|$'
        fi
        ;;
    "ergo")
        ERGO_LOG="$LOG_DIR/ergo_explorer.log"
        if check_file_exists "$ERGO_LOG"; then
            echo -e "${BLUE}Showing the last $LINES lines of the Ergo Explorer log:${NC}"
            tail $FOLLOW -n "$LINES" "$ERGO_LOG" | grep --color=auto -E 'error|warning|$'
        fi
        ;;
    "systemd")
        SYSTEMD_LOG="$LOG_DIR/systemd-ergo-openwebui.log"
        SYSTEMD_ERROR_LOG="$LOG_DIR/systemd-ergo-openwebui-error.log"
        
        echo -e "${BLUE}Showing the last $LINES lines of the systemd service logs:${NC}"
        echo -e "${YELLOW}Standard output:${NC}"
        if check_file_exists "$SYSTEMD_LOG"; then
            tail -n "$LINES" "$SYSTEMD_LOG"
        fi
        
        echo -e "\n${YELLOW}Standard error:${NC}"
        if check_file_exists "$SYSTEMD_ERROR_LOG"; then
            tail -n "$LINES" "$SYSTEMD_ERROR_LOG"
        fi
        
        echo -e "\n${YELLOW}Journalctl logs:${NC}"
        sudo journalctl -u ergo-openwebui.service -n "$LINES" $([[ -n "$FOLLOW" ]] && echo "-f")
        ;;
    "all")
        # Check if tmux is installed
        if ! command -v tmux &> /dev/null; then
            echo -e "${RED}Error: tmux is not installed. Please install it or view logs individually.${NC}"
            exit 1
        fi
        
        # Create a new detached tmux session
        tmux new-session -d -s "ergo-logs" "bash -c 'echo -e \"${YELLOW}Service Status Log${NC}\"; tail $FOLLOW -n \"$LINES\" \"$LOG_DIR/service_status.log\" 2>/dev/null || echo \"Status log not found\"; bash'"
        
        # Split the window horizontally and run the second command
        tmux split-window -h -t "ergo-logs" "bash -c 'echo -e \"${YELLOW}MCPO Log${NC}\"; tail $FOLLOW -n \"$LINES\" \"$LOG_DIR/mcpo.log\" 2>/dev/null || echo \"MCPO log not found\"; bash'"
        
        # Split the right pane vertically and run the third command
        tmux split-window -v -t "ergo-logs" "bash -c 'echo -e \"${YELLOW}Ergo Explorer Log${NC}\"; tail $FOLLOW -n \"$LINES\" \"$LOG_DIR/ergo_explorer.log\" 2>/dev/null || echo \"Ergo Explorer log not found\"; bash'"
        
        # Split the top-left pane vertically and run the fourth command
        tmux split-window -v -t "ergo-logs:0.0" "bash -c 'echo -e \"${YELLOW}Systemd Log${NC}\"; tail $FOLLOW -n \"$LINES\" \"$LOG_DIR/systemd-ergo-openwebui.log\" 2>/dev/null || echo \"Systemd log not found\"; bash'"
        
        # Attach to the session
        tmux attach-session -t "ergo-logs"
        ;;
esac 