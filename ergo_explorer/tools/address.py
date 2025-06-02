"""
MCP tools for working with Ergo blockchain addresses.
"""

from typing import Dict, Set, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import math
from collections import Counter, defaultdict
import itertools

from ergo_explorer.api import fetch_balance, fetch_address_transactions, fetch_transaction
from ergo_explorer.api import fetch_address_book, fetch_token_info
from ergo_explorer.response_format import standardize_response, smart_limit
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache for transaction data to avoid redundant API calls
tx_cache = {}

# Token cache to avoid multiple lookups
token_info_cache = {}

# Helper function to fetch token name with caching
async def get_token_name(token_id: str) -> str:
    """Fetch token name with caching."""
    if token_id in token_info_cache:
        return token_info_cache[token_id].get("name", token_id)
    
    try:
        token_info = await fetch_token_info(token_id)
        if token_info and "name" in token_info:
            token_info_cache[token_id] = token_info
            return token_info.get("name", token_id)
        return token_id
    except Exception as e:
        logger.warning(f"Error fetching token info for {token_id}: {e}")
        return token_id

# Helper function to fetch transaction with caching
async def fetch_transaction_cached(tx_id):
    """Fetch transaction details with caching."""
    if tx_id in tx_cache:
        return tx_cache[tx_id]
    
    try:
        tx_details = await fetch_transaction(tx_id)
        tx_cache[tx_id] = tx_details
        return tx_details
    except Exception as e:
        logger.error(f"Error fetching transaction {tx_id}: {e}")
        raise

@standardize_response
async def get_address_balance_json(address: str) -> Dict[str, Any]:
    """Get the confirmed balance for an Ergo address in standardized JSON format.
    
    Args:
        address: Ergo blockchain address
        
    Returns:
        Structured data containing address balance information
    """
    try:
        logger.info(f"Fetching balance for address: {address}")
        balance = await fetch_balance(address)
        
        # Format ERG amount
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        # Format token balances
        formatted_tokens = []
        for token in balance.get("tokens", []):
            token_amount = token.get("amount", 0)
            token_name = token.get("name", "Unknown Token")
            token_id = token.get("tokenId", "")
            token_decimals = token.get("decimals", 0)
            
            # Format decimal amount correctly
            if token_decimals > 0:
                token_formatted_amount = token_amount / (10 ** token_decimals)
            else:
                token_formatted_amount = token_amount
                
            formatted_tokens.append({
                "id": token_id,
                "name": token_name,
                "amount": token_amount,
                "formatted_amount": token_formatted_amount,
                "decimals": token_decimals
            })
            
        # Create structured response
        return {
            "address": address,
            "balance": {
                "nanoErgs": balance.get("nanoErgs", 0),
                "erg": erg_amount
            },
            "tokens": formatted_tokens,
            "token_count": len(formatted_tokens)
        }
    except Exception as e:
        logger.error(f"Error fetching balance for {address}: {str(e)}")
        raise Exception(f"Error retrieving address balance: {str(e)}")

# Original function kept for backward compatibility
async def get_transaction_history(address: str, limit: int = 20) -> str:
    """Get the transaction history for an Ergo address.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
    """
    try:
        tx_data = await fetch_address_transactions(address, limit=limit)
        
        # Extract basic statistics
        total = tx_data.get("total", 0)
        items = tx_data.get("items", [])
        
        if not items:
            return f"No transactions found for address {address}."
        
        result = f"Transaction History for {address}\n"
        result += f"Found {total} total transactions (showing {len(items)})\n\n"
        
        # Process each transaction
        for i, tx in enumerate(items, 1):
            tx_id = tx.get("id", "Unknown")
            timestamp = tx.get("timestamp", 0)
            date_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Calculate value change for this address
            value_in = 0
            value_out = 0
            
            # Process inputs
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    value_in += inp.get("value", 0)
            
            # Process outputs
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    value_out += out.get("value", 0)
            
            # Calculate net change
            net_change = value_out - value_in
            net_change_erg = net_change / 1_000_000_000
            
            # Format sign for readability
            if net_change > 0:
                change_str = f"+{net_change_erg:.9f} ERG"
            else:
                change_str = f"{net_change_erg:.9f} ERG"
            
            result += f"{i}. [{date_time}] {change_str}\n"
            result += f"   TX: {tx_id}\n"
            
            # Check if there were any token transfers
            in_tokens = set()
            out_tokens = set()
            
            # Process input tokens
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    for token in inp.get("assets", []):
                        in_tokens.add(token.get("tokenId", ""))
            
            # Process output tokens
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    for token in out.get("assets", []):
                        out_tokens.add(token.get("tokenId", ""))
            
            # Report token transfers
            if in_tokens or out_tokens:
                result += f"   Tokens: {'✓' if in_tokens or out_tokens else '✗'}\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error fetching transaction history: {str(e)}"

