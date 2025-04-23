"""
NFT Collection functionality

This module provides functionality for working with NFT collections.
"""

import asyncio
import time
from typing import Dict, List, Union
from ergo_explorer.logging_config import get_logger
from .api import fetch_node_api, fetch_explorer_api
from .tokens import get_token_by_id
from .boxes import get_box_by_id, get_unspent_boxes_by_token_id, get_boxes_by_token_id
from .cache import _CACHE

# Get module-specific logger
logger = get_logger("token_holders.collections")

async def get_collection_metadata(collection_id: str) -> Dict:
    """
    Get NFT collection metadata based on EIP-34 standard with caching support.
    
    Args:
        collection_id: Token ID of the collection
        
    Returns:
        Dictionary containing collection metadata
    """
    # Check cache first
    if collection_id in _CACHE["collections"]:
        logger.debug(f"Cache hit for collection metadata {collection_id}")
        return _CACHE["collections"][collection_id]
        
    try:
        logger.info(f"Fetching collection metadata for {collection_id}")
        
        # First get the token info to confirm it exists
        token_info = await get_token_by_id(collection_id)
        
        if "error" in token_info:
            logger.error(f"Error fetching collection token: {token_info.get('error')}")
            return {"error": f"Error fetching collection token: {token_info.get('error')}"}
            
        # Get the issuer box (has same ID as token ID)
        issuer_box = await get_box_by_id(collection_id)
        
        if "error" in issuer_box:
            logger.error(f"Error fetching issuer box: {issuer_box.get('error')}")
            return {"error": f"Error fetching issuer box: {issuer_box.get('error')}"}
            
        # Extract collection metadata according to EIP-34
        metadata = {
            "collection_id": collection_id,
            "token_name": token_info.get("name", "Unknown Collection"),
            "token_description": token_info.get("description", "")
        }
        
        # Get additional data from registers of the issuer box
        additional_registers = issuer_box.get("additionalRegisters", {})
        
        # R4: Collection standard version (Int)
        if "R4" in additional_registers:
            try:
                # Parse the register value
                r4_data = additional_registers["R4"]
                if isinstance(r4_data, dict):
                    r4_value = r4_data.get("renderedValue")
                    metadata["version"] = int(r4_value) if r4_value and r4_value.isdigit() else 1
                else:
                    metadata["version"] = 1
            except (ValueError, KeyError):
                metadata["version"] = 1
        else:
            metadata["version"] = 1
            
        # R5: Collection info as Coll[Coll[Byte]]
        # Contains: [logo_url, featured_image_url, banner_image_url, category]
        if "R5" in additional_registers:
            try:
                r5_data = additional_registers["R5"]
                r5_value = r5_data.get("renderedValue") if isinstance(r5_data, dict) else ""
                # This is a simplification - proper parsing would depend on the actual encoding
                collection_info = r5_value.split(",") if r5_value else []
                metadata["logo_url"] = collection_info[0] if len(collection_info) > 0 else ""
                metadata["featured_image_url"] = collection_info[1] if len(collection_info) > 1 else ""
                metadata["banner_image_url"] = collection_info[2] if len(collection_info) > 2 else ""
                metadata["category"] = collection_info[3] if len(collection_info) > 3 else ""
            except (ValueError, KeyError, TypeError, IndexError):
                # Set defaults if parsing fails
                metadata["logo_url"] = ""
                metadata["featured_image_url"] = ""
                metadata["banner_image_url"] = ""
                metadata["category"] = ""
                
        # Extract other registers R6-R8 (simplified)
        for reg in ["R6", "R7", "R8"]:
            if reg in additional_registers:
                try:
                    reg_data = additional_registers[reg]
                    if isinstance(reg_data, dict):
                        metadata[reg.lower()] = reg_data.get("renderedValue", {})
                except:
                    metadata[reg.lower()] = {}
        
        logger.info(f"Successfully retrieved collection metadata for {collection_id}")
        
        # Add result to cache
        if "error" not in metadata:
            _CACHE["collections"][collection_id] = metadata
            
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting collection metadata: {str(e)}")
        return {"error": f"Error getting collection metadata: {str(e)}"}

