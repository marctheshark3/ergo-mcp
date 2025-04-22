"""
ErgoClient - A client for interacting with Ergo blockchain APIs.
"""
import asyncio
import logging
import httpx
import json
import os
from typing import Dict, List, Union, Optional, Any

logger = logging.getLogger(__name__)

class ErgoClient:
    """A client for interacting with Ergo blockchain data."""
    
    def __init__(
        self, 
        explorer_api_url: str = "https://api.ergoplatform.com/api/v1",
        node_api_url: str = "http://213.239.193.208:9053",
        timeout: float = 30.0
    ):
        """
        Initialize the ErgoClient.
        
        Args:
            explorer_api_url: Base URL for the Ergo Explorer API
            node_api_url: Base URL for the Ergo Node API
            timeout: Request timeout in seconds
        """
        self.explorer_api_url = explorer_api_url
        self.node_api_url = node_api_url
        self.timeout = timeout
        
        # Configure logging based on environment variables
        self.log_full_responses = os.environ.get('LOG_FULL_RESPONSES', 'true').lower() == 'true'
        self.max_log_length = int(os.environ.get('MAX_RESPONSE_LOG_LENGTH', '1000'))
        self.pretty_print = os.environ.get('PRETTY_PRINT_JSON', 'true').lower() == 'true'
        
        logger.info(f"Initialized ErgoClient with explorer API: {explorer_api_url}")
        logger.info(f"Node API: {node_api_url}")
        logger.info(f"Logging configuration: Full responses: {self.log_full_responses}, "
                   f"Max length: {self.max_log_length}, Pretty print: {self.pretty_print}")
    
    def _format_response_for_log(self, data):
        """Format response data for logging with truncation and pretty printing."""
        if not data:
            return "Empty response"
        
        try:
            if self.pretty_print and isinstance(data, (dict, list)):
                formatted = json.dumps(data, indent=2, sort_keys=True)
            else:
                formatted = str(data)
            
            if self.max_log_length > 0 and len(formatted) > self.max_log_length:
                return f"{formatted[:self.max_log_length]}... [truncated, total length: {len(formatted)}]"
            return formatted
        except Exception as e:
            return f"Error formatting response: {e}"
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            params: URL parameters
            json_data: JSON data for POST requests
            headers: HTTP headers
            
        Returns:
            Response data as dictionary
        """
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        
        log_url = f"{url}"
        if params:
            log_params = ", ".join([f"{k}={v}" for k, v in params.items()])
            log_url += f" (params: {log_params})"
        
        logger.debug(f"Making {method} request to {log_url}")
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=default_headers)
                elif method.upper() == "POST":
                    response = await client.post(url, params=params, json=json_data, headers=default_headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                logger.debug(f"Received response: status={response.status_code}, content-type={response.headers.get('content-type', 'unknown')}")
                
                response.raise_for_status()
                response_data = response.json()
                
                if self.log_full_responses:
                    logger.info(f"Response from {method} {url.split('/')[-1]}:\n"
                               f"{self._format_response_for_log(response_data)}")
                else:
                    # Log just a summary of the response
                    if isinstance(response_data, dict):
                        keys = list(response_data.keys())
                        logger.info(f"Response keys: {keys}")
                    elif isinstance(response_data, list):
                        logger.info(f"Response is a list with {len(response_data)} items")
                    else:
                        logger.info(f"Response type: {type(response_data)}")
                
                return response_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            # Log the error response content if available
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text[:500]}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making request: {e}")
            raise
    
    async def blockchain_status(self) -> Dict[str, Any]:
        """
        Get blockchain status including height, difficulty, and hashrate.
        
        Returns:
            Dictionary with blockchain status information
        """
        logger.info("Fetching blockchain status")
        url = f"{self.explorer_api_url}/info"
        return await self._make_request("GET", url)
    
    async def get_token_holders(self, token_id: str) -> Dict[str, Any]:
        """
        Get token holders for a specific token.
        
        Args:
            token_id: The ID of the token
            
        Returns:
            Dictionary with token holder information
        """
        logger.info(f"Fetching token holders for {token_id}")
        # This endpoint might be custom to your implementation
        url = f"{self.explorer_api_url}/tokens/{token_id}/holders"
        try:
            return await self._make_request("GET", url)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Holders endpoint not found for {token_id}, falling back to token info")
                # Fall back to a different endpoint if the first one fails
                alt_url = f"{self.explorer_api_url}/tokens/{token_id}"
                token_info = await self._make_request("GET", alt_url)
                # Simulate holder information since the original endpoint doesn't exist
                result = {
                    "token": token_info,
                    "holders": [{"address": "unknown", "amount": token_info.get("emissionAmount", 0)}],
                    "summary": "Basic token information retrieved, holder data not available"
                }
                logger.info(f"Generated token holders data with {len(result.get('holders', []))} entries")
                return result
            raise
    
    async def get_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction details
        """
        logger.info(f"Fetching transaction {tx_id}")
        url = f"{self.explorer_api_url}/transactions/{tx_id}"
        return await self._make_request("GET", url)
    
    async def search_token(self, query: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Search for tokens by name or ID.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tokens or dictionary with token information
        """
        logger.info(f"Searching for tokens with query: {query}")
        url = f"{self.explorer_api_url}/tokens/search"
        return await self._make_request("GET", url, params={"query": query})
    
    async def get_latest_blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent blocks.
        
        Args:
            limit: Maximum number of blocks to return
            
        Returns:
            List of blocks
        """
        logger.info(f"Fetching latest {limit} blocks")
        url = f"{self.explorer_api_url}/blocks"
        return await self._make_request("GET", url, params={"limit": limit})
    
    async def get_block(self, block_id: str) -> Dict[str, Any]:
        """
        Get block by ID.
        
        Args:
            block_id: Block ID
            
        Returns:
            Block details
        """
        logger.info(f"Fetching block {block_id}")
        url = f"{self.explorer_api_url}/blocks/{block_id}"
        return await self._make_request("GET", url)
    
    async def get_address_balance(self, address: str) -> Dict[str, Any]:
        """
        Get balance for an address.
        
        Args:
            address: Ergo address
            
        Returns:
            Balance information
        """
        logger.info(f"Fetching balance for address {address}")
        url = f"{self.explorer_api_url}/addresses/{address}/balance"
        return await self._make_request("GET", url)
    
    async def get_mempool_transactions(self) -> List[Dict[str, Any]]:
        """
        Get transactions in the mempool.
        
        Returns:
            List of mempool transactions
        """
        logger.info("Fetching mempool transactions")
        url = f"{self.node_api_url}/transactions/unconfirmed"
        return await self._make_request("GET", url)
    
    async def mempool_status(self) -> Dict[str, Any]:
        """
        Get mempool status.
        
        Returns:
            Mempool status information
        """
        logger.info("Fetching mempool status")
        # This is a custom endpoint that may not exist on all node implementations
        url = f"{self.node_api_url}/info"
        node_info = await self._make_request("GET", url)
        
        # Extract mempool data if available, or create placeholder
        if "mempool" in node_info:
            logger.info("Mempool information found in node info")
            return node_info["mempool"]
        
        # Simulate mempool data if not available directly
        logger.info("Mempool information not found in node info, fetching transactions")
        mempool_txs = await self.get_mempool_transactions()
        result = {
            "size": len(mempool_txs),
            "transactions": mempool_txs[:5],  # Return first 5 for brevity
            "total": len(mempool_txs)
        }
        logger.info(f"Generated mempool status with {result['size']} transactions")
        return result 