@standardize_response
async def get_transaction_history_json(address: str, limit: int = 20) -> Dict[str, Any]:
    """Get the transaction history for an Ergo address in standardized JSON format.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
        
    Returns:
        Structured data containing transaction history
    """
    try:
        logger.info(f"Fetching transaction history for address: {address} (limit: {limit})")
        tx_data = await fetch_address_transactions(address, limit=limit)
        
        # Extract basic statistics
        total = tx_data.get("total", 0)
        items = tx_data.get("items", [])
        
        formatted_transactions = []
        for tx in items:
            tx_id = tx.get("id", "Unknown")
            timestamp = tx.get("timestamp", 0)
            date_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Calculate value change for this address
            value_in = 0
            value_out = 0
            
            # Process inputs
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    value_in += inp.get("value", 0)
            
            # Process outputs
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    value_out += out.get("value", 0)
            
            # Calculate net change
            net_change = value_out - value_in
            net_change_erg = net_change / 1_000_000_000
            
            # Check token transfers
            in_tokens = []
            out_tokens = []
            
            # Process input tokens
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    for token in inp.get("assets", []):
                        in_tokens.append({
                            "tokenId": token.get("tokenId", ""),
                            "amount": token.get("amount", 0)
                        })
            
            # Process output tokens
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    for token in out.get("assets", []):
                        out_tokens.append({
                            "tokenId": token.get("tokenId", ""),
                            "amount": token.get("amount", 0)
                        })
            
            formatted_transactions.append({
                "txId": tx_id,
                "timestamp": timestamp,
                "formatted_date": date_time,
                "valueChange": {
                    "nanoErgs": net_change,
                    "erg": net_change_erg
                },
                "tokenTransfers": {
                    "inTokens": in_tokens,
                    "outTokens": out_tokens,
                    "hasTokenTransfers": bool(in_tokens or out_tokens)
                }
            })
        
        # Apply smart limiting if needed
        limited_transactions, is_truncated = smart_limit(formatted_transactions, limit)
        
        return {
            "address": address,
            "total": total,
            "transactions": limited_transactions,
            "count": len(limited_transactions),
            "is_truncated": is_truncated
        }
    except Exception as e:
        logger.error(f"Error fetching transaction history for {address}: {str(e)}")
        raise Exception(f"Error retrieving transaction history: {str(e)}")