async def get_collection_nfts(collection_id: str, limit: int = 100, use_cache: bool = True) -> List[str]:
    """
    Find all NFTs belonging to a collection.
    
    This function identifies NFTs that are part of a collection by looking at boxes that
    contain the collection token and checking their R7 register for a reference to the 
    collection. NFTs in the collection have their box ID as their token ID.
    
    Args:
        collection_id: Token ID of the collection
        limit: Maximum number of NFTs to return
        use_cache: Whether to use cache
        
    Returns:
        List of token IDs belonging to the collection
    """
    # Check cache first if enabled
    if use_cache and collection_id in _CACHE["nfts"]:
        logger.debug(f"Cache hit for collection NFTs {collection_id}")
        cached_nfts = _CACHE["nfts"][collection_id]
        
        if len(cached_nfts["nfts"]) >= limit or cached_nfts.get("complete", False):
            return cached_nfts["nfts"][:limit]
    
    collection_nfts = []
    
    # The correct pattern to look for in R7 register
    collection_pattern = f"0e20{collection_id}"
    
    # Get all boxes (spent and unspent) containing the collection token
    try:
        logger.info(f"Searching for boxes containing the collection token {collection_id}")
        offset = 0
        page_size = 50
        max_attempts = 3  # Add retry logic
        
        for attempt in range(max_attempts):
            try:
                while len(collection_nfts) < limit and offset < 1000:
                    logger.debug(f"Fetching boxes with offset {offset}, page size {page_size}")
                    # Use the function to get all boxes (not just unspent)
                    boxes = await get_boxes_by_token_id(collection_id, offset, page_size)
                    
                    if not boxes:
                        logger.debug(f"No more boxes found at offset {offset}")
                        break
                        
                    # Process each box to find NFTs
                    for box in boxes:
                        box_id = box.get("boxId")
                        if not box_id:
                            continue
                            
                        # Check if the box has R7 register with the collection token pattern
                        additional_registers = box.get("additionalRegisters", {})
                        r7_value = None
                        
                        if "R7" in additional_registers:
                            r7_data = additional_registers["R7"]
                            if isinstance(r7_data, str):
                                r7_value = r7_data
                            elif isinstance(r7_data, dict):
                                r7_value = r7_data.get("serializedValue", "")
                            
                        # If R7 contains the collection token pattern, box ID is an NFT token ID
                        if r7_value and collection_pattern in r7_value:
                            logger.debug(f"Found NFT box with ID {box_id} for collection {collection_id}")
                            # Verify it's a valid token before adding
                            token_info = await get_token_by_id(box_id)
                            if "error" not in token_info:
                                if box_id not in collection_nfts:
                                    collection_nfts.append(box_id)
                                    logger.info(f"Added NFT {box_id} to collection {collection_id}")
                        
                        # If we have enough NFTs, stop
                        if len(collection_nfts) >= limit:
                            break
                    
                    # If we've reached our limit or got fewer boxes than requested, we're done
                    if len(collection_nfts) >= limit or len(boxes) < page_size:
                        break
                        
                    offset += page_size
                
                # If we found some NFTs, we can stop retrying
                if collection_nfts:
                    break
            except Exception as e:
                logger.warning(f"Error in attempt {attempt+1}/{max_attempts}: {str(e)}")
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to get collection NFTs after {max_attempts} attempts")
                else:
                    await asyncio.sleep(1)  # Wait before retrying
    except Exception as e:
        logger.error(f"Error getting collection NFTs: {str(e)}")
    
    # Deduplicate the NFTs
    collection_nfts = list(dict.fromkeys(collection_nfts))
    
    # Store in cache if enabled
    if use_cache:
        complete = len(collection_nfts) < limit
        _CACHE["nfts"][collection_id] = {
            "nfts": collection_nfts,
            "complete": complete,
            "timestamp": time.time()
        }
        
    logger.info(f"Found {len(collection_nfts)} NFTs for collection {collection_id}")
    return collection_nfts

async def process_nft_holders(nft_id: str) -> Dict:
    """
    Helper function to process holders for a single NFT.
    
    Args:
        nft_id: NFT token ID to process
        
    Returns:
        Dictionary with holder data for this NFT
    """
    try:
        # Get token info
        token_info = await get_token_by_id(nft_id)
        if "error" in token_info:
            return None
            
        # Get all boxes containing this token
        unspent_boxes = await get_unspent_boxes_by_token_id(nft_id)
        
        if not unspent_boxes:
            return {
                "token_id": nft_id,
                "token_name": token_info.get("name", "Unknown"),
                "supply": token_info.get("emissionAmount", "1"),
                "holders": [],
                "is_unique": True  # Mark as unique NFT by default
            }
        
        # Process boxes to extract holder information
        holders = {}
        total_supply = 0
        is_unique = True  # Assume it's a unique NFT (1 token) until proven otherwise
        
        for box in unspent_boxes:
            box_address = box.get("address")
            if not box_address:
                continue
                
            # Find the token in the box assets
            for asset in box.get("assets", []):
                if asset.get("tokenId") == nft_id:
                    amount = int(asset.get("amount", "0"))
                    total_supply += amount
                    
                    # If total amount is greater than 1, it's not a unique NFT
                    if total_supply > 1:
                        is_unique = False
                    
                    if box_address in holders:
                        holders[box_address] += amount
                    else:
                        holders[box_address] = amount
                    
                    break
        
        # Create holder data list sorted by amount
        holder_data = []
        
        for address, amount in holders.items():
            holder_data.append({
                "address": address,
                "amount": amount,
                "percentage": (amount / total_supply * 100) if total_supply > 0 else 0
            })
        
        # Sort by amount in descending order
        holder_data.sort(key=lambda x: x["amount"], reverse=True)
        
        return {
            "token_id": nft_id,
            "token_name": token_info.get("name", "Unknown"),
            "supply": total_supply,
            "holders": holder_data,
            "is_unique": is_unique  # Add flag to indicate if this is a unique NFT
        }
    except Exception as e:
        logger.warning(f"Error processing token {nft_id}: {str(e)}")
        return None

