# Ergo Explorer MCP Response Format Documentation

This document contains the response format analysis for all Ergo Explorer MCP endpoints.

## Response Format Summary

| Endpoint | Response Type | Status Code | Execution Time (ms) |
|----------|--------------|-------------|--------------------|
| `get_block_by_height` | json | 500 | 13.14 |
| `get_block_by_hash` | json | 200 | 5.65 |
| `get_latest_blocks` | json | 200 | 5.17 |
| `get_block_transactions` | json | 500 | 97.8 |
| `blockchain_status` | json | 200 | 5.87 |
| `mempool_status` | json | 404 | 1.16 |
| `get_transaction` | json | 200 | 141.86 |
| `get_box` | json | 200 | 6.33 |
| `get_token` | json | 200 | 12.64 |
| `search_token` | json | 200 | 2.41 |
| `get_token_holders` | json | 200 | 4.68 |
| `get_collection_holders` | json | 200 | 4.74 |
| `search_collections` | json | 200 | 156.0 |
| `blockchain_address_info` | json | 200 | 167.79 |
| `get_address_book` | json | 200 | 633.51 |
| `get_address_book_by_type` | json | 200 | 900.36 |
| `search_address_book` | json | 200 | 443.91 |
| `get_address_details` | json | 200 | 409.21 |
| `list_eips` | json | 200 | 3.23 |
| `get_eip` | json | 200 | 2.35 |

## Detailed Endpoint Responses

### get_block_by_height

**Parameters:** ```json
{
  "height": 1000000
}
```

**Response Type:** json

**Status Code:** 500

**Response Excerpt:**

```json
{
  "detail": {
    "message": "Unexpected error",
    "error": "500: {'message': \"Error executing tool get_block_by_height: 'miner'\"}"
  }
}
```

### get_block_by_hash

**Parameters:** ```json
{
  "block_hash": "b28a36ee7882142e6d6d7aab9b50c1c1dfdd0efe98fd97348b19e16ab18c660f"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Failed to fetch block data from Node API: Client error '404 Not Found' for url 'http://localhost:9053/blocks/b28a36ee7882142e6d6d7aab9b50c1c1dfdd0efe98fd97348b19e16ab18c660f'\nFor more information check: https://httpstatuses.com/404"
```

### get_latest_blocks

**Parameters:** ```json
{
  "limit": 5
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Error fetching latest blocks: Client error '400 Bad Request' for url 'http://localhost:9053/blocks/latest?limit=5'\nFor more information check: https://httpstatuses.com/400"
```

### get_block_transactions

**Parameters:** ```json
{
  "block_id": "fffef98a416257b8785bffbec164b13f83c433ee602292766650b3bbe459140b"
}
```

**Response Type:** json

**Status Code:** 500

**Response Excerpt:**

```json
{
  "detail": {
    "message": "Unexpected error",
    "error": "500: {'message': \"Error executing tool get_block_transactions: format_block_transactions() missing 1 required positional argument: 'block_id'\"}"
  }
}
```

### blockchain_status

**Parameters:** ```json
{}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"# Ergo Blockchain Status\n\n    ## Current State\n    Blockchain Height Information:\n\u2022 Indexed Height: 1,510,699\n\u2022 Full Height: 1,510,699\n\u2022 Blocks Behind: 0\n\n    ## Network Metrics\n    name 'logger' is not defined\n\n    ## Performance\n    name 'logger' is not defined\n    "
```

### mempool_status

**Parameters:** ```json
{}
```

**Response Type:** json

**Status Code:** 404

**Response Excerpt:**

```json
{
  "detail": "Not Found"
}
```

### get_transaction

**Parameters:** ```json
{
  "tx_id": "ff9b418e98074562f337d3ece5bfabbe78c3e7f38c6536cc382827caf15c6890"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```
