"""
Address utility functions with standardized response formatting.

This module provides functions for retrieving information about Ergo blockchain
addresses including balance and transaction history using standardized response formats.
"""

import logging
import requests
from typing import Dict, Any, List, Optional

from ergo_explorer.util.standardize import standardize_response

logger = logging.getLogger(__name__)

# Constants
EXPLORER_API_URL = "https://api.ergoplatform.com/api/v1"


def get_address_balance(address: str) -> str:
    """
    Get the confirmed balance for an Ergo address.

    Args:
        address: The Ergo blockchain address to query

    Returns:
        Markdown-formatted string with address balance details
    """
    logger.info(f"Retrieving balance for address: {address}")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/balance/confirmed")
        response.raise_for_status()
        
        balance_data = response.json()
        
        # Extract and format ERG balance
        nanoerg_balance = balance_data.get('nanoErgs', 0)
        erg_balance = nanoerg_balance / 1000000000  # Convert nanoErgs to ERGs
        
        # Format the response as markdown
        markdown = f"# Balance for address: {address}\n\n"
        markdown += f"**ERG Balance:** {erg_balance:,.9f}\n"
        
        # Add token balances if present
        tokens = balance_data.get('tokens', [])
        if tokens:
            markdown += "\n## Token Balances\n\n"
            for token in tokens:
                token_id = token.get('tokenId', 'Unknown')
                token_name = token.get('name', 'Unknown Token')
                token_amount = token.get('amount', 0)
                decimals = token.get('decimals', 0)
                
                formatted_amount = token_amount / (10 ** decimals) if decimals > 0 else token_amount
                markdown += f"- **{token_name}**: {formatted_amount:,}\n"
                markdown += f"  - ID: `{token_id}`\n"
        else:
            markdown += "\n*No tokens found for this address*\n"
        
        return markdown
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving balance for address {address}: {str(e)}")
        return f"Error retrieving address balance: {str(e)}"


@standardize_response
def get_address_balance_json(address: str) -> Dict[str, Any]:
    """
    Get the confirmed balance for an Ergo address in standardized JSON format.

    Args:
        address: The Ergo blockchain address to query

    Returns:
        Standardized JSON response with address balance details
    """
    logger.info(f"Retrieving JSON balance for address: {address}")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/balance/confirmed")
        response.raise_for_status()
        
        balance_data = response.json()
        
        # Extract ERG balance
        nanoerg_balance = balance_data.get('nanoErgs', 0)
        erg_balance = nanoerg_balance / 1000000000  # Convert nanoErgs to ERGs
        
        # Format token data
        tokens = []
        for token in balance_data.get('tokens', []):
            token_id = token.get('tokenId', 'Unknown')
            token_name = token.get('name', 'Unknown Token')
            token_amount = token.get('amount', 0)
            decimals = token.get('decimals', 0)
            
            formatted_amount = token_amount / (10 ** decimals) if decimals > 0 else token_amount
            
            tokens.append({
                "id": token_id,
                "name": token_name,
                "amount": {
                    "raw": token_amount,
                    "formatted": formatted_amount
                },
                "decimals": decimals
            })
        
        # Return structured data
        # The decorator will handle standardization
        return {
            "address": address,
            "balance": {
                "erg": {
                    "raw": nanoerg_balance,
                    "formatted": erg_balance
                }
            },
            "tokens": tokens,
            "token_count": len(tokens)
        }
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving balance for address {address}: {str(e)}")
        raise ValueError(f"Error retrieving address balance: {str(e)}")


def get_transaction_history(address: str, limit: int = 20) -> str:
    """
    Get transaction history for an Ergo address.

    Args:
        address: The Ergo blockchain address to query
        limit: Maximum number of transactions to return

    Returns:
        Markdown-formatted string with transaction history
    """
    logger.info(f"Retrieving transaction history for address: {address} (limit: {limit})")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/transactions?limit={limit}")
        response.raise_for_status()
        
        transactions = response.json().get('items', [])
        
        if not transactions:
            return f"No transactions found for address {address}."
        
        # Format the response as markdown
        markdown = f"# Transaction History for {address}\n\n"
        markdown += f"*Showing the most recent {min(limit, len(transactions))} transactions*\n\n"
        
        for tx in transactions:
            tx_id = tx.get('id', 'Unknown')
            timestamp = tx.get('timestamp', 0)
            
            # Calculate value change for the address
            value_change = 0
            for input_box in tx.get('inputs', []):
                if address in input_box.get('address', ''):
                    value_change -= input_box.get('value', 0)
            
            for output_box in tx.get('outputs', []):
                if address in output_box.get('address', ''):
                    value_change += output_box.get('value', 0)
            
            # Format as ERG
            erg_change = value_change / 1000000000
            
            # Determine transaction type
            tx_type = "Received" if erg_change > 0 else "Sent" if erg_change < 0 else "Self-transfer"
            
            markdown += f"## Transaction {tx_id[:8]}...\n"
            markdown += f"**Type:** {tx_type}\n"
            markdown += f"**Value Change:** {erg_change:+,.9f} ERG\n"
            markdown += f"**Date:** {timestamp}\n"
            markdown += f"**Full ID:** `{tx_id}`\n\n"
            markdown += "---\n\n"
        
        return markdown
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving transaction history for address {address}: {str(e)}")
        return f"Error retrieving transaction history: {str(e)}"


@standardize_response
def get_transaction_history_json(address: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get transaction history for an Ergo address in standardized JSON format.

    Args:
        address: The Ergo blockchain address to query
        limit: Maximum number of transactions to return

    Returns:
        Standardized JSON response with transaction history
    """
    logger.info(f"Retrieving JSON transaction history for address: {address} (limit: {limit})")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/transactions?limit={limit}")
        response.raise_for_status()
        
        transactions_data = response.json()
        transactions = transactions_data.get('items', [])
        
        # Process transactions
        processed_txs = []
        for tx in transactions:
            tx_id = tx.get('id', 'Unknown')
            timestamp = tx.get('timestamp', 0)
            
            # Calculate value change for the address
            value_change = 0
            for input_box in tx.get('inputs', []):
                if address in input_box.get('address', ''):
                    value_change -= input_box.get('value', 0)
            
            for output_box in tx.get('outputs', []):
                if address in output_box.get('address', ''):
                    value_change += output_box.get('value', 0)
            
            # Format as ERG
            erg_change = value_change / 1000000000
            
            # Determine transaction type
            tx_type = "received" if erg_change > 0 else "sent" if erg_change < 0 else "self"
            
            processed_txs.append({
                "id": tx_id,
                "timestamp": timestamp,
                "type": tx_type,
                "value_change": {
                    "nanoerg": value_change,
                    "erg": erg_change
                },
                "confirmations": tx.get('confirmationsCount', 0)
            })
        
        # Return structured data
        # The decorator will handle standardization
        return {
            "address": address,
            "transactions": processed_txs,
            "total_count": transactions_data.get('total', 0),
            "returned_count": len(processed_txs)
        }
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving transaction history for address {address}: {str(e)}")
        raise ValueError(f"Error retrieving transaction history: {str(e)}") 