async def get_collection_holders(collection_id: str, include_raw: bool = False, include_analysis: bool = True, 
                            use_cache: bool = True, batch_size: int = 10) -> Union[str, Dict]:
    """
    Get comprehensive holder information for an NFT collection.
    
    This function identifies all unique holders of NFTs in a collection and calculates
    the distribution of NFTs among these holders, ensuring no duplicate counts.
    
    Args:
        collection_id: Token ID of the collection
        include_raw: Include raw holder data
        include_analysis: Include analysis
        use_cache: Whether to use cache
        batch_size: Number of NFTs to process in parallel
        
    Returns:
        Markdown-formatted analysis or raw data
    """
    # Check cache first if enabled
    if use_cache and collection_id in _CACHE["holders"]:
        logger.debug(f"Cache hit for collection holders {collection_id}")
        cached_result = _CACHE["holders"][collection_id]
        
        # Check if we have the right format cached
        if include_raw and isinstance(cached_result, dict):
            return cached_result
        elif not include_raw and isinstance(cached_result, str):
            return cached_result
    
    try:
        # Get collection metadata
        collection_metadata = await get_collection_metadata(collection_id)
        if "error" in collection_metadata:
            return {"error": collection_metadata["error"]}
            
        # Get all NFTs in the collection
        nft_ids = await get_collection_nfts(collection_id, limit=1000, use_cache=use_cache)
        if not nft_ids:
            return {"error": "No NFTs found in this collection"}
            
        # Process NFTs in batches
        processed_nft_ids = []
        all_nft_holder_data = []
        
        for i in range(0, len(nft_ids), batch_size):
            batch = nft_ids[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(nft_ids)+batch_size-1)//batch_size}")
            
            # Process each NFT concurrently
            batch_tasks = []
            for nft_id in batch:
                batch_tasks.append(process_nft_holders(nft_id))
                processed_nft_ids.append(nft_id)
                
            # Wait for all batch tasks to complete
            batch_results = await asyncio.gather(*batch_tasks)
            all_nft_holder_data.extend([r for r in batch_results if r is not None])
        
        # Improved holder aggregation to avoid duplicates
        # Track which addresses hold which NFTs
        address_to_nfts = {}  # Maps addresses to sets of NFT IDs they hold
        all_holders = set()   # Set of all unique holder addresses
        distinct_nft_count = len(processed_nft_ids)  # Total unique NFT types
        
        # First pass: collect which NFTs each address holds
        for nft_data in all_nft_holder_data:
            nft_id = nft_data.get("token_id")
            if not nft_id:
                continue
                
            for holder in nft_data.get("holders", []):
                address = holder.get("address")
                if not address:
                    continue
                    
                all_holders.add(address)
                
                if address not in address_to_nfts:
                    address_to_nfts[address] = set()
                
                address_to_nfts[address].add(nft_id)
        
        # Now calculate the NFT count for each address
        address_nft_counts = {}
        for address, nft_set in address_to_nfts.items():
            address_nft_counts[address] = len(nft_set)
        
        # Build the result
        result = {
            "collection_id": collection_id,
            "collection_name": collection_metadata.get("token_name", "Unknown Collection"),
            "collection_description": collection_metadata.get("token_description", ""),
            "total_nfts": distinct_nft_count,
            "total_holders": len(all_holders),
            "holders": []
        }
        
        # Add holder information
        for address, nft_count in address_nft_counts.items():
            percentage = (nft_count / distinct_nft_count * 100) if distinct_nft_count > 0 else 0
            holder_info = {
                "address": address,
                "nft_count": nft_count,
                "percentage": round(percentage, 2),
                "nfts_held": list(address_to_nfts[address])  # Include which NFTs the address holds
            }
            result["holders"].append(holder_info)
        
        # Sort holders by NFT count in descending order
        result["holders"].sort(key=lambda x: x["nft_count"], reverse=True)
        
        # Cache raw data for future use
        if use_cache:
            _CACHE["holders"][collection_id + "_raw"] = result
            
        # Return raw data if requested
        if include_raw:
            return result
            
        # Format the result as markdown with optional analysis
        formatted_result = f"""# Collection Holder Analysis: {result["collection_name"]}

## Overview
- Collection ID: {collection_id}
- Name: {result["collection_name"]}
- Description: {result["collection_description"]}
- Total Unique NFTs: {result["total_nfts"]}
- Total Unique Holders: {result["total_holders"]}

## Top Holders
| Rank | Address | Unique NFTs Held | Percentage |
|------|---------|-----------|------------|
"""
        # Add top 20 holders or all if less than 20
        for i, holder in enumerate(result["holders"][:min(20, len(result["holders"]))]):
            formatted_result += f"| {i+1} | {holder['address']} | {holder['nft_count']} | {holder['percentage']}% |\n"

        # Add analysis if requested
        if include_analysis and result["total_holders"] > 0:
            # Calculate metrics
            top_10_holders = result["holders"][:min(10, len(result["holders"]))]
            top_10_percentage = sum(holder["percentage"] for holder in top_10_holders)
            unique_ratio = result["total_holders"] / result["total_nfts"] if result["total_nfts"] > 0 else 0
            avg_nfts_per_holder = result["total_nfts"] / result["total_holders"] if result["total_holders"] > 0 else 0
            
            formatted_result += f"""
## Distribution Analysis

### Concentration
- Top 10 holders control: {top_10_percentage:.2f}% of collection NFTs
- Number of unique holders: {result["total_holders"]}
- Average NFTs per holder: {avg_nfts_per_holder:.2f}

### Collection Metrics
- Unique holder ratio: {unique_ratio:.4f} (higher values mean more distributed ownership)
- Collection size: {result["total_nfts"]} unique NFTs
"""
            
        # Cache formatted result
        if use_cache:
            _CACHE["holders"][collection_id] = formatted_result
            
        return formatted_result
            
    except Exception as e:
        error_msg = f"Error analyzing collection holders: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

