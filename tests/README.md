# Ergo Explorer MCP Tests

This directory contains tests for the Ergo Explorer MCP tools and API.

## Test Structure

The tests are organized into the following directories:

- `api/`: Tests for the API routes and tools (focusing on functionality and integration)
- `unit/`: Unit tests for individual components and functions
- Root directory: Tests that don't fit neatly into the above categories

## Running Tests

### Using the Test Runner

We provide a test runner script that makes it easy to run specific tests or categories of tests:

```bash
# List all available tests
./run_ergo_tools_tests.py --list

# Run a specific test (without .py extension)
./run_ergo_tools_tests.py --test test_blockchain_routes

# Run all tests in a category
./run_ergo_tools_tests.py --category api

# Run all tests
./run_ergo_tools_tests.py --all

# Run with verbose output
./run_ergo_tools_tests.py --all --verbose
```

### Using pytest Directly

You can also use pytest directly:

```bash
# Run all tests
pytest

# Run a specific test file
pytest api/test_blockchain_routes.py

# Run a specific test function
pytest api/test_blockchain_routes.py::test_blockchain_status

# Run with verbose output
pytest -v
```

## Adding New Tests

When adding new tests:

1. Follow the existing structure and naming conventions
2. Create test files with the prefix `test_`
3. Create test functions with the prefix `test_`
4. Use fixtures for common setup and teardown
5. Mock external dependencies where appropriate

For API route tests:
- Place them in the `api/` directory
- Use the `mock_mcp`, `mock_context`, and route-specific fixtures
- Follow the pattern in existing tests to register routes and test them

For unit tests:
- Place them in the `unit/` directory
- Focus on testing individual functions and components
- Mock dependencies as needed

## Test Dependencies

Tests rely on the following:

- pytest
- pytest-asyncio (for testing async functions)
- unittest.mock (for mocking dependencies)

Make sure these are installed in your development environment.

## Troubleshooting

### Permission Issues with Logging

If you encounter permission issues related to logging configuration (e.g., "Permission denied" when trying to write to log files), you can use the isolated tests instead.

See the `/isolated_tests` directory for tests that don't rely on the actual codebase and avoid logging configuration issues.

```bash
# Run isolated tests
cd ../isolated_tests
./run_isolated_tests.py --all
```

### Import Errors

If you encounter import errors or circular dependencies, you can also use the isolated tests which have no dependencies on the actual codebase.

## Related Documentation

- Check out `/isolated_tests/README.md` for information about running isolated tests that don't depend on the actual codebase. 