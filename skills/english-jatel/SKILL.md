---
name: english-jatel
description: >
  App de ensino de ingles "English JATEL" (FastAPI + frontend estatico num so
  servidor) com auth de administrador e multi-usuario, TTS/STT/LLM, e pipeline
  CI/CD no GitHub Actions versionado por git tags. Use para rodar, estender,
  versionar (git tag vX.Y.Z), buildar a imagem Docker e publicar no Docker Hub,
  ou operar o processo de release deste repositorio.
---

# SKILL: english-jatel

Tutor de ingles full-stack com login e multi-usuario. Um unico servidor FastAPI
serve a API `/api/*` e o frontend SPA (`index.html`, `style.css`, `app.js`,
`auth.js`, `login.html`). CI/CD via GitHub Actions: testes no `ci.yaml`,
build/push da imagem no Docker Hub no `cd.yaml` disparado por **git tag `v*`**.

## Quando usar
- Rodar ou explicar o app English JATEL localmente ou via Docker.
- Adicionar funcionalidades, frases, vozes, categorias ou modulos.
- Ajustar autenticacao, usuarios, senhas ou permissoes.
- Fazer build, versionar por tags (`vX.Y.Z`) e publicar a imagem no Docker Hub.
- Operar o pipeline CI/CD ou investigar falhas de build/release.

## Arquitetura (ver docs/technical/arquitetura.md)
- `backend/main.py`: rotas `/api/*` ANTES de `app.mount("/", StaticFiles(...))`;
  `GET /` serve `frontend/index.html`. Middleware `auth_guard` protege `/` e
  `/api/*` (rotas publicas: `/api/health`, `/api/auth/login|logout|me`).
- `backend/engine.py`: toda a logica (correcao, TTS, STT, conversa, banco de
  frases) + auth (token HMAC em cookie, store de usuarios em `data/users.json`).
- `frontend/`: SPA vanilla com URLs relativas `/api/...`. `auth.js` mostra o
  overlay de login e os modais de troca de senha/usuarios.

## Como rodar
```bash
# Local
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Docker
docker compose up -d --build
```
- `.env` (gitignored) em `backend/` com `OPENROUTER_API_KEY`, `ADMIN_USER`,
  `ADMIN_PASS`, `SESSION_SECRET`. Base: `backend/.env.example`.
- Sem chave: modo demo (correcao heuristica + voz do navegador).

## Autenticacao e usuarios
- Login `admin` / `mudar123` por padrao (seed em `data/users.json`).
- `POST /api/auth/login` -> cookie `session` (HttpOnly, HMAC).
- `POST /api/auth/change-password` (exige login) e `POST /api/auth/register`
  (exige login) + `GET /api/auth/users`.
- Senhas com PBKDF2 (salt por usuario). `users.json` vive em volume nomeado
  (`userdata` -> `/app/data`) e **nao** e versionado.

## CI/CD (GitHub Actions)
- **`ci.yaml`**: em push/PR para `main` — `backend-test` (TestClient
  `/api/health`, precisa de `httpx` no pip install) e `frontend-test`
  (`node --check`). Use Node 24 para evitar warning de deprecacao do Node 20.
- **`cd.yaml`**: em `push` de tag `v*` — builda e publica
  `updateinformatica/english-jatel:latest` e `:vX.Y.Z` no Docker Hub, com
  smoke test usando `OPENROUTER_API_KEY` em runtime.

### Segredos no GitHub
`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `OPENROUTER_API_KEY` (obrigatorios);
`ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET` (opcionais).

## Versionamento por tags (release)
```bash
git checkout main && git pull
git tag v1.0.0
git push origin v1.0.0      # aciona cd.yaml -> build + push Docker Hub
```
- Mantenha `main` verde; corte tags so para releases.
- Rollback: `docker run ... updateinformatica/english-jatel:vX.Y.Z` ou re-tag.

## Como estender
- **Frases**: edite `LISTEN`/`READ` em `engine.py` (mantenha `CATEGORIES` em sync).
- **Modulo/aba**: rota em `main.py` + handler em `engine.py` + aba em
  `frontend/index.html` + listener em `app.js` (IDs e classes preservados).
- **Nova voz**: `EDGE_TTS_VOICE` ou seletor em `index.html`.

## Validacao (sem lint/testes automatizados)
```bash
# Backend (sem subir servidor)
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
# Frontend
node --check frontend/app.js && node --check frontend/auth.js
```

## Arquivos principais
- `backend/main.py`, `backend/engine.py`, `backend/.env.example`, `backend/requirements.txt`
- `frontend/index.html`, `frontend/style.css`, `frontend/app.js`, `frontend/auth.js`, `frontend/login.html`
- `.github/workflows/ci.yaml`, `.github/workflows/cd.yaml`
- `Dockerfile`, `docker-compose.yaml`
- `docs/technical/processo-e-versionamento.md`, `docs/technical/arquitetura.md`, `AGENTS.md`
