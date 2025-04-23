# MCP Ergo Tool Status Report

This report summarizes the observed status and presumed data sources for the MCP Ergo tools based on recent testing attempts, comparing observed behavior against standard Ergo Node API endpoints.

**Key Observation:** Several core Ergo tools appear to be failing due to incorrect interaction with the underlying Ergo Node API provided by the MCP server's target node (presumed to be `http://host.docker.internal:9053`). The errors suggest issues with API path configuration, request formation, or response parsing within the MCP server component.

**Standard Ergo Node API Endpoints (Verified):**
*   `/info`: Returns node status, including `fullHeight`. (Successfully tested)
*   `/blocks/at/{height}`: Returns header ID(s) for the block at `{height}`. (Successfully tested)
*   `/blocks/{headerId}`: Returns full block details for the given `{headerId}`. (Successfully tested)
*   `/transactions/unconfirmed/size`: Returns the count of mempool transactions. (Targeted by `mempool_status`, results in `400 Bad Request`)

| Tool Name                     | Expected Node Endpoint(s)                 | Observed Status | Error/Diagnosis                                                                                                |
| :---------------------------- | :---------------------------------------- | :-------------- | :------------------------------------------------------------------------------------------------------------- |
| `mcp_ergo_blockchain_status`  | `/info`                                   | **Failing**     | `AttributeError: 'str' object has no attribute 'get'`. Likely hitting wrong path or failing to parse JSON response. |
| `mcp_ergo_get_block_by_height`| `/blocks/at/{height}` then `/blocks/{id}` | **Failing**     | Initial "No block found" (potentially valid if height > `fullHeight`) + likely affected by `AttributeError` during response parsing. |
| `mcp_ergo_mempool_status`     | `/transactions/unconfirmed/size`          | **Failing**     | `400 Bad Request`. Indicates malformed request or node issue with this specific endpoint. Recommend removal/disabling. |
| *Other Core Blockchain Tools* | *(Varies, e.g., `/transactions/{txId}`)* | *Untested*      | *Likely affected by similar API interaction issues.*                                                          |

**Conclusion:**

The MCP Ergo tools `mcp_ergo_blockchain_status` and `mcp_ergo_get_block_by_height` are not correctly utilizing the standard Ergo Node API endpoints or are failing to parse the responses. The `mcp_ergo_mempool_status` tool consistently fails with a `400 Bad Request`, suggesting it should be disabled or requires significant investigation into the node's behavior at `/transactions/unconfirmed/size`.

**Recommendation:**

This report should be forwarded to the administrators or developers responsible for the MCP server instance. They need to:
1.  Verify and correct the API endpoint paths used by the `blockchain_status` and `get_block_by_height` tools within the MCP server component to match the standard `/info`, `/blocks/at/`, and `/blocks/` endpoints.
2.  Implement robust JSON response parsing and error handling for these tools.
3.  Investigate the `400 Bad Request` for `mempool_status` or disable/remove the tool. 