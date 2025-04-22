# Ergo Explorer MCP Integration Tests

This directory contains integration tests for the Ergo Explorer MCP client. These tests connect to real Ergo blockchain endpoints to validate functionality.

## Environment Configuration

Tests use environment variables from `.env.test` to configure connections and test data. You can override these settings by creating a `.env.test.local` file (which is gitignored).

### Setting Up Environment Variables

1. Review the `.env.test` file for default settings
2. Create a `.env.test.local` file for your local overrides:
   ```
   # Example .env.test.local
   TEST_LOG_LEVEL=DEBUG
   SKIP_RATE_LIMITED_TESTS=true
   ```

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `ERGO_EXPLORER_API` | Base URL for Explorer API | https://api.ergoplatform.com/api/v1 |
| `ERGO_NODE_API` | Base URL for Node API | http://213.239.193.208:9053 |
| `SKIP_RATE_LIMITED_TESTS` | Skip tests that might be rate-limited | false |
| `API_TIMEOUT` | Timeout in seconds for API requests | 30 |
| `TEST_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

Test data like addresses, token IDs, and transaction IDs are also defined in the environment files.

## Running Tests

Install required packages:

```bash
pip install -r requirements.txt
```

Run all live integration tests:

```bash
pytest test_live_integration.py -v
```

Run a specific test:

```bash
pytest test_live_integration.py::test_live_blockchain_status -v
```

## Skipping Specific Tests

To skip specific tests that might be problematic in certain environments:

1. Set `SKIP_RATE_LIMITED_TESTS=true` to skip all rate-limited tests
2. Set specific test skip flags:
   ```
   SKIP_TEST_GET_TOKEN_HOLDERS=true
   ```

## Adding New Tests

When adding new tests:

1. Use environment variables for any test data
2. Add sensible defaults for backward compatibility
3. Add proper error handling and skip tests that fail due to external issues
4. Update this documentation as needed

## Troubleshooting

If tests fail with connection errors:
- Check your network connection
- Verify the API endpoints are accessible
- Increase the timeout with `API_TIMEOUT=60`
- Check if the Ergo nodes are experiencing issues

For authentication issues:
- Some APIs may require authentication - add appropriate credentials in `.env.test.local` 