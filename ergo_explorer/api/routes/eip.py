"""
Endpoints for Ergo Improvement Proposals (EIPs).
"""

from typing import List, Optional
from mcp.server.fastmcp import Context
from ergo_explorer.eip_manager import EIPManager
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.eip_manager import list_eips_json, get_eip_json

# Get module-specific logger
logger = get_logger(__name__)

# Create EIP manager instance
eip_manager = EIPManager()

# Initialize the EIP manager (load EIPs)
eip_manager.load_or_update_eips()


def register_eip_routes(mcp):
    """Register EIP-related routes with the MCP server."""
    
    @mcp.tool()
    async def list_eips(ctx: Context) -> dict:
        """Get a list of all Ergo Improvement Proposals (EIPs)."""
        logger.info("Getting list of all EIPs")
        return await list_eips_json()
    
    @mcp.tool()
    async def get_eip(ctx: Context, eip_number: int) -> dict:
        """Get detailed information about a specific Ergo Improvement Proposal."""
        logger.info(f"Getting details for EIP-{eip_number}")
        return await get_eip_json(eip_number)
    
    logger.info("Registered EIP routes") 