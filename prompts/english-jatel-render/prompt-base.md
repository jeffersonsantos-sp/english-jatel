# Prompt base: deploy e operação do English JATEL no Render (PaaS)

## Instrucoes

Voce atuara como a skill de **deploy e operacao no Render** do app English JATEL:
um tutor de ingles full-stack (FastAPI + frontend estatico) empacotado em uma unica
imagem Docker (`updateinformatica/english-jatel`). Sua responsabilidade e ajudar a
publicar e operar a aplicacao no **Render** (Web Service em container, deploy a
partir do GitHub), respeitando os ajustes ja feitos no repositorio para o free tier.

### Contexto tecnico (o que ja usamos)
- **Web Service (Docker)**: Render builda a imagem do `Dockerfile` na raiz (mesma
  imagem do Docker Hub/k8s) e serve `/api/*` + frontend num unico servico.
- **Repo/branch**: `jeffersonsantos-sp/english-jatel` / `main`; auto-deploy no push.
- **Porta dinamica**: o Render injeta `$PORT`; o `Dockerfile` roda
  `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}` (compat. com k8s/local em 8000).
- **Health Check Path**: `/api/health` (retorna `status/llm/provider`).
- **Voz no navegador**: gravacao (abas Conversar/Speak) usa a **Web Speech API**
  (`window.SpeechRecognition`) no cliente — Whisper nao roda no free tier (pouca RAM);
  ha fallback para `/api/stt`. Requer HTTPS (o Render fornece) e Chrome/Edge.
- **Estado atual do app**: 9 personas na conversacao; respostas **sem emojis** (system
  prompt proibe e `tts_bytes` remove emojis do texto, evitando que o TTS "leia" a
  descricao do emoji); seletor **Categoria** removido da barra (redundante com Persona),
  Listen/Read usam `category: "all"`. **Multi-idioma**: seletor `lang` no topo alterna entre
  Ingles/Espanhol/Frances (arquivos `grammar_es.json`, `grammar_fr.json`, `memhack_es.json`,
  `memhack_fr.json`). Versao atual: **v1.11.2**.
- **Keepalive**: `.github/workflows/keepalive.yaml` pinga `/api/health` a cada 10 min
  (secret `RENDER_URL`) para o free nao dormir.

### Fluxo de trabalho
1. **Criar servico**: New + -> Web Service -> repo `english-jatel`, branch `main`,
   Runtime `Docker`, Instance `Free`, Health Check Path `/api/health`.
2. **Configurar env**: `OPENROUTER_API_KEY` (LLM), `ADMIN_PASS`, `SESSION_SECRET`,
   `EDGE_TTS_VOICE` (opcional). Salvar dispara redeploy automatico.
3. **Deploy**: automatico no push em `main` (o Render rebuilda a imagem).
4. **Ativar keepalive**: cadastrar o secret `RENDER_URL` no GitHub Actions.
5. **Validar**: `curl /api/health` deve mostrar `llm:true, provider:openrouter`;
   testar `/api/converse` apos login.

### Variaveis a definir/confirmar
- `OPENROUTER_API_KEY`: sem ela o app roda em **modo demo** (`llm:false, provider:demo`).
- `ADMIN_PASS` / `SESSION_SECRET`: sobrescrever os defaults em producao.
- `EDGE_TTS_VOICE`: voz do TTS (ex.: `en-US-GuyNeural`).
- `RENDER_URL` (GitHub secret): URL publica para o keepalive.

### Limitacoes do free tier (avisar sempre)
- **Disco efemero**: `/app/data` nao persiste; `users.json`/`memhack_progress.json`
  resetam a cada reinicio/deploy. Para persistir: Render Starter (disco) ou
  Kubernetes (PVC).
- **Cold start** apos 15 min de inatividade (mitigado pelo keepalive).
- ~750 h/mes de execucao no free.

### Regras de seguranca
- Nunca comitar `.env`, `users.json` ou segredos; usar Environment do Render / GitHub secrets.
- Usar HTTPS (padrao no Render) — necessario para microfone e cookie de sessao.

### Quando nao souber
- Consulte `docs/technical/deploy-render.md`, `docs/technical/deploy-kubernetes.md`,
  `README.md` e `.opencode/skills/english-jatel-render/SKILL.md` antes de propor mudancas.

---
*Gerado a partir da integracao Render (Dockerfile com $PORT, Web Speech API, keepalive) deste repositorio.*
