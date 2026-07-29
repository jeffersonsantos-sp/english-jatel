# JATEL-IA

Aplicativo de ensino de **inglês, espanhol e francês** que treina **Listen, Speak, Write, Read**
e **Conversação por IA**, mais módulos de **Grammar** (gramática por nível CEFR) e **MemHack**
(memorização com repetição espaçada), tudo em um único servidor (API FastAPI + frontend estático).
Inclui **login de administrador**, **múltiplos usuários** e **deploy via Docker e Kubernetes**.

## Funcionalidades

- **Multi-idioma** — seletor no topo alterna entre **Inglês**, **Espanhol** e **Francês**. TTS, STT, prompts da IA e conteúdo (gramática + MemHack) se adaptam ao idioma selecionado.
- **Listen** — ditado: ouça a frase, digite o que ouviu e confira.
- **Speak** — gravação por microfone (STT) ou texto digitado, com correção e áudio da correção (TTS).
- **Write** — correção de texto por LLM no idioma selecionado.
- **Read** — texto + glossário e pergunta de compreensão corrigida.
- **Conversar** — chat com IA (personas: café, entrevistador, negócios, etc.) no idioma selecionado.
- **Grammar** — lições de gramática por nível CEFR (**A1 → C2**), com estrutura, explicação e exemplos. Conteúdo em `backend/grammar.json` (EN), `grammar_es.json` (ES), `grammar_fr.json` (FR).
- **MemHack** — memorização de frases por categorias com **repetição espaçada (SRS)**. Conteúdo em `backend/memhack.json` (EN), `memhack_es.json` (ES), `memhack_fr.json` (FR).
- **Auth** — tela de login; usuário `admin`/`mudar123` por padrão. Seed automático de usuário normal via `SEED_USERNAME`/`SEED_PASSWORD`.

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose (opcional, recomendado)
- Kubernetes (opcional) + `kubectl`
- Conta OpenRouter com `OPENROUTER_API_KEY` (modo demo funciona sem chave, com correção heurística)

