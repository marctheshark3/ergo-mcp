#!/bin/bash
export ERGO_NODE_API="http://localhost:9053"
export ERGO_NODE_API_KEY="hashcream"

# Execute docker run, passing through any arguments ($@)
# We keep --rm and -p 3001:3001 as they are container configs
# We pass the variables using -e VAR_NAME so Docker inherits them
docker run --rm -p 3001:3001 -e ERGO_NODE_API -e ERGO_NODE_API_KEY mcp/ergo-explorer "$@" 