async def analyze_address(address: str, depth: int = 2, tx_limit: int = 5) -> str:
    """Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.
    
    Args:
        address: Ergo blockchain address to analyze
        depth: How many layers of transactions to analyze (1-4, default: 2)
        tx_limit: Maximum transactions per address to analyze (default: 5)
    """
    from ergo_explorer.api import fetch_transaction
    from datetime import datetime
    
    # Limit max depth to 4 for performance
    depth = min(depth, 4)
    
    try:
        # Results dictionary
        results = {
            "starting_address": address,
            "depth": depth,
            "related_addresses": set(),
            "transactions_analyzed": set(),
            "path_traces": []
        }
        
        async def analyze_level(addr, current_depth, parent_tx=None):
            """Recursive function to analyze an address at a specific depth level."""
            if current_depth > depth:
                return
                
            # Get transactions for this address
            tx_data = await fetch_address_transactions(addr, limit=tx_limit)
            tx_items = tx_data.get("items", [])
            
            for tx in tx_items:
                tx_id = tx.get("id")
                
                # Skip if already analyzed
                if tx_id in results["transactions_analyzed"]:
                    continue
                    
                results["transactions_analyzed"].add(tx_id)
                
                # Get full transaction details
                tx_details = await fetch_transaction(tx_id)
                
                # Record transaction path
                path = {
                    "tx_id": tx_id,
                    "depth": current_depth,
                    "parent_tx": parent_tx,
                    "timestamp": datetime.fromtimestamp(tx.get("timestamp", 0)/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "value": tx.get("value", 0) / 1_000_000_000,
                    "related_addresses": []
                }
                
                # Analyze inputs and outputs to find related addresses
                for inp in tx_details.get("inputs", []):
                    input_addr = inp.get("address")
                    if input_addr and input_addr != addr:
                        results["related_addresses"].add(input_addr)
                        path["related_addresses"].append({"address": input_addr, "type": "input"})
                
                for out in tx_details.get("outputs", []):
                    output_addr = out.get("address")
                    if output_addr and output_addr != addr:
                        results["related_addresses"].add(output_addr)
                        path["related_addresses"].append({"address": output_addr, "type": "output"})
                
                results["path_traces"].append(path)
                
                # Recursively analyze related addresses at next depth
                if current_depth < depth:
                    for rel_addr in path["related_addresses"]:
                        await analyze_level(rel_addr["address"], current_depth + 1, tx_id)
        
        # Start analysis from the root address
        await analyze_level(address, 1)
        
        # Format results into a readable report
        report = f"Forensic Analysis for {address}\n\n"
        report += f"Depth: {depth}\n"
        report += f"Transactions analyzed: {len(results['transactions_analyzed'])}\n"
        report += f"Related addresses found: {len(results['related_addresses'])}\n\n"
        
        # Transaction Paths
        if results["path_traces"]:
            report += "Transaction Paths:\n"
            
            # Group by depth for readability
            for level in range(1, depth + 1):
                level_paths = [p for p in results["path_traces"] if p["depth"] == level]
                
                if level_paths:
                    report += f"\nDepth {level}:\n"
                    
                    for path in level_paths:
                        report += f"• TX: {path['tx_id']}\n"
                        report += f"  Date: {path['timestamp']}\n"
                        report += f"  Value: {path['value']:.9f} ERG\n"
                        
                        if path["parent_tx"]:
                            report += f"  Parent TX: {path['parent_tx']}\n"
                            
                        if path["related_addresses"]:
                            report += f"  Related Addresses: {len(path['related_addresses'])}\n"
                        
                        report += "\n"
        
        return report
    except Exception as e:
        return f"Error during address analysis: {str(e)}"

# Token classification constants
TOKEN_TYPES = {
    "NFT": "nft",
    "UTILITY": "utility",
    "STABLECOIN": "stablecoin",
    "GOVERNANCE": "governance",
    "UNKNOWN": "unknown"
}

# Known token categorizations
KNOWN_TOKENS = {
    # Stablecoins
    "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04": TOKEN_TYPES["STABLECOIN"],  # SigUSD
    
    # Governance tokens
    "1fd6e032e8476c4aa54c18c1a308dce83940e8f4a28f576440513ed7326ad489": TOKEN_TYPES["GOVERNANCE"],  # ErgoPad
    
    # NFTs - Some examples
    "7ea0ad2e1d436bc2c0fb6456f569f0782a16361b61c6668af80c2e18b855d8d3": TOKEN_TYPES["NFT"],
    
    # Utility tokens
    "c316e07ea2c2bb020c670bc2b926df5b7da318026d3a97920ed09e7fa4110f07": TOKEN_TYPES["UTILITY"]
}

# Helper function to detect token type
def identify_token_type(token_id: str, token_amount: int = 1) -> str:
    """Determine token type based on ID and information."""
    # Check if it's in our known tokens database
    if token_id in KNOWN_TOKENS:
        return KNOWN_TOKENS[token_id]
    
    # Heuristic detection:
    # NFTs typically have amount = 1
    if token_amount == 1:
        return TOKEN_TYPES["NFT"]
    
    # Default to unknown
    return TOKEN_TYPES["UNKNOWN"]

# Helper function for address clustering
def find_related_addresses(tx_details_list: List[Dict], addressed_of_interest: str) -> Dict[str, Set]:
    """Identify potentially related addresses using common input ownership heuristic."""
    # Multi-input transactions potentially have inputs controlled by the same entity
    related_groups = defaultdict(set)
    tx_addr_map = {}  # Maps tx_id -> set of input addresses
    
    # First pass: build transaction to address mappings
    for tx in tx_details_list:
        tx_id = tx.get("id", "")
        if not tx_id:
            continue
            
        input_addresses = set()
        for inp in tx.get("inputs", []):
            addr = inp.get("address")
            if addr and addr != addressed_of_interest:
                input_addresses.add(addr)
        
        if len(input_addresses) > 1:  # Only consider multi-input txs
            tx_addr_map[tx_id] = input_addresses
    
    # Second pass: cluster addresses that appear together in inputs
    for tx_id, addresses in tx_addr_map.items():
        # Add all addresses from this tx to the related group
        for addr in addresses:
            related_groups[addr].update(addresses - {addr})
    
    return related_groups

# Helper function to format addresses and token IDs in a readable way
def format_id(full_id: str, prefix_len: int = 6, suffix_len: int = 6) -> str:
    """Format long IDs like addresses and token IDs in a readable way."""
    if len(full_id) <= prefix_len + suffix_len + 3:  # If ID is already short
        return full_id
    return f"{full_id[:prefix_len]}...{full_id[-suffix_len:]}"

async def get_common_interactions(address: str, limit: int = 100, min_interactions: int = 2, verbose: bool = True) -> Dict[str, Any]:
    """Analyze transaction history to identify addresses that commonly interact with this address.
    
    Args:
        address: The Ergo address to analyze
        limit: Maximum number of transactions to analyze (default: 100)
        min_interactions: Minimum number of interactions to consider an address as "common" (default: 2)
        verbose: Whether to return detailed information or a condensed version (default: True)
        
    Returns:
        Dict containing:
        - common_interactions: List of addresses that commonly interact with this address
        - statistics: General statistics about the address's interactions
    """
    logger.info(f"Analyzing common interactions for address: {address} (limit: {limit})")
    
    # Initialize data structure to track interactions
    interactions = {}
    
    # Track overall stats
    stats = {
        "total_transactions_analyzed": 0,
        "unique_addresses": 0,
        "total_incoming": 0,
        "total_outgoing": 0,
        "total_volume_nano": 0,
        "total_volume_erg": 0,
        "first_tx_timestamp": None,
        "last_tx_timestamp": None,
        "token_type_counts": defaultdict(int),
        "time_of_day_activity": defaultdict(int),
        "day_of_week_activity": defaultdict(int)
    }
    
    try:
        # Fetch address book for better categorization
        known_addresses = {}
        try:
            address_book = await fetch_address_book()
            if address_book and "addresses" in address_book:
                for addr_entry in address_book.get("addresses", []):
                    addr = addr_entry.get("address")
                    if addr:
                        known_addresses[addr] = {
                            "name": addr_entry.get("name", "Unknown"),
                            "type": addr_entry.get("type", "Unknown")
                        }
            logger.info(f"Loaded {len(known_addresses)} known addresses from address book")
        except Exception as e:
            logger.warning(f"Could not load address book: {str(e)}")
        
        # Known DEX addresses - only these will be classified as DEXes
        known_dex_addresses = {
            "5vSUZRZbdVbnk4sJWjg2uhL94VZWRg4iatK9VgMChufzUgdihgvhR8yWSUEJKszzV7Vmi6K8hCyKTNhUaiP8p5ko6YEU9yfHpjVuXdQ4i5p4cRCzch6ZiqWrNukYjv7Vs5jvBwqg5hcEJ8u1eerr537YLWUoxxi1M4vQxuaCihzPKMt8NDXP4WcbN6mfNxxLZeGBvsHVvVmina5THaECosCWozKJFBnscjhpr3AJsdaL8evXAvPfEjGhVMoTKXAb2ZGGRmR8g1eZshaHmgTg2imSiaoXU5eiF3HvBnDuawaCtt674ikZ3oZdekqswcVPGMwqqUKVsGY4QuFeQoGwRkMqEYTdV2UDMMsfrjrBYQYKUBFMwsQGMNBL1VoY78aotXzdeqJCBVKbQdD3ZZWvukhSe4xrz8tcF3PoxpysDLt89boMqZJtGEHTV9UBTBEac6sDyQP693qT3nKaErN8TCXrJBUmHPqKozAg9bwxTqMYkpmb9iVKLSoJxG7MjAj72SRbcqQfNCVTztSwN3cRxSrVtz4p87jNFbVtFzhPg7UqDwNFTaasySCqM": "ErgoDEX"
        }
        
        # Fetch transaction history
        offset = 0
        all_transactions = []
        
        # Paginate through transactions if needed
        while len(all_transactions) < limit:
            page_size = min(50, limit - len(all_transactions))
            tx_data = await fetch_address_transactions(address, limit=page_size, offset=offset)
            items = tx_data.get("items", [])
            
            if not items:
                break
                
            all_transactions.extend(items)
            offset += len(items)
            
            # If we got fewer than requested, there are no more
            if len(items) < page_size:
                break
        
        logger.info(f"Retrieved {len(all_transactions)} transactions for analysis")
        stats["total_transactions_analyzed"] = len(all_transactions)
        
        # Prepare for parallel transaction fetch
        tx_ids = [tx.get("id", "Unknown") for tx in all_transactions]
        timestamps = {tx.get("id", "Unknown"): tx.get("timestamp", 0) for tx in all_transactions}
        
        # Update timestamp stats and time window analytics
        for tx_id, timestamp in timestamps.items():
            if stats["first_tx_timestamp"] is None or timestamp < stats["first_tx_timestamp"]:
                stats["first_tx_timestamp"] = timestamp
            if stats["last_tx_timestamp"] is None or timestamp > stats["last_tx_timestamp"]:
                stats["last_tx_timestamp"] = timestamp
            
            # Time window analysis - add time of day and day of week stats
            tx_date = datetime.fromtimestamp(timestamp/1000)
            hour = tx_date.hour
            day_of_week = tx_date.strftime('%A')  # Monday, Tuesday, etc.
            
            # Log activity by time of day (in 3-hour windows)
            time_window = f"{(hour // 3) * 3}-{((hour // 3) * 3) + 3}"
            stats["time_of_day_activity"][time_window] += 1
            
            # Log activity by day of week
            stats["day_of_week_activity"][day_of_week] += 1
        
        # Fetch all transaction details in parallel
        tx_details_list = await asyncio.gather(*[fetch_transaction_cached(tx_id) for tx_id in tx_ids])
        
        # Find potentially related addresses using clustering
        address_clusters = find_related_addresses(tx_details_list, address)
        
        # Data structure to track temporal patterns
        time_patterns = {
            "daily": defaultdict(list),
            "weekly": defaultdict(list),
            "monthly": defaultdict(list)
        }
        
        # Data structure to track token patterns for each address
        token_patterns = defaultdict(lambda: defaultdict(int))
        
        # Smart contract detection patterns
        smart_contract_addresses = set()
        
        # First pass - identify potential smart contracts from transaction patterns
        for tx_details in tx_details_list:
            inputs = tx_details.get("inputs", [])
            outputs = tx_details.get("outputs", [])
            
            # Smart contracts typically have specific patterns in outputs
            for out in outputs:
                out_addr = out.get("address")
                if out_addr and out_addr != address:
                    # Long ergoTree is typically a contract
                    ergo_tree = out.get("ergoTree", "")
                    if ergo_tree and (len(ergo_tree) > 128 or ergo_tree.startswith("1001")):
                        smart_contract_addresses.add(out_addr)
                    
                    # Boxes with additional registers are likely contracts
                    additional_registers = out.get("additionalRegisters", {})
                    if additional_registers and len(additional_registers) > 0:
                        smart_contract_addresses.add(out_addr)
            
            # Identify data-input patterns (typically used by smart contracts)
            data_inputs = tx_details.get("dataInputs", [])
            if data_inputs:
                for inp in inputs:
                    input_addr = inp.get("address")
                    if input_addr and input_addr != address:
                        smart_contract_addresses.add(input_addr)
        
        # Process each transaction to extract interactions
        for i, tx_details in enumerate(tx_details_list):
            tx_id = tx_ids[i]
            timestamp = timestamps[tx_id]
            tx_date = datetime.fromtimestamp(timestamp/1000)
            
            # Process inputs (addresses sending to this address)
            for inp in tx_details.get("inputs", []):
                input_addr = inp.get("address")
                input_value = inp.get("value", 0)
                
                if input_addr and input_addr != address:
                    # Record this as an incoming interaction
                    if input_addr not in interactions:
                        interactions[input_addr] = {
                            "address": input_addr,
                            "incoming_count": 0,
                            "outgoing_count": 0,
                            "total_volume_nano": 0,
                            "first_interaction": timestamp,
                            "last_interaction": timestamp,
                            "token_transfers": set(),
                            "token_types": defaultdict(int),
                            "is_dex": False,
                            "is_smartcontract": False,
                            "is_p2p": False,
                            "is_recurring": False,
                            "name": None,
                            "type": None,
                            "related_addresses": set(),
                            "time_patterns": {
                                "timestamps": [],
                                "values": [],
                                "recurring_daily": False,
                                "recurring_weekly": False,
                                "recurring_monthly": False
                            },
                            "confidence_scores": {
                                "dex": 0.0,
                                "smartcontract": 0.0,
                                "p2p": 0.0,
                                "recurring": 0.0,
                                "related_entity": 0.0
                            }
                        }
                        
                        # Add known address info if available
                        if input_addr in known_addresses:
                            interactions[input_addr]["name"] = known_addresses[input_addr]["name"]
                            interactions[input_addr]["type"] = known_addresses[input_addr]["type"]
                        
                        # Add related addresses from clustering
                        if input_addr in address_clusters:
                            interactions[input_addr]["related_addresses"] = address_clusters[input_addr]
                    
                    # Update stats for this interaction
                    interactions[input_addr]["incoming_count"] += 1
                    interactions[input_addr]["total_volume_nano"] += input_value
                    interactions[input_addr]["last_interaction"] = timestamp
                    
                    # Record timestamp and value for time pattern analysis
                    interactions[input_addr]["time_patterns"]["timestamps"].append(timestamp)
                    interactions[input_addr]["time_patterns"]["values"].append(input_value)
                    
                    # Track time patterns
                    day_key = tx_date.strftime('%Y-%m-%d')
                    week_key = tx_date.strftime('%Y-%W')
                    month_key = tx_date.strftime('%Y-%m')
                    
                    time_patterns["daily"][day_key].append((input_addr, input_value))
                    time_patterns["weekly"][week_key].append((input_addr, input_value))
                    time_patterns["monthly"][month_key].append((input_addr, input_value))
                    
                    # Update first interaction if this is earlier
                    if timestamp < interactions[input_addr]["first_interaction"]:
                        interactions[input_addr]["first_interaction"] = timestamp
                    
                    # Track tokens if any and analyze token types
                    for asset in inp.get("assets", []):
                        token_id = asset.get("tokenId")
                        token_amount = asset.get("amount", 1)
                        
                        if token_id:
                            interactions[input_addr]["token_transfers"].add(token_id)
                            
                            # Token context analysis - identify token type
                            token_type = identify_token_type(token_id, token_amount)
                            interactions[input_addr]["token_types"][token_type] += 1
                            stats["token_type_counts"][token_type] += 1
                            
                            # Track token patterns for this address
                            token_patterns[input_addr][token_id] += 1
                    
                    # Update global stats
                    stats["total_incoming"] += 1
                    stats["total_volume_nano"] += input_value
            
            # Process outputs (addresses this address is sending to)
            for out in tx_details.get("outputs", []):
                output_addr = out.get("address")
                output_value = out.get("value", 0)
                
                if output_addr and output_addr != address:
                    # Record this as an outgoing interaction
                    if output_addr not in interactions:
                        interactions[output_addr] = {
                            "address": output_addr,
                            "incoming_count": 0,
                            "outgoing_count": 0,
                            "total_volume_nano": 0,
                            "first_interaction": timestamp,
                            "last_interaction": timestamp,
                            "token_transfers": set(),
                            "token_types": defaultdict(int),
                            "is_dex": False,
                            "is_smartcontract": False,
                            "is_p2p": False,
                            "is_recurring": False,
                            "name": None,
                            "type": None,
                            "related_addresses": set(),
                            "time_patterns": {
                                "timestamps": [],
                                "values": [],
                                "recurring_daily": False,
                                "recurring_weekly": False,
                                "recurring_monthly": False
                            },
                            "confidence_scores": {
                                "dex": 0.0,
                                "smartcontract": 0.0,
                                "p2p": 0.0,
                                "recurring": 0.0,
                                "related_entity": 0.0
                            }
                        }
                        
                        # Add known address info if available
                        if output_addr in known_addresses:
                            interactions[output_addr]["name"] = known_addresses[output_addr]["name"]
                            interactions[output_addr]["type"] = known_addresses[output_addr]["type"]
                        
                        # Add related addresses from clustering
                        if output_addr in address_clusters:
                            interactions[output_addr]["related_addresses"] = address_clusters[output_addr]
                    
                    # Update stats for this interaction
                    interactions[output_addr]["outgoing_count"] += 1
                    interactions[output_addr]["total_volume_nano"] += output_value
                    interactions[output_addr]["last_interaction"] = timestamp
                    
                    # Record timestamp and value for time pattern analysis
                    interactions[output_addr]["time_patterns"]["timestamps"].append(timestamp)
                    interactions[output_addr]["time_patterns"]["values"].append(output_value)
                    
                    # Track time patterns
                    day_key = tx_date.strftime('%Y-%m-%d')
                    week_key = tx_date.strftime('%Y-%W')
                    month_key = tx_date.strftime('%Y-%m')
                    
                    time_patterns["daily"][day_key].append((output_addr, output_value))
                    time_patterns["weekly"][week_key].append((output_addr, output_value))
                    time_patterns["monthly"][month_key].append((output_addr, output_value))
                    
                    # Update first interaction if this is earlier
                    if timestamp < interactions[output_addr]["first_interaction"]:
                        interactions[output_addr]["first_interaction"] = timestamp
                    
                    # Track tokens if any and analyze token types
                    for asset in out.get("assets", []):
                        token_id = asset.get("tokenId")
                        token_amount = asset.get("amount", 1)
                        
                        if token_id:
                            interactions[output_addr]["token_transfers"].add(token_id)
                            
                            # Token context analysis - identify token type
                            token_type = identify_token_type(token_id, token_amount)
                            interactions[output_addr]["token_types"][token_type] += 1
                            stats["token_type_counts"][token_type] += 1
                            
                            # Track token patterns for this address
                            token_patterns[output_addr][token_id] += 1
                    
                    # Update global stats
                    stats["total_outgoing"] += 1
                    stats["total_volume_nano"] += output_value
        
        # Analyze time patterns for recurring behavior detection
        for pattern_type in ["daily", "weekly", "monthly"]:
            for period, interactions_list in time_patterns[pattern_type].items():
                # Count occurrences of each address in this time period
                addr_counts = Counter([addr for addr, _ in interactions_list])
                
                # Addresses that appear regularly in this time pattern
                for addr, count in addr_counts.items():
                    if addr in interactions:
                        # If address appears multiple times in the same period, it might indicate a pattern
                        if count > 1:
                            if pattern_type == "daily":
                                interactions[addr]["time_patterns"]["recurring_daily"] = True
                            elif pattern_type == "weekly":
                                interactions[addr]["time_patterns"]["recurring_weekly"] = True
                            elif pattern_type == "monthly":
                                interactions[addr]["time_patterns"]["recurring_monthly"] = True
                                
                                # Mark as recurring when pattern is detected
                                if not interactions[addr]["is_recurring"]:
                                    interactions[addr]["is_recurring"] = True
        
        # Post-process the interaction data for categorical analysis
        processed_interactions = []
        for addr, data in interactions.items():
            # Calculate total interactions
            total_interactions = data["incoming_count"] + data["outgoing_count"]
            
            # Skip if below minimum threshold
            if total_interactions < min_interactions:
                continue
            
            # Fetch token names for all token IDs
            token_ids = list(data["token_transfers"])
            token_names = await asyncio.gather(*[get_token_name(token_id) for token_id in token_ids])
            
            # Format address for display
            formatted_address = format_id(addr)
            
            # Create a mapping of token IDs to names for the display
            token_transfers_with_names = []
            for i, token_id in enumerate(token_ids):
                token_name = token_names[i]
                # Check if token_name is the same as token_id, meaning no name was found
                if token_name == token_id:
                    display_name = f"Unknown Token ({format_id(token_id, 4, 4)})"
                else:
                    display_name = f"{token_name} ({format_id(token_id, 4, 4)})"
                    
                token_transfers_with_names.append({
                    "name": display_name,
                    "id": token_id
                })
            
            # Replace token_transfers with the enriched version
            data["token_transfers"] = token_transfers_with_names
            data["related_addresses"] = [format_id(addr) for addr in data["related_addresses"]]
            
            # Formatted address for display while keeping original for reference
            data["formatted_address"] = formatted_address
            
            # Convert defaultdict to regular dict for JSON serialization
            data["token_types"] = dict(data["token_types"])
            
            # Calculate time between interactions
            time_span = data["last_interaction"] - data["first_interaction"]
            avg_days_between = time_span / (86400 * 1000 * max(1, total_interactions - 1)) if total_interactions > 1 else 0
            data["avg_days_between_interactions"] = avg_days_between
            
            # Format timestamps
            data["first_interaction_date"] = datetime.fromtimestamp(data["first_interaction"]/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
            data["last_interaction_date"] = datetime.fromtimestamp(data["last_interaction"]/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Analyze time patterns of interactions
            timestamps = data["time_patterns"]["timestamps"]
            if len(timestamps) >= 3:
                # Check for regular intervals
                intervals = []
                for i in range(1, len(timestamps)):
                    intervals.append(timestamps[i] - timestamps[i-1])
                
                # Calculate the standard deviation of intervals as a percentage of the mean
                if intervals:
                    mean_interval = sum(intervals) / len(intervals)
                    if mean_interval > 0:
                        std_dev = math.sqrt(sum((x - mean_interval) ** 2 for x in intervals) / len(intervals))
                        consistency = 1.0 - min(1.0, std_dev / mean_interval)  # Higher is more consistent
                        
                        # Check if values are also consistent
                        values = data["time_patterns"]["values"]
                        if values:
                            mean_value = sum(values) / len(values)
                            if mean_value > 0:
                                value_std_dev = math.sqrt(sum((x - mean_value) ** 2 for x in values) / len(values))
                                value_consistency = 1.0 - min(1.0, value_std_dev / mean_value)
                                
                                # Combine time and value consistency
                                time_consistency_score = (consistency * 0.7) + (value_consistency * 0.3)
                                data["time_patterns"]["consistency_score"] = round(time_consistency_score, 2)
            
            # Convert volume to ERG
            data["total_volume_erg"] = data["total_volume_nano"] / 1_000_000_000
            
            # Apply categorization logic
            
            # 1. Check if it's a known DEX address (strict matching)
            if addr in known_dex_addresses:
                data["is_dex"] = True
                data["confidence_scores"]["dex"] = 1.0
                if not data["name"]:
                    data["name"] = known_dex_addresses[addr]
                if not data["type"]:
                    data["type"] = "DEX"
            
            # 2. Check address book info
            elif data["type"]:
                if "exchange" in data["type"].lower() or "dex" in data["type"].lower():
                    # Only set is_dex=True if it's exactly our known DEX address
                    data["confidence_scores"]["dex"] = 0.9
                    
                elif "contract" in data["type"].lower():
                    data["is_smartcontract"] = True
                    data["confidence_scores"]["smartcontract"] = 0.9
            
            # 3. Check if address was identified as a smart contract in our pre-analysis
            elif addr in smart_contract_addresses:
                data["is_smartcontract"] = True
                data["confidence_scores"]["smartcontract"] = 0.85
                if not data["type"]:
                    data["type"] = "Smart Contract"
            
            # 4. Apply heuristics only if not already categorized
            else:
                # Calculate confidence scores based on various metrics
                
                # Token context analysis to improve classification
                nft_count = data["token_types"].get(TOKEN_TYPES["NFT"], 0)
                utility_count = data["token_types"].get(TOKEN_TYPES["UTILITY"], 0)
                stablecoin_count = data["token_types"].get(TOKEN_TYPES["STABLECOIN"], 0)
                
                # DEX score (combination of interaction frequency, token variety and token types)
                token_variety = len(data["token_transfers"])
                interaction_score = min(1.0, total_interactions / 20)  # Max out at 20 interactions
                token_score = min(1.0, token_variety / 15)  # Max out at 15 token types
                
                # Adjust based on token types - DEXes typically handle varied tokens
                token_type_bonus = 0
                if utility_count > 0 and stablecoin_count > 0:
                    token_type_bonus = 0.2  # Handling both utility tokens and stablecoins is typical for DEXes
                
                # NFT-focused addresses might be marketplaces, but are less likely typical crypto DEXes
                if nft_count > 3 * (utility_count + stablecoin_count) and nft_count > 5:
                    token_type_bonus = -0.1  # Slightly reduce if predominantly NFT-focused
                
                dex_confidence = (interaction_score * 0.5) + (token_score * 0.3) + token_type_bonus
                data["confidence_scores"]["dex"] = round(min(1.0, max(0.0, dex_confidence)), 2)
                
                # No longer automatically setting is_dex based on confidence
                # Instead, only the specific DEX address will be marked as DEX
                
                # Smart Contract score with token context
                if data["incoming_count"] > 0 and data["outgoing_count"] == 0:
                    # Only receives, never sends - likely a smart contract
                    sc_confidence = min(1.0, data["incoming_count"] / 10)
                    
                    # Smart contracts often handle specific token types consistently
                    if token_variety == 1 and total_interactions > 3:
                        sc_confidence += 0.1  # Single token focus suggests contract
                    
                    data["confidence_scores"]["smartcontract"] = round(min(1.0, sc_confidence), 2)
                
                    if sc_confidence > 0.5:
                        data["is_smartcontract"] = True
                        
                elif data["outgoing_count"] > 0 and data["incoming_count"] == 0:
                    # Only sends, never receives - could be a contract or source
                    sc_confidence = min(1.0, data["outgoing_count"] / 10)
                    data["confidence_scores"]["smartcontract"] = round(sc_confidence, 2)
                    
                    if sc_confidence > 0.5:
                        data["is_smartcontract"] = True
                
                # P2P detection: Improved heuristic for peer-to-peer transactions
                # P2P typically involves:
                # 1. One-off or low-frequency interactions (not recurring)
                # 2. Simple transaction structure (not a contract) 
                # 3. Direct person-to-person transfers
                
                # Only consider as P2P if not already classified as DEX or smart contract
                if not data["is_dex"] and not data["is_smartcontract"] and not data["is_recurring"]:
                    # Low interaction count suggests P2P
                    p2p_base_score = 0.5 if total_interactions < 5 else (0.3 if total_interactions < 10 else 0.1)
                    
                    # Examine transaction patterns
                    # Simple ERG transfers without complex token interactions
                    simple_tx_pattern = token_variety <= 2  # Few token types involved
                    if simple_tx_pattern:
                        p2p_base_score += 0.3
                    
                    # Balance ratio is still useful - P2P often has some back-and-forth
                    balance_ratio = 1.0 - (abs(data["incoming_count"] - data["outgoing_count"]) / max(1, total_interactions))
                    # But pure one-way transactions can also be P2P
                    one_way_bonus = 0.2 if (data["incoming_count"] == 0 or data["outgoing_count"] == 0) else 0
                    
                    p2p_confidence = p2p_base_score + (balance_ratio * 0.2) + one_way_bonus
                    data["confidence_scores"]["p2p"] = round(p2p_confidence, 2)
                    
                    if p2p_confidence > 0.6:
                        data["is_p2p"] = True
                
                # Enhanced recurring score based on time window analysis
                recurring_confidence = 0.0
                
                # Incorporate time pattern consistency
                if "consistency_score" in data["time_patterns"]:
                    time_consistency = data["time_patterns"]["consistency_score"] 
                    recurring_base = time_consistency * min(1.0, total_interactions / 5)
                    
                    # Boost if we detected specific time patterns
                    pattern_boost = 0.0
                    if data["time_patterns"]["recurring_daily"]:
                        pattern_boost += 0.3
                    if data["time_patterns"]["recurring_weekly"]:
                        pattern_boost += 0.2
                    if data["time_patterns"]["recurring_monthly"]:
                        pattern_boost += 0.1
                    
                    recurring_confidence = min(1.0, recurring_base + pattern_boost)
                    data["confidence_scores"]["recurring"] = round(recurring_confidence, 2)
                    
                    if recurring_confidence > 0.6:
                        data["is_recurring"] = True
                
                # Address clustering score - related entity detection
                if data["related_addresses"]:
                    cluster_size = len(data["related_addresses"])
                    # Addresses with many relations are more likely part of the same entity
                    cluster_score = min(1.0, cluster_size / 5)  # Max out at 5 related addresses
                    data["confidence_scores"]["related_entity"] = round(cluster_score, 2)
            
            # Create a condensed version if verbose is False
            if not verbose:
                condensed_data = {
                    "address": data["address"],
                    "interaction_count": data["incoming_count"] + data["outgoing_count"],
                    "incoming_count": data["incoming_count"],
                    "outgoing_count": data["outgoing_count"],
                    "total_volume_erg": data["total_volume_nano"] / 1_000_000_000,
                    "first_seen": data["first_interaction_date"],
                    "last_seen": data["last_interaction_date"],
                    "token_count": len(data["token_transfers"]),
                    "classifications": {
                        "is_dex": data["is_dex"],
                        "is_smartcontract": data["is_smartcontract"],
                        "is_p2p": data["is_p2p"],
                        "is_recurring": data["is_recurring"]
                    },
                    "confidence_scores": data["confidence_scores"]
                }
                
                # Include name and type if available
                if data["name"]:
                    condensed_data["name"] = data["name"]
                if data["type"]:
                    condensed_data["type"] = data["type"]
                
                processed_interactions.append(condensed_data)
            else:
                processed_interactions.append(data)
        
        # Sort by total interactions (descending)
        processed_interactions.sort(key=lambda x: x["incoming_count"] + x["outgoing_count"], reverse=True)
        
        # Finalize stats
        stats["unique_addresses"] = len(interactions)
        stats["total_volume_erg"] = stats["total_volume_nano"] / 1_000_000_000
        stats["first_tx_date"] = datetime.fromtimestamp(stats["first_tx_timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S UTC') if stats["first_tx_timestamp"] else None
        stats["last_tx_date"] = datetime.fromtimestamp(stats["last_tx_timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S UTC') if stats["last_tx_timestamp"] else None
        
        # Convert defaultdicts to regular dicts for JSON serialization
        stats["token_type_counts"] = dict(stats["token_type_counts"])
        stats["time_of_day_activity"] = dict(stats["time_of_day_activity"])
        stats["day_of_week_activity"] = dict(stats["day_of_week_activity"])
        
        # Address clustering summary
        address_cluster_stats = {
            "total_clusters": len(address_clusters),
            "largest_cluster_size": max([len(cluster) for cluster in address_clusters.values()]) if address_clusters else 0,
            "avg_cluster_size": sum([len(cluster) for cluster in address_clusters.values()]) / len(address_clusters) if address_clusters else 0
        }
        
        # Format the return data structure
        result = {
            "address": address,
            "common_interactions": processed_interactions,
            "total_interactions_found": len(processed_interactions),
            "statistics": stats,
            "address_clustering": address_cluster_stats
        }
        
        # For non-verbose mode, simplify statistics too
        if not verbose:
            condensed_stats = {
                "total_transactions": stats["total_transactions_analyzed"],
                "unique_addresses": stats["unique_addresses"],
                "total_volume_erg": stats["total_volume_erg"],
                "first_tx_date": stats["first_tx_date"],
                "last_tx_date": stats["last_tx_date"],
                "token_type_summary": stats["token_type_counts"]
            }
            result["statistics"] = condensed_stats
            
            # Remove address clustering in non-verbose mode
            if "address_clustering" in result:
                del result["address_clustering"]
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing interactions for {address}: {str(e)}")
        raise Exception(f"Error analyzing address interactions: {str(e)}") 