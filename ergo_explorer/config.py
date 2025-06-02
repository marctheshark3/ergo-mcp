"""
Configuration settings for the Ergo Explorer MCP server.

This module contains all configuration settings for the various APIs used by the server:

1. Ergo Explorer API - Public blockchain explorer API
2. Ergo Node API - Direct node connection for real-time data
3. ErgoWatch API - Blockchain analytics and historical data

Each API serves a specific purpose and has its own configuration settings.
See docs/API_USAGE_GUIDE.md for detailed information on when to use each API.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ergo Explorer API settings
# Used for basic blockchain queries and cached data
ERGO_EXPLORER_API = "https://api.ergoplatform.com/api/v1"
USER_AGENT = "ErgoMCPServer/1.0"

# Ergo Node API settings
# Used for real-time blockchain data and direct interaction
ERGO_NODE_API = os.getenv("ERGO_NODE_API", "http://localhost:9053")
ERGO_NODE_API_KEY = os.getenv("ERGO_NODE_API_KEY", "")

# ErgoWatch API settings
# Used for blockchain analytics and historical data
ERGOWATCH_API_URL = os.getenv("ERGOWATCH_API_URL", "https://api.ergo.watch")

# Server settings
SERVER_NAME = "Ergo Explorer"
SERVER_PORT = 3001
SERVER_DEPENDENCIES = ["httpx", "python-dotenv"]

# API Documentation URLs
API_DOCS = {
    "explorer": "https://api.ergoplatform.com/api/v1/docs",
    "node": "https://github.com/ergoplatform/ergo/blob/master/src/main/resources/api/openapi.yaml",
    "ergowatch": "https://api.ergo.watch/docs"
}

# Rate Limiting Settings
# These are default values, actual limits may vary by API
RATE_LIMITS = {
    "explorer": 60,  # requests per minute
    "node": None,    # local resource limits apply
    "ergowatch": 60  # requests per minute
}

# Cache settings
# Default timeout for in-memory cache items (in seconds)
CACHE_TIMEOUT = 3600  # 1 hour
