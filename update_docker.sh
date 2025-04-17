
# 2. Build the Docker image
docker build -t ergo-explorer-mcp:latest .

# 3. Stop any currently running container
docker stop ergo-mcp || true

# 4. Remove the old container
docker rm ergo-mcp || true

# 5. Run the new container
docker run -d --name ergo-explorer-mcp -p 8000:8000 ergo-explorer-mcp:latest