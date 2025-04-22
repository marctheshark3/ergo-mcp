# Ergo Node API Documentation

This document provides a comprehensive guide to the Ergo Node APIs, including endpoints, request/response formats, and examples.

## Table of Contents

- [Blockchain APIs](#blockchain-apis)
- [UTXO APIs](#utxo-apis)
- [Script APIs](#script-apis)
- [Scan APIs](#scan-apis)
- [Mining APIs](#mining-apis)
- [Wallet APIs](#wallet-apis)
- [Transaction APIs](#transaction-apis)
- [Block APIs](#block-apis)
- [Peer APIs](#peer-apis)
- [Utility APIs](#utility-apis)
- [NiPoPoW APIs](#nipopow-apis)

## Blockchain APIs

### Get Indexed Height
```
GET /blockchain/indexedHeight
```
Get current indexed block height. The indexer has processed all blocks up to this height.

**Response:**
```json
{
  "indexedHeight": 1000000,
  "fullHeight": 1000050
}
```

### Get Transaction by ID
```
GET /blockchain/transaction/byId/{txId}
```
Retrieve a transaction by its ID.

**Parameters:**
- `txId`: Transaction ID (hex-encoded)

**Response:**
```json
{
  "id": "2ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
  "inputs": [...],
  "outputs": [...],
  "size": 1000
}
```

### Get Transaction by Index
```
GET /blockchain/transaction/byIndex/{txIndex}
```
Retrieve a transaction by its global index number.

**Parameters:**
- `txIndex`: Transaction index number

**Response:** Same as transaction by ID

### Get Transactions by Address
```
POST /blockchain/transaction/byAddress
```
Retrieve transactions associated with an address.

**Parameters:**
- `offset` (query, optional): Number of items to skip
- `limit` (query, optional): Maximum items to return
- Request body: Address string

**Response:**
```json
{
  "items": [
    {
      "id": "2ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
      "inputs": [...],
      "outputs": [...],
      "size": 1000
    }
  ],
  "total": 100
}
```

### Get Transaction Range
```
GET /blockchain/transaction/range
```
Get a range of transaction IDs.

**Parameters:**
- `offset` (query, optional): Number of items to skip
- `limit` (query, optional): Maximum items to return

**Response:**
```json
[
  "2ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
  "1cd9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd118"
]
```

### Get Box by ID
```
GET /blockchain/box/byId/{boxId}
```
Retrieve a box by its ID.

**Parameters:**
- `boxId`: Box ID (hex-encoded)

**Response:**
```json
{
  "boxId": "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
  "value": 1000000000,
  "ergoTree": "0008cd...",
  "assets": [...],
  "creationHeight": 100000
}
```

### Get Box by Index
```
GET /blockchain/box/byIndex/{boxIndex}
```
Retrieve a box by its global index number.

**Parameters:**
- `boxIndex`: Box index number

**Response:** Same as box by ID

### Get Boxes by Token ID
```
GET /blockchain/box/byTokenId/{tokenId}
```
Retrieve boxes containing a specific token.

**Parameters:**
- `tokenId`: Token ID (hex-encoded)

**Response:**
```json
{
  "items": [
    {
      "boxId": "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
      "value": 1000000000,
      "assets": [...],
      "creationHeight": 100000
    }
  ],
  "total": 10
}
```

### Get Unspent Boxes by Token ID
```
GET /blockchain/box/unspent/byTokenId/{tokenId}
```
Retrieve unspent boxes containing a specific token.

**Parameters:**
- `tokenId`: Token ID (hex-encoded)

**Response:** Same as boxes by token ID

### Get Boxes by Address
```
POST /blockchain/box/byAddress
```
Retrieve boxes associated with an address.

**Parameters:**
- Request body: Address string

**Response:** Same as boxes by token ID

### Get Unspent Boxes by Address
```
POST /blockchain/box/unspent/byAddress
```
Retrieve unspent boxes associated with an address.

**Parameters:**
- Request body: Address string

**Response:** Same as boxes by token ID

### Get Box Range
```
GET /blockchain/box/range
```
Get a range of box IDs.

**Parameters:**
- `offset` (query, optional): Number of items to skip
- `limit` (query, optional): Maximum items to return

**Response:**
```json
[
  "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
  "2cd9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd118"
]
```

### Get Boxes by ErgoTree
```
POST /blockchain/box/byErgoTree
```
Retrieve boxes by their associated ErgoTree.

**Parameters:**
- Request body: Hex-encoded ErgoTree

**Response:** Same as boxes by token ID

### Get Unspent Boxes by ErgoTree
```
POST /blockchain/box/unspent/byErgoTree
```
Retrieve unspent boxes by their associated ErgoTree.

**Parameters:**
- Request body: Hex-encoded ErgoTree

**Response:** Same as boxes by token ID

### Get Token by ID
```
GET /blockchain/token/byId/{tokenId}
```
Retrieve token information.

**Parameters:**
- `tokenId`: Token ID (hex-encoded)

**Response:**
```json
{
  "id": "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
  "boxId": "2cd9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd118",
  "name": "TestToken",
  "description": "Test Token Description",
  "decimals": 2,
  "type": "EIP-004"
}
```

### Get Tokens List
```
POST /blockchain/tokens
```
Retrieve minting information about multiple tokens.

**Response:**
```json
{
  "items": [
    {
      "id": "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
      "boxId": "2cd9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd118",
      "name": "TestToken",
      "description": "Test Token Description",
      "decimals": 2,
      "type": "EIP-004"
    }
  ],
  "total": 100
}
```

### Get Address Balance
```
POST /blockchain/balance
```
Get confirmed and unconfirmed balance for an address.

**Parameters:**
- Request body: Address string

**Response:**
```json
{
  "confirmed": {
    "nanoErgs": 1000000000,
    "tokens": [
      {
        "tokenId": "1ab9da11fc216660e974842cc3b7705e62ebb9e0bf5ff78e53f9cd40abadd117",
        "amount": 100,
        "decimals": 2,
        "name": "TestToken"
      }
    ]
  },
  "unconfirmed": {
    "nanoErgs": 0,
    "tokens": []
  }
}
```

## Error Responses

All endpoints may return the following error response:

```json
{
  "error": 400,
  "reason": "Invalid request",
  "detail": "Detailed error message"
}
```

## Authentication

Some endpoints require an API key to be included in the request headers:

```
api_key: YOUR_API_KEY
```

## Rate Limiting

The node may implement rate limiting. Please check the response headers for rate limit information:

```
X-Rate-Limit-Limit: 60
X-Rate-Limit-Remaining: 59
X-Rate-Limit-Reset: 1623456789
``` 