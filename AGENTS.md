# AGENTS.md — English JATEL

App de ensino de **inglês** (listen/speak/write/read + conversação por IA).
Backend FastAPI serve a API **e** o frontend estático a partir de um único servidor.

## Como rodar (um comando)
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Abra **http://localhost:8000** (o frontend `frontend/` é servido pelo próprio FastAPI; não há servidor estático separado).

## Ambiente Python (gotcha importante)
O Python deste SO é *externally managed* (PEP 668). `pip install` puro falha.
- Recomendado: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Alternativa: `pip install -r requirements.txt --break-system-packages`
- O STT usa `SpeechRecognition` (Google Speech API gratuita, sem chave) + `ffmpeg` para converter áudio. O ffmpeg precisa estar instalado no sistema.

## Segredos / config
- `backend/.env` contém `OPENROUTER_API_KEY`, `OPENAI_MODEL`, `OPENROUTER_TITLE`. Está no `.gitignore` — **não comitar**.
- `engine.py` carrega `.env` relativo ao próprio diretório (`backend/.env`).
- LLM usado: **OpenRouter** (texto-only). Não há TTS no OpenRouter; a voz vem do **Edge TTS** (sem chave, backend gera MP3). Fallback final no frontend: `speechSynthesis` do navegador.
- Para trocar a voz da IA: `export EDGE_TTS_VOICE=en-US-GuyNeural` (ou via seletor no topo da UI).

## Arquitetura (não óbvia pelos nomes)
- `backend/main.py`: rotas `/api/*` são registradas **antes** de `app.mount("/", StaticFiles(...))`, então elas têm prioridade sobre o estático. `GET /` retorna `frontend/index.html`.
- `backend/engine.py`: toda a lógica (correção, TTS, STT, conversa, conteúdo).
- `frontend/`: SPA vanilla (HTML/CSS/JS, sem build). `app.js` usa URLs relativas (`/api/...`).
- Banco de frases: dicionários `LISTEN`/`READ` em `engine.py` (para inglês) e arquivos `listen_{lang}.json`/`read_{lang}.json` para ES/FR, chaveados por `nível → categoria → lista`. `get_content` usa uma fila embaralhada por `(nível, módulo, categoria, lang)` (sem repetir até esgotar). **Para adicionar frases EN, edite esses dicts; para ES/FR, edite os arquivos JSON correspondentes.**
- **Grammar (CEFR)**: conteúdo é **orientado a dados**, em `backend/grammar.json` (`{"levels": [...], "grammar": {<nível>: [{topic, structure, explanation, examples}]}}`). No startup o `engine.py` carrega esse arquivo (fallback ao dicionário embutido se faltar/inválido). **Para adicionar/editar lições de Grammar, edite `grammar.json`** e recarregue sem rebuild via `POST /api/admin/reload-grammar` (só admin).
- Listen é exercício de **ditado**: o frontend esconde o texto da frase até o "Verificar". Não antecipe a exibição.
- **STT**: `SpeechRecognition` (Google Speech API, gratuita, sem chave) no frontend com fallback para `/api/stt`. O `lang` é enviado no body FormData (não como query param). O ffmpeg precisa estar instalado no sistema para conversão de áudio.

## Validação (sem lint/testes configurados)
- Backend (sem subir servidor): `python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"`
- Frontend: `node --check frontend/app.js`
- Não há suíte de testes, typecheck ou lint neste repo.

## Procedimentos de Backup (backup-procedures skill)
Antes de fazer qualquer alteração no código, configuração ou conteúdo, é obrigatório criar um backup usando a skill `backup-procedures`. Esta skill está disponível em `.opencode/skills/backup-procedures/SKILL.md` e fornece procedimentos para:

- Criar backup local completo antes de alterações
- Verificar a integridade do backup
- Restaurar do backup se necessário
- Melhores práticas para proteção contra erros humanos

Para usar esta skill, simplesmente siga os procedimentos descritos no arquivo SKILL.md ou peça para que eu (o agente) execute o backup antes de qualquer modificação.

Os backups são armazenados no diretório `repo-backup/` que está ignorado pelo Git (ver .gitignore).
