# Isolated Tests for Ergo Explorer MCP

This directory contains isolated tests for the Ergo Explorer MCP tools. These tests are designed to run independently of the main test framework, which can be helpful when encountering permission issues or import errors with the standard tests.

## Why Isolated Tests?

The standard test framework in `/tests` relies on imports from the actual codebase, which can lead to issues like:

1. Logging configuration errors (permission denied when writing to log files)
2. Import dependency issues
3. Configuration problems that prevent tests from running

These isolated tests use mocks and direct implementations to test the functionality without relying on the actual codebase.

## Running Isolated Tests

You can run the isolated tests using the included runner script:

```bash
# List all available tests
./run_isolated_tests.py --list

# Run a specific test
./run_isolated_tests.py --test test_address_balance

# Run all tests
./run_isolated_tests.py --all

# Run with verbose output
./run_isolated_tests.py --all -v
```

You can also run the tests directly with pytest:

```bash
# Run all isolated tests
python -m pytest .

# Run a specific test file
python -m pytest test_address_balance.py

# Run a specific test function
python -m pytest test_address_balance.py::test_get_address_balance_implementation
```

## Creating New Isolated Tests

When creating new isolated tests:

1. Create a new file with the prefix `test_` in this directory
2. Follow the pattern in existing tests:
   - Create fixtures for mocking MCP and Context
   - Define the tool implementation directly in the test file
   - Write test functions that verify the tool's behavior

Example:

```python
@pytest.fixture
def register_tools(mock_mcp):
    """Register the tools for testing."""
    @mock_mcp.tool()
    async def my_tool(ctx, param1, param2):
        """Mock my_tool implementation."""
        return f"Result for {param1} and {param2}"
    
    return mock_mcp

@pytest.mark.asyncio
async def test_my_tool(register_tools, mock_context):
    """Test my_tool."""
    my_tool = register_tools.tools["my_tool"]
    result = await my_tool(mock_context, "value1", "value2")
    assert "Result for value1 and value2" in result
```

## Tests Included

- `test_deprecated_routes.py`: Tests for deprecated routes like `get_address_balance`, `get_network_hashrate`, etc.
- `test_address_balance.py`: Specific tests for the `get_address_balance` tool functionality 