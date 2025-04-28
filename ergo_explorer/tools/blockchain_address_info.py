"""
Comprehensive blockchain address information utility.

This module provides functions for retrieving detailed information about
Ergo blockchain addresses including balance, transaction history, and
associated tokens with standardized response formats.
"""

import logging
import requests
from typing import Dict, Any, List, Optional, Union

from ergo_explorer.util.standardize import standardize_response

logger = logging.getLogger(__name__)

# Constants
EXPLORER_API_URL = "https://api.ergoplatform.com/api/v1"


@standardize_response
def blockchain_address_info(
    address: str, 
    include_transactions: bool = True,
    tx_limit: int = 10
) -> Dict[str, Any]:
    """
    Get comprehensive address information including balance, tokens, and recent transactions.
    
    Args:
        address: Ergo blockchain address to analyze
        include_transactions: Whether to include transaction history
        tx_limit: Maximum number of transactions to include in the response
        
    Returns:
        Standardized JSON response with comprehensive address information
    """
    logger.info(f"Retrieving comprehensive info for address: {address}")
    
    try:
        # Get address balance
        balance_response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/balance/confirmed")
        balance_response.raise_for_status()
        balance_data = balance_response.json()
        
        # Get address transactions if requested
        transactions = []
        total_tx_count = 0
        if include_transactions:
            tx_response = requests.get(f"{EXPLORER_API_URL}/addresses/{address}/transactions?limit={tx_limit}")
            tx_response.raise_for_status()
            tx_data = tx_response.json()
            transactions = tx_data.get('items', [])
            total_tx_count = tx_data.get('total', 0)
        
        # Process balance information
        nanoerg_balance = balance_data.get('nanoErgs', 0)
        erg_balance = nanoerg_balance / 1000000000  # Convert nanoErgs to ERGs
        
        # Process token information
        tokens = []
        for token in balance_data.get('tokens', []):
            token_id = token.get('tokenId', 'Unknown')
            token_name = token.get('name', 'Unknown Token')
            token_amount = token.get('amount', 0)
            decimals = token.get('decimals', 0)
            
            formatted_amount = token_amount / (10 ** decimals) if decimals > 0 else token_amount
            
            # Get additional token information
            try:
                token_response = requests.get(f"{EXPLORER_API_URL}/tokens/{token_id}")
                if token_response.status_code == 200:
                    token_details = token_response.json()
                    tokens.append({
                        "id": token_id,
                        "name": token_name,
                        "amount": {
                            "raw": token_amount,
                            "formatted": formatted_amount
                        },
                        "decimals": decimals,
                        "description": token_details.get('description', ''),
                        "type": token_details.get('type', 'Unknown'),
                        "is_nft": token_details.get('type') == 'EIP-004'
                    })
                else:
                    tokens.append({
                        "id": token_id,
                        "name": token_name,
                        "amount": {
                            "raw": token_amount,
                            "formatted": formatted_amount
                        },
                        "decimals": decimals
                    })
            except requests.RequestException:
                # Fall back to basic token info if detailed lookup fails
                tokens.append({
                    "id": token_id,
                    "name": token_name,
                    "amount": {
                        "raw": token_amount,
                        "formatted": formatted_amount
                    },
                    "decimals": decimals
                })
        
        # Process transaction history if requested
        processed_txs = []
        if include_transactions:
            for tx in transactions:
                tx_id = tx.get('id', 'Unknown')
                timestamp = tx.get('timestamp', 0)
                
                # Calculate value change for the address
                value_change = 0
                
                # Track tokens involved in the transaction
                tx_tokens = {}
                
                # Process inputs
                for input_box in tx.get('inputs', []):
                    if address in input_box.get('address', ''):
                        value_change -= input_box.get('value', 0)
                        
                        # Track tokens being sent
                        for asset in input_box.get('assets', []):
                            token_id = asset.get('tokenId', '')
                            amount = asset.get('amount', 0)
                            
                            if token_id in tx_tokens:
                                tx_tokens[token_id]['change'] -= amount
                            else:
                                tx_tokens[token_id] = {
                                    'id': token_id,
                                    'name': asset.get('name', 'Unknown Token'),
                                    'change': -amount
                                }
                
                # Process outputs
                for output_box in tx.get('outputs', []):
                    if address in output_box.get('address', ''):
                        value_change += output_box.get('value', 0)
                        
                        # Track tokens being received
                        for asset in output_box.get('assets', []):
                            token_id = asset.get('tokenId', '')
                            amount = asset.get('amount', 0)
                            
                            if token_id in tx_tokens:
                                tx_tokens[token_id]['change'] += amount
                            else:
                                tx_tokens[token_id] = {
                                    'id': token_id,
                                    'name': asset.get('name', 'Unknown Token'),
                                    'change': amount
                                }
                
                # Format as ERG
                erg_change = value_change / 1000000000
                
                # Determine transaction type
                tx_type = "received" if erg_change > 0 else "sent" if erg_change < 0 else "self"
                
                # Convert token dict to list and filter out zero-change tokens
                token_list = [t for t in tx_tokens.values() if t['change'] != 0]
                
                processed_txs.append({
                    "id": tx_id,
                    "timestamp": timestamp,
                    "type": tx_type,
                    "value_change": {
                        "nanoerg": value_change,
                        "erg": erg_change
                    },
                    "confirmations": tx.get('confirmationsCount', 0),
                    "tokens": token_list,
                    "size": tx.get('size', 0)
                })
        
        # Return structured data with all components
        # The decorator will handle standardization
        result = {
            "address": address,
            "balance": {
                "erg": {
                    "raw": nanoerg_balance,
                    "formatted": erg_balance
                }
            },
            "tokens": tokens,
            "token_count": len(tokens),
            "transaction_summary": {
                "total_count": total_tx_count
            }
        }
        
        # Only include transactions if requested
        if include_transactions:
            result["transactions"] = processed_txs
            result["transaction_summary"]["returned_count"] = len(processed_txs)
        
        return result
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving info for address {address}: {str(e)}")
        raise ValueError(f"Error retrieving address information: {str(e)}")


