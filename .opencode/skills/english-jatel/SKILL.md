---
name: english-jatel
description: >
  App de ensino de ingles "English JATEL" (FastAPI + frontend estatico num so
  servidor) com auth de administrador e multi-usuario, TTS/STT/LLM, modulos de
  Grammar (niveis CEFR A1-C2) e MemHack (repeticao espacada/SRS), conteudo
  orientado a dados (grammar.json, memhack.json), deploy via Docker/Docker Compose
  e Kubernetes, e pipeline CI/CD no GitHub Actions versionado por git tags.
  Use para rodar, explicar, estender, versionar (git tag vX.Y.Z), buildar a
  imagem Docker, publicar no Docker Hub, implantar no Kubernetes ou operar o
  processo de release deste repositorio.
---

# SKILL: english-jatel

Tutor de **ingles, espanhol e frances** full-stack com login e multi-usuario.
Seletor de idioma no topo alterna entre **en** (Ingles), **es** (Espanhol),
**fr** (Frances). Um unico servidor FastAPI serve a API `/api/*` e o frontend SPA
(`index.html`, `style.css`, `app.js`, `auth.js`, `login.html`). Modulos: **Listen,
Speak, Write, Read, Conversar, Grammar, MemHack**. CI/CD via GitHub Actions:
testes no `ci.yaml`, build/push da imagem no Docker Hub no `cd.yaml` disparado por
**git tag `v*`**. Deploy tambem via `docker compose` e manifestos Kubernetes em `k8s/`.

## Quando usar
- Rodar ou explicar o app English JATEL localmente, via Docker ou no Kubernetes.
- Adicionar funcionalidades, frases, vozes, categorias ou modulos.
- Ajustar autenticacao, usuarios, senhas ou permissoes (admin-only).
- Editar conteudo de Grammar (`grammar.json`) ou MemHack (`memhack.json`) sem mexer no codigo.
- Fazer build, versionar por tags (`vX.Y.Z`) e publicar a imagem no Docker Hub.
- Implantar/operar no Kubernetes (`kubectl apply -k k8s/`).
- Operar o pipeline CI/CD ou investigar falhas de build/release.

## Arquitetura (ver docs/technical/arquitetura.md)
- `backend/main.py`: rotas `/api/*` ANTES de `app.mount("/", StaticFiles(...))`;
  `GET /` serve `frontend/index.html`. Middleware `auth_guard` protege `/` e
  `/api/*` (rotas publicas: `/api/health`, `/api/auth/login|logout|me`).
  `_require_admin` (register/users/reload-grammar) exige `user == ADMIN_USER`.
- `backend/engine.py`: toda a logica (correcao, TTS, STT, conversa, banco de
  frases, Grammar, MemHack/SRS) + auth (token HMAC em cookie; store de usuarios
  em `DATA_DIR/users.json`; progresso MemHack em `DATA_DIR/memhack_progress.json`).
- `frontend/`: SPA vanilla com URLs relativas `/api/...`. `auth.js` mostra o
  overlay de login e os modais de troca de senha/usuarios (botao de usuarios
  oculto para nao-admin via `is_admin`).

## Modulos
- **Listen**: ditado (TTS da frase, texto oculto ate "Verificar").
- **Speak**: STT (gravacao) ou texto -> correcao + TTS da correcao.
- **Write**: correcao de texto (ERRO -> CORRECAO -> REGRA -> SUGESTAO).
- **Read**: texto + glossario + pergunta de compreensao.
- **Conversar**: chat com IA. **9 personas** (cafe, entrevistador, negocios,
  viagens, familia, filmes, musicas, futebol, devops) — expostas em `/api/personas`.
  - Gravacao de voz usa a **Web Speech API do navegador** (`window.SpeechRecognition`)
    no cliente (o Whisper/PyTorch nao roda em hospedagem com pouca RAM); fallback p/ `/api/stt`.
  - A IA **nao usa emojis** (system prompt proibe) e o `tts_bytes` remove emojis do texto
    antes da sintese, para o TTS nao "ler" a descricao do emoji em voz alta.
  - O seletor **Categoria** da barra foi removido (redundante com Persona); Listen/Read
    usam `category: "all"`. O MemHack mantem seu proprio seletor de categoria.
- **Multi-idioma**: seletor `lang` no topo alterna entre Ingles/Espanhol/Frances.
  TTS, STT, prompts da IA e conteudo (gramatica + MemHack) se adaptam ao idioma.
- **Grammar**: topicos por nivel CEFR (A1-C2), com `structure`/`explanation`/
  `examples`; arquivos `grammar.json` (EN), `grammar_es.json` (ES), `grammar_fr.json` (FR).
  Recarregavel via `POST /api/admin/reload-grammar`.
- **MemHack**: frases por categoria (rotina, trabalho, escola, familia, diversao,
  esportes) com SRS estilo Leitner (box 1-5; facil sobe, medio mantem, dificil
  desce). Arquivos `memhack.json` (EN), `memhack_es.json` (ES), `memhack_fr.json` (FR);
  progresso por usuario+idioma persistido.

## Como rodar
```bash
# Local
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Docker Compose
docker compose up -d --build

# Kubernetes
kubectl apply -k k8s/
kubectl -n english-jatel port-forward svc/english-jatel 8080:80
```
- `.env` (gitignored) em `backend/` com `OPENROUTER_API_KEY`, `ADMIN_USER`,
  `ADMIN_PASS`, `SESSION_SECRET`. Base: `backend/.env.example`.
