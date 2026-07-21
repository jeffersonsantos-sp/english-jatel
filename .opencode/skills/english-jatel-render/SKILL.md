# Skill: english-jatel-render

Deploy e operacao do **English JATEL** no **Render** (PaaS): Web Service em
container, construido a partir do `Dockerfile` da raiz e do repo GitHub, servindo
API `/api/*` + frontend SPA num unico servico. Foca no **free tier** e nos ajustes
que o repositorio ja tem para rodar nele. Complementa a skill `english-jatel`
(app) e `english-jatel-deploy` (Docker/Kubernetes).

## Quando usar
- Publicar o app no Render como Web Service (Docker) a partir do GitHub.
- Configurar variaveis de ambiente, health check e auto-deploy no Render.
- Diagnosticar "aba Conversar em modo demo" (falta `OPENROUTER_API_KEY`).
- Ativar/operar o keepalive para o free tier nao dormir.
- Explicar limitacoes do free (disco efemero, cold start) e alternativas de persistencia.
- Decidir entre Render, Kubernetes e Docker Compose para um cenario.

## Arquitetura no Render
- **Web Service (Docker)**: Render detecta o `Dockerfile` na raiz e builda a mesma
  imagem publicada no Docker Hub (`updateinformatica/english-jatel`). `backend/main.py`
  serve `/api/*` e o frontend estatico (`index.html`, `app.js`, ...).
- **Branch `main`**: auto-deploy a cada `git push` (o Render rebuilda).
- **Porta**: Render injeta `$PORT`. O `Dockerfile` roda
  `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}` (default 8000 em k8s/local).
- **Health Check Path**: `/api/health` → `{"status","llm","provider"}`.
- **HTTPS**: fornecido pelo Render (necessario para microfone e cookie de sessao).

## Ajustes do repositorio para o Render
1. **Porta dinamica** (`Dockerfile`): `CMD ["sh","-c","/opt/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]`.
2. **Voz no navegador** (`frontend/app.js`): gravacao das abas **Conversar** e
   **Speak** usa a **Web Speech API** (`window.SpeechRecognition`) no cliente, pois
   o Whisper (PyTorch) nao roda no free tier (~512 MB RAM). Fallback para `/api/stt`.
   Requer **Chrome/Edge** (Firefox nao suporta bem) e permissao de microfone.
3. **Keepalive** (`.github/workflows/keepalive.yaml`): `curl` em `/api/health` a
   cada 10 min via secret `RENDER_URL`, evitando o "sleep" apos 15 min.
4. **Sem emojis na conversa** (`backend/engine.py`): o `system prompt` proibe emojis
   e `tts_bytes` remove emojis do texto antes da sintese — o TTS nao "le" a descricao
   do emoji em voz alta.
5. **Seletor Categoria removido** da barra (`frontend/`): redundante com Persona (9
   personas ja cobrem os temas); Listen/Read usam `category: "all"`. MemHack mantem
   seu proprio seletor.
6. **Multi-idioma** (v1.9.0): seletor `lang` no topo alterna entre Ingles/Espanhol/
   Frances. TTS, STT, prompts da IA, gramatica (`grammar_es/fr.json`) e MemHack
   (`memhack_es/fr.json`) se adaptam ao idioma selecionado. Versao atual: **v1.9.0**.

## Passo a passo (dashboard)
1. **New + → Web Service** → repo `english-jatel`, branch `main`.
2. **Name** `english-jatel` · **Runtime** `Docker` · **Instance** `Free`.
3. **Health Check Path**: `/api/health`.
4. **Environment**: adicionar variaveis (abaixo). Salvar → redeploy automatico.
5. **Create Web Service** → URL `https://<name>.onrender.com`.
6. **Keepalive**: cadastrar o secret `RENDER_URL` no GitHub (Settings → Secrets → Actions).

## Variaveis de ambiente
| Variavel | Obrigatoria | Observacao |
|----------|-------------|------------|
| `OPENROUTER_API_KEY` | Sim (LLM) | Sem ela → modo demo (`llm:false, provider:demo`) |
| `ADMIN_PASS` | Recomendada | Sobrescreve o default `mudar123` |
| `SESSION_SECRET` | Recomendada | String longa aleatoria (assina o cookie) |
| `EDGE_TTS_VOICE` | Opcional | Voz do TTS (ex.: `en-US-GuyNeural`) |
| `RENDER_URL` (GitHub) | p/ keepalive | URL publica, sem `/` no fim |

## Validacao
```bash
# Deve retornar llm:true, provider:openrouter (com a chave configurada)
curl -s https://english-jatel.onrender.com/api/health

# Login + teste de conversa
curl -s -c c.txt -X POST https://english-jatel.onrender.com/api/auth/login \
  -H 'Content-Type: application/json' -d '{"user":"admin","password":"<ADMIN_PASS>"}'
curl -s -b c.txt -X POST https://english-jatel.onrender.com/api/converse \
  -H 'Content-Type: application/json' \
  -d '{"level":"A2","persona":"cafe","history":[],"message":"Hi!"}'
```

## Troubleshooting
- **Aba Conversar presa em "Hello! ... Can you tell me more?"** → `OPENROUTER_API_KEY`
  ausente/errada. Confirme em `/api/health` (`provider` deve ser `openrouter`).
- **Botao Gravar nao faz nada / "permissao do microfone negada"** → permissao do
  navegador (cadeado → Microfone → Permitir) e usar Chrome/Edge em HTTPS.
- **1o acesso lento** → cold start (free dormiu). Ative o keepalive.
- **Usuarios/progresso sumiram** → disco efemero do free (ver limitacoes).
- **Build falhou** → confira que o `Dockerfile` esta na raiz e a branch e `main`.

## Limitacoes do free tier
- **Disco efemero**: `/app/data` nao persiste; `users.json` e `memhack_progress.json`
  resetam a cada reinicio/deploy (admin volta ao seed).
- **Cold start** apos 15 min de inatividade (mitigado pelo keepalive).
- **~750 h/mes** de execucao.

### Persistencia real (alternativas)
- **Render Starter** (~US$7/mo): disco persistente + sem dormir.
- **Kubernetes** (PVC) — ver skill `english-jatel-deploy` / `docs/technical/deploy-kubernetes.md`.

## Alvos de deploy (mesma imagem)
| Alvo | Persistencia | Como |
|------|--------------|------|
| **Render** | Efemera (free) | Web Service Docker + branch `main` |
| **Kubernetes** | PVC `/app/data` | `kubectl apply -k k8s/` (blue/green) |
| **Docker Compose** | Volume `userdata` | `docker compose up -d --build` |

## Arquivos principais
- `Dockerfile` (porta `$PORT`), `.github/workflows/keepalive.yaml`
- `frontend/app.js` (Web Speech API + fallback `/api/stt`)
- `docs/technical/deploy-render.md`, `docs/technical/deploy-kubernetes.md`
- `prompts/english-jatel-render/prompt-base.md`
