# Processo de desenvolvimento e versionamento por tags

Este documento descreve o fluxo ponta a ponta do projeto English JATEL: desde o
desenvolvimento local até o build, os testes, a publicação da imagem no Docker Hub
e o versionamento semântico via git tags.

## Visão geral do pipeline

```
código local ──git push (main)──▶ CI (ci.yaml)
                                  ├─ backend: TestClient /api/health
                                  └─ frontend: node --check
                                        │ (main verde)
git tag vX.Y.Z ──git push (tag)──▶ CD (cd.yaml)
                                  ├─ build da imagem (Dockerfile)
                                  ├─ push → Docker Hub: updateinformatica/english-jatel:latest + :vX.Y.Z
                                  └─ smoke test (sobe container, checa /api/health com a chave)
```

- O **CI** garante qualidade a cada mudança.
- O **CD** só roda em **tags** (`v*`), então o deploy é sempre um release versionado.

## 1. Ambiente local

```bash
# Backend (API + frontend num servidor)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Ou tudo em Docker
docker compose up -d --build
```

Arquivo `backend/.env` (não versionado): `OPENROUTER_API_KEY`, `OPENAI_MODEL`,
`OPENROUTER_TITLE`, `EDGE_TTS_VOICE`, `ADMIN_USER`, `ADMIN_PASS`, `SESSION_SECRET`.
Use `backend/.env.example` como base.

## 2. CI — `ci.yaml`

Dispara em `push` e `pull_request` para `main`.

- `backend-test`: instala `fastapi uvicorn python-multipart python-dotenv httpx` e
  roda `TestClient(main.app).get('/api/health')` (precisa do `httpx` para o `TestClient`).
- `frontend-test`: `node --check frontend/app.js` e `frontend/auth.js`.

> ⚠️ O `httpx` **não** vem com o `fastapi`; por isso está explícito no `pip install`.
> Sem ele o job de backend falha com `ImportError`.

## 3. CD — `cd.yaml`

Dispara **apenas** no push de uma tag `v*`.

- Faz login no Docker Hub com `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`.
- Builda e publica duas tags:
  - `updateinformatica/english-jatel:latest`
  - `updateinformatica/english-jatel:<tag>` (ex.: `v1.0.0`)
- Smoke test: sobe a imagem com `OPENROUTER_API_KEY` (runtime, não embutido) e
  valida `GET /api/health` (`"llm": true` se a chave estiver presente).

Segredos necessários no GitHub (Settings → Secrets and variables → Actions):

| Segredo | Uso |
|---------|-----|
| `DOCKERHUB_USERNAME` | usuário do Docker Hub (ex.: `updateinformatica`) |
| `DOCKERHUB_TOKEN` | access token do Docker Hub (Read/Write) |
| `OPENROUTER_API_KEY` | chave da API (usada no smoke test e em runtime) |
| `ADMIN_USER` | (opcional) usuário admin padrão |
| `ADMIN_PASS` | (opcional) senha admin padrão |
| `SESSION_SECRET` | (opcional) segredo da assinatura do cookie de sessão |

## 4. Versionamento por tags (release)

O versionamento é **semântico** e baseado em git tags. O `cd.yaml` escuta `v*`.

```bash
# 1. Garanta que está no main atualizado e verde
git checkout main && git pull

# 2. (opcional) atualize a versão no código, se aplicável

# 3. Crie e envie a tag
git tag v1.0.0
git push origin v1.0.0
```

Resultado:
- O `cd.yaml` builda e publica `updateinformatica/english-jatel:v1.0.0` (e `:latest`).
- O smoke test confirma a saúde da imagem.

### Regras sugeridas

- `vMAJOR.0.0` — mudanças incompatíveis / grandes releases.
- `vMAJOR.MINOR.0` — novas funcionalidades compatíveis.
- `vMAJOR.MINOR.PATCH` — correções.
- Nunca force-push uma tag já enviada sem coordenação (quebra o deployment).

### Rollback

Para voltar a uma versão:

```bash
git tag v0.9.9 && git push origin v0.9.9   # reconstrói/republi­ca essa versão
```

Ou, no host de deploy, puxe e rode a tag desejada:

```bash
docker pull updateinformatica/english-jatel:v1.0.0
docker run -d -p 8000:8000 -e OPENROUTER_API_KEY=... updateinformatica/english-jatel:v1.0.0
```

## 5. Checklist de release

- [ ] `main` atualizado e CI verde.
- [ ] Mensagens de commit revisadas.
- [ ] `backend/.env` / secrets de produção definidos (não commitados).
- [ ] Tag criada (`git tag vX.Y.Z`) e enviada.
- [ ] `cd.yaml` concluído (imagem publicada + smoke test ok).
- [ ] Imagem puxada/deployada no host alvo com `OPENROUTER_API_KEY`.
- [ ] Login e funcionalidades validados em produção (HTTPS).

## 6. Segurança

- `.env` e `users.json` não são versionados (`.gitignore` / `.dockerignore`).
- A chave do OpenRouter é injetada em **runtime**, nunca embutida na imagem.
- Cookies de sessão são `HttpOnly` + assinados (HMAC com `SESSION_SECRET`).
- Exija HTTPS em produção (microfone e cookie de sessão dependem disso).
