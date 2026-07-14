# English JATEL

App de ensino de inglês que treina **Listen, Speak, Write e Read** com correções
automáticas e **conversação por IA** (a IA fala e você fala com ela).

## Início rápido

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Abra http://localhost:8000

> O backend serve a API e o frontend num único servidor. A chave do OpenRouter
> vai em `backend/.env` (gitignored) — use `backend/.env.example` como base.

## CI/CD

O repositório possui GitHub Actions (`.github/workflows/ci.yml`):
- Testa o backend (health check) e o frontend (`node --check`).
- Em push para `main`, builda e publica a imagem em `ghcr.io/jeffersonsantos-sp/english-jatel:latest`.

Para rodar com Docker:

```bash
docker compose up -d --build
```

## Documentação

- [Guia do usuário](docs/user/guia.md)
- [Documentação técnica](docs/technical/arquitetura.md)
- [AGENTS.md](AGENTS.md) — instruções para agentes de IA neste repo

## Estrutura

- `backend/` — API FastAPI + lógica (`engine.py`) + frontend servido
- `frontend/` — SPA sem build (HTML/CSS/JS)
- `brainstore/`, `scripts/`, `prompts/`, `skills/` — pipeline original de ideação
