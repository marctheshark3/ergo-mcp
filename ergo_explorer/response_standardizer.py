"""
Response standardization utilities for the Ergo Explorer MCP.

This module provides utilities to standardize response formats across endpoints.
It helps convert existing markdown-formatted responses to structured JSON data.
"""

import re
import json
import logging
from typing import Dict, List, Any, Union, Optional, Tuple

logger = logging.getLogger(__name__)

def parse_balance_string(balance_text: str) -> Dict[str, Any]:
    """
    Parse a balance string in markdown format to structured data.
    
    Args:
        balance_text: The markdown-formatted balance string
        
    Returns:
        Dictionary with structured balance data
    """
    try:
        # Extract address
        address_match = re.search(r"Balance for ([A-Za-z0-9]+):", balance_text)
        address = address_match.group(1) if address_match else "Unknown"
        
        # Extract ERG balance
        erg_match = re.search(r"• ([0-9.]+) ERG", balance_text)
        erg_amount = float(erg_match.group(1)) if erg_match else 0.0
        nano_ergs = int(erg_amount * 1_000_000_000)
        
        # Extract tokens
        tokens = []
        token_matches = re.finditer(r"• ([0-9.,]+) ([^(]+) \(ID: ([A-Za-z0-9]+)...\)", balance_text)
        
        for match in token_matches:
            amount_str = match.group(1).replace(",", "")
            amount = float(amount_str)
            name = match.group(2).strip()
            token_id = match.group(3) + "..."  # Partial ID
            
            tokens.append({
                "name": name,
                "amount": amount,
                "id": token_id
            })
        
        return {
            "address": address,
            "balance": {
                "nanoErgs": nano_ergs,
                "erg": erg_amount
            },
            "tokens": tokens,
            "token_count": len(tokens)
        }
    except Exception as e:
        logger.error(f"Error parsing balance string: {str(e)}")
        return {
            "error": f"Error parsing balance data: {str(e)}",
            "original_text": balance_text
        }

def parse_transaction_string(tx_text: str) -> Dict[str, Any]:
    """
    Parse a transaction string in markdown format to structured data.
    
    Args:
        tx_text: The markdown-formatted transaction string
        
    Returns:
        Dictionary with structured transaction data
    """
    try:
        # Extract transaction ID
        tx_id_match = re.search(r"Transaction Details for ([A-Za-z0-9]+):", tx_text)
        tx_id = tx_id_match.group(1) if tx_id_match else "Unknown"
        
        # Extract size
        size_match = re.search(r"• Size: ([0-9,]+) bytes", tx_text)
        size = int(size_match.group(1).replace(",", "")) if size_match else 0
        
        # Extract input/output counts
        inputs_match = re.search(r"• Inputs: ([0-9,]+)", tx_text)
        inputs_count = int(inputs_match.group(1).replace(",", "")) if inputs_match else 0
        
        outputs_match = re.search(r"• Outputs: ([0-9,]+)", tx_text)
        outputs_count = int(outputs_match.group(1).replace(",", "")) if outputs_match else 0
        
        # Extract inputs
        inputs = []
        input_matches = re.finditer(r"(\d+)\. Box ID: ([A-Za-z0-9]+)\n\s+Value: ([0-9.]+) ERG", tx_text)
        
        for match in input_matches:
            box_id = match.group(2)
            value = float(match.group(3))
            
            inputs.append({
                "boxId": box_id,
                "value": int(value * 1_000_000_000)  # Convert to nanoERGs
            })
        
        # Extract outputs
        outputs = []
        output_sections = re.split(r"\d+\. Box ID:", tx_text)[1:]  # Split by output number
        
        for section in output_sections:
            box_match = re.search(r"([A-Za-z0-9]+)\n\s+Address: ([A-Za-z0-9]+)\n\s+Value: ([0-9.]+) ERG", section)
            if not box_match:
                continue
                
            box_id = box_match.group(1)
            address = box_match.group(2)
            value = float(box_match.group(3))
            
            # Extract tokens for this output
            tokens = []
            token_matches = re.finditer(r"- ([A-Za-z0-9]+): ([0-9,]+)", section)
            
            for token_match in token_matches:
                token_id = token_match.group(1)
                amount = int(token_match.group(2).replace(",", ""))
                
                tokens.append({
                    "tokenId": token_id,
                    "amount": amount
                })
            
            outputs.append({
                "boxId": box_id,
                "address": address,
                "value": int(value * 1_000_000_000),  # Convert to nanoERGs
                "assets": tokens
            })
        
        return {
            "id": tx_id,
            "size": size,
            "inputsCount": inputs_count,
            "outputsCount": outputs_count,
            "inputs": inputs,
            "outputs": outputs
        }
    except Exception as e:
        logger.error(f"Error parsing transaction string: {str(e)}")
        return {
            "error": f"Error parsing transaction data: {str(e)}",
            "original_text": tx_text
        }

