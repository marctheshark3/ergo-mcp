# API Usage Guide

This document provides guidance on when to use each API service in the Ergo Explorer MCP.

## API Service Overview

### Ergo Explorer API
**Best for:**
- Basic address and transaction queries
- General blockchain information
- Quick lookups that don't require specialized data

**Use when:**
- You need basic blockchain data
- You want fast, cached responses
- You don't need real-time data

### Direct Node API
**Best for:**
- Real-time blockchain data
- Unconfirmed transaction information
- Direct blockchain interaction
- Custom queries

**Use when:**
- You need the most up-to-date data
- You need unconfirmed transaction data
- You're working with mempool transactions
- You need to submit transactions

### ErgoWatch API
**Best for:**
- Advanced blockchain analytics
- Historical balance tracking
- Rich lists and rankings
- Contract and P2PK statistics

**Use when:**
- You need historical balance data
- You want to analyze address rankings
- You need contract usage statistics
- You're tracking exchange addresses

## API Selection Guidelines

1. **For Basic Queries:**
   - Start with the Ergo Explorer API
   - Fall back to Node API if real-time data is needed

2. **For Analytics:**
   - Use ErgoWatch API for historical and statistical data
   - Combine with Explorer API for current state

3. **For Real-time Data:**
   - Use Node API for immediate state
   - Consider caching responses for repeated queries

## Performance Considerations

- Explorer API: Cached data, fastest responses
- Node API: Real-time data, may be slower
- ErgoWatch API: Best for analytical queries

## Error Handling

Each API may have different error responses and rate limits. Always implement proper error handling and respect rate limits:

- Explorer API: Standard rate limits apply
- Node API: Local resource limits
- ErgoWatch API: Standard rate limits apply

## Examples

### Address Analysis Workflow
```python
# Get current balance from Explorer
current_balance = await get_address_balance(address)

# Get historical data from ErgoWatch
balance_history = await get_address_balance_history(address)

# Check unconfirmed transactions from Node
unconfirmed = await get_address_balance_from_node(address)
``` 