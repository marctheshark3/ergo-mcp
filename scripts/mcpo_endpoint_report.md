# MCPO Endpoint Analysis Report

Total functions implemented: **138**

## Function count by module

- **blockchain**: 42 functions
- **address**: 13 functions
- **token**: 18 functions
- **transaction**: 3 functions
- **block**: 13 functions
- **network**: 13 functions
- **contracts**: 13 functions
- **tokenomics**: 13 functions
- **ergowatch**: 10 functions

## Unimplemented Phase 2 features

- Non-standard collection lookup mechanisms

## Unimplemented Phase 3 features


## Detailed function listing

### BLOCKCHAIN MODULE (42 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### Tuple (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _TupleType

#### Union (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### blockchain_status (async)

Get comprehensive blockchain status including height, difficulty metrics,
    network hashrate, and recent adjustments.
    
    Returns:
        Dictionary containing blockchain status information including:
        - height: Current blockchain height information
        - mining: Mining statistics and difficulty metrics
        - network: Network state and node information

#### calculate_hashrate (async)

Calculate estimated hashrate from difficulty.
    
    Args:
        difficulty: The network difficulty
        
    Returns:
        Estimated hashrate in H/s

#### condense_address (sync)

Condenses a blockchain address for display.

    Args:
        address: The full address string.
        length: The number of characters to show from the start and end.

    Returns:
        A condensed address string (e.g., 'abcde...vwxyz').

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_api (async)

Make a request to the Ergo Explorer API.

#### fetch_network_state (async)

Fetch the current network state.

#### fetch_node_api (async)

Make a request to the Ergo Node API.

#### format_difficulty (async)

Format difficulty in a more readable format.
    
    Args:
        difficulty: The raw difficulty value
        
    Returns:
        A human-readable string representation of the difficulty

#### get_address_balance (async)

Get confirmed and unconfirmed balance for an address.

#### get_address_full_balance (async)

Get detailed balance information for an address.
    
    Args:
        address: Ergo blockchain address
        
    Returns:
        Dictionary containing balance details including:
        - address: The queried address
        - confirmed: Dictionary containing confirmed balance info
        - unconfirmed: Dictionary containing unconfirmed balance info

#### get_address_transaction_history (async)

Get transaction history for an address.
    
    Args:
        address: Ergo blockchain address
        offset: Number of transactions to skip
        limit: Maximum number of transactions to return
        
    Returns:
        Dictionary containing:
        - address: The queried address
        - total_transactions: Total number of transactions found
        - transactions: List of transaction details
        - offset: Current offset
        - limit: Current limit

#### get_all_token_holders (async)

Get all addresses holding a specific token by fetching all unspent boxes.
    
    Args:
        token_id: Token ID to search for
        
    Returns:
        List of dictionaries containing address and amount information

#### get_blockchain_height (async)

Get the current blockchain height and indexing status.
    
    Returns:
        Dictionary with blockchain height information including:
        - blockHeight: Current full blockchain height

#### get_box_by_id (async)

Get box details by ID.

#### get_box_by_index (async)

Get box by global index number.

#### get_box_info (async)

Get detailed information about a box.
    
    Args:
        identifier: Box ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary containing box details including:
        - id: Box ID
        - value: Dictionary with nanoERG and ERG values
        - creation_height: Block height when box was created
        - ergo_tree: Box's ErgoTree script
        - assets: List of tokens in the box

#### get_box_range (async)

Get a range of box IDs.

#### get_boxes_by_address (async)

Get boxes for an address.

#### get_boxes_by_ergo_tree (async)

Get boxes by ErgoTree.

#### get_boxes_by_token_id (async)

Get boxes containing a specific token.

#### get_histogram_token_stats (async)

Get token holder distribution data suitable for histogram visualization.
    
    Args:
        token_id: Token ID to analyze
        bin_count: Number of bins to divide the holder amounts into
        
    Returns:
        Dictionary containing binned distribution data for token holders.

#### get_indexed_height (async)

Get current indexed block height.

#### get_token_by_id (async)

Get token information by ID.

#### get_token_holders (async)

Get comprehensive token holder information.
    
    Args:
        token_id: Token ID to analyze
        include_raw: Include raw holder data
        include_analysis: Include holder analysis

#### get_token_info (async)

Get detailed information about a token.
    
    Args:
        token_id: Token ID (hex string)
        
    Returns:
        A formatted string with token details

#### get_token_stats (async)

Get statistical analysis for token holders.

    Args:
        token_id: Token ID to analyze.

    Returns:
        Dictionary containing token statistics like total holders, supply, and distribution.

#### get_tokens (async)

Get list of tokens.

#### get_transaction_by_id (async)

Get transaction details by ID.

#### get_transaction_by_index (async)

Get transaction by global index number.

#### get_transaction_info (async)

Get detailed information about a transaction in standardized JSON format.
    
    Args:
        identifier: Transaction ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary with transaction details

#### get_transaction_range (async)

Get a range of transaction IDs.

#### get_transactions_by_address (async)

Get transactions for an address.

