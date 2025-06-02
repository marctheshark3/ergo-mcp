#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all running ergo_explorer and mcpo processes...${NC}"

# Find all ergo_explorer processes
ERGO_PIDS=$(pgrep -f "ergo_explorer" || echo "")
MCPO_PIDS=$(pgrep -f "mcpo" || echo "")

if [ -n "$ERGO_PIDS" ]; then
    echo -e "${YELLOW}Found ergo_explorer processes: $ERGO_PIDS${NC}"
    for pid in $ERGO_PIDS; do
        echo -e "Stopping ergo_explorer process $pid..."
        kill $pid 2>/dev/null || sudo kill $pid 2>/dev/null || sudo kill -9 $pid 2>/dev/null
        if ps -p $pid > /dev/null; then
            echo -e "${RED}Failed to stop process $pid${NC}"
        else
            echo -e "${GREEN}Successfully stopped process $pid${NC}"
        fi
    done
else
    echo -e "${GREEN}No ergo_explorer processes found${NC}"
fi

if [ -n "$MCPO_PIDS" ]; then
    echo -e "${YELLOW}Found mcpo processes: $MCPO_PIDS${NC}"
    for pid in $MCPO_PIDS; do
        echo -e "Stopping mcpo process $pid..."
        kill $pid 2>/dev/null || sudo kill $pid 2>/dev/null || sudo kill -9 $pid 2>/dev/null
        if ps -p $pid > /dev/null; then
            echo -e "${RED}Failed to stop process $pid${NC}"
        else
            echo -e "${GREEN}Successfully stopped process $pid${NC}"
        fi
    done
else
    echo -e "${GREEN}No mcpo processes found${NC}"
fi

# Verify all processes are stopped
sleep 2
ERGO_PIDS=$(pgrep -f "ergo_explorer" || echo "")
MCPO_PIDS=$(pgrep -f "mcpo" || echo "")

if [ -n "$ERGO_PIDS" ] || [ -n "$MCPO_PIDS" ]; then
    echo -e "${RED}Some processes are still running:${NC}"
    [ -n "$ERGO_PIDS" ] && echo -e "${RED}Ergo Explorer: $ERGO_PIDS${NC}"
    [ -n "$MCPO_PIDS" ] && echo -e "${RED}MCPO: $MCPO_PIDS${NC}"
    echo -e "${YELLOW}Attempting to force kill...${NC}"
    
    for pid in $ERGO_PIDS $MCPO_PIDS; do
        echo -e "Force killing process $pid..."
        sudo kill -9 $pid 2>/dev/null
    done
else
    echo -e "${GREEN}All processes successfully stopped${NC}"
fi

# Finally verify
sleep 1
ERGO_PIDS=$(pgrep -f "ergo_explorer" || echo "")
MCPO_PIDS=$(pgrep -f "mcpo" || echo "")

if [ -n "$ERGO_PIDS" ] || [ -n "$MCPO_PIDS" ]; then
    echo -e "${RED}Failed to stop all processes:${NC}"
    [ -n "$ERGO_PIDS" ] && echo -e "${RED}Ergo Explorer: $ERGO_PIDS${NC}"
    [ -n "$MCPO_PIDS" ] && echo -e "${RED}MCPO: $MCPO_PIDS${NC}"
    exit 1
else
    echo -e "${GREEN}All processes have been successfully stopped${NC}"
fi 