#!/usr/bin/env python3
import subprocess
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor FastMCP
mcp = FastMCP("Ubuntu Command Server")

# FastAPI app for HTTP serving on port 9000
app = FastAPI(title="Ubuntu Command Server", version="1.0.0")


class ExecRequest(BaseModel):
    command: str


class ExecResponse(BaseModel):
    returncode: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None

@mcp.tool()
def execute_command(command: str) -> str:
    """Executa um comando no shell do Ubuntu e retorna o resultado.

    Args:
        command: O comando a ser executado no shell

    Returns:
        A saída do comando ou mensagem de erro
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = f"Return Code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"

        return output.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 30 seconds"
    except Exception as e:
        return f"ERROR: {str(e)}"

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """Lista os arquivos e diretórios em um caminho específico.

    Args:
        path: O caminho do diretório a listar (padrão: diretório atual)

    Returns:
        Lista de arquivos e diretórios
    """
    try:
        result = subprocess.run(
            ["ls", "-lah", path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {str(e)}"

@mcp.tool()
def get_current_directory() -> str:
    """Retorna o diretório de trabalho atual.

    Returns:
        Caminho do diretório atual
    """
    try:
        result = subprocess.run(
            ["pwd"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

@mcp.tool()
def get_system_info() -> str:
    """Retorna informações do sistema.

    Returns:
        Informações básicas do sistema
    """
    try:
        uname = subprocess.run(["uname", "-a"], capture_output=True, text=True)
        whoami = subprocess.run(["whoami"], capture_output=True, text=True)

        return f"System:\n{uname.stdout}User: {whoami.stdout}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# ------------------
# HTTP endpoints
# ------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/exec", response_model=ExecResponse)
def api_exec(req: ExecRequest) -> ExecResponse:
    try:
        result = subprocess.run(
            req.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return ExecResponse(
            returncode=result.returncode,
            stdout=result.stdout or None,
            stderr=result.stderr or None,
        )
    except subprocess.TimeoutExpired:
        return ExecResponse(returncode=124, stdout=None, stderr="Command timed out after 30 seconds")
    except Exception as e:
        return ExecResponse(returncode=1, stdout=None, stderr=str(e))


if __name__ == "__main__":
    # Retém compatibilidade: quando executado diretamente, mantém o modo stdio do MCP
    mcp.run(transport="stdio")