#### get_unspent_boxes_by_address (async)

Get unspent boxes for an address.

#### get_unspent_boxes_by_ergo_tree (async)

Get unspent boxes by ErgoTree.

#### get_unspent_boxes_by_token_id (async)

Get unspent boxes containing a specific token.

#### standardize_response (sync)

Standardize a response to JSON format.
    Args:
        response: The response data to standardize
        response_format: The desired format ("json")
    Returns:
        Formatted response in JSON format

### ADDRESS MODULE (13 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Set (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### analyze_address (async)

Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.
    
    Args:
        address: Ergo blockchain address to analyze
        depth: How many layers of transactions to analyze (1-4, default: 2)
        tx_limit: Maximum transactions per address to analyze (default: 5)

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_address_transactions (async)

Fetch transactions for an address.

#### fetch_balance (async)

Fetch the confirmed balance for an address.

#### get_address_balance_json (sync)

Get the confirmed balance for an Ergo address in standardized JSON format.
    
    Args:
        address: Ergo blockchain address
        
    Returns:
        Structured data containing address balance information

#### get_transaction_history (async)

Get the transaction history for an Ergo address.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)

#### get_transaction_history_json (sync)

Get the transaction history for an Ergo address in standardized JSON format.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
        
    Returns:
        Structured data containing transaction history

#### smart_limit (sync)

Apply smart limiting to result data.
    
    Args:
        data: The list data to potentially limit
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (limited_data, is_truncated)

#### standardize_response (sync)

Decorator to standardize function responses.

### TOKEN MODULE (18 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### ResponseConfig (sync)

Configuration for response formatting.

#### Tuple (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _TupleType

#### Union (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_token_by_id (async)

Fetch details for a specific token by ID.

#### fetch_token_price (async)

Get the current price of a token in ERG.
    
    Args:
        token_id: ID of the token to check
        
    Returns:
        Dictionary with price information

#### fetch_tokens (async)

Search for tokens by ID or symbol.

#### format_token_price (async)

Format token price data into a readable string.
    
    Args:
        price_data: The price data to format
        
    Returns:
        A formatted string representation of the token price data

#### get_erg_price_usd (async)

Get the current price of ERG in USD.

#### get_token_info (async)

Get detailed information about a token using standardized response format.
    
    Args:
        token_id: ID of the token to retrieve
        
    Returns:
        A dictionary containing token information

#### get_token_price (async)

Get the current price of a token in ERG and USD.
    
    Args:
        token_id: ID of the token to check
        
    Returns:
        A dictionary containing price information

#### search_token_info (async)

Search for tokens by name or ID using standardized response format.
    
    Args:
        query: Search query (token name or ID)
        limit: Maximum number of results to return
        
    Returns:
        Tuple of (tokens_list, is_truncated)

#### smart_limit (sync)

Apply smart limiting to result data.
    
    Args:
        data: The list data to potentially limit
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (limited_data, is_truncated)

#### standardize_response (sync)

Decorator to standardize function responses.

### TRANSACTION MODULE (3 functions)

#### analyze_transaction (async)

Analyze a transaction on the Ergo blockchain.
    
    Args:
        tx_id: Transaction ID (hash)

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_transaction (async)

Fetch details for a specific transaction.

### BLOCK MODULE (13 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_node_api (async)

Make a request to the Ergo Node API.

#### format_block_data (async)

