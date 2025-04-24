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

## Phase Implementation Plan

### Phase 1 (Initial Release)

**Status: Completed**

- Core blockchain data retrieval (blocks, transactions, addresses)
- Basic network statistics (hashrate, difficulty)
- Token information and search
- Mempool monitoring
- OpenAPI integration via MCPO

### Phase 2 (Current Development)

**Status: In Progress**

- **Data Efficiency Optimizations**
  - Refined vs. verbose tooling response options
  - Smart result size limiting to reduce LLM context usage
  - Response format standardization and compression

- **Enhanced Token Analytics**
  - Token name-based search capabilities
  - Historical token holder distribution tracking
  - Non-standard collection lookup mechanisms
  - Collection marketplace statistics (listings, sales frequency)
  - Liquidity pool analysis (balance, % locked, holder distribution)
  - Token money flow trend analysis (inflow/outflow)
  - Advanced token metrics calculation (RSI, momentum indicators)

- **Advanced Address Intelligence**
  - Common address interaction detection
  - Address clustering for entity identification
  - Transaction pattern analysis between multiple addresses

- **Infrastructure Improvements**
  - Comprehensive automated testing suite for all MCP endpoints
  - MCPO OpenAPI endpoint testing framework
  - Performance optimization for data-intensive queries

- **Developer Features**
  - ErgoScript contract analysis
  - Oracle pool integration
  - DEX price and liquidity data

### Phase 3 (Future Enhancement)

**Status: Planned**

- Advanced analytics and visualization data
- Transaction pattern recognition
- Simplified transaction creation
- Smart contract simulation
- Enhanced security features

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

## Technical Architecture

### Component Diagram

```
[User/AI Assistant] → [MCP Client]
                            ↓
[Ergo Explorer MCP Server] ← [Cache Layer]
          ↓           ↓           ↓
    [Explorer API] [Node API] [3rd Party APIs]
          ↓           ↓           ↓
    [Explorer Node] [Ergo Node] [External Services]
```

### Service Architecture

1. **Core Server**
   - MCP protocol implementation
   - Request handling and routing
   - Response formatting

2. **API Integration Layer**
   - Explorer API client
   - Node API client
   - Third-party API clients

3. **Tool Implementation Layer**
   - Blockchain tools
   - Address tools
   - Transaction tools
   - Token tools
   - Contract tools

4. **Cache Layer**
   - Response caching
   - Rate limiting
   - Request deduplication

## Metrics and Success Criteria

1. **Usage Metrics**
   - Number of active users/installations
   - Queries per day
   - Unique tool usage distribution
   - Average response time

2. **Quality Metrics**
   - Response accuracy
   - System uptime
   - Error rate
   - Cache hit ratio

3. **Success Criteria**
   - Successful integration with multiple AI assistant platforms
   - Positive user feedback (> 4.5/5 average rating)
   - Growing monthly active users
   - Expanding tool set coverage

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