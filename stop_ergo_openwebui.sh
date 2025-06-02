#!/bin/bash
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true
echo "Stopped Ergo Explorer MCP and MCPO services."
# Deactivate virtual environment if it's activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
