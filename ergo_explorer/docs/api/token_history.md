# Historical Token Holder API Documentation

This document describes the API endpoints for tracking and analyzing historical token ownership on the Ergo blockchain.

## Endpoints

### Get Historical Token Holders

```
GET /token/historical-holders
```

Retrieve historical token holder distribution data showing how token ownership has changed over time. This endpoint provides both time-series snapshots of ownership concentration and individual token transfers.

#### Parameters

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|----------|
| token_id | string | Token ID to analyze | N/A | Yes |
| days_back | integer | Number of days to look back from today | null | No* |
| start_date | string | Start date in ISO format (YYYY-MM-DD) | null | No* |
| end_date | string | End date in ISO format (YYYY-MM-DD) | Current date | No |
| period | string | Time period for snapshots (daily, weekly, monthly, quarterly, yearly) | "monthly" | No |
| update_data | boolean | Whether to update historical data | false | No |
| lookup_days | integer | Days to look back when updating | 30 | No |
| offset | integer | Number of transfers to skip (pagination) | 0 | No |
| limit | integer | Maximum transfers to return per page | 100 | No |
| max_transactions | integer | Maximum number of transactions to look back | null | No** |
| use_boxes_endpoint | boolean | Use box/byTokenId endpoint for more efficient lookup | false | No |

\* Either `days_back` OR `start_date` should be provided, but not both.  
\** When `max_transactions` is provided, time-based parameters are ignored.

#### Lookup Methods

The API supports two different methods for looking up historical token data:

1. **Time-based lookup** (default): Use `days_back` or `start_date`/`end_date` to specify a time range.
2. **Transaction-based lookup**: Use `max_transactions` to specify how many past transactions to analyze and set `use_boxes_endpoint=true`.

The transaction-based lookup can be more efficient for tokens with a lot of activity, as it directly uses the `/blockchain/box/byTokenId/<tokenId>` endpoint to analyze the most recent transactions.

#### Example Requests

**Time-based lookup:**
```
GET /token/historical-holders?token_id=8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1&days_back=30
```

**Transaction-based lookup:**
```
GET /token/historical-holders?token_id=8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1&max_transactions=100&use_boxes_endpoint=true
```

#### Example Response

```json
{
  "status": "success",
  "token_id": "8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1",
  "token_info": {
    "id": "8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1",
    "name": "Example Token",
    "decimals": 0,
    "type": "EIP-004"
  },
  "snapshots": [
    {
      "timestamp": "2023-01-01T00:00:00",
      "holder_count": 45,
      "gini_coefficient": 0.82,
      "top_holders": {
        "top_1_percent": 56.2,
        "top_5_percent": 78.9,
        "top_10_percent": 92.4
      },
      "distribution": {
        "9hwWcMhrebzF41Cv7Kbgpx4PjeE2CZjP6JiFJQhM5TTKv1P6Rfc": 4500,
        "9gEcxPe4zyGXLMcXNG3rtq9XZ1VQBwxnSrz4YExRvXPEUT7WJeZ": 3200,
        // ... more addresses
      }
    },
    // ... more snapshots
  ],
  "recent_transfers": [
    {
      "tx_id": "a7e0c5800a0a064c5800a564c58a3c5800a0c5800a0c5800a0c580",
      "timestamp": "2023-02-15T18:32:45",
      "from_address": "9hwWcMhrebzF41Cv7Kbgpx4PjeE2CZjP6JiFJQhM5TTKv1P6Rfc",
      "from_address_condensed": "9hwWc...6Rfc",
      "to_address": "9gEcxPe4zyGXLMcXNG3rtq9XZ1VQBwxnSrz4YExRvXPEUT7WJeZ",
      "to_address_condensed": "9gEcx...WJeZ",
      "amount": 500,
      "amount_formatted": "500"
    },
    // ... more transfers
  ],
  "pagination": {
    "offset": 0,
    "limit": 100,
    "total": 245,
    "has_more": true
  },
  "query": {
    "token_id": "8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1",
    "period": "monthly",
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-02-28T23:59:59",
    "max_transactions": null,
    "use_boxes_endpoint": false
  }
}
```

## Error Responses

In case of an error, the API will return a response with an `error` field describing the issue:

```json
{
  "status": "error",
  "error": "Token ID not found",
  "token_id": "8e1e2418742582115958cd971ce38c000c782981d63aad5aba1bdb5d6ffeceb1"
}
```

## Notes

- The `update_data` parameter can be used to refresh the historical data before returning results. This may significantly increase response time for tokens with many transactions.
- The `period` parameter determines the frequency of snapshots in the returned dataset (e.g., "daily", "weekly", "monthly").
- Snapshot data includes Gini coefficient and top holder percentages to measure wealth concentration.
- The transaction-based lookup approach (`max_transactions` with `use_boxes_endpoint=true`) can be more efficient for recent data but may not cover the full history of the token.
- Historical data is cached to improve performance on subsequent requests. 