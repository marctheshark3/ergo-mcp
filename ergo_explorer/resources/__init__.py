"""
MCP resources for Ergo blockchain.
"""

from ergo_explorer.resources.address import get_address_balance_resource
from ergo_explorer.resources.transaction import get_transaction_resource
from ergo_explorer.resources.node_resources import (
    get_address_balance_node_resource,
    get_transaction_node_resource
)

# Import the new EIP resources
from ergo_explorer.resources.eip_resources import eip_resources

__all__ = [
    'get_address_balance_resource',
    'get_transaction_resource',
    'get_address_balance_node_resource',
    'get_transaction_node_resource',
    
    # EIP resources
    'eip_resources',
]
