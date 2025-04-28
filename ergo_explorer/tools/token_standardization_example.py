"""
Token-related utility functions with standardized response formatting.

This module provides functions for retrieving information about tokens
and searching for tokens on the Ergo blockchain.
"""

import time
import json
import requests
import logging
from typing import Dict, Any, List, Optional

from ergo_explorer.util.standardize import standardize_response

logger = logging.getLogger(__name__)

# Constants
EXPLORER_API_URL = "https://api.ergoplatform.com/api/v1"


def get_token(token_id: str) -> str:
    """
    Get detailed information about a token.

    Args:
        token_id: The ID of the token to retrieve

    Returns:
        Markdown-formatted string with token details
    """
    logger.info(f"Retrieving token with ID: {token_id}")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/tokens/{token_id}")
        response.raise_for_status()
        
        token = response.json()
        
        # Format the response as markdown
        markdown = f"# Token: {token.get('name', 'Unknown')}\n\n"
        markdown += f"**ID:** `{token_id}`\n"
        markdown += f"**Decimals:** {token.get('decimals', 0)}\n"
        markdown += f"**Type:** {token.get('type', 'Unknown')}\n"
        
        if "description" in token and token["description"]:
            markdown += f"\n**Description:** {token['description']}\n"
            
        emission_amount = token.get('emissionAmount', 0)
        if emission_amount:
            markdown += f"\n**Total Supply:** {emission_amount:,}\n"
        
        return markdown
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving token {token_id}: {str(e)}")
        return f"Error retrieving token: {str(e)}"


@standardize_response
def get_token_json(token_id: str) -> Dict[str, Any]:
    """
    Get token information in standardized JSON format.

    Args:
        token_id: The ID of the token to retrieve

    Returns:
        Standardized JSON response with token details
    """
    logger.info(f"Retrieving token JSON with ID: {token_id}")
    
    try:
        response = requests.get(f"{EXPLORER_API_URL}/tokens/{token_id}")
        response.raise_for_status()
        
        token = response.json()
        
        # Return the token data directly
        # The decorator will handle standardization
        return token
        
    except requests.RequestException as e:
        logger.error(f"Error retrieving token {token_id}: {str(e)}")
        raise ValueError(f"Error retrieving token: {str(e)}")


def search_token(query: str) -> str:
    """
    Search for tokens by name or ID.

    Args:
        query: Search query (token name or ID)

    Returns:
        Markdown-formatted string with search results
    """
    logger.info(f"Searching for token with query: {query}")
    
    try:
        # Use search endpoint or filter tokens
        response = requests.get(f"{EXPLORER_API_URL}/tokens/search?query={query}")
        response.raise_for_status()
        
        results = response.json()
        
        if not results or len(results) == 0:
            return "No tokens found matching your query."
        
        # Format results as markdown
        markdown = f"# Token Search Results for '{query}'\n\n"
        
        for token in results:
            markdown += f"## {token.get('name', 'Unknown Token')}\n"
            markdown += f"**ID:** `{token.get('id', 'Unknown')}`\n"
            markdown += f"**Decimals:** {token.get('decimals', 0)}\n"
            if "description" in token and token["description"]:
                markdown += f"**Description:** {token['description'][:100]}{'...' if len(token['description']) > 100 else ''}\n"
            markdown += "\n---\n\n"
        
        return markdown
        
    except requests.RequestException as e:
        logger.error(f"Error searching for token with query '{query}': {str(e)}")
        return f"Error searching for token: {str(e)}"


@standardize_response
def search_token_json(query: str) -> Dict[str, Any]:
    """
    Search for tokens by name or ID in JSON format.

    Args:
        query: Search query (token name or ID)

    Returns:
        Standardized JSON response with search results
    """
    logger.info(f"Searching for token JSON with query: {query}")
    
    try:
        # Use search endpoint or filter tokens
        response = requests.get(f"{EXPLORER_API_URL}/tokens/search?query={query}")
        response.raise_for_status()
        
        results = response.json()
        
        # Return the results directly
        # The decorator will handle standardization
        return {
            "tokens": results,
            "count": len(results),
            "query": query
        }
        
    except requests.RequestException as e:
        logger.error(f"Error searching for token with query '{query}': {str(e)}")
        raise ValueError(f"Error searching for token: {str(e)}") 