- Sem chave: modo demo (correcao heuristica + voz do navegador; Grammar/MemHack
  funcionam normalmente).

## Autenticacao e usuarios
- Login `admin` / `mudar123` por padrao (seed em `DATA_DIR/users.json`).
- `POST /api/auth/login` -> cookie `session` (HttpOnly, HMAC).
- `POST /api/auth/change-password` (qualquer usuario logado) e
  `POST /api/auth/register` + `GET /api/auth/users` (**somente admin**; 403 p/ comum).
- `POST /api/admin/reload-grammar` (**somente admin**).
- Senhas com PBKDF2 (salt por usuario). `users.json` e `memhack_progress.json`
  vivem em volume/PVC (`/app/data`) e **nao** sao versionados.

## Conteudo orientado a dados
- **Grammar**: `backend/grammar.json` — `{"levels":[...],"grammar":{<nivel>:[{topic,structure,explanation,examples}]}}`.
  Carregado em `GRAMMAR_FILE` no startup (fallback ao embutido). Recarrega sem rebuild via endpoint admin.
- **MemHack**: `backend/memhack.json` — `{"categories":[...],"phrases":{<cat>:[{id,en,pt}]}}`.
- **Listen/Read**: dicionarios `LISTEN`/`READ` em `engine.py` (fila embaralhada por nivel/modulo/categoria).

## Endpoints (resumo)
| Rota | Auth | Descricao |
|------|------|-----------|
| `/api/health` | — | status/llm/provider |
| `/api/grammar-levels` | — | niveis CEFR |
| `/api/memhack/categories` | — | categorias MemHack |
| `/api/content` | sim | frase/texto Listen/Read |
| `/api/correct`,`/api/tts`,`/api/stt`,`/api/converse` | sim | core |
| `/api/grammar` | sim | topico de gramatica |
| `/api/memhack/next`,`/api/memhack/review` | sim | SRS |
| `/api/auth/*` | ver auth | login/me/change-password/register/users |
| `/api/admin/reload-grammar` | **admin** | recarrega grammar.json |

## CI/CD (GitHub Actions)
- **`ci.yaml`**: em push/PR para `main` — `backend-test` (TestClient `/api/health`)
  e `frontend-test` (`node --check`). Node 24 recomendado.
- **`cd.yaml`**: em `push` de tag `v*` — builda e publica
  `updateinformatica/english-jatel:latest` e `:vX.Y.Z` no Docker Hub, com smoke test.

### Segredos no GitHub
`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `OPENROUTER_API_KEY` (obrigatorios);
`ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET` (opcionais).

## Versionamento por tags (release)
```bash
git checkout main && git pull
git tag v1.4.0
git push origin v1.4.0      # aciona cd.yaml -> build + push Docker Hub
```
- Mantenha `main` verde; corte tags so para releases. Rollback: `docker run ... :vX.Y.Z`.

## Deploy no Kubernetes (ver docs/technical/deploy-kubernetes.md)
- Manifestos em `k8s/` (namespace, configmap, pvc 1Gi, dois Deployments blue/green
  nao-root + readOnlyRootFilesystem + probes, service ClusterIP por seletor de slot).
  Validados com dry-run.
- **Blue/Green**: `deployment-blue.yaml` (slot ativo) + `deployment-green.yaml`
  (slot standby, 0 replicas). O Service roteia pelo `slot` ativo; promover = sobe o
  green, aguarda health e `patch` no seletor; rollback = patch de volta. Veja
  [`docs/technical/blue-green.md`](blue-green.md).
- App usa defaults de `ADMIN_PASS`/`SESSION_SECRET` (sem Secret comitado).
- Para LLM na implantacao: `kubectl -n english-jatel set env deploy/english-jatel-blue OPENROUTER_API_KEY=<key>` (ou no slot ativo).
- Exposicao: port-forward, ou trocar Service para LoadBalancer/NodePort/Ingress.
- Cuidado: ambos os slots montam o mesmo PVC (`/app/data`); mantenha um slot ativo
  por vez para evitar dupla escrita em `users.json`/`memhack_progress.json`.

## Como estender
- **Grammar**: edite `backend/grammar.json` e chame `POST /api/admin/reload-grammar`.
- **MemHack**: edite `backend/memhack.json` (categorias/frases).
- **Frases Listen/Read**: edite `LISTEN`/`READ` em `engine.py`.
- **Modulo/aba**: rota em `main.py` + handler em `engine.py` + aba em
  `frontend/index.html` + listener em `app.js`.

## Validacao (sem lint/testes automatizados)
```bash
# Backend (sem subir servidor)
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
# Frontend
node --check frontend/app.js && node --check frontend/auth.js
# Kubernetes
kubectl apply --dry-run=client -k k8s/
```

## Arquivos principais
- `backend/main.py`, `backend/engine.py`, `backend/grammar.json`, `backend/memhack.json`, `backend/.env.example`, `backend/requirements.txt`
- `frontend/index.html`, `frontend/style.css`, `frontend/app.js`, `frontend/auth.js`, `frontend/login.html`
- `Dockerfile`, `docker-compose.yaml`, `k8s/`
- `.github/workflows/ci.yaml`, `.github/workflows/cd.yaml`
- `docs/technical/arquitetura.md`, `docs/technical/deploy-kubernetes.md`, `docs/user/guia.md`, `AGENTS.md`
