#!/bin/bash
pkill -f "mcpo" || true
pkill -f "ergo_explorer" || true
echo "Stopped Ergo Explorer MCP and MCPO services."