"Transaction Details for ff9b418e98074562f337d3ece5bfabbe78c3e7f38c6536cc382827caf15c6890:\n• Size: 48,545 bytes\n• Inputs: 1\n• Outputs: 1002\n\nInputs:\n1. Box ID: 8c7b690c7502c3d6979c72953dd3cb448793aa6d5b37679bc0e99e96ac0b7e55\n   Value: 70.170164392 ERG\n\nOutputs:\n1. Box ID: c0fc5a612c003e70e1e14398f29741334b86ec05fdc8b07905cea51a92c7d5e0\n   Address: 9gwF9RS5rnBqQcm1K7a7WUPTA1GA2SVWxHh9Wu7nXbTEQzAQfX8\n   Value: 0.000043000 ERG\n   Tokens:\n   - f0d5bdf474fcbd4249608e6dc6e9cf34a327b218f66445ea545b4c711b4676e3: 1,234,321\n2. Box ID: ae4ce3c3b8f93d1cd6825ac01b02dc1121a227531663ebc0e0b02a7136cc7bfa\n   Address: 9eaxQt2uci1WY6p6io8QCimXnHwwtQKnfrhAjAyMfyCHyPTqorT\n   Value: 0.000043000 ERG\n   Tokens:\n   - ebb40ecab7bb7d2a935024100806db04f44c62c33ae9756cf6fc4cb6b9aa2d12: 69,420\n3. Box ID: 1d6d7fc750d7a2dfd0975850cd90a8bb025c266e1d051814ac7e18f37bcdbe25\n   Address: 9eaxQt2uci1WY6p6io8QCimXnHwwtQKnfrhAjAyMfyCHyPTqorT\n   Value: 0.000043000 ERG\n   Tokens:\n   - 6ad70cdbf928a2bdd397041a36a5c2490a35beb4d20eabb5666f004b103c7189: 69,420\n4. Box ID: d5d124f0bee236dabe22964d92c3bb288546d64db430cbf7788572e1afd7afd0\n   Address: 9eaxQt2uci1WY6p6io8QCimXnHwwtQKnfrhAjAyMfyCHyPTqorT\n   Value: 0.000043000 ERG\n   Tokens:\n   - f0d5bdf474fcbd4249608e6dc6e9cf34a327b218f66445ea545b4c711b4676e3: 1,234,321\n5. Box ID: 5e85c122cb352bb549865f3006d9747034dc9f45257c5e48a73fc75fadcf3be5\n   Address: 9gtYyzQuJTnKvUfhmBvLasb9nkYwFsTJejZNUp751FyWixegP26\n   Value: 0.000043000 ERG\n   Tokens:\n   - ebb40ecab7bb7d2a935024100806db04f44c62c33ae9756cf6fc4cb6b9aa2d12: 69,420\n6. Box ID: 63f0c3f4902125c2a9c7dddbaf16b5030d472fafe3b0746f737f6b76805d42fb\n   Address: 9gtYyzQuJTnKvUfhmBvLasb9nkYwFsTJejZNUp751FyWixegP26\n   Value: 0.000043000 ERG\n   Tokens:\n   - 6ad70cdbf928a2bdd397041a36a5c2490a35beb4d20eabb5666f004b103c7189: 69,420\n7. Box ID: 9e651adb711cedf5ce129e5a542b62a6926e8ad23390f1fb89188cfbbc28e39c\n   Address: 9gtYyzQuJTnKvUfhmBvLasb9nkYwFsTJejZNUp751FyWixegP26\n   Value: 0.00004300...
```

### get_box

**Parameters:** ```json
{
  "box_id": "00e9dceb28aa5939209c3b2e984689b505c129a611c706eb25783811e7fa9d05"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Box Details for 00e9dceb28aa5939209c3b2e984689b505c129a611c706eb25783811e7fa9d05:\n\u2022 Value: 0.000043000 ERG\n\u2022 Creation Height: 1,237,593\n\u2022 ErgoTree: 0008cd036ba5cfbc03ea2471fdf02737f64dbcd58c34461a7ec1e586dcd713dacbf89a12\n\nTokens:\n\u2022 f0d5bdf474fcbd4249608e6dc6e9cf34a327b218f66445ea545b4c711b4676e3: 1,234,321\n"
```

### get_token

**Parameters:** ```json
{
  "token_id": "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Error getting token info: Client error '404 Not Found' for url 'http://localhost:9053/blockchain/token/byId/d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413'\nFor more information check: https://httpstatuses.com/404"
```

### search_token

**Parameters:** ```json
{
  "query": "ERG"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Error searching for tokens from node: Token search is not available through the node API"
```

### get_token_holders

**Parameters:** ```json
{
  "token_id": "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Error fetching token info: HTTP error: 404"
```

### get_collection_holders

**Parameters:** ```json
{
  "token_id": "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
{
  "error": "Error fetching collection token: HTTP error: 404"
}
```

### search_collections

**Parameters:** ```json
{
  "query": "Ergo"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"No collections found matching 'Ergo'"
```

### blockchain_address_info

**Parameters:** ```json
{
  "address": "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"Balance for 9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K:\n\u2022 0.000000000 ERG\n\nNo tokens found.\n\n## Recent Transactions\nNo transactions found for address 9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K."
```

### get_address_book

**Parameters:** ```json
{}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
{
  "items": [],
  "total": 0,
  "tokens": [],
  "error": "Could not reach API and fallback data could not be loaded."
}
```

### get_address_book_by_type

**Parameters:** ```json
{
  "type_filter": "Exchange"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
{
  "items": [],
  "total": 0,
  "tokens": []
}
```

### search_address_book

**Parameters:** ```json
{
  "query": "Exchange"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
{
  "items": [],
  "total": 0,
  "tokens": []
}
```

### get_address_details

**Parameters:** ```json
{
  "address": "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K"
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
{
  "found": false,
  "message": "Address not found in the address book"
}
```

### list_eips

**Parameters:** ```json
{}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```json
"# Ergo Improvement Proposals (EIPs)\n\n## EIP-22: Auction contract\nStatus: Unknown\n\n## EIP-19: Cold Wallet: an interaction protocol between Hot and Cold mobile wallets\nStatus: Unknown\n\n## EIP-5: EIP-0005: Contract Template\nStatus: Unknown\n\n## EIP-2: Ergo grant program\nStatus: Unknown\n\n## EIP-43: EIP-43: Reduced Transaction \nStatus: Unknown\n\n## EIP-1: Unknown Title\nStatus: Unknown\n\n## EIP-37: Unknown Title\nStatus: Unknown\n\n## EIP-20: ErgoPay: an interaction protocol between wallet application and dApp\nStatus: Unknown\n\n## EIP-21: Genuine tokens verification\nStatus: Unknown\n\n## EIP-17: Proxy contracts\nStatus: Unknown\n\n## EIP-34: NFT Collection Standard\nStatus: Unknown\n\n## EIP-29: Ergo Box Attachments\nStatus: Unknown\n\n## EIP-31: Unknown Title\nStatus: Unknown\n\n## EIP-27: Unknown Title\nStatus: Unknown\n\n## EIP-6: EIP-0006: Informal Smart Contract Protocol Specification Format\nStatus: Unknown\n\n## EIP-4: Assets standard\nStatus: Unknown\n\n## EIP-3: Unknown Title\nStatus: Unknown\n\n## EIP-25: Unknown Title\nStatus: Unknown\n\n## EIP-44: Arbitrary Data Signing Standard\nStatus: Unknown\n\n## EIP-15: Unknown Title\nStatus: Unknown\n\n## EIP-24: Artwork Standard\nStatus: Unknown\n\n## EIP-39: EIP-39 Monotonic box creation height rule\nStatus: Unknown\n\n"
```

### get_eip

**Parameters:** ```json
{
  "eip_number": 1
}
```

**Response Type:** json

**Status Code:** 200

**Response Excerpt:**

```
"<h1>UTXO-Set Scanning Wallet API</h1>\n<ul>\n<li>Author: kushti, Robert Kornacki</li>\n<li>Status: Proposed</li>\n<li>Created: 09-Aug-2019</li>\n<li>Implemented: Ergo Protocol Reference Client 3.3.0</li>\n<li>Last edited: 23-July-2020</li>\n<li>License: CC0</li>\n<li>Forking: not needed </li>\n</ul>\n<h2>Motivation</h2>\n<p>Currently, the Ergo node wallet is able to search for boxes protected only by simplest scripts associated with P2PK \naddresses which is a large barrier for dApps. This makes development of external applications which use smart contracts \nquite challenging. Development would involve scanning the blockchain state independently by the off-chain portion of \nthe dApp itself with handling forks, confirmation numbers, and so on.</p>\n<p>This Ergo Improvement Proposal focused on extending the wallet to be able to serve the needs of external applications by providing \na flexible scanning interface and the possibility for applications to register scans with the wallet to ensure that they are tracked. Scans that have successfully passed are considered to belong to the application.</p>\n<p>Each scan has a given scan ID, and each box found that matches said scan is tracked by the wallet and thus is associated with the scan ID. Among possible scans, there are some pre-defined scans <br />\nimplemented by the node wallet, to track wallet's public keys and also mining rewards. Other scans are not directly implemented inside of \nthe wallet but can be added by a user or an external application.</p>\n<h2>Specification: Scanning</h2>\n<p>A new request to scan is initiated which registers said scan to be checked for all future UTXO-set changes (thus it is forward-looking).</p>\n<p>A predicate (function which returns a boolean value for a box) is required to register a scan.\nPredicates available are:</p>\n<ul>\n<li><code>CONTAINS(register, value)</code> returns true if certain register contains given value. If <em>register</em> argument is missed, R1 (script re...
```

## Response Format Recommendations

Based on the above findings, here are recommendations for standardizing response formats:

All endpoints are returning JSON, which is the recommended format. However, the structure should be standardized as follows:

```json
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "metadata": {
    "execution_time_ms": 123,
    "result_size_bytes": 456,
    "is_truncated": false,
    "token_estimate": 789
  }
}
```