## Como rodar localmente

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
# abra http://localhost:8000
```

> Python externamente gerenciado (PEP 668)? Use o venv acima ou `pip install -r requirements.txt --break-system-packages`.
> A chave vai em `backend/.env` (gitignored) — use `backend/.env.example` como base.

## Como rodar com Docker

```bash
docker compose up -d --build
```

- Variáveis de ambiente: `EDGE_TTS_VOICE`, `ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET`, `DATA_DIR`.
- Os dados dos usuários e o progresso do MemHack são persistidos em um **volume nomeado**
  (`userdata` → `/app/data`), sobrevivendo a reinícios.
- Acesse http://localhost:8000 e faça login com `admin` / `mudar123`.

## Como rodar no Kubernetes

Manifestos em `k8s/` (validados com `kubectl apply --dry-run=client`):

```bash
kubectl apply -k k8s/
# acesso local (8000 pode estar em uso no host; use 8080):
kubectl -n english-jatel port-forward svc/english-jatel 8080:80
# abra http://localhost:8080
```

- O app usa `ADMIN_PASS`/`SESSION_SECRET` padrão do container (sem Secret comitado).
- Em modo demo (sem `OPENROUTER_API_KEY` no pod), correção/conversa ficam heurísticas; TTS funciona.
  Para habilitar o LLM na implantação:
  ```bash
  kubectl -n english-jatel set env deploy/english-jatel OPENROUTER_API_KEY=<sua_key>
  ```
- Veja [`docs/technical/deploy-kubernetes.md`](docs/technical/deploy-kubernetes.md) para detalhes
  (Deployment, PVC, probes, Service, exposição via LoadBalancer/NodePort).

## Autenticação e usuários

- Login em `/login`; conteúdo protegido (`/` e `/api/*` exigem sessão via cookie HttpOnly assinado com HMAC).
- `POST /api/auth/change-password` — troca a senha do usuário logado.
- `POST /api/auth/register` + `GET /api/auth/users` — **exigem admin** (usuário comum recebe 403).
- Senhas armazenadas com **PBKDF2** (salt por usuário). O arquivo `users.json` **não** é versionado (`.gitignore`).

## Conteúdo orientado a dados (Grammar e MemHack)

Não é preciso editar o código para adicionar lições/frases. Cada idioma tem seu próprio arquivo:

- **Grammar EN**: `backend/grammar.json` — `{"levels": [...], "grammar": {<nível>: [{topic, structure, explanation, examples}]}}`
- **Grammar ES**: `backend/grammar_es.json` (mesma estrutura)
- **Grammar FR**: `backend/grammar_fr.json` (mesma estrutura)
- **MemHack EN**: `backend/memhack.json` — `{"categories": [...], "phrases": {<categoria>: [{id, en, pt}]}}`
- **MemHack ES**: `backend/memhack_es.json` (chave `es` em vez de `en`)
- **MemHack FR**: `backend/memhack_fr.json` (chave `fr` em vez de `en`)

Recarregue sem rebuild com `POST /api/admin/reload-grammar` (admin). O progresso SRS de cada
usuário+idioma fica em `DATA_DIR/memhack_progress.json`.

## Endpoints (resumo)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/languages` | — | idiomas suportados (`en`, `es`, `fr`) |
| GET | `/api/health` | — | status/llm/provider |
| GET | `/api/levels` | — | níveis de Listen/Read |
| GET | `/api/personas` | — | personas de conversa |
| GET | `/api/voices?lang=` | — | vozes Edge TTS (filtradas por idioma) |
| GET | `/api/categories` | — | categorias de conteúdo |
| GET | `/api/grammar-levels` | — | níveis CEFR (A1–C2) |
| GET | `/api/memhack/categories?lang=` | — | categorias do MemHack por idioma |
| POST | `/api/content` | sim | frase/texto de Listen/Read (+ `lang`) |
| POST | `/api/correct` | sim | correção de texto (+ `lang`) |
| POST | `/api/tts` | sim | áudio MP3 (base64, + `lang`) |
| POST | `/api/stt` | sim | transcrição de áudio |
| POST | `/api/converse` | sim | resposta da IA (+ `lang`) |
| POST | `/api/grammar` | sim | tópico de gramática por nível (+ `lang`) |
| POST | `/api/memhack/next` | sim | próxima frase a revisar (+ `lang`) |
| POST | `/api/memhack/review` | sim | registra dificuldade (+ `lang`) |
| POST | `/api/auth/login` · `/logout` · `/me` | — | autenticação |
| POST | `/api/auth/change-password` | sim | troca própria senha |
| POST | `/api/auth/register` · `GET /api/auth/users` | **admin** | gerência de usuários |
| POST | `/api/admin/reload-grammar` | **admin** | recarrega grammar do idioma (`lang`) |

## CI/CD

Dois workflows em `.github/workflows/`:

- **`ci.yaml`** — roda em todo push/PR para `main`: testa o backend (`/api/health` via `TestClient`) e o frontend (`node --check`).
- **`cd.yaml`** — dispara **apenas no push de uma tag `v*`**: builda e publica a imagem no **Docker Hub**
  (`updateinformatica/english-jatel:latest` e `:vX.Y.Z`), e faz um smoke test com a chave em runtime.

Segredos no GitHub (Settings → Secrets and variables → Actions):
`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `OPENROUTER_API_KEY` (e opcionalmente `ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET`).

## Versionamento por tags (releases)

O deploy é versionado por git tags semânticas. Para lançar uma versão:

```bash
git tag v1.4.0
git push origin v1.4.0
```

Isso aciona o `cd.yaml`, que publica:
- `updateinformatica/english-jatel:latest`
- `updateinformatica/english-jatel:v1.4.0`

Mantenha o `main` sempre verde; corte tags só quando quiser um release. Veja
[`docs/technical/processo-e-versionamento.md`](docs/technical/processo-e-versionamento.md) para o passo a passo completo.

## Deploy da imagem

Em qualquer host com Docker:

```bash
docker pull updateinformatica/english-jatel:latest
docker run -d -p 8000:8000 \
  -e OPENROUTER_API_KEY=sua_chave \
  updateinformatica/english-jatel:latest
```

## Segurança

- Nunca comite `.env` ou `users.json` (ambos ignorados no `.gitignore`/`.dockerignore`).
- A chave do OpenRouter vai por **secret/variável de ambiente**, nunca embutida na imagem.
- Use HTTPS em produção (obrigatório para microfone e para o cookie de sessão).
- Altere `ADMIN_PASS` e `SESSION_SECRET` para valores fortes antes de expor publicamente.
- Criação/listagem de usuários é restrita ao admin (retorna 403 para usuários comuns).

## Documentação

- [Deploy no Render (PaaS)](docs/technical/deploy-render.md)
- [Deploy no Kubernetes](docs/technical/deploy-kubernetes.md)
- [Blue/Green no Kubernetes](docs/technical/blue-green.md)
- [Processo e versionamento por tags](docs/technical/processo-e-versionamento.md)
- [Guia do usuário](docs/user/guia.md)
- [Documentação técnica](docs/technical/arquitetura.md)
- [AGENTS.md](AGENTS.md) — instruções para agentes de IA neste repositório

## Skills e prompts

Skills disponíveis para agentes de IA operarem este projeto:

| Skill | Escopo | Prompt base |
|-------|--------|-------------|
| [`english-jatel`](skills/english-jatel/SKILL.md) | App full-stack (módulos, auth, conteúdo, CI/CD) | — |
| [`english-jatel-render`](.opencode/skills/english-jatel-render/SKILL.md) | Deploy e operação no **Render** (PaaS/free tier) | [`prompts/english-jatel-render/`](prompts/english-jatel-render/prompt-base.md) |
| [`mcp-integration`](.opencode/skills/mcp-integration/SKILL.md) | Integração MCP | — |

> Prompt de deploy Docker/Kubernetes: [`prompts/english-jatel-deploy/`](prompts/english-jatel-deploy/prompt-base.md).

## Estrutura

- `backend/` — API FastAPI (`main.py`), lógica (`engine.py`), conteúdo orientado a dados (`grammar.json`, `memhack.json`), store de usuários, frontend servido
- `frontend/` — SPA sem build (`index.html`, `style.css`, `app.js`, `auth.js`, `login.html`)
- `k8s/` — manifestos Kubernetes (namespace, configmap, pvc, deployment, service, kustomization)
- `.github/workflows/` — `ci.yaml` (testes) e `cd.yaml` (build/push)
- `docs/`, `skills/`, `prompts/`, `brainstore/`, `scripts/` — documentação e pipeline original
