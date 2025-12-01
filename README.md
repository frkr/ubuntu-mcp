# Ubuntu MCP — Ubuntu Command Server (Dockerized)

This project provides a small Ubuntu-based container that exposes a safe-ish HTTP API to execute shell commands inside the container. It also includes an MCP (Model Context Protocol) tool definition using FastMCP when run in stdio mode. By default, the Docker image serves an HTTP API with FastAPI/Uvicorn on port 9000.

> The goal here is to provide a sandbox for other AI`s to run local code without changing the system.

Contents:

- Ubuntu 22.04 base image
- Python 3 with FastAPI, Uvicorn, and FastMCP
- HTTP endpoints:
  - GET `/health` — health check
  - POST `/api/exec` — execute a command in the container and get back `returncode`, `stdout`, `stderr`
- Optional FastMCP tools available when running `server.py` directly (stdio transport)

Prerequisites

- Docker (recommended)
- curl (for quick tests)
- jq (optional, for pretty-printing JSON in examples)

Quick start (Docker)

1) Build the image (Apple Silicon/ARM users: the project pins linux/amd64 for compatibility):

```bash
docker build --platform linux/amd64 -t frkr/ubuntu-mcp:22.04 .
```

2) Run the container, mounting your current directory into `/home/mcpuser` and exposing port 9000:

```bash
docker run --platform linux/amd64 \
  -v "$(pwd)":/home/mcpuser \
  --rm -d --name frkr/ubuntu-mcp \
  -p 9000:9000 \
  frkr/ubuntu-mcp:22.04
```

3) Check health:

```bash
curl -s http://localhost:9000/health
# {"status":"ok"}
```

4) Execute a command via HTTP:

```bash
curl -s -X POST http://localhost:9000/api/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}' | jq .
```

Stop and remove the container:

```bash
docker rm -f ubuntu-mcp
```

One-liner run (current directory):

```bash
docker run --platform linux/amd64 -v"$(pwd)":/home/mcpuser --rm -d --name ubuntu-mcp -p 9000:9000 frkr/ubuntu-mcp:22.04
```

API reference

- GET `/health`
  - Response: `{ "status": "ok" }`

- POST `/api/exec`
  - Request JSON:
    ```json
    { "command": "ls -la" }
    ```
  - Response JSON (example):
    ```json
    {
      "returncode": 0,
      "stdout": "total 0\n-rw-r--r-- 1 mcpuser mcpuser 0 Dec  1 00:00 example.txt\n",
      "stderr": null
    }
    ```
  - Notes:
    - Commands run with a 30s timeout; on timeout, `returncode` will be `124` and `stderr` will describe the timeout.
    - The working directory is `/home/mcpuser` (where your volume is mounted in the examples).

Demo script

There is a helper script that builds the image, runs the container, waits for readiness, calls the API, prints logs, and cleans up:

```bash
./test.sh
```

## MCP integration notes

- The included `mcp.json` is a minimal mapping to demonstrate pointing a client/tooling layer at the HTTP exec endpoint:
  ```json
  {
    "mcpServers": {
      "ubuntu_mcp": {
        "description": "Ubuntu Command Server, its only way to execute commands because of security.",
        "url": "http://localhost:9000/api/exec"
      }
    }
  }
  ```
- `server.py` defines several FastMCP tools (`execute_command`, `list_directory`, `get_current_directory`, `get_system_info`). These are available when running in stdio mode (`python3 server.py`). When serving over HTTP (Uvicorn), you interact via the REST API described above.
- A small Deno example is provided in `testdeno.ts` that POSTs to the HTTP API:
  ```bash
  deno run --allow-net testdeno.ts
  ```

Security considerations

- The `/api/exec` endpoint executes arbitrary shell commands sent by the client.
- Do not expose this service to untrusted networks.
- Prefer running inside a disposable container, as shown here.
- The container uses a non-root user (`mcpuser`), but that does not eliminate risk.

Troubleshooting

- Port already in use: change `-p 9000:9000` to another host port.
- Apple Silicon (ARM64) hosts: the examples specify `--platform linux/amd64`. You can omit it if building/running natively for ARM, but ensure base/image compatibility.
- Volume permissions: if you cannot see files inside the container, check the path you mounted and permissions. On Windows, adjust the `-v` path syntax accordingly.

License

MIT — see [LICENSE](LICENSE).