def blockchain_address_info_markdown(
    address: str,
    include_transactions: bool = True,
    tx_limit: int = 10
) -> str:
    """
    Get comprehensive address information formatted as markdown.
    
    Args:
        address: Ergo blockchain address to analyze
        include_transactions: Whether to include transaction history
        tx_limit: Maximum number of transactions to include in the response
        
    Returns:
        Markdown-formatted string with comprehensive address information
    """
    try:
        # Get the data using the JSON function first
        data = blockchain_address_info(
            address=address,
            include_transactions=include_transactions,
            tx_limit=tx_limit
        )
        
        # Check if we have a standardized response with 'result' key
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        
        # Now format as markdown
        markdown = f"# Address Information: {address}\n\n"
        
        # Balance section
        erg_balance = data.get('balance', {}).get('erg', {}).get('formatted', 0)
        markdown += f"## Balance\n\n"
        markdown += f"**ERG Balance:** {erg_balance:,.9f}\n\n"
        
        # Tokens section
        tokens = data.get('tokens', [])
        if tokens:
            markdown += f"## Tokens ({len(tokens)})\n\n"
            for token in tokens:
                token_name = token.get('name', 'Unknown Token')
                token_id = token.get('id', 'Unknown')
                amount = token.get('amount', {}).get('formatted', 0)
                
                markdown += f"### {token_name}\n\n"
                markdown += f"- **Amount:** {amount:,}\n"
                markdown += f"- **ID:** `{token_id}`\n"
                
                # Add optional token details if available
                if 'description' in token and token['description']:
                    markdown += f"- **Description:** {token['description']}\n"
                
                if 'type' in token:
                    markdown += f"- **Type:** {token['type']}\n"
                
                if 'is_nft' in token and token['is_nft']:
                    markdown += f"- **NFT:** Yes\n"
                
                markdown += "\n"
        else:
            markdown += "## Tokens\n\n*No tokens found for this address*\n\n"
        
        # Transaction history section
        if include_transactions:
            transactions = data.get('transactions', [])
            total_count = data.get('transaction_summary', {}).get('total_count', 0)
            
            markdown += f"## Transaction History\n\n"
            markdown += f"*Showing {len(transactions)} of {total_count} total transactions*\n\n"
            
            if transactions:
                for tx in transactions:
                    tx_id = tx.get('id', 'Unknown')
                    timestamp = tx.get('timestamp', 0)
                    tx_type = tx.get('type', 'unknown').capitalize()
                    erg_change = tx.get('value_change', {}).get('erg', 0)
                    
                    markdown += f"### Transaction {tx_id[:8]}...\n\n"
                    markdown += f"- **Type:** {tx_type}\n"
                    markdown += f"- **Value Change:** {erg_change:+,.9f} ERG\n"
                    markdown += f"- **Date:** {timestamp}\n"
                    markdown += f"- **Confirmations:** {tx.get('confirmations', 0)}\n"
                    markdown += f"- **Full ID:** `{tx_id}`\n"
                    
                    # Add token transfers if any
                    tx_tokens = tx.get('tokens', [])
                    if tx_tokens:
                        markdown += "\n**Token Transfers:**\n\n"
                        for token in tx_tokens:
                            token_name = token.get('name', 'Unknown Token')
                            token_change = token.get('change', 0)
                            change_sign = "+" if token_change > 0 else ""
                            
                            markdown += f"- {token_name}: {change_sign}{token_change:,}\n"
                    
                    markdown += "\n---\n\n"
            else:
                markdown += "*No transactions found*\n\n"
        
        return markdown
        
    except Exception as e:
        return f"Error generating markdown for address {address}: {str(e)}" 