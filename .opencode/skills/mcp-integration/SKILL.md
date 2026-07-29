---
name: mcp-integration
description: >
  Integra o projeto (skills geradas a partir de brainstore, ex.: english-jatel) com
  servidores MCP (Model Context Protocol): expoe capacidades como ferramentas MCP
  ou consome servidores MCP externos. Use para conectar as skills do repo a um
  agente/IDE via MCP, ou para dar as skills acesso a ferramentas externas.
---

# SKILL: mcp-integration

Scaffold para conectar as skills deste repositorio (ver `skills/english-jatel/`,
`brainstore/`, `scripts/`) a servidores MCP (Model Context Protocol).

> Estado: **parcialmente implementado**. `mcp/server.py` ja expoe as capacidades
> do backend como ferramentas MCP (transporte stdio). Veja "Como rodar". Nao inventa
> ferramentas alem das listadas em `mcp/server.py`.

## Quando usar
- Expor uma skill do repo (ex.: `english-jatel`) como um servidor MCP (ferramentas
  tipo `correct_text`, `generate_tts`, `converse`).
- Fazer uma skill consumir ferramentas de um servidor MCP externo (busca, arquivos, API).
- Padronizar descoberta e invocacao de skills via MCP em vez de prompt solto.

## Contexto do repositorio (verificado)
- Pipeline: `brainstore/ideias-*.md` -> `scripts/convert_brainstore_to_prompt.py`
  -> `prompts/<skill>/` (markdown+json) -> `skills/<skill>/` (SKILL.md + codigo).
- `skills/english-jatel/` ja tem `SKILL.md` e `app.py` (prototipo CLI) e a app web
  em `backend/` (FastAPI) com endpoints `/api/*` documentados em `docs/technical/`.
- `mcp/` (raiz) existe mas esta vazio — provavel velocity para servidores MCP.

## Padrao sugerido (a implementar)
1. **Servidor MCP da skill** (em `mcp/`): um processo que registra ferramentas
   mapeadas dos endpoints do `backend` (ex.: `correct`, `tts`, `converse`).
   - Cada ferramenta expoe o mesmo contrato de `backend/main.py`
     (ver tabela em `docs/technical/arquitetura.md`).
2. **Cliente MCP na skill**: a skill pode chamar um servidor MCP externo para
   obter contexto (ex.: buscar frases de um banco, ler arquivos do usuario).
3. **Descoberta**: listar ferramentas via `tools/list`; invocar via `tools/call`.
   Manter nomes estaveis (snake_case) e schemas de entrada/saida documentados.

## Como rodar (servidor ja implementado)
O servidor reusa `backend/engine.py` (sem duplicar logica) e expoe 4 ferramentas MCP:

| Ferramenta | Entrada | Retorno |
|-----------|---------|---------|
| `correct_text` | `text`, `level` | correcao (ERRO->CORRECAO->REGRA->SUGESTAO) |
| `generate_tts` | `text`, `voice?` | MP3 em base64 (vazio se indisponivel) |
| `converse` | `level`, `persona`, `history?`, `message` | resposta da IA |
| `get_content` | `level`, `module`, `category?` | frase/texto de treino |

```bash
# dependencias
pip install -r backend/requirements.txt -r mcp/requirements.txt   # ou --break-system-packages
# sobe o servidor MCP (stdio)
python mcp/server.py
```
Conecte a um cliente/agente MCP apontando para `mcp/server.py`. O servidor herda
`backend/.env` (OPENROUTER_API_KEY etc.) porque `engine.py` o carrega no import.

## Proximos passos (restantes)
- [x] `mcp/server.py` expondo `correct`/`tts`/`converse`/`get_content` via MCP (reusa `engine.py`)
- [ ] Cliente MCP na skill para consumir servidores externos (opcional)
- [x] Documentar a conexao a um agente/IDE em `docs/technical/mcp.md`

## Restricoes / boas praticas
- Nao duplicar a logica de `engine.py`: o servidor MCP deve importar/chamar o backend.
- Manter segredos no `backend/.env` (OPENROUTER_API_KEY etc.); o MCP server herda o env.
- Python externamente gerenciado (PEP 668): usar venv ou `pip install --break-system-packages`.

## Arquivos relacionados
- `skills/english-jatel/SKILL.md` — skill de exemplo ja documentada.
- `backend/main.py`, `backend/engine.py` — fonte real das capacidades.
- `docs/technical/arquitetura.md` — endpoints e arquitetura.
- `AGENTS.md` — convencoes gerais do repo.
