# Ergo Validation Tools

This directory contains validation tools to test the Ergo project's tokenomics and smart contract analysis features with real Ergo blockchain data.

## Overview

Two validation scripts are provided:

1. **validate_features.py**: Runs a comprehensive validation of all new features with predefined test cases
2. **quick_validate.py**: Allows quick validation of specific features via command-line arguments

These scripts will help ensure that the newly implemented features work correctly with real data from the Ergo blockchain without requiring manual testing.

## Prerequisites

- Python 3.7+
- Installed requirements from the project
- Connection to the internet to reach Ergo blockchain APIs

## Using validate_features.py

This script tests all the tokenomics and smart contract analysis features with predefined test cases. It runs automatically without additional input and generates a report.

```bash
# Run the comprehensive validation
./validate_features.py
```

The script will:

1. Test tokenomics features (price info, price charts, liquidity pools, token swaps)
2. Test smart contract analysis features (contract analysis, statistics, simulation)
3. Generate a detailed report showing which tests passed or failed
4. Save the results to a JSON file for further analysis

## Using quick_validate.py

This script allows targeted validation of specific features through command-line arguments. It's useful for testing individual features quickly.

```bash
# Show help with all available commands
./quick_validate.py --help
```

### Examples

Test token price information:
```bash
./quick_validate.py price SigUSD
```

Get liquidity pool information:
```bash
# All pools
./quick_validate.py pools

# Pools for specific token
./quick_validate.py pools SigUSD
```

Get token swap estimate:
```bash
./quick_validate.py swap ERG SigUSD 10
```

Analyze a smart contract:
```bash
./quick_validate.py contract 9hXmgvzndtakdSAgJ92fQ8ZjuKirYEPnQZ2KumygbrJao1rr5ko
```

Get contract statistics:
```bash
./quick_validate.py contract-stats
```

Simulate contract execution:
```bash
./quick_validate.py contract-sim 9hXmgvzndtakdSAgJ92fQ8ZjuKirYEPnQZ2KumygbrJao1rr5ko
```

## Understanding Results

The validation scripts provide detailed output for each test:

- **Success**: The feature is working correctly with real data
- **Error**: The feature returned an error or unexpected result
- **Timing**: How long each operation took to complete

## Troubleshooting

If validation fails, check the following:

1. Internet connectivity to Ergo blockchain APIs
2. Correct configuration in your .env file (API endpoints, etc.)
3. The contract addresses or token IDs used in the tests still exist on the blockchain
4. The Ergo node is running and accessible (for contract analysis features)
5. Make sure the `ergo` module is properly installed or in your Python path

## Adding Custom Test Cases

You can modify these scripts to test with your own token IDs, contract addresses, or other parameters by editing the token and contract lists in the `validate_features.py` file or by passing different arguments to `quick_validate.py`.

## Unit Testing

The validation scripts are also covered by unit tests to ensure they function correctly. You can run these tests with:

```bash
pytest tests/test_validation.py
``` 