Format block data (received from Node API's /blocks/{id} endpoint) into a readable string.
    
    Args:
        block_data: The block data dictionary to format
        
    Returns:
        A formatted string representation of the block data

#### format_block_transactions (async)

Format block transactions data into a readable string.
    
    Args:
        tx_data: The transactions data to format
        block_id: The ID of the block
        
    Returns:
        A formatted string representation of the block transactions

#### format_latest_blocks (async)

Format latest blocks data into a readable string.
    
    Args:
        blocks_data: The blocks data to format
        
    Returns:
        A formatted string representation of the latest blocks

#### get_block_by_hash (async)

Fetch a block by its hash using the direct Node API.
    
    Args:
        block_hash: The hash (ID) of the block to fetch
        
    Returns:
        A dictionary containing block data or an error message

#### get_block_by_height (async)

Fetch a block by its height using the direct Node API.
    
    Args:
        height: The height of the block to fetch
        
    Returns:
        A dictionary containing block data or an error message

#### get_block_transactions (async)

Fetch transactions from a specific block.
    
    Args:
        block_id: The ID of the block
        limit: Maximum number of transactions to retrieve (default: 100)
        
    Returns:
        A dictionary containing the block's transactions

#### get_latest_blocks (async)

Fetch the latest blocks from the Ergo blockchain.
    
    Args:
        limit: Maximum number of blocks to retrieve (default: 10)
        
    Returns:
        A dictionary containing the latest blocks

### NETWORK MODULE (13 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### datetime (sync)

datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.

#### fetch_api (async)

Make a request to the Ergo Explorer API.

#### fetch_network_state (async)

Fetch the current network state.

#### fetch_node_api (async)

Make a request to the Ergo Node API.

#### format_blockchain_stats (async)

Format blockchain statistics into a readable string.
    
    Args:
        stats_data: The blockchain statistics data to format
        
    Returns:
        A formatted string representation of the blockchain statistics

#### format_mining_difficulty (async)

Format mining difficulty data into a readable string.
    
    Args:
        difficulty_data: The difficulty data to format
        
    Returns:
        A formatted string representation of the mining difficulty

#### format_network_hashrate (async)

Format network hashrate data into a readable string.
    
    Args:
        hashrate_data: The hashrate data to format
        
    Returns:
        A formatted string representation of the network hashrate

#### format_readable_difficulty (sync)

Format the difficulty value into a human-readable form.
    
    Args:
        difficulty: Raw difficulty value
        
    Returns:
        Formatted difficulty string with appropriate unit

#### get_blockchain_stats (async)

Fetch overall statistics about the Ergo blockchain.
    
    Returns:
        A dictionary containing blockchain statistics

### CONTRACTS MODULE (13 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### analyze_smart_contract (async)

Analyze a smart contract from its address.
    
    Args:
        address: Ergo blockchain address of the contract

#### decode_register (async)

Decode register value to human readable format if possible.
    
    Args:
        register_value: Base16 or Base64 encoded register value
        
    Returns:
        Human readable string representation

#### decompile_contract (async)

Attempt to decompile an ErgoTree to identify contract template and provide description.
    
    Args:
        ergo_tree: Base16-encoded ErgoTree
        
    Returns:
        Tuple of (contract_template, description)

#### fetch_api (async)

Make a request to the Ergo Explorer API.

#### get_box_by_id_node (async)

Legacy function for getting box details.

#### get_contract_statistics (async)

Get statistics about smart contract usage on the Ergo blockchain.
    
    Returns:
        Formatted string with contract statistics

#### get_contract_use_cases (async)

Get common use cases for a contract template.
    
    Args:
        contract_template: The identified contract template
        
    Returns:
        Formatted string with use cases

#### get_unspent_boxes_by_address_node (async)

Legacy function for getting unspent boxes.

#### simulate_contract_execution (async)

Simulate the execution of a smart contract with given inputs.
    
    Args:
        address: Contract address
        input_data: Dictionary of input data for simulation
        
    Returns:
        Formatted string with simulation results

### TOKENOMICS MODULE (13 functions)

#### Any (sync)

Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    checks.

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### get_erg_price_usd (async)

Get the current price of ERG in USD.

#### get_liquidity_pool_info (async)

Get information about liquidity pools, optionally filtered by token.
    
    Args:
        token_query: Optional token name or ID to filter pools

#### get_liquidity_pools (async)

Get liquidity pools information, optionally filtered by token.
    
    Args:
        token_id: Optional token ID to filter pools
        
    Returns:
        List of liquidity pools with detailed information

#### get_price_history (async)

Get historical price data for a token.
    
    Args:
        token_id: ID of the token to check
        days: Number of days to fetch history for
        
    Returns:
        List of historical price points

#### get_token_price (async)

Get the current price of a token in ERG.
    
    Args:
        token_id: ID of the token to check
        
    Returns:
        Dictionary with price information

#### get_token_price_chart (async)

Get price chart data for a token.
    
    Args:
        token_query: Token name or ID to search for
        days: Number of days to show history for (default: 7)

#### get_token_price_info (async)

Get the current price and basic market information for a token.
    
    Args:
        token_query: Token name or ID to search for

#### get_token_swap_info (async)

Get swap information between two tokens.
    
    Args:
        from_token: Source token name or ID
        to_token: Target token name or ID
        amount: Amount of source token to swap

#### search_tokens (async)

Search for tokens by ID or symbol.

### ERGOWATCH MODULE (10 functions)

#### Dict (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### List (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialGenericAlias

#### Optional (sync)

Error retrieving information: module, class, method, function, traceback, frame, or code object was expected, got _SpecialForm

#### get_address_balance_at_height (async)

Get address balance at a specific height.
    
    Args:
        address: The Ergo address to check
        height: Block height to check balance at
        token_id: Optional token ID to get balance for specific token

#### get_address_balance_history (async)

Get balance history for an address.
    
    Args:
        address: The Ergo address to check
        token_id: Optional token ID to get history for specific token

#### get_address_rank (async)

Get rank of a P2PK address in terms of balance.
    
    Args:
        address: The P2PK address to check

#### get_contract_stats (async)

Get statistics about contract addresses.

#### get_exchange_addresses (async)

Get list of tracked exchange addresses.

#### get_p2pk_stats (async)

Get statistics about P2PK addresses.

#### get_rich_list (async)

Get rich list of addresses sorted by balance.
    
    Args:
        limit: Number of addresses to return (default: 10)
        token_id: Optional token ID to get rich list for specific token


## Next steps

1. Implement missing Phase 2 features with highest priority
2. Develop token usage optimization for existing endpoints
3. Add comprehensive tests for all endpoints
4. Prepare for Phase 3 feature development
