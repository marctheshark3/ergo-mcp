# Ergo Explorer MCP - Product Requirements Document

## Overview

The Ergo Explorer Model Context Protocol (MCP) server is a comprehensive service that provides AI assistants with direct access to Ergo blockchain data. This product bridges the gap between AI assistants and the Ergo blockchain ecosystem, enabling complex blockchain data analysis, transaction monitoring, wallet interactions, and smart contract operations through a standardized protocol.

## Product Vision

To become the definitive interface between AI assistants and the Ergo blockchain, allowing both technical and non-technical users to interact with blockchain data through natural language conversations without requiring specialized knowledge of blockchain technologies.

## Target Audience

1. **AI Assistant Users**: Individuals using Claude, GPT, or other AI assistants who want to access Ergo blockchain data
2. **Blockchain Developers**: Developers building applications on Ergo who need AI-powered data analysis
3. **Blockchain Researchers**: Academics and researchers analyzing on-chain data and patterns
4. **Traders and Investors**: Users seeking tokenomics information, price data, and market analysis
5. **General Ergo Community**: Community members wanting simplified access to blockchain data

## Key Features

### Core Functionality

1. **Blockchain Exploration**
   - Retrieve blocks by height, hash, or recency
   - Access transaction data and history
   - Analyze network statistics (hashrate, difficulty, block times)
   - Monitor mempool for pending transactions

2. **Address Interaction**
   - Query address balances and transaction history
   - Perform forensic analysis on addresses
   - View address rankings and rich lists
   - Track historical balance changes
   - Identify common transaction partners
   - Address clustering analysis
   - **NEW**: Comprehensive address information with token details and transaction analysis

3. **Token Analysis**
   - Search and retrieve token information by ID or name
   - View current and historical token holder distributions
   - Analyze NFT collections (including non-EIP standard collections)
   - Track token prices and market metrics
   - Analyze liquidity pool balances and distribution
   - Monitor token money flow trends
   - Calculate advanced token metrics (RSI, etc.)
   - Track NFT marketplace listings and sales history

4. **Smart Contract Interaction**
   - Analyze smart contracts
   - Retrieve contract statistics
   - View contract execution data
   - Simulate contract execution

5. **Ergo Ecosystem Integration**
   - Access EIP (Ergo Improvement Proposal) information
   - Query oracle pool data
   - Analyze DEX liquidity and trading volume
   - Reference address book data for known entities

### Technical Requirements

1. **Integration Methods**
   - Direct MCP protocol support for Claude/Anthropic ecosystem
   - MCPO proxy support for OpenAI-compatible APIs (Open WebUI integration)
   - Docker deployment option
   - Local installation option
   - Comprehensive automated testing for all endpoints

2. **Performance Requirements**
   - Response time < 2 seconds for standard queries
   - Support for concurrent requests (minimum 10 simultaneous users)
   - Graceful degradation under heavy load
   - Efficient caching of frequently requested data
   - Optimized data handling for large result sets

3. **Security Requirements**
   - API key authentication for MCPO proxy
   - Rate limiting to prevent abuse
   - Safe handling of node API keys
   - No private key management or signing capabilities
   - Sandboxed execution environment

4. **Deployment Options**
   - Docker image with easy configuration
   - Python package for direct installation
   - Automated setup scripts
   - Environment variable configuration

5. **Token Usage Optimization**
   - Token metrics for all MCP endpoints
   - Optimized response payloads for LLM consumption
   - Automatic response truncation for large datasets
   - Token usage tracking and reporting

## Use Cases

1. **Blockchain Data Analysis**
   - "What was the average transaction fee over the last 100 blocks?"
   - "Show me the top 10 addresses by ERG balance"
   - "How many transactions occurred in block #1000000?"

2. **Token Research**
   - "What's the current price of SigUSD?"
   - "Who are the top holders of the Ergognomes NFT collection?"
   - "Show me the historical holder distribution for token X"
   - "How many tokens were minted for project X?"
   - "What's the RSI for token X over the last 14 days?"
   - "How much of token X is locked in liquidity pools?"

