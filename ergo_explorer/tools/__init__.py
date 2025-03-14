"""
Tools for the Ergo Explorer MCP server.
"""

# Address tools
from ergo_explorer.tools.address import (
    get_address_balance,
    get_transaction_history,
    analyze_address
)

# Transaction tools
from ergo_explorer.tools.transaction import (
    analyze_transaction
)

# ErgoWatch tools
from ergo_explorer.tools.ergowatch import (
    get_address_balance_history,
    get_address_balance_at_height,
    get_contract_stats,
    get_exchange_addresses,
    get_rich_list,
    get_address_rank
)

# Misc tools
from ergo_explorer.tools.misc import (
    search_for_token,
    get_network_status
)

# Node tools
from ergo_explorer.tools.node import (
    get_address_balance_from_node,
    analyze_transaction_from_node,
    get_transaction_history_from_node,
    get_network_status_from_node,
    search_for_token_from_node
)

# Tokenomics tools
from ergo_explorer.tools.tokenomics import (
    get_token_price_info,
    get_token_price_chart,
    get_liquidity_pool_info,
    get_token_swap_info
)

# Smart contract tools
from ergo_explorer.tools.contracts import (
    analyze_smart_contract,
    get_contract_statistics,
    simulate_contract_execution
)

__all__ = [
    # Address tools
    'get_address_balance',
    'get_transaction_history',
    'analyze_address',
    
    # Transaction tools
    'analyze_transaction',
    
    # ErgoWatch tools
    'get_address_balance_history',
    'get_address_balance_at_height',
    'get_contract_stats',
    'get_exchange_addresses',
    'get_rich_list',
    'get_address_rank',
    
    # Misc tools
    'search_for_token',
    'get_network_status',
    
    # Node tools
    'get_address_balance_from_node',
    'analyze_transaction_from_node',
    'get_transaction_history_from_node',
    'get_network_status_from_node',
    'search_for_token_from_node',
    
    # Tokenomics tools
    'get_token_price_info',
    'get_token_price_chart',
    'get_liquidity_pool_info',
    'get_token_swap_info',
    
    # Smart contract tools
    'analyze_smart_contract',
    'get_contract_statistics',
    'simulate_contract_execution'
]