async def search_collections(query: str, limit: int = 10) -> Dict:
    """
    Search for NFT collections by name or ID.
    
    Args:
        query: Search query (collection name or ID)
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    try:
        logger.info(f"Searching for collections with query: {query}")
        
        # First try direct token ID search if the query looks like a token ID
        if len(query) >= 64 and all(c in '0123456789abcdefABCDEF' for c in query):
            # This looks like a token ID, try to get it directly
            collection_metadata = await get_collection_metadata(query)
            if "error" not in collection_metadata:
                # Found a direct match, return it as a single result
                return {
                    "items": [{
                        "collection_id": query,
                        "name": collection_metadata.get("token_name", "Unknown Collection"),
                        "description": collection_metadata.get("token_description", ""),
                        "logo_url": collection_metadata.get("logo_url", ""),
                        "category": collection_metadata.get("category", "")
                    }],
                    "total": 1
                }
        
        # Search for tokens using Explorer API
        # (assuming this is implemented elsewhere in the codebase)
        try:
            from ergo_explorer.api.explorer import search_tokens
            response = await search_tokens(query)
        except ImportError:
            # Fallback: use our own explorer search
            response = await fetch_explorer_api("tokens/search", {"query": query, "limit": limit * 2})
        
        if "error" in response or not response:
            return {"items": [], "total": 0}
            
        items = response.get("items", [])
        
        if not items:
            return {"items": [], "total": 0}
        
        # Filter and process potential collections
        collections = []
        
        for token in items[:limit * 2]:
            token_id = token.get("id")
            
            if not token_id:
                continue
                
            # Skip tokens with very high emission amounts (unlikely to be collections)
            emission_amount = token.get("emissionAmount")
            if emission_amount and int(emission_amount) > 1000000:
                continue
            
            # Try to get collection metadata
            try:
                collection_metadata = await get_collection_metadata(token_id)
                
                # Skip if error or if the process couldn't extract metadata
                if "error" in collection_metadata:
                    continue
                
                # Add to results
                collections.append({
                    "collection_id": token_id,
                    "name": collection_metadata.get("token_name", token.get("name", "Unknown")),
                    "description": collection_metadata.get("token_description", token.get("description", "")),
                    "logo_url": collection_metadata.get("logo_url", ""),
                    "category": collection_metadata.get("category", "")
                })
                
                # If we have enough results, stop
                if len(collections) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"Error processing potential collection {token_id}: {str(e)}")
                continue
        
        return {
            "items": collections,
            "total": len(collections)
        }
        
    except Exception as e:
        error_msg = f"Error searching for collections: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg} 