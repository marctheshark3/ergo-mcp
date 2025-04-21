"""
MCP resources implementation for Ergo Improvement Proposals (EIPs).
"""

import re
from typing import Dict, List, Optional

from mcp.resources import Resource, ResourceContent
from mcp.types import AnyUrl

from ergo_explorer.eip_manager import EIPManager
from ergo_explorer.logging_config import get_logger

logger = get_logger(__name__)

# Create EIP manager instance
eip_manager = EIPManager()


class EipResources:
    """Handler for EIP resources."""

    URI_PATTERN = r"^ergo://eips/(\d+)$"
    
    def __init__(self):
        """Initialize EIP resources handler."""
        # Ensure EIPs are loaded
        eip_manager.load_or_update_eips()
    
    async def list_resources(self) -> List[Resource]:
        """List all available EIP resources."""
        logger.info("Listing EIP resources")
        
        # Ensure EIPs are loaded
        if not eip_manager.eip_cache:
            eip_manager.load_or_update_eips()
        
        eips = eip_manager.get_all_eips()
        resources = []
        
        for eip in eips:
            resources.append(
                Resource(
                    uri=f"ergo://eips/{eip.number}",
                    name=f"EIP-{eip.number}: {eip.title}",
                    description=f"Status: {eip.status}",
                    mimeType="text/html"
                )
            )
        
        logger.info(f"Listed {len(resources)} EIP resources")
        return resources
    
    async def read_resource(self, uri: AnyUrl) -> Dict[str, List[ResourceContent]]:
        """Read content of a specific EIP resource."""
        uri_str = str(uri)
        logger.info(f"Reading EIP resource: {uri_str}")
        
        # Parse the URI to extract the EIP number
        match = re.match(self.URI_PATTERN, uri_str)
        if not match:
            logger.error(f"Invalid EIP URI: {uri_str}")
            raise ValueError(f"Invalid EIP URI: {uri_str}")
        
        eip_number = int(match.group(1))
        eip = eip_manager.get_eip_details(eip_number)
        
        if eip is None:
            logger.error(f"EIP-{eip_number} not found")
            raise ValueError(f"EIP-{eip_number} not found")
        
        content = ResourceContent(
            uri=uri_str,
            mimeType="text/html",
            text=eip.content
        )
        
        return {"contents": [content]}


# Export the resources handler
eip_resources = EipResources() 