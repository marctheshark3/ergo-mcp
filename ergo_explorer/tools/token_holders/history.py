"""
Historical token holder tracking

This module provides functionality to track and analyze historical token ownership data,
showing how distribution has changed over time.
"""

from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime, timedelta
import time
import logging
from ergo_explorer.logging_config import get_logger
from .tokens import get_token_by_id
from .boxes import get_unspent_boxes_by_token_id
from ergo_explorer.api import fetch_address_transactions, fetch_transaction

# Get module-specific logger
logger = get_logger("token_holders.history")

# Define time period constants for sampling frequencies
PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
PERIOD_QUARTERLY = "quarterly"
PERIOD_YEARLY = "yearly"

# Define data structure for historical token holder snapshots
"""
Historical data is organized hierarchically:

TokenHistoryData = {
    "token_id": {
        "metadata": {
            "token_id": str,
            "token_name": str,
            "decimals": int,
            "minted_at": datetime,
            "first_tracked": datetime,
            "last_updated": datetime
        },
        "snapshots": {
            "timestamp_1": {
                "timestamp": datetime,
                "total_supply": int,
                "total_holders": int,
                "holders": [
                    {
                        "address": str,
                        "amount": int,
                        "percentage": float
                    },
                    ...
                ],
                "concentration": {
                    "top_10_percentage": float,
                    "top_20_percentage": float,
                    "top_50_percentage": float,
                    "gini_coefficient": float
                }
            },
            "timestamp_2": { ... },
            ...
        },
        "transfers": [
            {
                "timestamp": datetime,
                "tx_id": str,
                "from_address": str,
                "to_address": str,
                "amount": int
            },
            ...
        ]
    },
    ...
}
"""

class TokenHistorySnapshot:
    """A class representing a snapshot of token holder distribution at a specific time."""
    
    def __init__(self, 
                 token_id: str, 
                 timestamp: datetime,
                 total_supply: int = 0,
                 total_holders: int = 0,
                 holders: List[Dict[str, Any]] = None,
                 concentration: Dict[str, float] = None):
        """
        Initialize a token history snapshot.
        
        Args:
            token_id: The unique identifier for the token
            timestamp: The time when this snapshot was taken
            total_supply: The total supply of the token at this time
            total_holders: The number of unique holders at this time
            holders: List of holder information dictionaries
            concentration: Dictionary of concentration metrics
        """
        self.token_id = token_id
        self.timestamp = timestamp
        self.total_supply = total_supply
        self.total_holders = total_holders
        self.holders = holders or []
        self.concentration = concentration or {
            "top_10_percentage": 0.0,
            "top_20_percentage": 0.0,
            "top_50_percentage": 0.0,
            "gini_coefficient": 0.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the snapshot to a dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_supply": self.total_supply,
            "total_holders": self.total_holders,
            "holders": self.holders,
            "concentration": self.concentration
        }
    
    @classmethod
    def from_dict(cls, token_id: str, data: Dict[str, Any]) -> 'TokenHistorySnapshot':
        """Create a snapshot from a dictionary."""
        return cls(
            token_id=token_id,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            total_supply=data["total_supply"],
            total_holders=data["total_holders"],
            holders=data["holders"],
            concentration=data["concentration"]
        )


