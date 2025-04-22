# Ergo Explorer MCP Migration Guide

This document outlines the steps needed to remove deprecated functionality and clean up the codebase to improve maintainability and reduce errors.

## Overview of Deprecated Components

1. **Deprecated API Routes** (`ergo_explorer/api/routes/deprecated.py`)
   - Several outdated API endpoints that redirect to newer implementations
   - Some implementations contain errors (like the address balance function)

2. **Monolithic Token Holders Implementation** (`ergo_explorer/tools/token_holders.py`)
   - Legacy file acting as a compatibility layer
   - The implementation has been moved to `ergo_explorer/tools/token_holders/` package

3. **Import References** 
   - Many files still import from deprecated paths
   - These should be updated to import from the new module structure

## Migration Plan

### Phase 1: Fix Immediate Issues

1. **Fix Address Balance Implementation**
   - Current Issue: `get_address_balance` in deprecated.py incorrectly redirects to token holders function
   - Correct implementation:
   ```python
   @mcp.tool()
   async def get_address_balance(ctx: Context, address: str) -> str:
       """Get the confirmed balance for an Ergo address."""
       logger.warning("get_address_balance is deprecated; use blockchain_address_info instead")
       from ergo_explorer.tools.address import get_address_balance
       return await get_address_balance(address)
   ```

2. **Create a New Address Info Tool**
   - Create a comprehensive blockchain_address_info tool in blockchain.py that combines balance and transaction data
   - This will be the recommended replacement for get_address_balance

### Phase 2: Update Import References

1. **Inventory Import References**
   - Run `grep -r "from ergo_explorer.tools.token_holders import" --include="*.py" .`
   - Update each reference to use the new modular imports

2. **Update Documentation**
   - Update README.md and other documentation to reference new functions 
   - Add migration notes for users

### Phase 3: Add Proper Deprecation Warnings

1. **Modify Deprecated Functions**
   - Add clear deprecation warnings with deprecation timeline
   - Example:
   ```python
   import warnings
   
   def deprecated_function():
       warnings.warn(
           "This function will be removed in version X.Y. "
           "Use new_function() instead.",
           DeprecationWarning,
           stacklevel=2
       )
       return new_function()
   ```

### Phase 4: Remove Deprecated Components

1. **Create a Cleanup Branch**
   - Branch name: `cleanup/remove-deprecated-components`

2. **Remove deprecated.py**
   - Delete the file after updating all references

3. **Remove token_holders.py**
   - Delete the legacy file after ensuring all imports use the new structure

4. **Update and Test Documentation**
   - Ensure all documentation is updated to reflect the new structure

## Specific Fixes

### Address Balance Issue Fix

The current implementation incorrectly directs `get_address_balance` to the token holders module:

```python
@mcp.tool()
async def get_address_balance(ctx: Context, address: str) -> str:
    """
    DEPRECATED: Use get_token_holders instead.
    Get the confirmed balance for an Ergo address.
    """
    logger.warning("get_address_balance is deprecated; use get_token_holders instead")
    from ergo_explorer.tools.token_holders.holders import get_token_holders as get_token_holders_impl
    return await get_token_holders_impl(address, include_raw=False, include_analysis=True)
```

This is incorrect as `get_token_holders` expects a token ID, not an address. The correct implementation should use `get_address_balance` from the address module:

```python
@mcp.tool()
async def get_address_balance(ctx: Context, address: str) -> str:
    """
    DEPRECATED: Use blockchain_address_info instead.
    Get the confirmed balance for an Ergo address.
    """
    logger.warning("get_address_balance is deprecated; use blockchain_address_info instead")
    from ergo_explorer.tools.address import get_address_balance
    return await get_address_balance(address)
```

### New Recommended API Structure

For better API organization, we recommend the following structure:

- **blockchain.py**: Core blockchain data including blocks, transactions, and network status
- **address.py**: Address-specific functions (balance, transactions, analysis)
- **token.py**: Token-specific functions (info, holders)
- **collections.py**: NFT collection functionality

## Testing Recommendations

1. **Unit Tests**
   - Create/update unit tests for all migrated functions
   - Ensure coverage of edge cases

2. **Integration Tests**
   - Test with real blockchain data
   - Verify API responses match expectations

3. **Regression Testing**
   - Test common use cases to ensure no functionality is broken
   - Create automated tests for critical paths

## Migration Timeline

1. **Immediate (Current Version)**
   - Fix critical issues (address balance lookup)
   - Update documentation

2. **Next Minor Release**
   - Add proper deprecation warnings
   - Begin updating import references

3. **Next Major Release**
   - Remove all deprecated components
   - Complete API cleanup

## Additional Recommendations

1. **API Versioning**
   - Consider implementing API versioning for future changes
   - Example: `/api/v1/...` and `/api/v2/...`

2. **Consistent Error Handling**
   - Implement consistent error handling across all API endpoints
   - Return structured error responses

3. **Documentation Generation**
   - Set up automatic documentation generation
   - Keep API documentation in sync with code

4. **Monitoring**
   - Add telemetry to track usage of deprecated functions
   - Inform users of upcoming removals 