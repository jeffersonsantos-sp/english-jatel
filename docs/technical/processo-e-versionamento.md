# Processo de desenvolvimento e versionamento por tags

Este documento descreve o fluxo ponta a ponta do projeto JATEL-IA: desde o
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
- [ ] Referências de versão atualizadas em `k8s/` e `docs/` (configmap, deployments, docs técnicos).

## 6. Próximos passos

### 6.1 Estado atual do conteúdo (v1.12.0)

| Módulo | EN | ES | FR |
|--------|----|----|----|
| Grammar (CEFR A1–C2) | ✅ Completo (46 tópicos) | ✅ Completo (46 tópicos, `structure`/`examples` em ES) | ✅ Completo (47 tópicos, `structure`/`examples` em FR) |
| MemHack (SRS) | ✅ Completo (6 categorias × 8 frases) | ✅ Completo (6 categorias × 8 frases) | ✅ Completo (6 categorias × 8 frases) |
| Listen (ditado) | ✅ Embutido no `engine.py` (LISTEN dict) | ✅ `listen_es.json` (3 níveis × 3 categorias × 8 frases) | ✅ `listen_fr.json` (3 níveis × 3 categorias × 8 frases) |
| Read (leitura) | ✅ Embutido no `engine.py` (READ dict) | ✅ `read_es.json` (3 níveis × 3 categorias × 3 textos + glossário PT-BR) | ✅ `read_fr.json` (3 níveis × 3 categorias × 3 textos + glossário PT-BR) |
| Conversar / Corrigir | ✅ Prompts multilíngues (EN/ES/FR) | ✅ Prompts multilíngues | ✅ Prompts multilíngues |
| TTS | ✅ Vozes Edge TTS por idioma | ✅ Vozes Edge TTS por idioma | ✅ Vozes Edge TTS por idioma |
| STT | ✅ Web Speech API (cliente) + fallback `/api/stt` | ✅ Web Speech API + fallback | ✅ Web Speech API + fallback |

### 6.2 Grammar ES/FR — concluído

O Grammar para **Espanhol** e **Francês** foi traduzido. Os arquivos `grammar_es.json` e `grammar_fr.json` têm:
- **`structure`** — fórmulas gramaticais adaptadas para o idioma-alvo (ES/FR).
- **`explanation`** — explicação em português do BR, contextualizada para o idioma-alvo.
- **`examples`** — frases modelo em ES/FR com tradução PT-BR (ex.: "Yo soy estudiante." em vez de "I am a student.").

Validação: 0 exemplos em inglês nas versões ES/FR. Recarregar via `POST /api/admin/reload-grammar` e conferir no frontend (abas Grammar → ES/FR).

### 6.3 i18n completo da UI (internacionalização) — ✅ Implementado

Ao selecionar o idioma (English / Español / Français) no seletor `<select id="lang">`, **toda a página é traduzida** para o idioma escolhido. Implementado com `i18n.js` (dicionário `I18N`) + atributos `data-i18n` no HTML.

Elementos traduzidos:

| Elemento | Exemplo |
|----------|---------|
| Tagline / header | "Learn by listening, speaking & conversing" |
| Abas | "Escuchar", "Écouter", "Parler" |
| Labels / placeholders | "Niveau:", "Voz de IA:", "Categoría:" |
| Botões | "Escuchar frase", "Gravar", "Enregistrer", "Corregir" |
| Mensagens de feedback | "Correct!", "Correcto!", "Correct !" |
| Textos de instrução | "Escucha la frase..." |
| Erros / alerts | "Permission du microphone refusée" |
| Modais (senha, usuários) | "Changer le mot de passe", "Gestionar usuarios" |

Arquivos: `frontend/i18n.js` (dicionário EN/ES/FR), `frontend/index.html` (atributos `data-i18n`), `frontend/app.js` (chamadas `t()` + `applyI18n()`).

### 6.4 Criar novos usuários

Usuários padrão criados via seed no `engine.py`:
- `admin` / `mudar123` (admin, pode trocar senha)
- `jatel` / `Update2026!` (não-admin, pode trocar senha)
- `estudante` / `Estudo@2026!` (não-admin, **não pode** trocar senha)

Para adicionar usuários via API (requer admin):
```
POST /api/auth/register  {"username":"<user>","password":"<pass>"}
```

### 6.5 Adicionar novo idioma

Procedimento padronizado em `.opencode/skills/english-jatel-add-lang/SKILL.md`.
Resumo:
1. Crie `backend/grammar_{lang}.json` (A1–C2, copie A1 do EN, traduza A2–C2)
2. Crie `backend/memhack_{lang}.json` (categorias + frases, chave `{lang}` nos objetos)
3. Adicione opção ao `<select id="lang">` no frontend
4. Recarregue via `POST /api/admin/reload-grammar` (admin)
5. Atualize README.md e este documento
6. Faça commit, tag `vX.Y.Z`, build e push da imagem

### 6.7 Atualizar versão do K8s e docs

1. Atualize `k8s/configmap.yaml` → `IMAGE: updateinformatica/english-jatel:vX.Y.Z`
2. Atualize `k8s/deployment-blue.yaml` e `k8s/deployment-green.yaml` → `image: ...`
3. Atualize referências de versão em `docs/technical/deploy-kubernetes.md`, `docs/technical/blue-green.md` e `docs/apresentacao-multilingua.md`
4. Valide com `kubectl apply --dry-run=client -k k8s/`
5. Faça commit e tag

## 7. Segurança

- `.env` e `users.json` não são versionados (`.gitignore` / `.dockerignore`).
- A chave do OpenRouter é injetada em **runtime**, nunca embutida na imagem.
- Cookies de sessão são `HttpOnly` + assinados (HMAC com `SESSION_SECRET`).
- Exija HTTPS em produção (microfone e cookie de sessão dependem disso).
