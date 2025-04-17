# Naming Conventions

This document establishes the naming conventions to be used throughout the codebase to ensure consistency and maintainability.

## Function Naming

### General Principles

1. Use descriptive names that clearly indicate the function's purpose
2. Follow a verb-noun pattern for function names
3. Use full words rather than abbreviations
4. Maintain consistency across related functions
5. Use snake_case for all function names

### Specific Patterns

| Entity Type | Function Pattern | Examples |
|-------------|------------------|----------|
| Transactions | `get_transaction_*` | `get_transaction`, `get_transaction_by_index` |
| Boxes | `get_box_*` | `get_box`, `get_box_by_index` |
| Tokens | `get_token_*` | `get_token`, `get_token_price`, `get_token_holders` |
| Blocks | `get_block_*` | `get_block_by_height`, `get_block_by_hash` |
| Addresses | `get_address_*` | `get_address_balance`, `get_address_transactions` |
| Node | `get_node_*` | `get_node_wallet`, `get_node_info` |
| Network | `get_network_*` | `get_network_status`, `get_mempool_status` |

### MCP Tool Naming

For MCP tools exposed in server.py:

1. Use the same function name as the underlying implementation
2. When exposing to MCP with a prefix, use `mcp_ergo_explorer_` followed by the function name
3. Do not use abbreviations like `tx` (use `transaction` instead)
4. Be consistent with parameter names across related functions

### Deprecated Functions

When deprecating functions:

1. Add "DEPRECATED" to the docstring with migration guidance
2. Update the function to use the new implementation internally
3. Keep the old name temporarily for backward compatibility
4. Add deprecation warnings that point to the new function
5. Add to the deprecated list in README.md

## Variable Naming

1. Use descriptive variable names that indicate purpose and type
2. Use snake_case for variable names
3. Use plural names for collections (lists, dicts, etc.)
4. Use type hints consistently to clarify variable types

## Module Naming

1. Use singular names for modules that focus on a specific entity (e.g., `token.py`)
2. Use lowercase names for all modules
3. Group related functionality in a single module
4. Name test modules with a `test_` prefix followed by the name of the module being tested

## Consistency Enforcement

These naming conventions should be enforced through:

1. Code reviews
2. Documentation updates
3. Refactoring of non-compliant code as it's encountered
4. Adding docstrings that follow these conventions 