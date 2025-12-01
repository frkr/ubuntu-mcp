#!/usr/bin/env -S deno run --allow-net

import { Client } from "npm:@modelcontextprotocol/sdk@latest/client/index.js";

// Implementação básica do MCPClient para o exemplo
class MCPClient {
    private client?: Client;

    async connect(serverName: string) {
        console.log(`Conectando ao servidor: ${serverName}`);
        // Aqui você implementaria a conexão real com o servidor MCP
        // usando as configurações do mcp.json
        return true;
    }

    async call(method: string, params: any) {
        console.log(`Chamando método: ${method}`, params);

        // Simulação de execução de comando via HTTP para o servidor ubuntu_mcp
        try {
            const response = await fetch("http://localhost:9000/api/exec", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(params),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error("Erro ao executar comando:", error);
            return { error: error.message };
        }
    }
}

// Conectar ao servidor ubuntu_mcp
const client = new MCPClient();
await client.connect("ubuntu_mcp");

// Executar comando
const result = await client.call("execute", {
    command: "ls -la"
});

console.log(result);
