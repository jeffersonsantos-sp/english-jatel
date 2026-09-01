# AGENTS.md — JATEL-IA

Multilingual AI-powered language learning app (English, Spanish, French).
FastAPI backend serves both the API and the static frontend SPA from a single server.

## How to run (one command)
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Open **http://localhost:8000** (the frontend `frontend/` is served by FastAPI itself; no separate static server).

## Python environment (important gotcha)
This OS Python is *externally managed* (PEP 668). Plain `pip install` fails.
- Recommended: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Alternative: `pip install -r requirements.txt --break-system-packages`
- STT uses `SpeechRecognition` (Google Speech API, free, no key) + `ffmpeg` for audio conversion. ffmpeg must be installed on the system.

## Secrets / config
- `backend/.env` contains `OPENROUTER_API_KEY`, `OPENAI_MODEL`, `OPENROUTER_TITLE`. It's in `.gitignore` — **never commit**.
- `engine.py` loads `.env` relative to its own directory (`backend/.env`).
- LLM: **OpenRouter** (text-only). TTS: **Edge TTS** (neural, no key needed). Fallback: browser `speechSynthesis`.
- To change AI voice: `export EDGE_TTS_VOICE=en-US-GuyNeural` (or via the UI voice selector).

## Architecture (not obvious from names)
- `backend/main.py`: `/api/*` routes are registered **before** `app.mount("/", StaticFiles(...))`, so API takes priority. `GET /` returns `frontend/index.html`.
- `backend/engine.py`: all logic (correction, TTS, STT, conversation, content).
- `frontend/`: SPA vanilla (HTML/CSS/JS, no build). `app.js` uses relative URLs (`/api/...`).
- Content is **data-driven**: Grammar in `grammar.json`/`grammar_es.json`/`grammar_fr.json`, MemHack in `memhack.json`/`memhack_es.json`/`memhack_fr.json`, Listen/Read in JSON files per language.
- **i18n**: `frontend/i18n.js` contains EN/ES/FR translation dictionary (120+ keys). HTML uses `data-i18n` attributes. `applyI18n()` is called on load and on every language change.
- **Persona selector**: located inside the Conversation section header (moved from topbar in v1.12.1).
- **Tabs**: Listen, Pronunciation (renamed from Speak in v1.12.2), Write, Read, Conversation, Grammar, MemHack.
- **STT**: Web Speech API (browser) with fallback to `/api/stt`. `lang` sent in FormData body.

## Validation (no lint/test suite configured)
- Backend (no server needed): `python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"`
- Frontend: `node --check frontend/app.js && node --check frontend/i18n.js`
- No test suite, typecheck, or lint configured in this repo.

## Backup procedures
Before making any code, config, or content changes, create a backup in `repo-backup/` (gitignored).

## Skills disponíveis

| Skill | Caminho | Uso |
|---|---|---|
| `setup-https` | `.opencode/setup-https/SKILL.md` | Configurar HTTPS/TLS com Let's Encrypt no AKS |
| `aks-deploy` | `.opencode/skills/aks-deploy/SKILL.md` | Deploy da app no AKS com Terraform |
| `azure-migration` | `.opencode/skills/azure-migration/SKILL.md` | Migração automatizada para nova conta Azure |

## Referências rápidas

- **HTTPS/TLS**: `.opencode/setup-https/SKILL.md` e `docs/technical/setup-https.md`
- **Deploy AKS**: `docs/technical/deploy-aks.md`
- **Prompt setup-https**: `prompts/setup-https/prompt-setup-https.md`
- **Migração Azure**: `.opencode/skills/azure-migration/SKILL.md` e `docs/technical/azure-migration.md`
- **Prompt migração**: `prompts/azure-migration/prompt-azure-migration.md`
