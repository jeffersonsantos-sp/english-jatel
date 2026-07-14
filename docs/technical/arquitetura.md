# Documentação Técnica — English Flow

App de ensino de inglês: backend FastAPI que serve a API **e** o frontend SPA
num único servidor.

## Estrutura

```
backend/
  main.py        # FastAPI: rotas /api/* + monta o frontend estático em /
  engine.py      # lógica: correção (LLM), TTS (Edge/OpenAI/pyttsx3), STT, conversa, banco de frases
  requirements.txt
  .env           # segredos (OPENROUTER_API_KEY, OPENAI_MODEL...) — gitignored
frontend/
  index.html     # SPA, sem build
  style.css
  app.js         # lógica do cliente (fetch /api/*, gravação de voz, TTS)
brainstore/      # notas de ideias (markdown)
scripts/         # convert_brainstore_to_prompt.py (brainstore -> prompts)
prompts/         # prompts gerados por skill
skills/          # skill/cli protótipo (english-flow/app.py, SKILL.md)
docs/            # user/ e technical/
```

## Como rodar

```bash
cd backend
pip install -r requirements.txt        # ou: pip install --break-system-packages ...
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Python deste SO é *externally managed* (PEP 668); use venv ou `--break-system-packages`.

O `main.py` registra as rotas `/api/*` **antes** de `app.mount("/", StaticFiles(...))`,
então a API tem prioridade sobre os arquivos estáticos. `GET /` retorna `frontend/index.html`.

## LLM e TTS

- **LLM**: OpenRouter (texto-only) via cliente OpenAI compatível. `engine.py` lê
  `OPENROUTER_API_KEY` (ou `OPENAI_API_KEY`) e aponta `BASE_URL` para
  `https://openrouter.ai/api/v1`, enviando headers `HTTP-Referer`/`X-Title`.
- **TTS** (`engine.tts_bytes`): prioridade Edge TTS (vozes neurais, sem chave) →
  OpenAI `tts-1` → `pyttsx3` (offline). O frontend (`app.js` → `playTts`) reproduz
  o MP3 base64; se tudo falhar, usa `speechSynthesis` do navegador.
- **Voz**: `EDGE_TTS_VOICE` (env) ou parâmetro `voice` no `/api/tts`; UI tem seletor.

## Endpoints

| Método | Rota | Corpo | Retorno |
|--------|------|-------|---------|
| GET | `/api/health` | — | `{status, llm, provider}` |
| GET | `/api/levels` | — | níveis |
| GET | `/api/personas` | — | personas de conversa |
| GET | `/api/voices` | — | vozes em inglês (Edge TTS) |
| GET | `/api/categories` | — | categorias de conteúdo |
| POST | `/api/content` | `{level, module, category?}` | `{text, glossary?}` (frase/texto aleatória sem repetir) |
| POST | `/api/correct` | `{text, level}` | `{correction}` (erro→correção→regra→sugestão) |
| POST | `/api/tts` | `{text, voice?}` | `{audio_b64, format:"mp3"}` |
| POST | `/api/stt` | multipart (áudio) | `{transcript}` (Whisper, opcional) |
| POST | `/api/converse` | `{level, persona, history, message}` | `{reply}` |
| GET | `/api/grammar-levels` | — | níveis CEFR (A1–C2) |
| POST | `/api/grammar` | `{level}` | tópico de gramática (topic, structure, explanation, examples) |
| GET | `/api/memhack/categories` | — | categorias do MemHack |
| POST | `/api/memhack/next` | `{category}` | próxima frase vencida (SRS) |
| POST | `/api/memhack/review` | `{category, phrase_id, difficulty}` | registra dificuldade e devolve próxima |
| POST | `/api/auth/register` | `{username, password}` | cria usuário (**admin**) |
| GET | `/api/auth/users` | — | lista usuários (**admin**) |
| POST | `/api/admin/reload-grammar` | — | recarrega `grammar.json` (**admin**) |

## Conteúdo orientado a dados

- **Listen/Read**: dicionários `LISTEN` e `READ` em `engine.py`, chaveados por
  `nível -> categoria -> lista`. `get_content` mantém uma **fila embaralhada** por
  `(nível, módulo, categoria)` (sem repetição até esgotar). `CATEGORIES` alimenta a UI.
- **Grammar**: `backend/grammar.json` — `{"levels": [...], "grammar": {<nível>: [{topic, structure, explanation, examples}]}}`.
  Carregado em `GRAMMAR_FILE` no startup (fallback ao embutido). `reload_grammar()` + endpoint
  `POST /api/admin/reload-grammar` recarregam em runtime sem rebuild.
- **MemHack**: `backend/memhack.json` — `{"categories": [...], "phrases": {<categoria>: [{id, en, pt}]}}`.
  Progresso de repetição espaçada por usuário em `DATA_DIR/memhack_progress.json`.

## MemHack — repetição espaçada (SRS)

Estilo Leitner: cada frase tem um "box" 1–5 com intervalos crescentes
(1min → 10min → 1h → 1d → 7d). `get_memhack_next(user, category)` devolve a próxima frase
**vencida** (ou nova). `review_memhack(user, category, phrase_id, difficulty)` ajusta o box:
`facil` sobe, `medio` mantém, `dificil` desce; `due = now + intervalo(box)`. O progresso é
persistido por usuário (multi-tenant).

## Autenticação e autorização

- Middleware `auth_guard` em `main.py` protege `/` e `/api/*` (exceto rotas públicas), exigindo
  cookie de sessão HMAC (`verify_token`). Redireciona `/` → `/login` quando não autenticado.
- `_require_admin` (register/users/reload-grammar) exige usuário == `ADMIN_USER` (403 p/ comum).
- Qualquer usuário autenticado troca a própria senha (`/api/auth/change-password`).
- `me` retorna `{user, is_admin}` para o frontend ocultar a UI de gerência de usuários.

## Frontend

- Sem framework/build: HTML/CSS/JS puro.
- `app.js` usa URLs relativas (`/api/...`), então funciona no mesmo servidor.
- Gravação de voz: `MediaRecorder`; reprodução de TTS: `new Audio(data:...)`.
- Listen é ditado: o texto da frase fica oculto (`classList.add("hidden")`) até o
  "Verificar", quando é revelado (`classList.remove("hidden")`).

## Validação

Sem lint/testes automatizados. Verificação manual:
```bash
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
node --check frontend/app.js
```

## Conexao MCP

O servidor `mcp/server.py` expoe as capacidades como ferramentas MCP (stdio).
Veja [docs/technical/mcp.md](mcp.md) para conectar a Claude Desktop / OpenCode.

## Pipeline original (brainstore → skill)

`brainstore/ideias-*.md` → `scripts/convert_brainstore_to_prompt.py` →
`prompts/<skill>/` (markdown + json). `skills/english-flow/` tem o protótipo CLI
original (`app.py` + `SKILL.md`).
