---
name: english-flow
description: >
  App de ensino de ingles que treina as 4 habilidades (listen, speak, write, read)
  com correcao automatica e conversacao por IA (voz com voz). Use para ensinar,
  praticar ou estender um tutor de ingles em português: ditado, fala, escrita,
  leitura e chat de conversacao com LLM + TTS neural.
---

# SKILL: english-flow

Tutor de ingles full-stack: backend FastAPI (API + frontend estatico num so
servidor) e frontend SPA sem build. Corrige texto com LLM, fala com Edge TTS
(vozes neurais, sem chave) e conversa por LLM (OpenRouter, texto-only).

## Quando usar
- Criar, rodar ou explicar o app English Flow.
- Adicionar frases/textos, vozes, categorias ou modulos de treino.
- Integrar LLM/TTS/STT ou ajustar correcao gramatical.
- Estender a conversacao por IA (personas, contexto, niveis).

## Arquitetura (ver docs/technical/arquitetura.md)
- `backend/main.py`: rotas `/api/*` registradas ANTES de `app.mount("/", StaticFiles(...))`,
  entao a API tem prioridade. `GET /` serve `frontend/index.html`.
- `backend/engine.py`: toda a logica (correcao, TTS, STT, conversa, banco de frases).
- `frontend/`: SPA vanilla (`index.html`, `style.css`, `app.js`), URLs relativas `/api/...`.
- Banco de frases: `LISTEN`/`READ` em `engine.py`, chaveados por `nivel -> categoria -> lista`.
  `get_content` usa fila embaralhada por `(nivel, modulo, categoria)` — sem repetir ate esgotar.

## Como rodar
```bash
cd backend
pip install -r requirements.txt            # PEP 668: use venv ou --break-system-packages
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# abra http://localhost:8000
```
- `backend/.env` (gitignored) tem `OPENROUTER_API_KEY`, `OPENAI_MODEL`, `OPENROUTER_TITLE`.
- Sem chave: correcao heuristica + voz do navegador (modo demo).

## Provedores (config via env)
- **LLM**: OpenRouter (texto-only) via cliente OpenAI-compatível; `BASE_URL` aponta para
  `https://openrouter.ai/api/v1`, com headers `HTTP-Referer`/`X-Title`.
- **TTS**: `engine.tts_bytes` prioriza Edge TTS (sem chave) -> OpenAI `tts-1` -> `pyttsx3`;
  frontend faz fallback para `speechSynthesis`. Voz: `EDGE_TTS_VOICE` ou param `voice` em `/api/tts`.
- **STT**: Whisper opcional no `/api/stt` (transcreve audio enviado).

## Modulos e fluxo
- **listen (ditado)**: `POST /api/content` (module=listen) -> TTS da frase; frontend ESCODE o
  texto ate "Verificar" (`classList.add("hidden")`), depois revela e compara com o ditado.
  "Proxima" puxa nova frase sem repetir.
- **speak**: grava (MediaRecorder) -> `POST /api/stt` -> transcricao -> `POST /api/correct`.
- **write**: texto -> `POST /api/correct` -> `ERRO -> CORRECAO -> REGRA -> SUGESTAO`.
- **read**: `POST /api/content` (module=read) -> texto + glossario; pergunta -> `POST /api/correct`.
- **converse**: `POST /api/converse` com `{level, persona, history, message}` -> resposta da IA;
  frontend fala a resposta (TTS) e mantem o historico.

## Endpoints (resumo)
| Metodo | Rota | Corpo | Retorno |
|--------|------|-------|---------|
| GET | `/api/health` | — | `{status, llm, provider}` |
| GET | `/api/levels` | — | niveis |
| GET | `/api/personas` | — | personas |
| GET | `/api/voices` | — | vozes em ingles (Edge TTS) |
| GET | `/api/categories` | — | categorias |
| POST | `/api/content` | `{level, module, category?}` | `{text, glossary?}` |
| POST | `/api/correct` | `{text, level}` | `{correction}` |
| POST | `/api/tts` | `{text, voice?}` | `{audio_b64, format:"mp3"}` |
| POST | `/api/stt` | multipart audio | `{transcript}` |
| POST | `/api/converse` | `{level, persona, history, message}` | `{reply}` |

## Como estender
- **Mais frases**: edite `LISTEN`/`READ` em `engine.py` (mantenha `CATEGORIES` em sync).
- **Nova voz**: `export EDGE_TTS_VOICE=...` ou adicione ao seletor em `frontend/index.html`.
- **Nova categoria**: adicione a `CATEGORIES` e às chaves dos dicionarios.
- **Novo modulo**: adicione rota em `main.py` + handler em `engine.py` + aba em `frontend/index.html` + listener em `app.js`.

## Validacao (sem lint/testes)
```bash
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"
node --check frontend/app.js
```

## Arquivos principais
- `backend/main.py`, `backend/engine.py`, `backend/.env`, `backend/requirements.txt`
- `frontend/index.html`, `frontend/style.css`, `frontend/app.js`
- `docs/user/guia.md`, `docs/technical/arquitetura.md`, `AGENTS.md`
- Protótipo CLI original: `skills/english-flow/app.py`
