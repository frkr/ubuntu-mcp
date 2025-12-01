#!/usr/bin/env bash
set -euo pipefail

# Clean up any previous container
docker rm -f ubuntu-mcp >/dev/null 2>&1 || true

# Run container detached and map port 9000
docker run --platform linux/amd64 -v`pwd`:/home/mcpuser --rm -d --name ubuntu-mcp -p 9000:9000 frkr/ubuntu-mcp:22.04
echo run --platform linux/amd64 -v`pwd`:/home/mcpuser --rm -d --name ubuntu-mcp -p 9000:9000 frkr/ubuntu-mcp:22.04

echo "Done!"