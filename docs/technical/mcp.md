# Conectando o servidor MCP a um agente/IDE

O servidor em `mcp/server.py` expoe as capacidades do English Flow como ferramentas
MCP via **transporte stdio**. Um cliente MCP (agente/IDE) o executa como subprocesso.

> Substitua `<REPO>` pelo caminho absoluto do repo
> (ex.: `/home/devops/Desktop/projeto-aiops`). Use **caminhos absolutos** no `command`
> e em `args`, pois o cliente pode nao herdar o diretorio de trabalho esperado.

## Pré-requisitos

As dependencias devem estar no Python que vai executar o servidor:

```bash
pip install -r backend/requirements.txt -r mcp/requirements.txt   # ou --break-system-packages
```

`backend/.env` (OPENROUTER_API_KEY etc.) e carregado automaticamente por `engine.py`
no import — nenhuma configuracao extra de segredos no cliente.

## Testar o servidor manualmente

Em um terminal, o servidor fica aguardando JSON-RPC no stdin (nao tem saida propria):
```bash
python mcp/server.py
```
Se subir sem erro, esta pronto para ser conectado.

## Claude Desktop

Edite o arquivo de configuracao do Claude Desktop:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "english-flow": {
      "command": "<REPO>/.venv/bin/python",
      "args": ["<REPO>/mcp/server.py"]
    }
  }
}
```
- Se nao usar venv, troque `command` pelo `python3` (absoluto) que tem os pacotes `mcp` instalados.
- Reinicie o Claude Desktop. As ferramentas `correct_text`, `generate_tts`,
  `converse`, `get_content` aparecem no menu de ferramentas.

## OpenCode (exemplo — confira a documentacao do OpenCode)

OpenCode costuma declarar servidores MCP em `opencode.json` (ou `~/.config/opencode/`).
Exemplo representativo:

```json
{
  "mcpServers": {
    "english-flow": {
      "command": "<REPO>/.venv/bin/python",
      "args": ["<REPO>/mcp/server.py"]
    }
  }
}
```
> O nome da chave (`mcpServers`) e o local do arquivo podem variar entre versoes do
> OpenCode — valide na documentacao da sua instalacao antes de confiar neste trecho.

## Verificacao

Apos conectar, liste as ferramentas no cliente (ex.: comando "list tools" / seletor
de ferramentas). Esperado: `correct_text`, `generate_tts`, `converse`, `get_content`.
Um teste rapido: chamar `correct_text` com `"He go to school"` deve retornar a correcao.

## Troubleshooting

- **Ferramenta nao aparece**: confirme caminhos absolutos em `command`/`args` e que o
  Python aponta para o ambiente com `mcp` instalado (`python -c "from mcp.server.fastmcp import FastMCP"`).
- **Erro de correcao/TTS**: verifique `backend/.env` e acesso a rede (OpenRouter / Edge TTS).
- **PEP 668 (pip install falha)**: use venv ou `pip install --break-system-packages`.
- **Erro de import do engine**: o servidor adiciona `backend/` ao `sys.path` sozinho;
  nao rode o script de fora do repo sem esse caminho.
