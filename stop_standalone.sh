#!/bin/bash
MCPO_PID=$(pgrep -f "mcpo --config mcpo_config_standalone.json")
ERGO_MCP_PID=$(pgrep -f "python -m ergo_explorer --port 3001")

if [ -n "$MCPO_PID" ]; then
    echo "Stopping MCPO (PID: $MCPO_PID)..."
    kill $MCPO_PID
    echo "MCPO stopped."
else
    echo "MCPO is not running."
fi

if [ -n "$ERGO_MCP_PID" ]; then
    echo "Stopping Ergo Explorer MCP (PID: $ERGO_MCP_PID)..."
    kill $ERGO_MCP_PID
    echo "Ergo Explorer MCP stopped."
else
    echo "Ergo Explorer MCP is not running."
fi
