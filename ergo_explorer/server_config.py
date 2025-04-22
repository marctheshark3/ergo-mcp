"""
Server configuration for Ergo Explorer MCP.

This module handles the server configuration and setup.
"""

import os
from mcp.server.fastmcp import FastMCP
from ergo_explorer.logging_config import get_logger, init_root_logger
from ergo_explorer.api.routes import register_all_routes

# Initialize root logger
init_root_logger()

# Get module-specific logger
logger = get_logger(__name__)

def create_server():
    """Create and configure the MCP server."""
    # Create MCP server
    mcp = FastMCP("Ergo Explorer", dependencies=["httpx"])
    
    # Register all routes
    register_all_routes(mcp)
    
    # Log API endpoints
    logger.debug(f"ERGO_EXPLORER_API: {os.environ.get('ERGO_EXPLORER_API')}")
    logger.debug(f"ERGO_NODE_API: {os.environ.get('ERGO_NODE_API')}")
    logger.debug(f"ERGOWATCH_API_URL: {os.environ.get('ERGOWATCH_API_URL')}")
    
    # Log server initialization
    logger.info("Initialized Ergo Explorer MCP server")
    
    return mcp

def run_server(mcp=None):
    """Run the MCP server."""
    if mcp is None:
        mcp = create_server()
        
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", "3001"))
    
    logger.info(f"Server config: {host}:{port}")
    
    if hasattr(mcp, "host"):
        mcp.host = host
    if hasattr(mcp, "port"):
        mcp.port = port
        
    logger.info("Starting Ergo Explorer MCP server...")
    mcp.run() 