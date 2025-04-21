#!/bin/bash
MCPO_PID=$(ps aux | grep "mcpo --config mcpo_config_standalone.json" | grep -v grep | awk '{print $2}')
if [ -n "$MCPO_PID" ]; then
    echo "Stopping MCPO (PID: $MCPO_PID)..."
    kill $MCPO_PID
    echo "MCPO stopped successfully."
else
    echo "MCPO is not running."
fi
