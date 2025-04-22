# Unit Testing TODO

## Issue Summary

The ergo-explorer-mcp codebase has undergone significant refactoring which broke the existing test suite. The main architectural changes include:

1. Functions previously imported directly from `server.py` have been moved to specific modules in the `api/routes/` directory
2. API endpoints are now defined at function scope inside `register_*_routes` functions, not at module level
3. The routing structure has changed to use a more modular approach with domain-specific route files
4. Some functions have been renamed or replaced with new implementations

## High-Level Tasks

- [x] Identify broken test imports
- [x] Add temporary workaround using `collect_ignore` in `conftest.py`
- [ ] Update test architecture to match new codebase structure
- [ ] Re-enable all tests
- [ ] Add new tests for newly added functionality

## Specific Test Files to Fix

### 1. `test_server.py`

- [ ] Remove direct imports of functions from `api/routes/*` modules
- [ ] Create a proper context and MCP server instance for testing
- [ ] Update tests to call tools through the MCP server instance
- [ ] Update mocks to patch the correct API functions
- [ ] Consider splitting into multiple test files by domain (blockchain, token, etc.)

### 2. `test_address_tools.py`

- [ ] Update imports to use functions from `api/routes/deprecated`
- [ ] Fix assertions to match new return types (dict vs str)
- [ ] Update mocking approach to work with new API client

### 3. `test_network_tools.py`

- [ ] Update imports to use the correct module paths
- [ ] Update test expectations to match new return types
- [ ] Create proper mocks for the underlying API functions

### 4. `test_token_tools.py`

- [ ] Update import for `search_for_token` to use `search_for_token_from_node` from `tools/node`
- [ ] Update test structure to correctly mock the API calls

### 5. `test_misc_tools.py`

- [ ] Update import for `get_network_status` to the correct location
- [ ] Ensure test matches the new implementation details

### 6. `test_token_holders.py`

- [ ] Fix the `test_get_token_holders_success` test to account for changes in pagination
- [ ] Update mocking strategy to properly stub out API calls

## Test Architecture Changes

The new testing approach should follow these principles:

1. **Server-based testing**: Instead of importing and calling functions directly, tests should create a test MCP server and use it to invoke tools

```python
@pytest.fixture
def test_mcp():
    """Create a test MCP server with all routes registered."""
    from ergo_explorer.server_config import create_server
    server = create_server()
    return server

@pytest.mark.asyncio
async def test_blockchain_status(test_mcp):
    """Test blockchain_status tool via the MCP server."""
    # Use the server to invoke tools
    result = await test_mcp.invoke_tool("blockchain_status", {})
    assert "Ergo Blockchain Status" in result
```

2. **Proper Context Objects**: Create mock `Context` objects for testing functions that expect them

```python
@pytest.fixture
def mock_context():
    """Create a mock context object for MCP tool functions."""
    from mcp.server.fastmcp import Context
    ctx = MagicMock(spec=Context)
    ctx.path = "mock/path"
    ctx.method = "GET"
    ctx.json = {}
    ctx.headers = {}
    ctx.query_params = {}
    return ctx
```

3. **Direct Route Testing**: For functions inside route registration functions, extract and test them directly

```python
@pytest.mark.asyncio
async def test_blockchain_status_direct():
    """Test the blockchain_status function directly."""
    # Extract the function from the route registration
    from ergo_explorer.api.routes.blockchain import register_blockchain_routes
    
    # Create a mock MCP server to register routes
    mock_mcp = MagicMock()
    register_blockchain_routes(mock_mcp)
    
    # Extract the tool function that was registered
    blockchain_status = mock_mcp.tool.call_args_list[0][0][0]
    
    # Call it with a mock context
    result = await blockchain_status(mock_context)
    assert "Ergo Blockchain Status" in result
```

## Order of Implementation

1. Update `test_token_export.py` and `test_token_holders.py` first (already mostly working)
2. Create a new testing architecture for server-based tests
3. Implement new test approach for `test_server.py`
4. Fix remaining test files based on the new architecture
5. Verify all tests pass before removing `collect_ignore` entries

## Long-term Improvements

- [ ] Refactor tests to follow domain-based organization (matching the API routes structure)
- [ ] Add integration tests that test the full API flow
- [ ] Improve test coverage for edge cases and error conditions
- [ ] Add documentation on the new testing approach for future contributors 