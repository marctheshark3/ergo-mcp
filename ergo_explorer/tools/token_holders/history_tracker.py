"""
Token transfer tracking and historical analysis

This module provides functionality to track token transfers from transaction data
and build historical token ownership records.
"""

from typing import Dict, List, Any, Union, Optional, Tuple, Set
from datetime import datetime, timedelta
import time
import logging
import json
from ergo_explorer.logging_config import get_logger
from ergo_explorer.api import fetch_address_transactions, fetch_transaction
from .tokens import get_token_by_id
from .history import (
    get_token_history,
    TokenHistory,
    TokenHistorySnapshot,
    TokenTransfer
)
from .holders import get_token_holders
from .boxes import get_boxes_by_token_id
from .cache import save_token_history_to_disk, load_token_history_from_disk
import httpx

# Get module-specific logger
logger = get_logger("token_holders.history_tracker")

# NOTE: The time-based tracking method (track_token_transfers and scan_address_for_token_transfers) 
# has been removed in favor of the more comprehensive box-based method (track_token_transfers_by_boxes)
# which provides block height information and a complete history of all token movements.

async def track_token_transfers_by_boxes(
    token_id: str,
    max_transactions: int = 1000,
    include_snapshots: bool = True,
    batch_size: int = 50
) -> Dict[str, Any]:
    """
    Track token transfers by examining all boxes containing the token.
    This is the primary method for tracking token history, using the /blockchain/box/byTokenId/ endpoint.
    
    This approach provides comprehensive token history information including:
    - All addresses that have held the token
    - Block heights when tokens were in each wallet
    - Complete transaction history for the token
    
    Args:
        token_id: The token ID to track
        max_transactions: Maximum number of transactions to process
        include_snapshots: Whether to include periodic snapshots of holder distribution
        batch_size: Number of boxes to fetch in each API request
        
    Returns:
        Statistics about the tracking operation
    """
    start_time = time.time()
    logger.info(f"Starting token transfer tracking for {token_id} using box API, max transactions: {max_transactions}")
    
    # Get token information
    try:
        token_info = await get_token_by_id(token_id)
        token_name = token_info.get("name", "Unknown Token")
        logger.info(f"Token name: {token_name}")
    except Exception as e:
        logger.warning(f"Could not fetch token info: {str(e)}")
        token_name = "Unknown Token"
    
    # Get token history object
    history = get_token_history(token_id)
    
    # Update token metadata
    history.metadata["token_name"] = token_name
    if "first_tracked" not in history.metadata:
        history.metadata["first_tracked"] = datetime.now()
    history.metadata["last_updated"] = datetime.now()
    
    # Try to load existing history from disk
    loaded_data = load_token_history_from_disk(token_id)
    if loaded_data:
        # Update history from loaded data
        loaded_history = TokenHistory.from_dict(token_id, loaded_data)
        
        # Merge transfers
        existing_tx_ids = {t.tx_id for t in history.transfers}
        for transfer in loaded_history.transfers:
            if transfer.tx_id not in existing_tx_ids:
                history.transfers.append(transfer)
                existing_tx_ids.add(transfer.tx_id)
        
        # Merge snapshots
        for ts, snapshot in loaded_history.snapshots.items():
            if ts not in history.snapshots:
                history.snapshots[ts] = snapshot
        
        # Update metadata (keep the newest last_updated)
        if history.metadata.get("minted_at") is None and loaded_history.metadata.get("minted_at") is not None:
            history.metadata["minted_at"] = loaded_history.metadata.get("minted_at")
        if loaded_history.metadata.get("first_tracked") is not None:
            if history.metadata.get("first_tracked") is None:
                history.metadata["first_tracked"] = loaded_history.metadata.get("first_tracked")
            else:
                history_ft = history.metadata.get("first_tracked")
                loaded_ft = loaded_history.metadata.get("first_tracked")
                if isinstance(loaded_ft, str):
                    loaded_ft = datetime.fromisoformat(loaded_ft)
                if isinstance(history_ft, str):
                    history_ft = datetime.fromisoformat(history_ft)
                if loaded_ft and history_ft and loaded_ft < history_ft:
                    history.metadata["first_tracked"] = loaded_ft
    
    # Keep track of seen transactions to avoid duplicates
    seen_txs = {transfer.tx_id for transfer in history.transfers}
    
    # Fetch boxes containing the token
    processed_txs = 0
    offset = 0
    new_transfers = 0
    total_boxes = 0
    
    # Track the earliest and latest blocks we've seen
    earliest_height = None
    latest_height = None
    
    # Track addresses and their balances over time
    address_balance_history = {}
    
    while processed_txs < max_transactions:
        # Fetch a batch of boxes
        try:
            logger.info(f"Fetching boxes for token {token_id}, offset={offset}, limit={batch_size}")
            boxes = await get_boxes_by_token_id(token_id, offset=offset, limit=batch_size)
            
            if not boxes or len(boxes) == 0:
                logger.info(f"No more boxes found for token {token_id}")
                break
                
            total_boxes += len(boxes)
            logger.debug(f"Found {len(boxes)} boxes for token {token_id}")
            
            # Process each box to extract transaction data
            for box in boxes:
                # Get the transaction ID from the box
                tx_id = box.get("transactionId")
                if not tx_id or tx_id in seen_txs:
                    continue
                
                # Get box creation timestamp (or use current time if not available)
                timestamp_ms = box.get("creationTimestamp", int(time.time() * 1000))
                tx_time = datetime.fromtimestamp(timestamp_ms / 1000)
                
                # Get creation height (block height)
                creation_height = box.get("creationHeight", 0)
                
                # Track earliest and latest heights
                if earliest_height is None or creation_height < earliest_height:
                    earliest_height = creation_height
                if latest_height is None or creation_height > latest_height:
                    latest_height = creation_height
                
                # Get address from box
                address = box.get("address", "Unknown")
                
                # Get token amount from box assets
                token_amount = 0
                for asset in box.get("assets", []):
                    if asset.get("tokenId") == token_id:
                        token_amount = asset.get("amount", 0)
                        break
                
                # Update address balance history
                if address not in address_balance_history:
                    address_balance_history[address] = []
                
                # Add balance entry with height info
                address_balance_history[address].append({
                    "height": creation_height,
                    "amount": token_amount,
                    "timestamp": tx_time
                })
                
                # Extract token transfers from this transaction
                tx_transfers = await extract_token_transfers_with_height(tx_id, tx_time, token_id, creation_height)
                if tx_transfers:
                    for transfer in tx_transfers:
                        history.add_transfer(transfer)
                        new_transfers += 1
                    
                    seen_txs.add(tx_id)
                    processed_txs += 1
                    
                    # Log progress periodically
                    if processed_txs % 10 == 0:
                        logger.info(f"Processed {processed_txs} transactions, found {new_transfers} transfers")
                
                # Check if we've reached the maximum
                if processed_txs >= max_transactions:
                    logger.info(f"Reached maximum transactions limit ({max_transactions})")
                    break
            
            # Move to the next batch
            offset += batch_size
            
        except Exception as e:
            logger.error(f"Error fetching boxes for token {token_id}: {str(e)}")
            break
    
    # Create snapshots if requested
    if include_snapshots and new_transfers > 0:
        # Create snapshots at major height milestones
        if earliest_height is not None and latest_height is not None:
            # Calculate height range
            height_range = latest_height - earliest_height
            
            # Create snapshots at regular height intervals (10 snapshots max)
            num_snapshots = min(10, height_range // 1000 + 1)
            height_step = max(1000, height_range // num_snapshots)
            
            logger.info(f"Creating {num_snapshots} snapshots at {height_step} block intervals")
            
            # Generate snapshots at each interval
            for i in range(num_snapshots + 1):
                target_height = earliest_height + i * height_step
                if target_height > latest_height:
                    target_height = latest_height
                
                # Find the approximate timestamp for this height
                timestamp = None
                for transfers in history.transfers:
                    if hasattr(transfers, 'block_height') and transfers.block_height is not None:
                        if abs(transfers.block_height - target_height) < 100:  # Close enough
                            timestamp = transfers.timestamp
                            break
                
                if timestamp is None:
                    # If we couldn't find a close timestamp, estimate based on avg block time
                    # Ergo has ~2 minute blocks
                    now = datetime.now()
                    estimated_age = (latest_height - target_height) * 120  # seconds
                    timestamp = now - timedelta(seconds=estimated_age)
                
                # Create a snapshot for this height
                snapshot = await create_holder_snapshot(token_id, timestamp)
                if snapshot:
                    snapshot.metadata["block_height"] = target_height
                    history.snapshots[timestamp.isoformat()] = snapshot
                    logger.info(f"Created snapshot for block height {target_height}")
    
    # Save the updated history to disk
    save_token_history_to_disk(token_id, history.to_dict())
    
    # Return statistics about the operation
    execution_time_ms = int((time.time() - start_time) * 1000)
    return {
        "token_id": token_id,
        "token_name": token_name,
        "status": "success",
        "transactions_processed": processed_txs,
        "boxes_examined": total_boxes,
        "transfers_found": new_transfers,
        "total_transfers": len(history.transfers),
        "total_snapshots": len(history.snapshots),
        "earliest_height": earliest_height,
        "latest_height": latest_height,
        "execution_time_ms": execution_time_ms
    }

async def extract_token_transfers_with_height(tx_id: str, tx_time: datetime, token_id: str, block_height: int) -> List[TokenTransfer]:
    """
    Extract token transfers from a transaction with block height information.
    
    Args:
        tx_id: The transaction ID
        tx_time: The transaction timestamp
        token_id: The token ID to look for
        block_height: The block height of this transaction
        
    Returns:
        A list of token transfers found in this transaction
    """
    try:
        # Get detailed transaction data using fetch_transaction
        tx_data = await fetch_transaction(tx_id)
        
        if not tx_data:
            logger.debug(f"No data found for transaction {tx_id}")
            return []
        
        # Process inputs and outputs to find token movements
        inputs = tx_data.get("inputs", [])
        outputs = tx_data.get("outputs", [])
        
        # Track token amounts in inputs and outputs
        input_tokens = {}  # address -> amount
        output_tokens = {}  # address -> amount
        
        # Process input boxes
        for input_box in inputs:
            address = input_box.get("address")
            if not address:
                continue
                
            # Check for token in assets
            for asset in input_box.get("assets", []):
                if asset.get("tokenId") == token_id:
                    amount = asset.get("amount", 0)
                    if address in input_tokens:
                        input_tokens[address] += amount
                    else:
                        input_tokens[address] = amount
        
        # Process output boxes
        for output_box in outputs:
            address = output_box.get("address")
            if not address:
                continue
                
            # Check for token in assets
            for asset in output_box.get("assets", []):
                if asset.get("tokenId") == token_id:
                    amount = asset.get("amount", 0)
                    if address in output_tokens:
                        output_tokens[address] += amount
                    else:
                        output_tokens[address] = amount
        
        # Calculate net changes for each address
        all_addresses = set(list(input_tokens.keys()) + list(output_tokens.keys()))
        transfers = []
        
        for address in all_addresses:
            input_amount = input_tokens.get(address, 0)
            output_amount = output_tokens.get(address, 0)
            net_change = output_amount - input_amount
            
            # If address received tokens
            if net_change > 0:
                # Try to determine sender (could be multiple)
                senders = [addr for addr in input_tokens.keys() if addr != address]
                sender = senders[0] if senders else None
                
                transfer = TokenTransfer(
                    tx_id=tx_id,
                    timestamp=tx_time,
                    from_address=sender,
                    to_address=address,
                    amount=net_change,
                    block_height=block_height
                )
                transfers.append(transfer)
                
            # If address sent tokens
            elif net_change < 0:
                # Try to determine receiver (could be multiple)
                receivers = [addr for addr in output_tokens.keys() if addr != address and output_tokens[addr] > 0]
                receiver = receivers[0] if receivers else None
                
                # Only add this transfer if we didn't already capture it from the receiver's perspective
                if not receiver or receiver not in all_addresses:
                    transfer = TokenTransfer(
                        tx_id=tx_id,
                        timestamp=tx_time,
                        from_address=address,
                        to_address=receiver,
                        amount=abs(net_change),
                        block_height=block_height
                    )
                    transfers.append(transfer)
        
        return transfers
        
    except Exception as e:
        logger.error(f"Error extracting token transfers from {tx_id}: {str(e)}")
        return []

async def create_historical_snapshots(
    token_id: str,
    history: TokenHistory,
    start_time: datetime,
    end_time: datetime,
    interval_days: int = 1
) -> List[TokenHistorySnapshot]:
    """
    Create historical snapshots of token holder distribution.
    
    Args:
        token_id: The token ID
        history: The token history object
        start_time: The start of the time range
        end_time: The end of the time range
        interval_days: Number of days between snapshots
        
    Returns:
        A list of snapshots created
    """
    # Calculate snapshot timestamps
    current_time = start_time
    interval = timedelta(days=interval_days)
    snapshots = []
    
    while current_time <= end_time:
        # Check if we already have a snapshot near this time
        existing_snapshots = list(history.snapshots.values())
        
        # Find the closest existing snapshot
        closest_snapshot = None
        closest_distance = None
        
        for snapshot in existing_snapshots:
            distance = abs((snapshot.timestamp - current_time).total_seconds())
            if closest_distance is None or distance < closest_distance:
                closest_snapshot = snapshot
                closest_distance = distance
        
        # If we have a snapshot within 6 hours, skip this timestamp
        if closest_distance is not None and closest_distance < 6 * 3600:
            current_time += interval
            continue
        
        # Get current holder data
        snapshot = await create_holder_snapshot(token_id, current_time)
        if snapshot:
            history.add_snapshot(snapshot)
            snapshots.append(snapshot)
        
        current_time += interval
    
    logger.info(f"Created {len(snapshots)} historical snapshots for token {token_id}")
    return snapshots

async def create_holder_snapshot(token_id: str, timestamp: datetime) -> Optional[TokenHistorySnapshot]:
    """
    Create a snapshot of token holder distribution at a specific time.
    
    Args:
        token_id: The token ID
        timestamp: The timestamp for this snapshot
        
    Returns:
        A snapshot of token holder distribution, or None if creation failed
    """
    try:
        # Get current token holders
        holder_info = await get_token_holders(token_id, include_raw=True)
        
        # If not a valid response or no holders found, return None
        if not isinstance(holder_info, dict) or "holders" not in holder_info:
            logger.warning(f"No holders found for token {token_id} at {timestamp}")
            return None
        
        # Extract holder data
        holders = holder_info.get("holders", [])
        total_supply = holder_info.get("total_supply", 0)
        total_holders = holder_info.get("total_holders", 0)
        
        # Calculate concentration metrics
        concentration = calculate_concentration_metrics(holders)
        
        # Create and return the snapshot
        return TokenHistorySnapshot(
            token_id=token_id,
            timestamp=timestamp,
            total_supply=total_supply,
            total_holders=total_holders,
            holders=holders,
            concentration=concentration
        )
    
    except Exception as e:
        logger.error(f"Error creating holder snapshot for {token_id} at {timestamp}: {str(e)}")
        return None

def calculate_concentration_metrics(holders: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate concentration metrics for token holders.
    
    Args:
        holders: A list of holder dictionaries with address, amount, percentage
        
    Returns:
        A dictionary of concentration metrics
    """
    # Sort holders by amount (descending)
    sorted_holders = sorted(holders, key=lambda h: h.get("amount", 0), reverse=True)
    
    # Calculate top holder percentages
    top_10_percentage = sum(h.get("percentage", 0) for h in sorted_holders[:min(10, len(sorted_holders))])
    top_20_percentage = sum(h.get("percentage", 0) for h in sorted_holders[:min(20, len(sorted_holders))])
    top_50_percentage = sum(h.get("percentage", 0) for h in sorted_holders[:min(50, len(sorted_holders))])
    
    # Calculate Gini coefficient if there are enough holders
    gini = 0.0
    if len(sorted_holders) > 1:
        # Get holder amounts
        amounts = [h.get("amount", 0) for h in sorted_holders]
        n = len(amounts)
        
        # Calculate Gini coefficient
        # Formula: G = (2 * sum(i*y_i) / (n * sum(y_i))) - (n+1)/n
        # where y_i are the values in ascending order and i is the rank
        amounts.sort()  # Sort in ascending order
        sum_amounts = sum(amounts)
        sum_indexed = sum((i+1) * y for i, y in enumerate(amounts))
        
        if sum_amounts > 0:
            gini = (2 * sum_indexed / (n * sum_amounts)) - (n + 1) / n
    
    return {
        "top_10_percentage": round(top_10_percentage, 2),
        "top_20_percentage": round(top_20_percentage, 2),
        "top_50_percentage": round(top_50_percentage, 2),
        "gini_coefficient": round(gini, 4)
    }

async def get_historical_token_holders(
    token_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    period: str = "monthly"
) -> Dict[str, Any]:
    """
    Get historical token holder distribution data.
    
    Args:
        token_id: Token ID to analyze
        start_time: Start time for filtering (deprecated, included for backwards compatibility)
        end_time: End time for filtering (deprecated, included for backwards compatibility)
        period: Time period for snapshots (daily, weekly, monthly, quarterly, yearly)
        
    Returns:
        Dictionary containing historical token holder distribution data
    """
    try:
        logger.info(f"Getting historical token holders for {token_id}")
        
        # Get token history from cache/storage
        history = get_token_history(token_id)
        
        # Load previously saved history if available
        loaded_data = load_token_history_from_disk(token_id)
        if loaded_data:
            # Update history from loaded data
            loaded_history = TokenHistory.from_dict(token_id, loaded_data)
            
            # Merge transfers
            existing_tx_ids = {t.tx_id for t in history.transfers}
            for transfer in loaded_history.transfers:
                if transfer.tx_id not in existing_tx_ids:
                    history.transfers.append(transfer)
            
            # Merge snapshots
            for ts, snapshot in loaded_history.snapshots.items():
                if ts not in history.snapshots:
                    history.snapshots[ts] = snapshot
            
            # Update metadata
            if history.metadata.get("minted_at") is None and loaded_history.metadata.get("minted_at") is not None:
                history.metadata["minted_at"] = loaded_history.metadata.get("minted_at")
        
        # Get all transfers, no time filtering
        transfers = history.transfers
        
        # Sort transfers by timestamp/block height (newest first)
        transfers.sort(key=lambda t: t.timestamp, reverse=True)
        
        # Create list of formatted transfers
        recent_transfers = [t.to_dict() for t in transfers[:100]]
        
        # Get snapshot data for all time periods
        snapshots = list(history.snapshots.values())
        snapshots.sort(key=lambda s: s.timestamp)
        
        # Format snapshots for distribution changes over time
        distribution_changes = []
        for snapshot in snapshots:
            snapshot_data = snapshot.to_dict()
            distribution_changes.append(snapshot_data)
        
        # Format the response
        return {
            "token_id": token_id,
            "token_name": history.metadata.get("token_name", "Unknown"),
            "first_tracked": history.metadata.get("first_tracked"),
            "last_updated": history.metadata.get("last_updated"),
            "distribution_changes": distribution_changes,
            "recent_transfers": recent_transfers,
            "total_transfers": len(history.transfers),
            "total_snapshots": len(history.snapshots)
        }
    
    except Exception as e:
        logger.error(f"Error getting historical token holders for {token_id}: {str(e)}")
        return {
            "error": str(e),
            "token_id": token_id
        } 