3. **Address Monitoring**
   - "Has address X received any funds in the last 24 hours?"
   - "What's the total value of tokens held by address Y?"
   - "Show me all transactions between addresses A and B"
   - "What addresses most commonly interact with address X?"
   - "Identify all addresses likely belonging to the same entity as address X"

4. **Developer Assistance**
   - "Explain what this ErgoScript contract does"
   - "What are the parameters for a token issuance transaction?"
   - "Find all transactions using a specific script template"

5. **Market Analysis**
   - "What's the current liquidity for ERG/SigUSD on ErgoDEX?"
   - "Show price history for token X over the past month"
   - "What's the total market cap of the Ergo ecosystem?"
   - "Show me the money flow trends for token X over the last 30 days"
   - "How many listings and sales for NFT collection Y in the past week?"

## Standardized Response Formats

All API responses follow a standardized format to ensure consistency and ease of integration:

```json
{
  "status": "success", // or "error"
  "data": {
    // Endpoint-specific structured data
  },
  "metadata": {
    "execution_time_ms": 123,
    "result_size_bytes": 456,
    "is_truncated": false,
    "token_estimate": 789
  }
}
```

## Token Estimation Implementation

To optimize interactions between AI assistants and the MCP server, we have implemented token estimation features that provide accurate token counts for various LLM models. This allows AI assistants to make informed decisions about context window usage and response handling.

### Current Implementation

- **Token Counting Utilities**: Created a comprehensive module (`token_counter.py`) that estimates tokens for different LLM models
- **Model-Specific Estimation**: Support for various LLM models including Claude, GPT-4, GPT-3.5, Gemini, Mistral, and LLaMA
- **Response Integration**: All MCP responses now include token count estimates and section breakdowns in their metadata
- **Fallback Mechanisms**: Graceful degradation when tiktoken library is not available
- **Threshold Configuration**: Customizable thresholds for token truncation based on model type
- **Token Usage Tiers**: Categorization of responses into minimal, standard, intensive, and excessive tiers

### Future Token Optimization Plans

- **Response Truncation**: Implement automatic truncation of responses that exceed token thresholds
- **Summarization Options**: Provide summarized versions of data-intensive responses with options to retrieve full details
- **Pagination Parameters**: Add pagination for responses with high token counts
- **Selective Field Selection**: Allow clients to request specific fields to reduce token usage
- **Token Budget Parameter**: Allow clients to specify a maximum token budget for responses
- **Caching Optimization**: Cache token estimates for common responses to improve performance
- **Model-Optimized Formatting**: Format responses differently based on which model will consume them

### Metrics and Analysis

We've created tools to analyze the token usage of all MCPO endpoints:

1. **MCPO Endpoint Analyzer** (`scripts/mcpo_endpoints.py`): Identifies all implemented endpoints and their feature categories
2. **Token Estimation Script** (`scripts/analyze_mcpo_endpoints.py`): Measures token usage across all endpoints with various test data

Initial analysis shows that most simple query endpoints use fewer than 500 tokens, while data-intensive endpoints like address transaction history or token holder lists can use 2,000-10,000 tokens depending on the data size.

## Implementation Progress

### Completed Features

- Basic blockchain query endpoints (block, transaction, address info)
- Token information and holder lists
- Network statistics endpoints
- Response standardization framework
- Token estimation integration

### In-Progress Features

- Address interaction detection
- Token transaction analysis
- Smart contract interaction endpoints

### Planned Features

- Wallet integration
- Oracle pool integration
- Comprehensive transaction analysis
- EIP-specific endpoints

## Data Sources and Integration

### Primary Data Sources

1. **Ergo Explorer API**
   - Public blockchain data access
   - Historical transaction information
   - Address balances and history