def parse_box_string(box_text: str) -> Dict[str, Any]:
    """
    Parse a box string in markdown format to structured data.
    
    Args:
        box_text: The markdown-formatted box string
        
    Returns:
        Dictionary with structured box data
    """
    try:
        # Extract box ID
        box_id_match = re.search(r"Box Details for ([A-Za-z0-9]+):", box_text)
        box_id = box_id_match.group(1) if box_id_match else "Unknown"
        
        # Extract value
        value_match = re.search(r"• Value: ([0-9.]+) ERG", box_text)
        value = float(value_match.group(1)) if value_match else 0.0
        
        # Extract creation height
        height_match = re.search(r"• Creation Height: ([0-9,]+)", box_text)
        creation_height = int(height_match.group(1).replace(",", "")) if height_match else 0
        
        # Extract ErgoTree
        tree_match = re.search(r"• ErgoTree: ([A-Za-z0-9]+)", box_text)
        ergo_tree = tree_match.group(1) if tree_match else ""
        
        # Extract tokens
        tokens = []
        token_matches = re.finditer(r"• ([A-Za-z0-9]+): ([0-9,]+)", box_text)
        
        for match in token_matches:
            token_id = match.group(1)
            amount = int(match.group(2).replace(",", ""))
            
            tokens.append({
                "tokenId": token_id,
                "amount": amount
            })
        
        return {
            "id": box_id,
            "value": int(value * 1_000_000_000),  # Convert to nanoERGs
            "formattedValue": value,
            "creationHeight": creation_height,
            "ergoTree": ergo_tree,
            "assets": tokens
        }
    except Exception as e:
        logger.error(f"Error parsing box string: {str(e)}")
        return {
            "error": f"Error parsing box data: {str(e)}",
            "original_text": box_text
        }

def parse_token_string(token_text: str) -> Dict[str, Any]:
    """
    Parse a token description string in markdown format to structured data.
    
    Args:
        token_text: The markdown-formatted token string
        
    Returns:
        Dictionary with structured token data
    """
    try:
        # Check for error messages
        if "Error" in token_text:
            return {
                "error": token_text,
                "id": None,
                "name": None
            }
        
        # Extract token name and ticker
        name_match = re.search(r"### ([^(]+) \(([^)]+)\)", token_text)
        name = name_match.group(1).strip() if name_match else "Unknown"
        ticker = name_match.group(2) if name_match else ""
        
        # Extract token ID
        id_match = re.search(r"- \*\*Token ID\*\*: ([A-Za-z0-9]+)", token_text)
        token_id = id_match.group(1) if id_match else "Unknown"
        
        # Extract price information
        price_erg_match = re.search(r"- \*\*Price in ERG\*\*: ([0-9.]+) ERG", token_text)
        price_erg = float(price_erg_match.group(1)) if price_erg_match else 0.0
        
        price_usd_match = re.search(r"- \*\*Price in USD\*\*: \$([0-9.]+)", token_text)
        price_usd = float(price_usd_match.group(1)) if price_usd_match else 0.0
        
        # Extract liquidity information
        liquidity_erg_match = re.search(r"- \*\*ERG in Pool\*\*: ([0-9,.]+) ERG", token_text)
        liquidity_erg = float(liquidity_erg_match.group(1).replace(",", "")) if liquidity_erg_match else 0.0
        
        liquidity_token_match = re.search(r"- \*\*Tokens in Pool\*\*: ([0-9,.]+)", token_text)
        liquidity_token = float(liquidity_token_match.group(1).replace(",", "")) if liquidity_token_match else 0.0
        
        return {
            "id": token_id,
            "name": name,
            "ticker": ticker,
            "price": {
                "erg": price_erg,
                "usd": price_usd
            },
            "liquidity": {
                "erg": liquidity_erg,
                "token": liquidity_token
            }
        }
    except Exception as e:
        logger.error(f"Error parsing token string: {str(e)}")
        return {
            "error": f"Error parsing token data: {str(e)}",
            "original_text": token_text
        }

