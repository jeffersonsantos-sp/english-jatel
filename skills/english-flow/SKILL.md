---
name: english-jatel
description: >
  Multilingual AI-powered language learning app (EN/ES/FR) with Listen, Pronunciation,
  Write, Read, Conversation (AI), Grammar (CEFR A1–C2), and MemHack (SRS).
  Full i18n UI, CI/CD, Docker, Kubernetes Blue/Green, Render PaaS.
  Use to run, explain, extend, deploy, or operate this full-stack application.
---

# SKILL: english-jatel (JATEL-IA)

Multilingual language learning platform: FastAPI backend serves API + static SPA.
Supports **English, Spanish, French** with full UI internationalization (120+ translation keys).

## When to use
- Run, explain, or extend the JATEL-IA application.
- Add content (Grammar topics, MemHack phrases, Listen/Read sentences) per language.
- Integrate LLM/TTS/STT or adjust grammar correction.
- Deploy via Docker, Kubernetes, or Render.
- Operate CI/CD pipeline (GitHub Actions).

## Architecture (see docs/technical/arquitetura.md)
- `backend/main.py`: routes `/api/*` registered before `app.mount("/", StaticFiles(...))`
- `backend/engine.py`: all logic (correction, TTS, STT, conversation, content, auth)
- `frontend/`: SPA vanilla (`index.html`, `style.css`, `app.js`, `auth.js`, `i18n.js`)
- **i18n**: `i18n.js` contains EN/ES/FR dictionary (120+ keys). `applyI18n()` on load + lang change.
- **Tabs**: Listen, Pronunciation, Write, Read, Conversation, Grammar, MemHack
- **Persona**: inside Conversation section header (moved from topbar in v1.12.1)
- **Content**: data-driven JSON files per language (edit files, not code)

## How to run
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# Open http://localhost:8000
```

## Providers (config via env)
- **LLM**: OpenRouter (text-only, OpenAI-compatible)
- **TTS**: Edge TTS (neural, free) → OpenAI tts-1 → pyttsx3 fallback
- **STT**: Web Speech API (browser) → SpeechRecognition + ffmpeg (backend fallback)

## Modules
- **Listen**: dictation — TTS speaks, user types, check reveals answer
- **Pronunciation**: record voice → transcript → AI correction → listen to correction
- **Write**: free text → detailed correction (error → fix → rule → suggestion)
- **Read**: leveled text + glossary → comprehension question → correction
- **Conversation**: AI chat with personas (9 options) + voice support
- **Grammar**: CEFR lessons (A1–C2), 46+ topics per language, hot-reloadable
- **MemHack**: spaced repetition (Leitner boxes 1–5), per-user progress

## Key endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Status + LLM availability |
| POST | `/api/content` | Listen/Read content |
| POST | `/api/correct` | AI text correction |
| POST | `/api/tts` | Text-to-speech (MP3) |
| POST | `/api/stt` | Speech-to-text |
| POST | `/api/converse` | AI conversation |
| POST | `/api/grammar` | Grammar topic |
| POST | `/api/memhack/next` | Next SRS phrase |
| POST | `/api/memhack/review` | Record difficulty |

## How to extend
- **Add Grammar**: edit `backend/grammar_{lang}.json`, reload via `POST /api/admin/reload-grammar`
- **Add MemHack phrases**: edit `backend/memhack_{lang}.json`
- **Add Listen/Read**: edit `backend/listen_{lang}.json` or `backend/read_{lang}.json`
- **Add language**: see procedure in docs — create JSON content files + add option to `<select id="lang">`
- **New module**: add route in `main.py` + handler in `engine.py` + tab in `index.html` + logic in `app.js`

## Deployment
- **Docker**: `docker compose up -d --build`
- **Kubernetes**: `kubectl apply -k k8s/` (Blue/Green)
- **Render**: auto-deploy on push to `main`
- **CI/CD**: tag `v*` → `cd.yaml` builds + pushes to Docker Hub

## Validation
```bash
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
node --check frontend/app.js && node --check frontend/i18n.js
```

## Key files
- `backend/main.py`, `backend/engine.py`, `backend/.env`
- `frontend/index.html`, `frontend/app.js`, `frontend/i18n.js`, `frontend/auth.js`
- `k8s/` — Kubernetes manifests (Blue/Green)
- `docs/technical/` — architecture, deploy, versioning, blue/green
- `PROVAS_CRIACAO.md` — authorship proof
