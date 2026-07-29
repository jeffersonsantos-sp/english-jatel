# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure
The project (JATEL-IA) is a multilingual teaching app (**English, Spanish, French**): a FastAPI backend that serves both the API and a static frontend SPA from a single server. Language selector (`lang`) switches between EN/ES/FR. Full UI i18n translates all labels, buttons, tabs, and messages.

- **`backend/`** — FastAPI app (`main.py`), business logic (`engine.py`), data-driven content (`grammar.json`, `grammar_es.json`, `grammar_fr.json`, `memhack.json`, `memhack_es.json`, `memhack_fr.json`), user store, and serves `frontend/`
- **`frontend/`** — build-free SPA: `index.html`, `style.css`, `app.js`, `auth.js`, `i18n.js` (120+ translation keys EN/ES/FR), `login.html` (vanilla HTML/CSS/JS, no framework)
- **`mcp/`** — `server.py`, an MCP (stdio) server exposing backend capabilities as tools, reusing `engine.py`
- **`k8s/`** — Kubernetes manifests (namespace, configmap, pvc, deployment-blue, deployment-green, service, kustomization)
- **`docker-compose.yaml`, `Dockerfile`** — containerized deployment
- **`docs/`** — `technical/` (architecture, k8s deploy, versioning, blue/green, render) and `user/` (guide)
- **`skills/`, `prompts/`, `brainstore/`** — AI agent skill/prompt pipeline

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
node --check frontend/app.js && node --check frontend/i18n.js
```

### Backup Procedures (required before changes)
Before making any code, config, or content changes, create a backup in `repo-backup/` (gitignored).

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
- **Multi-language**: every endpoint accepts `lang` (`en`/`es`/`fr`). TTS uses `LANG_VOICES`, STT adjusts recognition language, LLM prompts adapt via `LANG_META`. Grammar and MemHack files are per-language. Progress is namespaced as `{user}::{lang}`.
- **i18n UI**: `frontend/i18n.js` contains a translation dictionary with 120+ keys per language (EN/ES/FR). HTML elements use `data-i18n` attributes. `applyI18n()` is called on page load and on every language change. Dynamic strings in `app.js` use the `t()` helper function.
- **Content is data-driven** (edit files, not code):
  - Listen/Read: JSON files per language (`listen_es.json`, `read_fr.json`, etc.) or dicts in `engine.py` for EN.
  - Grammar (CEFR A1–C2): `grammar.json`, `grammar_es.json`, `grammar_fr.json` — reload via `POST /api/admin/reload-grammar`.
  - MemHack (SRS): `memhack.json`, `memhack_es.json`, `memhack_fr.json` — Leitner boxes 1–5.
- **UI layout**: Persona selector is inside the Conversation section header (not in topbar). Tab "Pronunciation" (was "Speak" before v1.12.2).

## Important conventions

- **Never commit** `backend/.env` or `backend/data/users.json` (both gitignored).
- **Listen is a dictation exercise**: the frontend hides the sentence text until "Verificar".
- **Frontend is vanilla JS** with relative URLs (`/api/...`). No build step.
- Versioning is by git tags (`v*`) — `cd.yaml` builds/pushes the Docker image only on a `v*` tag push.

## Key files
- `backend/main.py` — FastAPI app, routes, auth middleware
- `backend/engine.py` — all business logic (correction, TTS, STT, conversation, content, auth helpers)
- `frontend/i18n.js` — EN/ES/FR translation dictionary
- `frontend/app.js`, `frontend/auth.js` — client logic
- `mcp/server.py` — MCP stdio server wrapping `engine.py`
- `k8s/` — Kubernetes manifests (Blue/Green)
