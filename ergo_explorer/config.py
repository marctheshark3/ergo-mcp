"""
Configuration settings for the Ergo Explorer MCP server.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
ERGO_EXPLORER_API = "https://api.ergoplatform.com/api/v1"
USER_AGENT = "ErgoMCPServer/1.0"

# Ergo Node API settings
ERGO_NODE_API = os.getenv("ERGO_NODE_API", "http://localhost:9053")
ERGO_NODE_API_KEY = os.getenv("ERGO_NODE_API_KEY", "")

# Server settings
SERVER_NAME = "Ergo Explorer"
SERVER_PORT = 3001
SERVER_DEPENDENCIES = ["httpx", "python-dotenv"]
