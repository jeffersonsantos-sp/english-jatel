---
name: english-jatel
description: >
  App de ensino de ingles "English JATEL" (FastAPI + frontend estatico num so
  servidor) com auth de administrador e multi-usuario, TTS/STT/LLM, modulos de
  Grammar (niveis CEFR A1-C2), MemHack (repeticao espacada/SRS) e Numbers
  (numeros/categorias), conteudo orientado a dados (grammar.json, memhack.json,
  calendar_numbers.json), deploy via Docker/Docker Compose e Kubernetes, e
  pipeline CI/CD no GitHub Actions versionado por git tags. Suporta 5 idiomas:
  ingles, espanhol, frances, italiano e alemao.
  Use para rodar, explicar, estender, versionar (git tag vX.Y.Z), buildar a
  imagem Docker, publicar no Docker Hub, implantar no Kubernetes ou operar o
  processo de release deste repositorio.
---

# SKILL: english-jatel

Tutor de **ingles, espanhol, frances, italiano e alemao** full-stack com login e multi-usuario.
Seletor de idioma alterna entre **en** (Ingles), **es** (Espanhol), **fr** (Frances),
**it** (Italiano) e **de** (Alemao). Um unico servidor FastAPI serve a API `/api/*` e o frontend SPA
(`index.html`, `style.css`, `app.js`, `auth.js`, `login.html`). Modulos: **Listen,
Pronunciation, Write, Read, Conversar, Grammar, MemHack, Numbers**. CI/CD via GitHub Actions:
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
- **Pronunciation**: STT (gravacao) ou texto -> correcao + TTS da correcao.
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
- **Multi-idioma**: seletor `lang` alterna entre 5 idiomas: Ingles, Espanhol, Frances,
  Italiano e Alemao. TTS, STT, prompts da IA e conteudo (gramatica, MemHack, Numbers)
  se adaptam ao idioma.
- **Grammar**: topicos por nivel CEFR (A1-C2), com `structure`/`explanation`/
  `examples`; arquivos `grammar.json` (EN), `grammar_es.json` (ES), `grammar_fr.json` (FR),
  `grammar_it.json` (IT), `grammar_de.json` (DE). Recarregavel via `POST /api/admin/reload-grammar`.
- **MemHack**: frases por categoria (rotina, trabalho, escola, familia, diversao,
  esportes) com SRS estilo Leitner (box 1-5; facil sobe, medio mantem, dificil
  desce). Arquivos `memhack.json` (EN), `memhack_es.json` (ES), `memhack_fr.json` (FR),
  `memhack_it.json` (IT), `memhack_de.json` (DE); progresso por usuario+idioma persistido.
- **Numbers**: numeros 1-1000, ordinais, meses, dias da semana. Arquivos
  `calendar_numbers.json` (EN), `calendar_numbers_es.json` (ES), `calendar_numbers_fr.json` (FR),
  `calendar_numbers_it.json` (IT), `calendar_numbers_de.json` (DE).

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
- **Grammar**: `backend/grammar.json` (EN), `grammar_es.json` (ES), `grammar_fr.json` (FR),
  `grammar_it.json` (IT), `grammar_de.json` (DE) — `{"levels":[...],"grammar":{<nivel>:[{topic,structure,explanation,examples}]}}`.
  Carregado em `GRAMMAR_FILE` no startup (fallback ao embutido). Recarrega sem rebuild via endpoint admin.
- **MemHack**: `backend/memhack.json` (EN), `memhack_es.json` (ES), `memhack_fr.json` (FR),
  `memhack_it.json` (IT), `memhack_de.json` (DE) — `{"categories":[...],"phrases":{<cat>:[{id,en,pt}]}}`.
- **Listen**: `backend/listen_es.json` (ES), `listen_fr.json` (FR), `listen_it.json` (IT), `listen_de.json` (DE).
- **Read**: `backend/read_es.json` (ES), `read_fr.json` (FR), `read_it.json` (IT), `read_de.json` (DE).
- **Numbers**: `backend/calendar_numbers.json` (EN), `calendar_numbers_es.json` (ES),
  `calendar_numbers_fr.json` (FR), `calendar_numbers_it.json` (IT), `calendar_numbers_de.json` (DE).

## Endpoints (resumo)
| Rota | Auth | Descricao |
|------|------|-----------|
| `/api/health` | — | status/llm/provider |
| `/api/grammar-levels` | — | niveis CEFR |
| `/api/memhack/categories` | — | categorias MemHack |
| `/api/calendar-numbers` | — | numeros, ordinais, meses, dias |
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

## URLs de Producao
- **Azure AKS**: `https://learn.jfs-devops.shop` (NGINX Ingress + cert-manager + Let's Encrypt)
- **Render PaaS**: `https://english-jatel.onrender.com` (auto-deploy on push to `main`)
- **Cluster**: `aks-english-jatel` (Free Tier, `centralindia`, `Standard_B2als_v2`, K8s v1.35.6)
- **Ingress IP**: (dynamic via Terraform)

## Como estender
- **Grammar**: edite `backend/grammar.json` (EN), `grammar_es.json` (ES), `grammar_fr.json` (FR),
  `grammar_it.json` (IT), `grammar_de.json` (DE) e chame `POST /api/admin/reload-grammar`.
- **MemHack**: edite `backend/memhack.json` (EN), `memhack_es.json` (ES), `memhack_fr.json` (FR),
  `memhack_it.json` (IT), `memhack_de.json` (DE) (categorias/frases).
- **Numbers**: edite `backend/calendar_numbers.json` (EN), `calendar_numbers_es.json` (ES),
  `calendar_numbers_fr.json` (FR), `calendar_numbers_it.json` (IT), `calendar_numbers_de.json` (DE).
- **Listen**: edite `backend/listen_es.json` (ES), `listen_fr.json` (FR), `listen_it.json` (IT), `listen_de.json` (DE).
- **Read**: edite `backend/read_es.json` (ES), `read_fr.json` (FR), `read_it.json` (IT), `read_de.json` (DE).
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
- `backend/main.py`, `backend/engine.py`, `backend/.env.example`, `backend/requirements.txt`
- `backend/grammar.json`, `backend/grammar_es.json`, `backend/grammar_fr.json`, `backend/grammar_it.json`, `backend/grammar_de.json`
- `backend/memhack.json`, `backend/memhack_es.json`, `backend/memhack_fr.json`, `backend/memhack_it.json`, `backend/memhack_de.json`
- `backend/calendar_numbers.json`, `backend/calendar_numbers_es.json`, `backend/calendar_numbers_fr.json`, `backend/calendar_numbers_it.json`, `backend/calendar_numbers_de.json`
- `backend/listen_es.json`, `backend/listen_fr.json`, `backend/listen_it.json`, `backend/listen_de.json`
- `backend/read_es.json`, `backend/read_fr.json`, `backend/read_it.json`, `backend/read_de.json`
- `frontend/index.html`, `frontend/style.css`, `frontend/app.js`, `frontend/auth.js`, `frontend/login.html`
- `frontend/i18n.js` (dicionario EN/ES/FR/IT/DE)
- `Dockerfile`, `docker-compose.yaml`, `k8s/`
- `.github/workflows/ci.yaml`, `.github/workflows/cd.yaml`
- `docs/technical/arquitetura.md`, `docs/technical/deploy-kubernetes.md`, `docs/user/guia.md`, `AGENTS.md`
