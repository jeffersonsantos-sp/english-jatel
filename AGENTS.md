# AGENTS.md — English JATEL (multi-idioma)

App de ensino de **inglês, espanhol e francês** (listen/speak/write/read + conversação por IA).
Backend FastAPI serve a API **e** o frontend estático a partir de um único servidor.
Seletor de idioma no topo alterna entre **en** (Inglês), **es** (Espanhol), **fr** (Francês).

## Como rodar (um comando)
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Abra **http://localhost:8000** (o frontend `frontend/` é servido pelo próprio FastAPI; não há servidor estático separado).

## Ambiente Python (gotcha importante)
O Python deste SO é *externally managed* (PEP 668). `pip install` puro falha.
- Recomendado: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Alternativa: `pip install -r requirements.txt --break-system-packages`

## Segredos / config
- `backend/.env` contém `OPENROUTER_API_KEY`, `OPENAI_MODEL`, `OPENROUTER_TITLE`. Está no `.gitignore` — **não comitar**.
- `engine.py` carrega `.env` relativo ao próprio diretório (`backend/.env`).
- LLM usado: **OpenRouter** (texto-only). Não há TTS no OpenRouter; a voz vem do **Edge TTS** (sem chave, backend gera MP3). Fallback final no frontend: `speechSynthesis` do navegador.
- Para trocar a voz da IA: `export EDGE_TTS_VOICE=en-US-GuyNeural` (ou via seletor no topo da UI).
- **Seed de usuário normal**: variáveis `SEED_USERNAME` (padrão `jatel`) e `SEED_PASSWORD` (padrão `jatel2026`) criam um usuário não-admin no primeiro startup.

## Arquitetura (não óbvia pelos nomes)
- `backend/main.py`: rotas `/api/*` são registradas **antes** de `app.mount("/", StaticFiles(...))`, então elas têm prioridade sobre o estático. `GET /` retorna `frontend/index.html`.
- `backend/engine.py`: toda a lógica (correção, TTS, STT, conversa, conteúdo).
- `frontend/`: SPA vanilla (HTML/CSS/JS, sem build). `app.js` usa URLs relativas (`/api/...`).
- Banco de frases: dicionários `LISTEN`/`READ` em `engine.py`, chaveados por `nível -> categoria -> lista`. `get_content` usa uma fila embaralhada por `(nível, módulo, categoria)` (sem repetir até esgotar). **Para adicionar frases, edite esses dicionários.** `CATEGORIES` alimenta o seletor da UI.
- **Grammar (CEFR)**: conteúdo é **orientado a dados**, em `backend/grammar.json` (`{"levels": [...], "grammar": {<nível>: [{topic, structure, explanation, examples}]}}`). No startup o `engine.py` carrega esse arquivo (fallback ao dicionário embutido se faltar/inválido). **Para adicionar/editar lições de Grammar, edite `grammar.json`** e recarregue sem rebuild via `POST /api/admin/reload-grammar` (só admin). Para sobrescrever em runtime, monte um arquivo e ajuste `GRAMMAR_FILE`.
- **Multi-idioma**: cada idioma tem seu próprio grammar file (`grammar_es.json`, `grammar_fr.json`) e memhack file (`memhack_es.json`, `memhack_fr.json`). O seletor `lang` no frontend controla qual conteúdo é carregado.
- Listen é exercício de **ditado**: o frontend esconde o texto da frase até o "Verificar". Não antecipe a exibição.

## Validação (sem lint/testes configurados)
- Backend (sem subir servidor): `python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"`
- Frontend: `node --check frontend/app.js`
- Não há suíte de testes, typecheck ou lint neste repo.

## Pipeline original do projeto (brainstore → skill)
- `brainstore/ideias-*.md` (notas) → `scripts/convert_brainstore_to_prompt.py` → `prompts/<skill>/` (markdown + json).
- `skills/english-flow/` tem o protótipo CLI original (`app.py` + `SKILL.md`).

## Skills disponíveis (`.opencode/skills/`)
- **`english-jatel`** — app full-stack (módulos Listen/Speak/Write/Read/Conversar/Grammar/MemHack, auth, conteúdo orientado a dados, CI/CD por tags).
- **`english-jatel-render`** — deploy e operação no **Render** (Web Service Docker a partir do GitHub, ajustes de free tier: porta `$PORT`, voz via Web Speech API, keepalive, disco efêmero). Prompt base em `prompts/english-jatel-render/`.
- **`mcp-integration`** — integração MCP.
- Prompt de deploy Docker/Kubernetes: `prompts/english-jatel-deploy/`; doc em `docs/technical/deploy-kubernetes.md` e `docs/technical/deploy-render.md`.
