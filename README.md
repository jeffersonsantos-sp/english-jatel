# JATEL-IA

### Multilingual AI-Powered Language Learning Platform

[![CI](https://github.com/jeffersonsantos-sp/english-jatel/actions/workflows/ci.yaml/badge.svg)](https://github.com/jeffersonsantos-sp/english-jatel/actions/workflows/ci.yaml)
[![CD](https://github.com/jeffersonsantos-sp/english-jatel/actions/workflows/cd.yaml/badge.svg)](https://github.com/jeffersonsantos-sp/english-jatel/actions/workflows/cd.yaml)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/updateinformatica/english-jatel)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-ready-326CE5?logo=kubernetes)](k8s/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v1.12.3-green)](https://github.com/jeffersonsantos-sp/english-jatel/releases)

> Full-stack application that trains **English, Spanish, and French** across Listen, Pronunciation, Write, Read, Conversation (AI-powered), Grammar (CEFR A1–C2), and Spaced Repetition (MemHack) — with a complete **i18n UI** that translates the entire interface per language.

---

## Screenshots

<table>
  <tr>
    <td align="center"><strong>🇺🇸 English</strong></td>
    <td align="center"><strong>🇪🇸 Español</strong></td>
    <td align="center"><strong>🇫🇷 Français</strong></td>
  </tr>
  <tr>
    <td><img src="img/front-en.png" alt="JATEL-IA English UI" width="400"></td>
    <td><img src="img/front-es.png" alt="JATEL-IA Spanish UI" width="400"></td>
    <td><img src="img/front-fr.png" alt="JATEL-IA French UI" width="400"></td>
  </tr>
</table>

---

## Highlights

| Capability | Details |
|-----------|---------|
| **3 Languages** | English, Spanish, French — full UI + content + TTS + STT |
| **7 Learning Modules** | Listen, Pronunciation, Write, Read, Conversation, Grammar, MemHack |
| **Full i18n** | Every label, button, tab, placeholder, and message translates when switching language |
| **AI Correction** | LLM-powered grammar/fluency correction via OpenRouter |
| **Neural TTS** | Edge TTS voices per language (zero cost, no API key) |
| **Speech-to-Text** | Web Speech API (browser) + backend fallback |
| **Spaced Repetition** | Leitner-style SRS with per-user progress persistence |
| **CEFR Grammar** | 46+ topics per language (A1–C2), data-driven, hot-reloadable |
| **Auth & Multi-user** | PBKDF2 passwords, admin roles, session cookies |
| **CI/CD** | GitHub Actions — CI on push, CD on git tag → Docker Hub |
| **Deploy Ready** | Docker, Docker Compose, Kubernetes (Blue/Green), Render (PaaS) |

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │         FastAPI Backend           │
                    │   main.py (routes + auth)         │
                    │   engine.py (logic + LLM + TTS)   │
                    ├──────────────────────────────────┤
  Browser ────────▶ │  /api/*   (JSON endpoints)        │
  localhost:8000    │  /         (static SPA frontend)   │
                    └──────────┬───────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ OpenRouter│   │ Edge TTS │   │ Web Speech   │
        │ (LLM)    │   │ (neural) │   │ API (STT)    │
        └──────────┘   └──────────┘   └──────────────┘
```

- **Single server** serves both API and static frontend (no separate build step)
- **Data-driven content**: edit JSON files to add lessons — no code changes needed
- **Multi-tenant SRS**: progress per user + language combination

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JS (SPA, no framework, no build) |
| **LLM** | OpenRouter (OpenAI-compatible API) |
| **TTS** | Edge TTS (neural voices, free) → OpenAI tts-1 → pyttsx3 fallback |
| **STT** | Web Speech API (browser) → SpeechRecognition + ffmpeg (backend fallback) |
| **Auth** | HMAC-signed HttpOnly cookies, PBKDF2 passwords |
| **Database** | JSON files (users.json, memhack_progress.json) |
| **Container** | Docker multi-stage (python:3.11-slim), 367MB |
| **Orchestration** | Docker Compose, Kubernetes (Kustomize, Blue/Green) |
| **CI/CD** | GitHub Actions (ci.yaml + cd.yaml) |
| **Hosting** | Docker Hub, Render (PaaS), Kubernetes |

---

## Quick Start

### Option 1 — Local (Python)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# Open http://localhost:8000
```

### Option 2 — Docker Compose

```bash
docker compose up -d --build
# Open http://localhost:8000
```

### Option 3 — Kubernetes

```bash
kubectl apply -k k8s/
kubectl -n english-jatel port-forward svc/english-jatel 8080:80
# Open http://localhost:8080
```

### Option 4 — Azure AKS (Production)

```bash
# 1. Provision infrastructure with Terraform
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 2. Configure kubectl
az aks get-credentials --resource-group rg-english-jatel --name aks-english-jatel

# 3. Install NGINX Ingress + cert-manager
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace \
    --set controller.service.type=LoadBalancer
helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager --create-namespace \
    --set installCRDs=true

# 4. Deploy application
kubectl apply -k k8s/

# 5. Configure DNS at registrar (Azure DNS name servers)
# 6. Access: https://learn.jfs-devops.shop
```


---

## Modules

### Listen (Dictation)
AI speaks a sentence → you type what you heard → check for accuracy. Text stays hidden until verification.

### Pronunciation (Speech)
Record your voice (or type) → get transcript + AI correction → listen to corrected version. Uses Web Speech API with backend fallback.

### Write (Writing)
Write a paragraph → receive detailed correction: error → fix → rule → suggestion.

### Read (Comprehension)
Read a leveled text with glossary → answer a comprehension question → get corrected.

### Conversation (AI Chat)
Chat with an AI persona (Café, Interviewer, Business, Travel, Family, Movies, Music, Football, DevOps) — in the selected language. AI speaks first option, voice recording support.

### Grammar (CEFR)
Lessons from A1 to C2: topic, structure formula, explanation, and example sentences with TTS. 46+ topics per language, data-driven from JSON.

### MemHack (Spaced Repetition)
Memorize phrases with Leitner-style SRS (boxes 1–5, intervals from 1min to 7days). Rate difficulty → system schedules next review. Progress persists per user.

---

## i18n — Full UI Internationalization

When switching language (English / Español / Français), **every UI element** translates:

| Element | EN | ES | FR |
|---------|----|----|-----|
| Tabs | Listen, Pronunciation, Write, Read, Conversation, Grammar, MemHack | Escuchar, Pronunciación, Escribir, Leer, Conversar, Gramática, MemHack | Écouter, Prononciation, Écrire, Lire, Conversation, Grammaire, MemHack |
| Buttons | Check, Record, Stop, Load | Comprobar, Grabar, Parar, Cargar | Vérifier, Enregistrer, Arrêter, Charger |
| Labels | Level, AI Voice, Language, Persona | Nivel, Voz de IA, Idioma, Persona | Niveau, Voix de l'IA, Langue, Persona |
| Feedback | Correct! | ¡Correcto! | Correct ! |
| Errors | Microphone permission denied | Permiso de micrófono denegado | Permission du microphone refusée |

Implementation: `frontend/i18n.js` (translation dictionary) + `data-i18n` attributes in HTML.

---

## Content Management

No code changes needed to add lessons. Each language has its own JSON files:

| Content | EN | ES | FR |
|---------|----|----|-----|
| Grammar | `backend/grammar.json` | `backend/grammar_es.json` | `backend/grammar_fr.json` |
| MemHack | `backend/memhack.json` | `backend/memhack_es.json` | `backend/memhack_fr.json` |
| Listen | `LISTEN` dict in `engine.py` | `backend/listen_es.json` | `backend/listen_fr.json` |
| Read | `READ` dict in `engine.py` | `backend/read_es.json` | `backend/read_fr.json` |

Hot-reload Grammar without rebuild: `POST /api/admin/reload-grammar` (admin only).

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | — | Status, LLM availability |
| GET | `/api/languages` | — | Supported languages |
| GET | `/api/levels` | — | Difficulty levels |
| GET | `/api/voices?lang=` | — | TTS voices per language |
| GET | `/api/grammar-levels?lang=` | — | CEFR levels (A1–C2) |
| GET | `/api/memhack/categories?lang=` | — | MemHack categories |
| POST | `/api/content` | ✓ | Get Listen/Read content |
| POST | `/api/correct` | ✓ | AI text correction |
| POST | `/api/tts` | ✓ | Text-to-speech (MP3) |
| POST | `/api/stt` | ✓ | Speech-to-text |
| POST | `/api/converse` | ✓ | AI conversation |
| POST | `/api/grammar` | ✓ | Grammar topic |
| POST | `/api/memhack/next` | ✓ | Next SRS phrase |
| POST | `/api/memhack/review` | ✓ | Record difficulty |
| POST | `/api/auth/login` | — | Login |
| POST | `/api/auth/register` | Admin | Create user |
| POST | `/api/admin/reload-grammar` | Admin | Reload grammar |

---

## CI/CD Pipeline

```
git push main ──▶ CI (ci.yaml)
                   ├─ backend: TestClient /api/health
                   └─ frontend: node --check

git tag vX.Y.Z ──▶ CD (cd.yaml)
                   ├─ build Docker image
                   ├─ push → Docker Hub (latest + vX.Y.Z)
                   └─ smoke test (health check with API key)
```

**Secrets**: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `OPENROUTER_API_KEY`

---

## Deploy Options

| Platform | Method | Status |
|----------|--------|--------|
| **Docker Hub** | `updateinformatica/english-jatel:latest` | ✅ Published |
| **Kubernetes** | Kustomize Blue/Green (`kubectl apply -k k8s/`) | ✅ Ready |
| **Azure AKS** | Terraform + K8s + NGINX Ingress + TLS | ✅ Configured |
| **Render** | Auto-deploy on push to `main` | ✅ Configured |
| **Local** | `docker compose up` or `uvicorn` | ✅ Ready |

---

## Security

- `.env` and `users.json` are gitignored — never committed
- API key injected at runtime via environment variable
- Passwords stored with PBKDF2 (per-user salt)
- Session cookies: HttpOnly + HMAC-signed
- HTTPS required in production (microphone + cookies)
- Admin-only routes: user management, grammar reload

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/technical/arquitetura.md) | Technical deep-dive |
| [Kubernetes Deploy](docs/technical/deploy-kubernetes.md) | k8s manifests + Blue/Green |
| [Azure AKS Deploy](docs/technical/deploy-aks.md) | AKS + Terraform + NGINX + TLS |
| [Blue/Green Strategy](docs/technical/blue-green.md) | Zero-downtime deployment |
| [Render Deploy](docs/technical/deploy-render.md) | PaaS deployment guide |
| [Versioning Process](docs/technical/processo-e-versionamento.md) | Release workflow |
| [User Guide](docs/user/guia.md) | End-user manual |
| [Multilingual Presentation](docs/apresentacao-multilingua.md) | Business case deck |
| [MCP Integration](docs/technical/mcp.md) | AI agent tooling |

---

## Skills & Prompts (AI Agent Integration)

| Skill | Scope |
|-------|-------|
| [`english-jatel`](skills/english-flow/SKILL.md) | Full-stack app (modules, auth, content, CI/CD) |
| [`aks-deploy`](.opencode/skills/aks-deploy/SKILL.md) | Azure AKS deployment with Terraform |
| [`mcp-integration`](.opencode/skills/mcp-integration/SKILL.md) | MCP server integration |

| Prompt | Purpose |
|--------|---------|
| [Deploy](prompts/english-jatel-deploy/prompt-base.md) | Docker + Kubernetes deployment |
| [AKS Deploy](prompts/english-jatel-deploy-aks/prompt-aks.md) | Azure AKS deployment |
| [Render Deploy](prompts/english-jatel-render/prompt-base.md) | Render PaaS deployment |
| [Role](prompts/english-jatel-role/prompt-base.md) | AI agent role definition |
| [Brainstorm](prompts/brainstorm.md) | Feature ideation |

---

## Project Structure

```
english-jatel/
├── backend/
│   ├── main.py              # FastAPI app, routes, auth middleware
│   ├── engine.py             # All business logic (LLM, TTS, STT, content)
│   ├── grammar.json          # EN grammar (CEFR A1–C2)
│   ├── grammar_es.json       # ES grammar
│   ├── grammar_fr.json       # FR grammar
│   ├── memhack.json          # EN phrases (SRS)
│   ├── memhack_es.json       # ES phrases
│   ├── memhack_fr.json       # FR phrases
│   ├── listen_es.json        # ES dictation sentences
│   ├── listen_fr.json        # FR dictation sentences
│   ├── read_es.json          # ES reading texts
│   ├── read_fr.json          # FR reading texts
│   └── requirements.txt
├── frontend/
│   ├── index.html            # SPA main page
│   ├── login.html            # Login page
│   ├── style.css             # Dark theme UI
│   ├── app.js                # Client logic (modules, i18n integration)
│   ├── auth.js               # Authentication logic
│   └── i18n.js               # EN/ES/FR translation dictionary (120+ keys)
├── terraform/                # Azure infrastructure (AKS, DNS, IP)
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   └── outputs.tf
├── k8s/                      # Kubernetes manifests (Blue/Green)
├── k8s/production/           # Production add-ons (Prometheus, ArgoCD)
├── mcp/                      # MCP stdio server
├── .github/workflows/        # CI/CD pipelines
├── docs/                     # Technical + user documentation
├── prompts/                  # AI agent prompt templates
├── skills/                   # AI agent skills
├── brainstore/               # Feature ideation notes
├── Dockerfile                # Multi-stage build
├── docker-compose.yaml       # Local development
└── PROVAS_CRIACAO.md         # Authorship proof
```

## Login

Default credentials are set in `backend/.env` (gitignored). See `backend/.env.example` for reference.

| User | Role | Can change password |
|------|------|-------------------|
| `admin` | Admin | Yes |
| `jatel` | Normal | Yes |
| `estudante` | Normal | No |

---

## Author

**Jefferson Santos** — Full-stack Developer

- GitHub: [jeffersonsantos-sp](https://github.com/jeffersonsantos-sp)
- Docker Hub: [updateinformatica](https://hub.docker.com/r/updateinformatica/english-jatel)

---

## License & Intellectual Property

**Private — All Rights Reserved**

© 2026 Jefferson Santos. Unauthorized copying, reproduction, distribution, or modification of this software, in whole or in part, is strictly prohibited.

This repository and its contents (source code, documentation, images, prompts, skills) are the intellectual property of the author. Forking, cloning for redistribution, or deriving derivative works without explicit written permission is not permitted.

For inquiries, contact: [jeffersonsantos-sp](https://github.com/jeffersonsantos-sp)
