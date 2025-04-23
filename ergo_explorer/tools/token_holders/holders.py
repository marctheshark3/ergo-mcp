"""
Token holder analysis

This module provides functionality to analyze token holder distribution.
"""

from typing import Dict, Union
from ergo_explorer.logging_config import get_logger
from .tokens import get_token_by_id
from .boxes import get_unspent_boxes_by_token_id

# Get module-specific logger
logger = get_logger("token_holders.holders")

async def get_token_holders(token_id: str, include_raw: bool = False, include_analysis: bool = True) -> Union[str, Dict]:
    """
    Get comprehensive token holder information.
    
    Args:
        token_id: Token ID to analyze
        include_raw: Include raw holder data
        include_analysis: Include holder analysis
        
    Returns:
        Formatted string with token holder information or raw data dictionary
    """
    try:
        logger.info(f"Fetching token information for {token_id}")
        token_info = await get_token_by_id(token_id)
        
        if "error" in token_info:
            logger.error(f"Error fetching token info: {token_info.get('error')}")
            error_msg = f"Error fetching token info: {token_info.get('error')}"
            return error_msg if not include_raw else {"error": token_info.get("error"), "token_id": token_id}
            
        logger.info(f"Fetching unspent boxes for token {token_id}")
        all_boxes = []
        offset = 0
        limit = 100  # Max items per request
        
        while True:
            logger.debug(f"Fetching boxes at offset={offset}, limit={limit}")
            boxes = await get_unspent_boxes_by_token_id(token_id, offset, limit)
            
            if not boxes or "error" in boxes:
                if "error" in boxes:
                    logger.error(f"Error fetching boxes: {boxes.get('error')}")
                break
                
            all_boxes.extend(boxes)
            logger.debug(f"Retrieved {len(boxes)} boxes, total now: {len(all_boxes)}")
            
            # If we got fewer boxes than the limit, we've reached the end
            if len(boxes) < limit:
                break
                
            offset += limit
        
        # Process boxes to get address holdings
        logger.info(f"Processing {len(all_boxes)} boxes to extract holder information")
        address_holdings = {}
        for box in all_boxes:
            address = box.get("address")
            if not address:
                continue
                
            # Find the specific token in the box's assets
            for asset in box.get("assets", []):
                if asset.get("tokenId") == token_id:
                    amount = int(asset.get("amount", 0))
                    if address in address_holdings:
                        address_holdings[address] += amount
                    else:
                        address_holdings[address] = amount
        
        # Calculate total supply and percentages
        total_supply = sum(address_holdings.values())
        logger.info(f"Found {len(address_holdings)} unique holders with total supply of {total_supply}")
        
        # Extract token metadata
        token_name = token_info.get("name", "Unknown Token")
        token_decimals = token_info.get("decimals", 0)
        
        # Build the result
        result = {
            "token_id": token_id,
            "token_name": token_name,
            "decimals": token_decimals,
            "total_supply": total_supply,
            "total_holders": len(address_holdings),
            "holders": []
        }
        
        # Add holder information
        for address, amount in address_holdings.items():
            percentage = (amount / total_supply * 100) if total_supply > 0 else 0
            holder_info = {
                "address": address,
                "amount": amount,
                "percentage": round(percentage, 6)
            }
            result["holders"].append(holder_info)
        
        # Sort holders by amount in descending order
        result["holders"].sort(key=lambda x: x["amount"], reverse=True)
        
        # Return raw data if requested
        if include_raw:
            return result
            
        # Analyze distribution if requested
        distribution_analysis = ""
        if include_analysis and result["total_holders"] > 0:
            # Calculate concentration metrics
            top_10_holders = result["holders"][:min(10, len(result["holders"]))]
            top_10_percentage = sum(holder["percentage"] for holder in top_10_holders)
            
            distribution_analysis = f"""
## Distribution Analysis

### Concentration
- Top 10 holders control: {top_10_percentage:.2f}% of supply
- Number of unique holders: {result["total_holders"]}
- Average holding per address: {total_supply / result["total_holders"]:.2f} tokens
"""
        
        # Format the result as markdown
        formatted_result = f"""# Token Holder Analysis: {token_name}

## Overview
- Token ID: {token_id}
- Name: {token_name}
- Decimals: {token_decimals}
- Total Supply: {total_supply}
- Total Holders: {result["total_holders"]}

## Top Holders
| Rank | Address | Amount | Percentage |
|------|---------|--------|------------|
"""
        # Add top 20 holders or all if less than 20
        for i, holder in enumerate(result["holders"][:min(20, len(result["holders"]))]):
            formatted_result += f"| {i+1} | {holder['address']} | {holder['amount']} | {holder['percentage']}% |\n"

        # Add distribution analysis if included
        if distribution_analysis:
            formatted_result += distribution_analysis
            
        return formatted_result
        
    except Exception as e:
        logger.error(f"Error getting token holders: {str(e)}")
        error_msg = f"Error getting token holders: {str(e)}"
        return error_msg if not include_raw else {"error": str(e), "token_id": token_id} 