def parse_eip_string(eip_text: str) -> Dict[str, Any]:
    """
    Parse EIP information in markdown format to structured data.
    
    Args:
        eip_text: The markdown-formatted EIP string
        
    Returns:
        Dictionary with structured EIP data or list of EIPs
    """
    try:
        # Check if this is a list of EIPs or a single EIP
        if "# Ergo Improvement Proposals (EIPs)" in eip_text:
            # This is a list of EIPs
            eips = []
            eip_matches = re.finditer(r"## EIP-(\d+): ([^\n]+)\nStatus: ([^\n]+)", eip_text)
            
            for match in eip_matches:
                eip_number = int(match.group(1))
                title = match.group(2).strip()
                status = match.group(3).strip()
                
                eips.append({
                    "number": eip_number,
                    "title": title,
                    "status": status
                })
            
            return {
                "eips": eips,
                "count": len(eips)
            }
        else:
            # This is a single EIP
            # Extract EIP number and title
            title_match = re.search(r"<h1>([^<]+)</h1>", eip_text)
            title = title_match.group(1).strip() if title_match else "Unknown Title"
            
            # Extract author
            author_match = re.search(r"<li>Author: ([^<]+)</li>", eip_text)
            author = author_match.group(1).strip() if author_match else "Unknown"
            
            # Extract status
            status_match = re.search(r"<li>Status: ([^<]+)</li>", eip_text)
            status = status_match.group(1).strip() if status_match else "Unknown"
            
            # Extract creation date
            created_match = re.search(r"<li>Created: ([^<]+)</li>", eip_text)
            created = created_match.group(1).strip() if created_match else "Unknown"
            
            # Extract implementation info
            implemented_match = re.search(r"<li>Implemented: ([^<]+)</li>", eip_text)
            implemented = implemented_match.group(1).strip() if implemented_match else "Not implemented"
            
            # Extract content sections
            sections = {}
            section_matches = re.finditer(r"<h2>([^<]+)</h2>\n<p>([^<]+)</p>", eip_text)
            
            for match in section_matches:
                section_name = match.group(1).strip()
                section_content = match.group(2).strip()
                sections[section_name] = section_content
            
            return {
                "title": title,
                "author": author,
                "status": status,
                "created": created,
                "implemented": implemented,
                "sections": sections
            }
    except Exception as e:
        logger.error(f"Error parsing EIP string: {str(e)}")
        return {
            "error": f"Error parsing EIP data: {str(e)}",
            "original_text": eip_text
        }

def convert_markdown_to_json(text: str, data_type: str) -> Dict[str, Any]:
    """
    Convert a markdown-formatted string to structured JSON based on data type.
    
    Args:
        text: The markdown text to convert
        data_type: The type of data ("balance", "transaction", "box", "token", "eip")
        
    Returns:
        Dictionary with structured data
    """
    if data_type == "balance":
        return parse_balance_string(text)
    elif data_type == "transaction":
        return parse_transaction_string(text)
    elif data_type == "box":
        return parse_box_string(text)
    elif data_type == "token":
        return parse_token_string(text)
    elif data_type == "eip":
        return parse_eip_string(text)
    else:
        return {
            "error": f"Unknown data type: {data_type}",
            "original_text": text
        }

def standardize_response(response: Any, response_format: str = "markdown") -> Union[str, Dict[str, Any]]:
    """
    Standardize a response based on the requested format.
    
    Args:
        response: The response data to standardize
        response_format: The desired format ("markdown" or "json")
        
    Returns:
        Formatted response in the requested format
    """
    # If response is already a string and format is markdown, return as is
    if isinstance(response, str) and response_format.lower() == "markdown":
        return response
    
    # If response is a dict and format is json, return as is
    if isinstance(response, dict) and response_format.lower() == "json":
        return response
    
    # If response is a string and format is json, attempt to convert
    if isinstance(response, str) and response_format.lower() == "json":
        # Determine the type of data in the string
        if "Balance for" in response:
            return parse_balance_string(response)
        elif "Transaction Details for" in response:
            return parse_transaction_string(response)
        elif "Box Details for" in response:
            return parse_box_string(response)
        elif "### " in response and "Token ID" in response:
            return parse_token_string(response)
        elif "Ergo Improvement Proposals" in response or "<h1>" in response:
            return parse_eip_string(response)
        else:
            # Return a basic conversion
            return {
                "message": response,
                "format": "plain_text"
            }
    
    # For any other case, return the original response
    logger.warning(f"Could not standardize response to format: {response_format}")
    return response 