# Deploy no Render

Guia de como o **English JATEL** está integrado ao [Render](https://render.com)
como Web Service em container, além dos ajustes feitos no repositório para rodar
no free tier. Complementa `docs/technical/deploy-kubernetes.md` (k8s) e
`docs/technical/blue-green.md`.

> URL de produção (teste): `https://english-jatel.onrender.com`

## Visão geral

O Render constrói a imagem a partir do **`Dockerfile` na raiz** (mesma imagem do
Docker Hub/k8s) e serve API `/api/*` + frontend estático num único serviço, igual
ao `backend/main.py`. Deploy automático a cada `git push` na branch `main`.

| Item | Valor |
|------|-------|
| Tipo | Web Service (Docker) |
| Repo/branch | `jeffersonsantos-sp/english-jatel` / `main` |
| Runtime | Docker (detecta o `Dockerfile` da raiz) |
| Porta | `$PORT` (Render injeta; default 8000) |
| Health Check Path | `/api/health` |
| Instance Type | Free |
| Auto-deploy | On push em `main` |

## Ajustes no repositório para o Render

### 1. Porta dinâmica (`$PORT`)
O Render define a porta via variável de ambiente `PORT`. O `Dockerfile` foi
ajustado para respeitá-la, mantendo compatibilidade com k8s/local (default 8000):

```dockerfile
# Render define a porta via env var PORT; k8s/local não a definem (default 8000).
CMD ["sh", "-c", "/opt/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### 2. Reconhecimento de voz no navegador (sem Whisper no servidor)
O free tier tem pouca RAM (~512 MB) e **não roda Whisper (PyTorch)**. Por isso a
gravação de voz (abas **Conversar** e **Speak**) usa a **Web Speech API do
navegador** (`window.SpeechRecognition`), que transcreve no cliente — sem depender
do backend. Há fallback para `/api/stt` em navegadores sem suporte.

> Requer **HTTPS** (o Render já fornece) e navegador compatível (**Chrome/Edge**;
> Firefox não suporta bem). Ao gravar pela 1ª vez, aceite a permissão do microfone.

### 4. Comportamentos recentes do app (v1.8.x)
- **Sem emojis na conversa**: o `system prompt` proíbe emojis e o `tts_bytes` remove
  emojis do texto antes da síntese — o TTS não "lê" a descrição do emoji em voz alta.
- **Seletor Categoria removido** da barra (redundante com Persona — as 9 personas já
  cobrem os temas). Listen/Read passam a usar `category: "all"`; o **MemHack** mantém
  seu próprio seletor de categoria.

### 3. Keepalive (não deixar o free tier dormir)
O free "dorme" após 15 min de inatividade (cold start de ~30-60 s). O workflow
`.github/workflows/keepalive.yaml` faz `curl` em `/api/health` a cada 10 min.

## Passo a passo do deploy (dashboard)

1. **New + → Web Service** → selecione o repo `english-jatel`, branch `main`.
2. **Name:** `english-jatel` · **Runtime:** `Docker` · **Instance Type:** `Free`.
3. **Health Check Path:** `/api/health`.
4. **Environment** → adicione as variáveis (abaixo).
5. **Create Web Service** → aguarde o build (~2-3 min). O Render gera a URL
   `https://<name>.onrender.com`.

## Variáveis de ambiente (Environment)

| Variável | Obrigatória | Observação |
|----------|-------------|------------|
| `OPENROUTER_API_KEY` | Sim (p/ LLM) | Sem ela → **modo demo** (`/api/health` mostra `llm:false, provider:demo`) |
| `ADMIN_PASS` | Recomendada | Sobrescreve o default `mudar123` |
| `SESSION_SECRET` | Recomendada | String longa aleatória (assinatura do cookie) |
| `EDGE_TTS_VOICE` | Opcional | Voz do TTS (ex.: `en-US-GuyNeural`) |

> Ao salvar mudanças em Environment, o Render faz **redeploy automático**.

## Ativar o keepalive

Após o deploy, cadastre o secret no GitHub:

1. GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `RENDER_URL` · Value: `https://english-jatel.onrender.com` (sem `/` no fim).
3. O workflow roda no cron (a cada 10 min) ou manualmente em **Actions → Keepalive → Run workflow**.

## Validação

```bash
# Deve retornar llm:true, provider:openrouter (com a chave configurada)
curl -s https://english-jatel.onrender.com/api/health

# Login (cookie de sessão) e teste da conversa
curl -s -c cookies.txt -X POST https://english-jatel.onrender.com/api/auth/login \
  -H 'Content-Type: application/json' -d '{"user":"admin","password":"<ADMIN_PASS>"}'
curl -s -b cookies.txt -X POST https://english-jatel.onrender.com/api/converse \
  -H 'Content-Type: application/json' \
  -d '{"level":"A2","persona":"cafe","history":[],"message":"Hi, I am learning English."}'
```

## Limitações do free tier

- **Disco efêmero** ⚠️: o Render free **não persiste** `/app/data`. A cada
  reinício/deploy, `users.json` e `memhack_progress.json` são recriados — contas de
  aluno e progresso do MemHack **resetam** (o `admin` volta ao seed). Para uso real:
  - **Render Starter** (~US$7/mo) com disco persistente, ou
  - apontar os dados para um **Postgres externo** (Supabase/Neon), ou
  - usar **Kubernetes** (PVC) / **Oracle Always Free** (`docker run -v`).
- **Cold start** após dormir (mitigado pelo keepalive).
- **~750 h/mês** de execução no free (suficiente p/ 1 serviço 24/7 com keepalive).

## Como o Render se encaixa nos alvos de deploy

O mesmo `Dockerfile`/imagem serve três destinos:

| Alvo | Persistência | Como | Doc |
|------|--------------|------|-----|
| **Render** | Efêmera (free) | Web Service Docker + `main` | este arquivo |
| **Docker Hub + k8s** | PVC (`/app/data`) | `kubectl apply -k k8s/` (blue/green) | `deploy-kubernetes.md`, `blue-green.md` |
| **Docker Compose** | Volume `userdata` | `docker compose up -d --build` | `README.md` |

## Referências

- `Dockerfile`, `.github/workflows/keepalive.yaml`
- `frontend/app.js` (Web Speech API + fallback `/api/stt`)
- `docs/technical/deploy-kubernetes.md`, `docs/technical/blue-green.md`
- `docs/technical/arquitetura.md`