2. **Ergo Node API**
   - Direct blockchain access
   - Mempool information
   - Transaction creation and submission
   - Contract validation

3. **Third-party Services**
   - ErgoWatch for analytics
   - DEX APIs for pricing (Spectrum, ErgoDEX)
   - Oracle pools for off-chain data
   - NFT marketplace APIs for collection data

### Database Schema

The MCP server is primarily stateless, relying on external APIs for data. Limited local caching may be implemented with the following structure:

```
cache/
  ├── blocks/             # Cached block data
  │   ├── by_height/      # Indexed by block height
  │   └── by_hash/        # Indexed by block hash
  ├── transactions/       # Cached transaction data
  │   └── by_id/          # Indexed by transaction ID
  ├── addresses/          # Cached address data
  │   └── by_address/     # Indexed by address
  └── tokens/             # Cached token data
      └── by_id/          # Indexed by token ID
```

## Key Components and APIs

### Core MCP Functions

#### Blockchain Status

```python
@standardize_response
def blockchain_status() -> dict:
    """Get comprehensive blockchain status including height, difficulty metrics, and network hashrate."""
    # Implementation details
```

#### Address Information (New)

```python
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
    # Implementation details
```

#### Token Information

```python
@standardize_response
def get_token(token_id: str) -> dict:
    """Get detailed information about a token."""
    # Implementation details
```

### Token Analysis Tools

```python
@standardize_response
def analyze_mcpo_endpoints() -> Dict[str, Any]:
    """
    Analyze all MCPO endpoints and generate a token usage report.
    This is used by the scripts/analyze_mcpo_endpoints.py tool.
    
    Returns:
        Dictionary with token usage statistics for all endpoints
    """
    # Implementation in scripts/analyze_mcpo_endpoints.py
```

## Limitations and Constraints

1. **Technical Limitations**
   - Dependency on external APIs
   - Explorer API rate limits
   - Node API access requirements
   - Blockchain data size constraints
   - Historic data availability limitations

2. **User Experience Limitations**
   - Complex queries may have longer response times
   - Historical data may be limited by API constraints
   - Private network data not accessible
   - No private key management for security reasons
   - Large result sets may need to be truncated for LLM context limits

## Future Roadmap

1. **Enhanced Analytics**
   - Advanced pattern recognition in transaction flows
   - Machine learning for anomaly detection
   - Predictive analytics for network activity

2. **Expanded Integrations**
   - Support for additional AI platforms
   - Integration with more Ergo ecosystem services
   - Support for cross-chain data via connectors

3. **User Experience Improvements**
   - Data visualization outputs
   - Interactive query building
   - Natural language query optimization

4. **Developer Tools**
   - Transaction building assistance
   - Contract template generation
   - Box selection optimization

## Appendix

### Environment Variables

| Variable Name | Description | Default Value | Required |
|---------------|-------------|---------------|----------|
| ERGO_EXPLORER_API | URL for Ergo Explorer API | https://api.ergoplatform.com/api/v1 | No |
| ERGO_NODE_API | URL for Ergo Node API | http://localhost:9053 | No |
| ERGO_NODE_API_KEY | API key for Ergo Node | None | Only for Node API |
| SERVER_PORT | Port for MCP server | 3001 | No |
| LOG_LEVEL | Logging level | INFO | No |
| CACHE_TIMEOUT | Cache timeout in seconds | 300 | No |
| DEBUG | Enable debug mode | False | No |
| RESPONSE_VERBOSITY | Response detail level (normal, minimal) | normal | No |

### API Documentation References

- [Ergo Explorer API](https://api.ergoplatform.com/api/v1/docs/)
- [Ergo Node API](https://github.com/ergoplatform/ergo/blob/master/src/main/resources/api/openapi.yaml)
- [Spectrum DEX](https://spectrum.fi/docs)
- [ErgoDEX](https://docs.ergodex.io/)
- [Oracle Pools](https://github.com/ergoplatform/oracle-core) 