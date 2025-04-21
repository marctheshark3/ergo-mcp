# Ergo Explorer MCP Resources Implementation

## Overview

This document outlines our plan to implement MCP resources for the Ergo Explorer MCP server. Resources provide a way to expose content from our server to LLMs in an application-controlled manner, which is ideal for static or semi-static content like EIPs.

## Current Status

- [x] Basic MCP server implementation with tools
- [x] Resource capability implementation
- [x] EIP resources implementation
- [ ] Blockchain resources implementation

## Resource Types to Implement

### 1. EIP Resources (Priority)

- **URI Scheme**: `ergo://eips/{number}`
- **Content Type**: HTML (converted from Markdown)
- **Implementation Status**: Complete

### 2. Blockchain Reference Resources

- **URI Scheme**: `ergo://docs/{category}/{topic}`
- **Content Type**: Text
- **Implementation Status**: Not started

### 3. Token Information Resources

- **URI Scheme**: `ergo://tokens/{tokenId}`
- **Content Type**: JSON
- **Implementation Status**: Not started

## Implementation Steps

1. ✅ Add resource capabilities to server configuration
2. ✅ Create resource URI handlers 
3. ✅ Connect existing data sources to resource endpoints
4. ✅ Add resource discovery mechanisms
5. [ ] Implement resource update notifications
6. [ ] Test resource access from different MCP clients

## Resource URIs Design

We'll use the following URI structure for all Ergo resources:

```
ergo://{resource_type}/{resource_id}
```

Examples:
- `ergo://eips/4` (EIP-4 document)
- `ergo://tokens/0cd8c9f416e5b1ca9f986a7f10a84191dfb85941619e49e53c0dc30ebf83324b` (Token information)
- `ergo://docs/contracts/proxy` (Documentation on proxy contracts)

## How to Use Resources in Practice

### From an MCP Client

1. **Discover Available Resources**
   - Client makes a `resources/list` request to our server
   - Server responds with all available resources
   - Client displays these resources to the user or selects relevant ones based on heuristics

2. **Access Resource Content**
   - Client makes a `resources/read` request with the resource URI
   - Server responds with the resource content
   - Client provides this content to the LLM as context

3. **Stay Updated**
   - Client subscribes to resource updates with `resources/subscribe`
   - Server notifies client when resources change via `notifications/resources/updated`
   - Client refreshes content as needed

### From the Server Side

1. **Registering Resources**
   ```python
   @app.list_resources()
   async def list_resources() -> list[types.Resource]:
       return [
           types.Resource(
               uri="ergo://eips/4",
               name="EIP-4: Assets Standard",
               description="Standard for issuing and tracking custom tokens",
               mimeType="text/html"
           ),
           # Other resources...
       ]
   ```

2. **Serving Resource Content**
   ```python
   @app.read_resource()
   async def read_resource(uri: str) -> dict:
       # Parse the URI and retrieve content
       # ...
       
       return {
           "contents": [
               {
                   "uri": uri,
                   "mimeType": "text/html",
                   "text": content
               }
           ]
       }
   ```

3. **Notifying About Updates**
   ```python
   async def update_resources():
       # Update resource content
       # ...
       
       # Notify clients
       await app.notify_resources_list_changed()
   ```

## Client Usage Examples

### Python Client Example

```python
import asyncio
from mcp.client import Client

async def main():
    # Connect to the Ergo Explorer MCP server
    async with Client("http://localhost:3001") as client:
        # List available resources
        resources = await client.list_resources()
        
        # Print available EIPs
        for resource in resources:
            if resource.uri.startswith("ergo://eips/"):
                print(f"Found EIP: {resource.name}")
        
        # Read a specific EIP
        eip4_uri = "ergo://eips/4"
        eip4_content = await client.read_resource(eip4_uri)
        
        # Use the content with an LLM
        print(f"EIP-4 content: {eip4_content.contents[0].text[:100]}...")  # First 100 chars

asyncio.run(main())
```

### TypeScript Client Example

```typescript
import { Client } from '@mcp/client';

async function main() {
  // Connect to the Ergo Explorer MCP server
  const client = new Client('http://localhost:3001');
  
  try {
    // List available resources
    const resources = await client.listResources();
    
    // Filter for EIP resources
    const eipResources = resources.filter(r => r.uri.startsWith('ergo://eips/'));
    console.log(`Found ${eipResources.length} EIPs`);
    
    // Read a specific EIP
    if (eipResources.length > 0) {
      const firstEip = eipResources[0];
      const content = await client.readResource(firstEip.uri);
      
      console.log(`${firstEip.name} content:`);
      console.log(content.contents[0].text.substring(0, 100) + '...'); // First 100 chars
    }
  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

## Next Steps

1. ✅ Create base resource handler classes
2. ✅ Implement EIP resources (highest priority)
3. ✅ Add resource capability to server configuration
4. [ ] Test with Claude and other MCP clients
5. [ ] Add resource update notifications
6. [ ] Expand to other resource types 