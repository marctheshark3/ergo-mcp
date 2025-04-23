"""
Endpoints for Ergo Improvement Proposals (EIPs).
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from mcp.server.fastmcp import Context

from ergo_explorer.eip_manager import EIPManager
from ergo_explorer.eip_manager.eip_manager import EIPDetail, EIPSummary
from ergo_explorer.logging_config import get_logger

# Get module-specific logger
logger = get_logger(__name__)

# Create EIP manager instance
eip_manager = EIPManager()

# Initialize the EIP manager (load EIPs)
eip_manager.load_or_update_eips()


def register_eip_routes(mcp):
    """Register EIP-related routes with the MCP server."""
    
    @mcp.tool()
    async def list_eips(ctx: Context) -> str:
        """
        Get a list of all Ergo Improvement Proposals (EIPs).
        
        This provides a comprehensive list of all EIPs with their numbers,
        titles, and current status.
        """
        logger.info("Getting list of all EIPs")
        
        # Ensure EIPs are loaded
        if not eip_manager.eip_cache:
            eip_manager.load_or_update_eips()
        
        eips = eip_manager.get_all_eips()
        
        # Format the data as markdown
        result = "# Ergo Improvement Proposals (EIPs)\n\n"
        
        for eip in eips:
            result += f"## EIP-{eip.number}: {eip.title}\n"
            result += f"Status: {eip.status}\n\n"
        
        return result
    
    @mcp.tool()
    async def get_eip(ctx: Context, eip_number: int) -> str:
        """
        Get detailed information about a specific Ergo Improvement Proposal.
        
        Args:
            eip_number: The EIP number to retrieve.
        
        Returns:
            Detailed information about the requested EIP, including its full content.
        """
        logger.info(f"Getting details for EIP-{eip_number}")
        
        # Ensure EIPs are loaded
        if not eip_manager.eip_cache:
            eip_manager.load_or_update_eips()
        
        eip = eip_manager.get_eip_details(eip_number)
        
        if eip is None:
            return f"Error: EIP-{eip_number} not found"
        
        return eip.content
    
    logger.info("Registered EIP routes") 