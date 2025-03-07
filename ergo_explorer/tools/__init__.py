"""
MCP tools for Ergo blockchain.
"""

from ergo_explorer.tools.address import get_address_balance, get_transaction_history, analyze_address
from ergo_explorer.tools.transaction import analyze_transaction
from ergo_explorer.tools.misc import search_for_token, get_network_status
from ergo_explorer.tools.node import (
    get_address_balance_from_node,
    analyze_transaction_from_node,
    get_transaction_history_from_node,
    get_network_status_from_node,
    search_for_token_from_node
)
from ergo_explorer.tools.ergowatch import (
    get_address_balance_history,
    get_address_balance_at_height,
    get_contract_stats,
    get_p2pk_stats,
    get_exchange_addresses,
    get_rich_list,
    get_address_rank
)

__all__ = [
    # Core Explorer Tools
    'get_address_balance',
    'get_transaction_history',
    'analyze_address',
    'analyze_transaction',
    'search_for_token',
    'get_network_status',
    
    # Node API Tools
    'get_address_balance_from_node',
    'analyze_transaction_from_node',
    'get_transaction_history_from_node',
    'get_network_status_from_node',
    'search_for_token_from_node',
    
    # ErgoWatch Tools
    'get_address_balance_history',
    'get_address_balance_at_height',
    'get_contract_stats',
    'get_p2pk_stats',
    'get_exchange_addresses',
    'get_rich_list',
    'get_address_rank'
]
