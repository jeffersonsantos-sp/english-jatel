# English Flow — App de ensino de inglês

Treina as 4 habilidades (**listen, speak, write, read**) com correções e
**conversação por IA** (a IA fala e você fala com ela).

## Arquitetura
- `backend/` — API FastAPI (`engine.py` + `main.py`)
- `frontend/` — SPA sem build (HTML/CSS/JS puro)
- `skills/english-flow/` — skill/cli protótipo original
- `brainstore/` — ideia de produto (origem)
- `prompts/english-flow/` — prompt gerado a partir do brainstore

## Como rodar (um único servidor)

O backend serve a API **e** o frontend (SPA) na mesma porta, evitando
problemas de CORS/portas.

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Abra **http://localhost:8000** no navegador (Chrome recomendado para voz).

> O frontend usa URL relativa (`/api/...`), então não precisa de servidor
> separado nem de CORS.

## Modo demo vs. modo IA

### OpenRouter (recomendado — texto-only)
```bash
export OPENROUTER_API_KEY=sk-or-...
export OPENAI_MODEL=openai/gpt-4o-mini   # slug do OpenRouter
# opcional: export OPENROUTER_REFERER=... OPENROUTER_TITLE="English Flow"
```
> A **voz da IA é gerada pelo Edge TTS** (vozes neurais em inglês, sem chave),
> muito superior à voz padrão do navegador. Voz padrão `en-US-JennyNeural`;
> troque com `export EDGE_TTS_VOICE=en-US-GuyNeural`. Se o Edge TTS falhar,
> o frontend usa `speechSynthesis` como fallback.

### OpenAI (opcional, com TTS)
```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini
```
Usa `tts-1` para voz da IA quando disponível.

### Sem chave (modo demo)
Correção heurística + voz do navegador. Funciona para testar a UI.

Em todos os casos, a fala do usuário pode ser transcrita via Whisper no
endpoint `/api/stt` (opcional).


## Endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/health` | status + se LLM está ativo |
| GET | `/api/levels` | níveis disponíveis |
| GET | `/api/personas` | personas de conversação |
| POST | `/api/content` | texto/glossário por nível+módulo |
| POST | `/api/correct` | corrige texto (erro→correção→regra→sugestão) |
| POST | `/api/tts` | gera áudio (base64) da frase |
| POST | `/api/stt` | transcreve áudio enviado |
| POST | `/api/converse` | turno de conversa com a IA |

## Próximos passos sugeridos
- Histórico de erros recorrentes + revisão espaçada.
- Autenticação de usuário e progresso persistente.
- Mais conteúdo por nível e testes automatizados.
