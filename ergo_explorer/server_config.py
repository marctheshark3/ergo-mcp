"""
Server configuration for Ergo Explorer MCP.

This module handles the server configuration and setup.
"""

import os
from mcp.server.fastmcp import FastMCP
from ergo_explorer.logging_config import get_logger, init_root_logger
from ergo_explorer.api.routes import register_all_routes
from ergo_explorer.resources.eip_resources import eip_resources

# Initialize root logger
init_root_logger()

# Get module-specific logger
logger = get_logger(__name__)

def create_server():
    """Create and configure the MCP server."""
    # Create MCP server with resource capabilities
    mcp = FastMCP(
        "Ergo Explorer", 
        dependencies=["httpx"],
        capabilities={"resources": {}}
    )
    
    # Register all API routes
    register_all_routes(mcp)
    
    # Register resource handlers
    @mcp.list_resources()
    async def list_resources():
        """List all available resources."""
        # List EIP resources
        eip_list = await eip_resources.list_resources()
        
        # In the future, combine with other resource types
        return eip_list
    
    @mcp.read_resource()
    async def read_resource(uri):
        """Read a specific resource by URI."""
        uri_str = str(uri)
        
        # Route to appropriate resource handler based on URI
        if uri_str.startswith("ergo://eips/"):
            return await eip_resources.read_resource(uri)
        
        # Add handlers for other resource types here
        
        # If no handler matched
        raise ValueError(f"Unknown resource URI: {uri_str}")
    
    # Log API endpoints
    logger.debug(f"ERGO_EXPLORER_API: {os.environ.get('ERGO_EXPLORER_API')}")
    logger.debug(f"ERGO_NODE_API: {os.environ.get('ERGO_NODE_API')}")
    logger.debug(f"ERGOWATCH_API_URL: {os.environ.get('ERGOWATCH_API_URL')}")
    
    # Log server initialization
    logger.info("Initialized Ergo Explorer MCP server with resource capabilities")
    
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