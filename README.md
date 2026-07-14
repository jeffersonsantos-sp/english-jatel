# English JATEL

Aplicativo de ensino de inglês que treina **Listen, Speak, Write e Read** com correção
automática por IA e **conversação por LLM**, tudo em um único servidor (API FastAPI +
frontend estático). Inclui **login de administrador** e **múltiplos usuários**.

## Funcionalidades

- **Listen** — ditado: ouça a frase, digite o que ouviu e confira.
- **Speak** — gravação por microfone (STT) ou texto digitado, com correção e áudio da correção (TTS).
- **Write** — correção de texto em inglês por LLM.
- **Read** — texto + glossário e pergunta de compreensão corrigida.
- **Conversar** — chat com IA (personas: café, entrevistador, negócios).
- **Auth** — tela de login; usuário `admin`/`mudar123` por padrão (alterável); criação de novos usuários e troca de senha.

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose (opcional, recomendado)
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
- Os usuários são persistidos em um **volume nomeado** (`userdata` → `/app/data/users.json`), sobrevivendo a reinícios.
- Acesse http://localhost:8000 e faça login com `admin` / `mudar123`.

## Autenticação e usuários

- Login em `/login`; conteúdo protegido (`/` e `/api/*` exigem sessão via cookie HttpOnly assinado com HMAC).
- `POST /api/auth/change-password` — troca a senha do usuário logado.
- `POST /api/auth/register` + `GET /api/auth/users` — cria/lista usuários (exige login).
- Senhas armazenadas com **PBKDF2** (salt por usuário). O arquivo `users.json` **não** é versionado (`.gitignore`).

## CI/CD

Dois workflows em `.github/workflows/`:

- **`ci.yaml`** — roda em todo push/PR para `main`: testa o backend (`/api/health` via `TestClient`) e o frontend (`node --check`).
- **`cd.yaml`** — dispara **apenas no push de uma tag `v*`**: builda e publica a imagem no **Docker Hub** (`updateinformatica/english-jatel:latest` e `:vX.Y.Z`), e faz um smoke test com a chave em runtime.

Segredos no GitHub (Settings → Secrets and variables → Actions):
`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `OPENROUTER_API_KEY` (e opcionalmente `ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET`).

## Versionamento por tags (releases)

O deploy é versionado por git tags semânticas. Para lançar uma versão:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Isso aciona o `cd.yaml`, que publica:
- `updateinformatica/english-jatel:latest`
- `updateinformatica/english-jatel:v1.0.0`

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

## Documentação

- [Processo e versionamento por tags](docs/technical/processo-e-versionamento.md)
- [Guia do usuário](docs/user/guia.md)
- [Documentação técnica](docs/technical/arquitetura.md)
- [AGENTS.md](AGENTS.md) — instruções para agentes de IA neste repositório
- [Skill do projeto](skills/english-jatel/SKILL.md)

## Estrutura

- `backend/` — API FastAPI (`main.py`), lógica (`engine.py`), store de usuários, frontend servido
- `frontend/` — SPA sem build (`index.html`, `style.css`, `app.js`, `auth.js`, `login.html`)
- `.github/workflows/` — `ci.yaml` (testes) e `cd.yaml` (build/push)
- `docs/`, `skills/`, `prompts/`, `brainstore/`, `scripts/` — documentação e pipeline original
