FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip git curl wget jq dos2unix && \
    apt-get clean && \
    pip3 install fastmcp fastapi uvicorn

# Cria um usuário não-root opcional para segurança
RUN useradd -ms /bin/bash mcpuser

WORKDIR /home/mcpuser
VOLUME /home/mcpuser

# Copia o servidor e garante propriedade do usuário
COPY server.py /home/mcpuser
RUN chown mcpuser:mcpuser /home/mcpuser/server.py && \
    chmod +x /home/mcpuser/server.py

EXPOSE 9000

# Troca para usuário não-root somente após preparar os arquivos
USER mcpuser

# Execute com uvicorn para servir HTTP na porta 9000
CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9000"]