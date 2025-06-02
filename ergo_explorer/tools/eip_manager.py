import logging
from typing import Dict, Any, List, Optional

from ergo_explorer.response_standardizer import standardize_response
from ergo_explorer.eip_manager import EIPManager
from ergo_explorer.eip_manager.eip_manager import EIPDetail, EIPSummary

logger = logging.getLogger(__name__)

# Create EIP manager instance
eip_manager = EIPManager()

# Initialize the EIP manager (load EIPs)
eip_manager.load_or_update_eips()

# Original function kept for backward compatibility
async def list_eips() -> str:
    """
    Get a list of all Ergo Improvement Proposals (EIPs).
    
    This provides a comprehensive list of all EIPs with their numbers,
    titles, and current status.
    """
    logger.info("Getting list of all EIPs")
    eips_data = await fetch_eip_list()
    
    # Format the data as markdown
    result = "# Ergo Improvement Proposals (EIPs)\n\n"
    
    for eip in eips_data:
        eip_number = eip.get("number", 0)
        title = eip.get("title", "Unknown")
        status = eip.get("status", "Unknown")
        result += f"## EIP-{eip_number}: {title}\n"
        result += f"Status: {status}\n\n"
    
    return result

@standardize_response
async def list_eips_json() -> Dict[str, Any]:
    """
    Get a list of all Ergo Improvement Proposals (EIPs) in standardized JSON format.
    
    Returns:
        Dictionary with structured EIP list data
    """
    try:
        logger.info("Fetching list of EIPs")
        eips_data = await fetch_eip_list()
        
        # Format EIPs into standardized structure
        formatted_eips = []
        for eip in eips_data:
            eip_number = eip.get("number", 0)
            title = eip.get("title", "Unknown")
            status = eip.get("status", "Unknown")
            
            formatted_eips.append({
                "number": eip_number,
                "title": title,
                "status": status
            })
        
        # Sort by EIP number for consistency
        formatted_eips.sort(key=lambda x: x["number"])
        
        return {
            "eips": formatted_eips,
            "count": len(formatted_eips)
        }
    except Exception as e:
        logger.error(f"Error fetching EIP list: {str(e)}")
        raise Exception(f"Error retrieving EIP list: {str(e)}")

# Original function kept for backward compatibility
async def get_eip(eip_number: int) -> str:
    """
    Get detailed information about a specific Ergo Improvement Proposal.
    
    Args:
        eip_number: The EIP number to retrieve.
    
    Returns:
        Detailed information about the requested EIP, including its full content.
    """
    logger.info(f"Getting details for EIP-{eip_number}")
    
    try:
        eip_data = await fetch_eip_details(eip_number)
        
        if not eip_data:
            return f"Error: EIP-{eip_number} not found"
        
        return eip_data.get("content", f"Error: Content for EIP-{eip_number} not available")
    except Exception as e:
        logger.error(f"Error retrieving EIP-{eip_number}: {str(e)}")
        return f"Error retrieving EIP-{eip_number}: {str(e)}"

@standardize_response
async def get_eip_json(eip_number: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific Ergo Improvement Proposal in standardized JSON format.
    
    Args:
        eip_number: The EIP number to retrieve
        
    Returns:
        Dictionary with structured EIP data
    """
    try:
        logger.info(f"Fetching EIP-{eip_number}")
        eip_data = await fetch_eip_details(eip_number)
        
        # Check if EIP exists
        if not eip_data:
            raise Exception(f"EIP-{eip_number} not found")
        
        return {
            "number": eip_number,
            "title": eip_data.get("title", f"EIP-{eip_number}"),
            "status": eip_data.get("status", "Unknown"),
            "content": eip_data.get("content", ""),
            "url": f"https://github.com/ergoplatform/eips/blob/master/eip-{eip_number:04d}.md"
        }
    except Exception as e:
        logger.error(f"Error fetching EIP-{eip_number}: {str(e)}")
        raise Exception(f"Error retrieving EIP-{eip_number}: {str(e)}")

# Helper function to fetch EIP list
async def fetch_eip_list() -> List[Dict[str, Any]]:
    """
    Fetch the list of all EIPs from the repository.
    
    Returns:
        List of EIP data dictionaries
    """
    # Ensure EIPs are loaded
    if not eip_manager.eip_cache:
        eip_manager.load_or_update_eips()
    
    # Get all EIPs from the manager
    eip_summaries = eip_manager.get_all_eips()
    
    # Convert EIPSummary objects to dictionaries
    return [
        {
            "number": eip.number,
            "title": eip.title,
            "status": eip.status
        }
        for eip in eip_summaries
    ]

# Helper function to fetch EIP details
async def fetch_eip_details(eip_number: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about a specific EIP.
    
    Args:
        eip_number: The EIP number to fetch
        
    Returns:
        Dictionary with EIP data or None if not found
    """
    # Ensure EIPs are loaded
    if not eip_manager.eip_cache:
        eip_manager.load_or_update_eips()
    
    # Get EIP details from the manager
    eip_detail = eip_manager.get_eip_details(eip_number)
    
    if eip_detail is None:
        return None
    
    # Convert EIPDetail object to dictionary
    return {
        "number": eip_detail.number,
        "title": eip_detail.title,
        "status": eip_detail.status,
        "content": eip_detail.content
    } 