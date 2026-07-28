# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure
The project (English JATEL) is a multi-language teaching app (**English, Spanish, French**): a FastAPI backend that serves both the API and a static frontend SPA from a single server. Language selector (`lang`) in the top bar switches between EN/ES/FR.

- **`backend/`** — FastAPI app (`main.py`), business logic (`engine.py`), data-driven content (`grammar.json`, `grammar_es.json`, `grammar_fr.json`, `memhack.json`, `memhack_es.json`, `memhack_fr.json`), user store, and serves `frontend/`
- **`frontend/`** — build-free SPA: `index.html`, `style.css`, `app.js`, `auth.js`, `login.html` (vanilla HTML/CSS/JS, no framework)
- **`mcp/`** — `server.py`, an MCP (stdio) server exposing backend capabilities as tools, reusing `engine.py`
- **`k8s/`** — Kubernetes manifests (namespace, configmap, pvc, deployment, service, kustomization)
- **`docker-compose.yaml`, `Dockerfile`** — containerized deployment
- **`docs/`** — `technical/` (architecture, k8s deploy, versioning) and `user/` (guide)
- **`skills/`, `prompts/`, `brainstore/`, `scripts/`** — original skill/prompt pipeline (brainstore notes → prompts)

## Common Development Tasks

### Run locally
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # OS Python is externally-managed (PEP 668)
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# open http://localhost:8000
```
Alternative if no venv: `pip install -r requirements.txt --break-system-packages`.

### Run with Docker
```bash
docker compose up -d --build
# http://localhost:8000  (login admin / mudar123)
```

### Run the MCP server (stdio)
```bash
python mcp/server.py
```
Connect to Claude Desktop / OpenCode — see `docs/technical/mcp.md`.

### Validate (no test suite / lint / typecheck configured in this repo)
```bash
# Backend smoke test (no server needed):
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
# Frontend syntax check:
node --check frontend/app.js
```
### Backup Procedures (Obrigatório antes de alterações)

Antes de fazer QUALQUER alteração no código, configuração ou conteúdo, você DEVE seguir os procedimentos de backup da skill `backup-procedures`.

Esta skill está disponível em `.opencode/skills/backup-procedures/SKILL.md` e fornece:

- Procedimentos para criar backup local completo antes de alterações
- Verificação da integridade do backup
- Instruções para restaurar do backup se necessário
- Melhores práticas para proteção contra erros humanos

Como usar:

```bash
# Pergunte se deseja fazer backup (sempre faça isso primeiro!)
# Crie diretório de backup e copie o repositório (excluindo o próprio backup)
mkdir -p repo-backup
rsync -av --exclude='repo-backup/' . ./repo-backup/

# Verifique se o backup foi criado corretamente
find . -type f | ! -path "./repo-backup/*" | wc -l
find ./repo-backup -type f | wc -l
```
### Kubernetes
```bash
kubectl apply -k k8s/
kubectl -n english-jatel port-forward svc/english-jatel 8080:80
```

## Architecture (non-obvious points)

- **Route priority**: in `backend/main.py`, the `/api/*` routes are registered **before** `app.mount("/", StaticFiles(...))`, so the API wins over static files. `GET /` serves `frontend/index.html`.
- **Single backend module**: all logic (correction, TTS, STT, conversation, content) lives in `backend/engine.py`. `main.py` is routing + auth only.
- **Auth**: middleware `auth_guard` protects `/` and `/api/*` (except public routes) via an HMAC-signed HttpOnly session cookie (`engine.verify_token`). Admin-only routes (`_require_admin`): `register`, `users`, `reload-grammar`. Any authenticated user can change their own password. Default admin `admin`/`mudar123`; passwords stored as PBKDF2 (per-user salt) in `backend/data/users.json` (gitignored).
- **LLM**: OpenRouter (text-only) via OpenAI-compatible client. `engine.py` reads `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`) and points `BASE_URL` to `https://openrouter.ai/api/v1`. Demo mode works without a key (heuristic correction).
- **TTS**: `engine.tts_bytes` tries Edge TTS (neural, no key) → OpenAI `tts-1` → `pyttsx3` (offline). Fallback in frontend: `speechSynthesis`. Voice via `EDGE_TTS_VOICE` env or `voice` param.
- **Multi-language**: every endpoint accepts `lang` (`en`/`es`/`fr`). TTS uses `LANG_VOICES`, STT adjusts recognition language, LLM prompts adapt via `LANG_META`. Grammar and MemHack files are per-language (`grammar_es.json`, `grammar_fr.json`, `memhack_es.json`, `memhack_fr.json`). Progress is namespaced as `{user}::{lang}`.
- **Content is data-driven** (edit files, not code):
  - Listen/Read: `LISTEN`/`READ` dicts in `engine.py`, keyed `level → category → list`; `get_content` uses a shuffled queue per `(level, module, category)` (no repeats until exhausted).
  - Grammar (CEFR A1–C2 per language): `backend/grammar.json` (`{"levels": [...], "grammar": {<level>: [{topic, structure, explanation, examples}]}}`), loaded at startup (falls back to embedded). Reload at runtime via `POST /api/admin/reload-grammar` (admin only).
  - MemHack (spaced repetition / SRS): `backend/memhack.json` (`{"categories": [...], "phrases": {<category>: [{id, en, pt}]}}`); per-user progress in `DATA_DIR/memhack_progress.json`. Leitner-style boxes 1–5 with growing intervals (1min→10min→1h→1d→7d); `review` moves box up (facil)/hold (medio)/down (dificil).

## Important conventions

- **Never commit** `backend/.env` or `backend/data/users.json` (both gitignored). LLM key goes via env/secret, never baked into the image.
- **Listen is a dictation exercise**: the frontend hides the sentence text until "Verificar" — don't pre-reveal it.
- **Frontend is vanilla JS** with relative URLs (`/api/...`), so it works served from the same server. No build step.
- Versioning is by git tags (`v*`) — `cd.yaml` builds/pushes the Docker image only on a `v*` tag push. Keep `main` green; cut tags for releases.

## Key files
- `backend/main.py` — FastAPI app, routes, auth middleware
- `backend/engine.py` — all business logic (correction, TTS, STT, conversation, content, auth helpers)
- `backend/grammar.json` / `backend/memhack.json` — data-driven lesson/phrase content
- `mcp/server.py` — MCP stdio server wrapping `engine.py`
- `frontend/app.js`, `frontend/auth.js` — client logic
- `k8s/` — Kubernetes manifests
