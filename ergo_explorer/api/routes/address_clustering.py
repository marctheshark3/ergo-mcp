"""
Address clustering and entity identification API routes.

This module contains routes for identifying and analyzing potential entities through
address clustering in the Ergo blockchain.
"""

from typing import Dict, Any, Optional
import json
from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.entity_identification import identify_entities_json, format_entity_detection_result
from ergo_explorer.visualization.entity_viz import generate_entity_viz_html, process_entity_data_for_viz

# Get module-specific logger
logger = get_logger(__name__)

def register_address_clustering_routes(mcp):
    """Register address clustering and entity identification routes with the MCP server."""
    
    @mcp.tool()
    async def identify_address_clusters(ctx: Context, address: str, depth: int = 2, tx_limit: int = 100, 
                                     min_confidence: float = 0.0, compact: bool = True) -> Dict[str, Any]:
        """
        Identify potential entity clusters based on address transaction patterns.
        
        Args:
            address: The Ergo address to analyze
            depth: How many degrees of separation to analyze (1-3)
            tx_limit: Maximum number of transactions to analyze per address
            min_confidence: Minimum confidence score (0-1) for including a cluster (ignored in current implementation)
            compact: Whether to return a compact output suitable for LLM consumption (reduces verbosity). Default is True.
            
        Returns:
            Dictionary containing entity clusters and analysis results
        """
        logger.info(f"Identifying address clusters for {address} with depth {depth}, compact={compact}")
        
        try:
            # Call the entity identification logic with compact_output parameter
            result_json = await identify_entities_json(
                address, 
                depth=depth, 
                tx_limit=tx_limit, 
                compact_output=compact
            )
            result = json.loads(result_json)
            
            # Handle minimum confidence filtering in the route if needed
            if min_confidence > 0 and isinstance(result, dict) and "clusters" in result:
                # This would be implemented here if needed
                pass
                
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            logger.error(f"Error identifying entities: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_entity_visualization(ctx: Context, address: str, depth: int = 2, tx_limit: int = 100, 
                                   min_confidence: float = 0.0, compact: bool = True) -> Dict[str, Any]:
        """
        Generate a visualization of entity clusters for an address.
        
        Args:
            address: The Ergo address to analyze and visualize
            depth: How many degrees of separation to analyze (1-3)
            tx_limit: Maximum number of transactions to analyze per address
            min_confidence: Minimum confidence score (0-1) for including a cluster (ignored in current implementation)
            compact: Whether to use compact data format for LLM consumption (reduces verbosity). Default is True.
            
        Returns:
            Dictionary containing HTML visualization and data for Open WebUI
        """
        logger.info(f"Generating entity visualization for {address} with depth {depth}, compact={compact}")
        
        try:
            # First identify the entities with compact_output parameter
            entity_json = await identify_entities_json(
                address, 
                depth=depth, 
                tx_limit=tx_limit, 
                compact_output=compact
            )
            raw_entity_data = json.loads(entity_json)
            
            # Process data for visualization
            viz_data = process_entity_data_for_viz(raw_entity_data)
            
            # Generate HTML visualization
            html = generate_entity_viz_html(viz_data)
            
            # Return both the raw data and the visualization
            response = {
                "success": True,
                "visualization_html": html,
                "entity_data": raw_entity_data,
                "visualization_data": viz_data
            }
            
            return response
        except Exception as e:
            logger.error(f"Error in entity visualization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "visualization_html": f"<html><body><p>Error: {str(e)}</p></body></html>"
            }
    
    @mcp.tool()
    async def openwebui_entity_tool(ctx: Context, address: str, depth: int = 2, tx_limit: int = 100, 
                                 min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Special endpoint for Open WebUI integration that follows their expected response format.
        
        Args:
            address: The Ergo address to analyze
            depth: How many degrees of separation to analyze (1-3)
            tx_limit: Maximum number of transactions to analyze per address
            min_confidence: Minimum confidence score (0-1) for including a cluster (ignored in current implementation)
            
        Returns:
            Formatted response compatible with Open WebUI tools
        """
        logger.info(f"Open WebUI entity tool called for address {address}")
        
        try:
            # Always use compact output for LLM consumption
            entity_json = await identify_entities_json(
                address, 
                depth=depth, 
                tx_limit=tx_limit, 
                compact_output=True
            )
            entity_data = json.loads(entity_json)
            
            # Create formatted text response using the helper function
            text_response = format_entity_detection_result(entity_data, html=False)
            
            # Format for Open WebUI - they typically expect a 'text' field
            openwebui_response = {
                "text": text_response,
                # Only include essential data to reduce token usage
                "data": {
                    "seed_address": entity_data.get("seed_address"),
                    "seed_cluster_id": entity_data.get("seed_cluster_id"),
                    "address_count": entity_data.get("address_count", 0),
                    "relationship_count": entity_data.get("relationship_count", 0)
                }
            }
            
            return openwebui_response
        except Exception as e:
            logger.error(f"Error in OpenWebUI entity tool: {str(e)}")
            return {
                "text": f"Error identifying entities for address {address}: {str(e)}",
                "data": {}
            }
    
    @mcp.tool()
    async def openwebui_entity_viz_tool(ctx: Context, address: str, depth: int = 2, tx_limit: int = 100, 
                                     min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Special visualization endpoint for Open WebUI integration.
        
        Args:
            address: The Ergo address to visualize
            depth: How many degrees of separation to analyze (1-3)
            tx_limit: Maximum number of transactions to analyze per address
            min_confidence: Minimum confidence score (0-1) for including a cluster (ignored in current implementation)
            
        Returns:
            Formatted response with HTML visualization for Open WebUI tools
        """
        logger.info(f"Open WebUI visualization tool called for address {address}")
        
        try:
            # Always use compact output for LLM consumption
            entity_json = await identify_entities_json(
                address, 
                depth=depth, 
                tx_limit=tx_limit, 
                compact_output=True
            )
            entity_data = json.loads(entity_json)
            
            # Process for visualization
            viz_data = process_entity_data_for_viz(entity_data)
            
            # Generate HTML
            html = generate_entity_viz_html(viz_data)
            
            # Format specifically for Open WebUI - minimal text, just the HTML
            openwebui_response = {
                "text": f"Entity visualization for address {address} showing {entity_data.get('address_count', 0)} addresses in {len(entity_data.get('clusters', {}))} clusters.",
                "html": html
            }
            
            return openwebui_response
            
        except Exception as e:
            logger.error(f"Error in OpenWebUI visualization: {str(e)}", exc_info=True)
            return {
                "text": f"Error generating visualization: {str(e)}",
                "html": f"<html><body><p>Error: {str(e)}</p></body></html>"
            }
    
    logger.info("Registered address clustering routes") 