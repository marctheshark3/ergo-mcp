# Ergo Explorer MCP Testing Infrastructure

This directory contains the testing infrastructure for the Ergo Explorer MCP, including response format standardization testing and performance benchmarking.

## Directory Structure

```
tests/
├── config/                          # Test configuration
│   ├── test_config.json             # General test configuration
│   └── endpoint_params.json         # Parameters for testing each endpoint
├── endpoint_tests/                  # Endpoint-specific tests
│   └── test_response_format.py      # Tests for response format standardization
├── performance/                     # Performance testing tools
│   ├── benchmarks.py                # Benchmark runner
│   └── visualization.py             # Visualization tools for benchmark results
├── run_benchmarks.py                # Main script to run benchmarks
├── reports/                         # Generated benchmark reports
└── TEST_README.md                   # This file
```

## Response Format Standardization

The MCP has been updated to provide standardized response formats across all endpoints:

- **Standard Format**: All responses include `status`, `data`, and `metadata` fields
- **Metadata**: Includes execution time, result size metrics, and token usage estimates
- **Smart Limiting**: Responses intelligently limit result sizes and indicate truncation
- **Verbose vs. Minimal**: Support for both verbose (with metadata) and minimal response formats

## Running Tests

### Response Format Tests

To test the standardized response format across all endpoints:

```bash
python -m tests.endpoint_tests.test_response_format
```

This will validate that all endpoints:
- Return responses with standard fields
- Include required metadata
- Return expected data fields
- Handle error cases properly
- Properly limit response sizes
- Support minimal response format

### Performance Benchmarks

To run performance benchmarks for all endpoints:

```bash
python -m tests.run_benchmarks
```

Command line options:
- `--categories`: Comma-separated list of endpoint categories to benchmark (default: all)
- `--iterations`: Number of benchmark iterations (default: 5)
- `--warmup`: Number of warmup iterations (default: 2) 
- `--concurrent`: Number of concurrent requests (default: 1)
- `--report-dir`: Directory to save reports (default: tests/reports)
- `--base-url`: Base URL for the API (default: http://localhost:3001)
- `--verbose`: Enable verbose output

Example:
```bash
python -m tests.run_benchmarks --iterations 10 --concurrent 5
```

## Benchmark Reports

The benchmark runner generates several outputs:

1. **JSON Data**: Raw benchmark results saved to `reports/benchmark_results.json`
2. **Charts**:
   - Response times (`reports/response_times.png`)
   - Token usage estimates (`reports/token_usage.png`)
   - Response sizes (`reports/response_sizes.png`)
3. **Report Summary**: Markdown summary at `reports/report.md`
4. **Endpoint Comparison**: Detailed comparison table at `reports/endpoint_comparison.md`

## Configuration

### Test Configuration

The `config/test_config.json` file contains configuration for test runs:

```json
{
    "general": {
        "base_url": "http://localhost:3001",
        "timeout": 10,
        "retries": 3
    },
    "performance": {
        "benchmark_iterations": 5,
        "warmup_iterations": 2,
        "concurrent_users": [1, 5, 10],
        "delay_between_requests": 0.5,
        "performance_threshold_ms": 2000,
        "memory_tracking_enabled": true
    },
    "token_tracking": {
        "enabled": true,
        "warning_threshold": 4000,
        "critical_threshold": 8000
    },
    "reporting": {
        "generate_charts": true,
        "output_directory": "tests/reports",
        "chart_formats": ["png"],
        "save_raw_data": true
    },
    "test_mode": {
        "use_mocks": false,
        "record_responses": true,
        "response_cache_dir": "tests/fixtures/responses"
    }
}
```

### Endpoint Parameters

The `config/endpoint_params.json` file contains test parameters for each endpoint, including:
- Valid parameter sets for positive testing
- Invalid parameter sets for error handling testing
- Expected fields to validate in responses

## Adding New Tests

### Adding a New Endpoint Test

To test a new endpoint:

1. Add test parameters to `config/endpoint_params.json`
2. The existing test modules will automatically include the new endpoint in their tests

### Adding a New Test Type

To add a new type of test:

1. Create a new test module in `endpoint_tests/`
2. Use the provided test infrastructure (config loading, endpoint parameters)
3. Implement the tests using standard pytest patterns 