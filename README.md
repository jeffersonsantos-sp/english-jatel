# English JATEL

Aplicativo de ensino de inglês que treina **Listen, Speak, Write, Read** e **Conversação por IA**,
mais módulos de **Grammar** (gramática por nível CEFR) e **MemHack** (memorização com repetição
espaçada), tudo em um único servidor (API FastAPI + frontend estático). Inclui **login de
administrador**, **múltiplos usuários** e **deploy via Docker e Kubernetes**.

## Funcionalidades

- **Listen** — ditado: ouça a frase, digite o que ouviu e confira.
- **Speak** — gravação por microfone (STT) ou texto digitado, com correção e áudio da correção (TTS).
- **Write** — correção de texto em inglês por LLM.
- **Read** — texto + glossário e pergunta de compreensão corrigida.
- **Conversar** — chat com IA (personas: café, entrevistador, negócios).
- **Grammar** — lições de gramática por nível CEFR (**A1 → C2**), com estrutura (fórmula), explicação e exemplos. Conteúdo em `backend/grammar.json` (orientado a dados).
- **MemHack** — memorização de frases por categorias (Rotina, Trabalho, Escola, Família, Diversão, Esportes) com **repetição espaçada (SRS)**. Ouça a frase, treine e classifique: Fácil / Médio / Difícil. Conteúdo em `backend/memhack.json`.
- **Auth** — tela de login; usuário `admin`/`mudar123` por padrão. Apenas o **admin** cria/lista usuários; qualquer usuário troca a própria senha.

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

Não é preciso editar o código para adicionar lições/frases:

- **Grammar**: `backend/grammar.json` — `{"levels": [...], "grammar": {<nível>: [{topic, structure, explanation, examples}]}}`.
  Carregado no startup (fallback ao embutido se faltar). Recarregue sem rebuild:
  `POST /api/admin/reload-grammar` (somente admin).
- **MemHack**: `backend/memhack.json` — `{"categories": [...], "phrases": {<categoria>: [{id, en, pt}]}}`.
  O progresso de repetição espaçada de cada usuário fica em `DATA_DIR/memhack_progress.json`.
- `LISTEN`/`READ` (Listen/Read) continuam em dicionários em `engine.py`.

## Endpoints (resumo)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/health` | — | status/llm/provider |
| GET | `/api/levels` | — | níveis de Listen/Read |
| GET | `/api/personas` | — | personas de conversa |
| GET | `/api/voices` | — | vozes Edge TTS |
| GET | `/api/categories` | — | categorias de conteúdo |
| GET | `/api/grammar-levels` | — | níveis CEFR (A1–C2) |
| GET | `/api/memhack/categories` | — | categorias do MemHack |
| POST | `/api/content` | sim | frase/texto de Listen/Read |
| POST | `/api/correct` | sim | correção de texto |
| POST | `/api/tts` | sim | áudio MP3 (base64) |
| POST | `/api/stt` | sim | transcrição de áudio |
| POST | `/api/converse` | sim | resposta da IA |
| POST | `/api/grammar` | sim | tópico de gramática por nível |
| POST | `/api/memhack/next` | sim | próxima frase a revisar |
| POST | `/api/memhack/review` | sim | registra dificuldade e devolve próxima |
| POST | `/api/auth/login` · `/logout` · `/me` | — | autenticação |
| POST | `/api/auth/change-password` | sim | troca própria senha |
| POST | `/api/auth/register` · `GET /api/auth/users` | **admin** | gerência de usuários |
| POST | `/api/admin/reload-grammar` | **admin** | recarrega `grammar.json` |

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

- [Deploy no Kubernetes](docs/technical/deploy-kubernetes.md)
- [Processo e versionamento por tags](docs/technical/processo-e-versionamento.md)
- [Guia do usuário](docs/user/guia.md)
- [Documentação técnica](docs/technical/arquitetura.md)
- [AGENTS.md](AGENTS.md) — instruções para agentes de IA neste repositório
- [Skill do projeto](skills/english-jatel/SKILL.md)

## Estrutura

- `backend/` — API FastAPI (`main.py`), lógica (`engine.py`), conteúdo orientado a dados (`grammar.json`, `memhack.json`), store de usuários, frontend servido
- `frontend/` — SPA sem build (`index.html`, `style.css`, `app.js`, `auth.js`, `login.html`)
- `k8s/` — manifestos Kubernetes (namespace, configmap, pvc, deployment, service, kustomization)
- `.github/workflows/` — `ci.yaml` (testes) e `cd.yaml` (build/push)
- `docs/`, `skills/`, `prompts/`, `brainstore/`, `scripts/` — documentação e pipeline original