class TokenTransfer:
    """A class representing a token transfer between addresses."""
    
    def __init__(self,
                 token_id: str,
                 tx_id: str,
                 timestamp: datetime,
                 from_address: str,
                 to_address: str,
                 amount: int,
                 block_height: Optional[int] = None):
        """
        Initialize a token transfer.
        
        Args:
            token_id: The unique identifier for the token
            tx_id: The transaction ID where this transfer occurred
            timestamp: The time when this transfer occurred
            from_address: The sending address (or None for minting)
            to_address: The receiving address (or None for burning)
            amount: The amount of tokens transferred
            block_height: The blockchain height when this transfer occurred
        """
        self.token_id = token_id
        self.tx_id = tx_id
        self.timestamp = timestamp
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.block_height = block_height
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transfer to a dictionary."""
        return {
            "tx_id": self.tx_id,
            "timestamp": self.timestamp.isoformat(),
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "block_height": self.block_height
        }
    
    @classmethod
    def from_dict(cls, token_id: str, data: Dict[str, Any]) -> 'TokenTransfer':
        """Create a transfer from a dictionary."""
        return cls(
            token_id=token_id,
            tx_id=data["tx_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            from_address=data["from_address"],
            to_address=data["to_address"],
            amount=data["amount"],
            block_height=data.get("block_height")  # Handle older data without this field
        )


class TokenHistory:
    """A class for managing and accessing a token's ownership history."""
    
    def __init__(self, token_id: str, token_metadata: Dict[str, Any] = None):
        """
        Initialize token history tracking.
        
        Args:
            token_id: The unique identifier for the token
            token_metadata: Optional metadata about the token
        """
        self.token_id = token_id
        self.metadata = token_metadata or {
            "token_id": token_id,
            "token_name": "Unknown",
            "decimals": 0,
            "minted_at": None,
            "first_tracked": datetime.now(),
            "last_updated": datetime.now()
        }
        self.snapshots: Dict[str, TokenHistorySnapshot] = {}
        self.transfers: List[TokenTransfer] = []
    
    def add_snapshot(self, snapshot: TokenHistorySnapshot) -> None:
        """
        Add a new snapshot to the history.
        
        Args:
            snapshot: The snapshot to add
        """
        timestamp_key = snapshot.timestamp.isoformat()
        self.snapshots[timestamp_key] = snapshot
        self.metadata["last_updated"] = datetime.now()
    
    def add_transfer(self, transfer: TokenTransfer) -> None:
        """
        Add a new transfer to the history.
        
        Args:
            transfer: The transfer to add
        """
        self.transfers.append(transfer)
        self.metadata["last_updated"] = datetime.now()
    
    def get_snapshots_in_range(self, start_time: datetime, end_time: datetime) -> List[TokenHistorySnapshot]:
        """
        Get snapshots within a time range.
        
        Args:
            start_time: The start of the time range
            end_time: The end of the time range
            
        Returns:
            A list of snapshots within the specified time range
        """
        result = []
        for timestamp_key, snapshot in self.snapshots.items():
            if start_time <= snapshot.timestamp <= end_time:
                result.append(snapshot)
        
        # Sort by timestamp
        result.sort(key=lambda x: x.timestamp)
        return result
    
    def get_transfers_in_range(self, start_time: datetime, end_time: datetime) -> List[TokenTransfer]:
        """
        Get transfers within a time range.
        
        Args:
            start_time: The start of the time range
            end_time: The end of the time range
            
        Returns:
            A list of transfers within the specified time range
        """
        result = []
        for transfer in self.transfers:
            if start_time <= transfer.timestamp <= end_time:
                result.append(transfer)
        
        # Sort by timestamp
        result.sort(key=lambda x: x.timestamp)
        return result
    
    def get_distribution_changes(self, period: str = PERIOD_MONTHLY, 
                                start_time: Optional[datetime] = None, 
                                end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get distribution changes over time at the specified frequency.
        
        Args:
            period: The time period for sampling (daily, weekly, monthly, etc.)
            start_time: The start of the time range (or earliest available if None)
            end_time: The end of the time range (or latest available if None)
            
        Returns:
            A list of summary snapshots showing distribution changes
        """
        # Get the full range of snapshots
        all_snapshots = list(self.snapshots.values())
        if not all_snapshots:
            return []
            
        # Sort snapshots by timestamp
        all_snapshots.sort(key=lambda x: x.timestamp)
        
        # If no start or end time provided, use the range of available data
        if start_time is None:
            start_time = all_snapshots[0].timestamp
        if end_time is None:
            end_time = all_snapshots[-1].timestamp
        
        # Filter snapshots by time range
        in_range_snapshots = [s for s in all_snapshots if start_time <= s.timestamp <= end_time]
        
        # Sample snapshots according to the period
        period_map = {
            PERIOD_DAILY: timedelta(days=1),
            PERIOD_WEEKLY: timedelta(weeks=1),
            PERIOD_MONTHLY: timedelta(days=30),
            PERIOD_QUARTERLY: timedelta(days=90),
            PERIOD_YEARLY: timedelta(days=365)
        }
        
        interval = period_map.get(period, timedelta(days=30))
        current_time = start_time
        result = []
        
        while current_time <= end_time:
            # Find the snapshot closest to the current time
            closest_snapshot = None
            closest_distance = None
            
            for snapshot in in_range_snapshots:
                distance = abs((snapshot.timestamp - current_time).total_seconds())
                if closest_distance is None or distance < closest_distance:
                    closest_snapshot = snapshot
                    closest_distance = distance
            
            if closest_snapshot and closest_distance is not None and closest_distance < interval.total_seconds():
                # Create a summarized snapshot for the distribution change
                summary = {
                    "timestamp": closest_snapshot.timestamp.isoformat(),
                    "total_holders": closest_snapshot.total_holders,
                    "concentration": closest_snapshot.concentration
                }
                result.append(summary)
            
            current_time += interval
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the token history to a dictionary."""
        return {
            "metadata": self.metadata,
            "snapshots": {ts: snapshot.to_dict() for ts, snapshot in self.snapshots.items()},
            "transfers": [t.to_dict() for t in self.transfers]
        }
    
    @classmethod
    def from_dict(cls, token_id: str, data: Dict[str, Any]) -> 'TokenHistory':
        """Create a token history from a dictionary."""
        history = cls(token_id, data.get("metadata", {}))
        
        # Fix metadata timestamp fields
        if isinstance(history.metadata.get("first_tracked"), str):
            history.metadata["first_tracked"] = datetime.fromisoformat(history.metadata["first_tracked"])
        if isinstance(history.metadata.get("last_updated"), str):
            history.metadata["last_updated"] = datetime.fromisoformat(history.metadata["last_updated"])
        if isinstance(history.metadata.get("minted_at"), str):
            history.metadata["minted_at"] = datetime.fromisoformat(history.metadata["minted_at"])
        
        # Load snapshots
        for ts, snapshot_data in data.get("snapshots", {}).items():
            history.snapshots[ts] = TokenHistorySnapshot.from_dict(token_id, snapshot_data)
        
        # Load transfers
        for transfer_data in data.get("transfers", []):
            history.transfers.append(TokenTransfer.from_dict(token_id, transfer_data))
        
        return history


# Token history storage
_TOKEN_HISTORY_CACHE: Dict[str, TokenHistory] = {}


def get_token_history(token_id: str) -> TokenHistory:
    """
    Get the token history object for a token ID.
    
    Args:
        token_id: The token ID to get history for
        
    Returns:
        A TokenHistory object for the specified token
    """
    if token_id not in _TOKEN_HISTORY_CACHE:
        # Create a new history object
        _TOKEN_HISTORY_CACHE[token_id] = TokenHistory(token_id)
        
        # Init with token metadata
        init_token_history(token_id)
    
    return _TOKEN_HISTORY_CACHE[token_id]


async def init_token_history(token_id: str) -> None:
    """
    Initialize token history with metadata.
    
    Args:
        token_id: The token ID to initialize
    """
    try:
        history = get_token_history(token_id)
        
        # Get token metadata
        token_info = await get_token_by_id(token_id)
        if token_info and "name" in token_info:
            history.metadata["token_name"] = token_info.get("name", "Unknown")
            history.metadata["decimals"] = token_info.get("decimals", 0)
            
            # Try to get minted timestamp if available
            if "emissionAmount" in token_info:
                # This is an approximation - we'd need to get the actual first transaction
                # for this token to get the exact minting time
                history.metadata["minted_at"] = datetime.fromisoformat(token_info.get("creationTimestamp", datetime.now().isoformat()))
    
    except Exception as e:
        logger.error(f"Error initializing token history for {token_id}: {str(e)}")


def clear_token_history_cache() -> None:
    """Clear the token history cache."""
    _TOKEN_HISTORY_CACHE.clear()


def get_token_history_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the token history cache.
    
    Returns:
        A dictionary with statistics about the cached token histories
    """
    stats = {
        "total_tokens": len(_TOKEN_HISTORY_CACHE),
        "tokens": {}
    }
    
    for token_id, history in _TOKEN_HISTORY_CACHE.items():
        stats["tokens"][token_id] = {
            "snapshots": len(history.snapshots),
            "transfers": len(history.transfers),
            "first_tracked": history.metadata.get("first_tracked"),
            "last_updated": history.metadata.get("last_updated")
        }
    
    return stats 