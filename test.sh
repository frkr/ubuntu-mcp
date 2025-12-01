#!/usr/bin/env bash
set -euo pipefail

docker build --platform linux/amd64 -t frkr/ubuntu-mcp:22.04 .

# Clean up any previous container
docker rm -f ubuntu-mcp >/dev/null 2>&1 || true

# Run container detached and map port 9000
docker run --platform linux/amd64 -v`pwd`:/home/mcpuser --rm -d --name ubuntu-mcp -p 9000:9000 frkr/ubuntu-mcp:22.04

# Wait for health endpoint
echo "Waiting for server to become healthy on http://localhost:9000/health ..."
for i in {1..30}; do
  if curl -sf http://localhost:9000/health >/dev/null; then
    echo "Server is up"
    break
  fi
  sleep 1
done

echo "Executing sample command via HTTP API..."
curl -s -X POST http://localhost:9000/api/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}' | jq .

echo "Recent container logs:"
docker logs ubuntu-mcp --tail 50 || true

echo "Removing container..."
docker rm -f ubuntu-mcp

echo "Done!"