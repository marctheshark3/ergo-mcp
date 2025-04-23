# MCP Ergo Tool Fix Implementation Plan

This document outlines the plan to fix the MCP Ergo tools based on the findings in `report.md`. The primary goal is to ensure `mcp_ergo_blockchain_status` and `mcp_ergo_get_block_by_height` correctly interact with the standard Ergo Node API endpoints on the target node (`http://host.docker.internal:9053`) and handle responses robustly. The `mcp_ergo_mempool_status` tool will be removed.

## Implementation Phases

**Phase 1: Deep Dive Investigation & Logging (MCP Server Component)**

*   [ ] **Task:** Instrument the MCP Server Ergo component to log the exact outgoing request (URL, headers, body) and the full raw incoming response (status code, headers, body) for calls intended for the target node's `/info`, `/blocks/at/{height}`, and `/blocks/{headerId}` endpoints when the corresponding MCP tools are invoked.
*   [ ] **Goal:** Confirm the precise point of failure (e.g., wrong URL called, malformed request sent, unexpected response format received) for `blockchain_status` and `get_block_by_height`.
*   [ ] **Verification:** Review logs after invoking the failing tools to understand the exact request/response flow and identify the root cause of the `AttributeError`.

**Phase 2: Fix `mcp_ergo_blockchain_status` (MCP Server Component)**

*   [ ] **Task:** Modify the tool's handler to explicitly target the `/info` endpoint on `http://host.docker.internal:9053`.
*   [ ] **Task:** Implement correct JSON parsing for the response, specifically extracting `fullHeight`, `difficulty`, etc.
*   [ ] **Task:** Add robust error handling (e.g., try-except blocks) to manage potential `JSONDecodeError`, `KeyError` (if fields are missing), or network errors. Return a meaningful error message to the MCP tool caller in case of failure.
*   [ ] **Testing:**
    *   [ ] Unit tests mocking `/info` responses (valid JSON, error string, JSON missing fields).
    *   [ ] Integration test calling the tool end-to-end.

**Phase 3: Fix `mcp_ergo_get_block_by_height` (MCP Server Component)**

*   [ ] **Task:** Refactor the handler to perform the two-step API call:
    1.  Call `/blocks/at/{height}` on `http://host.docker.internal:9053`.
    2.  Parse the response array for the header ID.
    3.  If found, call `/blocks/{headerId}` on `http://host.docker.internal:9053` using the obtained ID.
*   [ ] **Task:** Implement robust JSON parsing for *both* API responses.
*   [ ] **Task:** Handle errors gracefully: height not found (return specific message), header ID not found, non-JSON responses, network errors.
*   [ ] **Testing:**
    *   [ ] Unit tests mocking `/blocks/at/` and `/blocks/` responses (success, height not found, header not found, invalid JSON).
    *   [ ] Integration test calling the tool with valid and invalid heights.

**Phase 4: Remove `mcp_ergo_mempool_status` (MCP Server Component)**

*   [ ] **Task:** Remove the code handler for the `mcp_ergo_mempool_status` tool within the MCP Server Ergo component.
*   [ ] **Task:** Update any tool registration or manifest files to remove `mcp_ergo_mempool_status` from the list of available Ergo tools.
*   [ ] **Verification:** Ensure the tool is no longer listed or callable.

**Phase 5: Deployment & Verification**

*   [ ] **Task:** Deploy the updated MCP server component to the relevant environment.
*   [ ] **Task:** Perform end-to-end verification:
    *   [ ] Call `mcp_ergo_blockchain_status` and confirm it returns correct data.
    *   [ ] Call `mcp_ergo_get_block_by_height` with a known valid height and confirm it returns correct block data.
    *   [ ] Call `mcp_ergo_get_block_by_height` with a known future height and confirm it returns an appropriate "not found" message.
    *   [ ] Confirm `mcp_ergo_mempool_status` is no longer available or callable. 