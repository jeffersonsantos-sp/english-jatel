# Multi-idioma — Plano de Implementação Passo a Passo

> **Documentação de progresso**: o que já foi feito e o que ainda falta.
> Baseado na Opção C aprovada pela diretoria (Julho/2026).
> Última atualização: Julho/2026.

---

## Resumo do Estado Atual

| Módulo | Status | Notas |
|--------|--------|-------|
| Voz da IA (TTS) | ✅ **Funcional** | Vozes filtradas por idioma (en-/es-/fr-) |
| Gramática (Grammar) | ✅ **Funcional** | Arquivos `grammar_es.json` e `grammar_fr.json` criados e carregando |
| MemHack | ✅ **Funcional** | Arquivos `memhack_es.json` e `memhack_fr.json` criados, progresso name-spaced por `{user}::{lang}` |
| Conversar (Converse) | ✅ **Funcional** | Prompts da IA adaptam ao idioma selecionado |
| Correcao (Correct) | ✅ **Funcional** | Prompt do LLM adapta ao idioma |
| STT (fala → texto) | ✅ **Funcional** | Idioma dinâmico no frontend e backend (query param → body FormData) |
| Listen (ditado) | ✅ **Funcional** | Arquivos `listen_es.json` e `listen_fr.json` criados e carregando por idioma |
| Read (leitura) | ✅ **Funcional** | Arquivos `read_es.json` e `read_fr.json` criados com glossário PT-BR |
| Write (escrita) | ✅ **Funcional** | Usa `correct()` que agora é por idioma |

---

## Detalhamento do que foi implementado

### 1. Infraestrutura de idiomas (`engine.py`)

Adicionados ao topo do arquivo:

```python
SUPPORTED_LANGS = ("en", "es", "fr")
DEFAULT_LANG = "en"

LANG_META = {
    "en": {"label": "Inglês", "prompt_prefix": "professor de inglês", "stt_lang": "en-US"},
    "es": {"label": "Espanhol", "prompt_prefix": "profesor de español", "stt_lang": "es-ES"},
    "fr": {"label": "Francês", "prompt_prefix": "professeur de français", "stt_lang": "fr-FR"},
}

LANG_VOICES = {
    "en": "en-US-JennyNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
}
```

Funções auxiliares: `get_lang_meta()`, `get_default_voice()`, `_grammar_file_for_lang()`, `_memhack_file_for_lang()`.

### 2. Grammar por idioma

- `grammar.json` (EN) — já existia
- `grammar_es.json` — **criado** (6 níveis, 8 tópicos cada)
- `grammar_fr.json` — **criado** (6 níveis, 8 tópicos cada)
- `load_grammar_data(lang)` — suporta carregar por idioma
- `_load_grammar(lang)` — usa cache por idioma, fallback para EN
- `get_grammar(level, lang)` — agora aceita `lang`

### 3. MemHack por idioma

- `memhack.json` (EN) — já existia
- `memhack_es.json` — **criado** (6 categorias, 8 frases cada)
- `memhack_fr.json` — **criado** (6 categorias, 8 frases cada)
- Progresso name-spaced por `{user}::{lang}` em `memhack_progress.json`
- `get_memhack_next(user, category, lang)` — por idioma
- `review_memhack(user, category, phrase_id, difficulty, lang)` — por idioma

### 4. TTS (Text-to-Speech)

- `tts_bytes(text, voice, lang)` — seleciona voz padrão por idioma via `get_default_voice(lang)`
- `list_voices(lang)` — filtra vozes por prefixo de idioma (en-, es-, fr-)
- Cache por idioma em `_VOICES_CACHE`

### 5. STT (Speech-to-Text)

- `stt_transcribe(audio_bytes, suffix, lang)` — usa `LANG_META[lang]["stt_lang"]` para código STT
- Exemplo: ES → `es-ES`, FR → `fr-FR`

### 6. Correcao e Conversa

- `correct(text, level, lang)` — prompt adapta: "professor de español" / "professeur de français"
- `converse(level, persona, history, message, lang)` — system prompt adapta ao idioma

### 7. Frontend (`app.js`)

- Todas as chamadas API agora enviam `lang=state.lang`
- Seletor de idioma na UI muda o `state.lang`
- Troca de idioma tambem recarrega as vozes (`/api/voices?lang=es`)
- `playTts()` envia `lang` no body da requisicao TTS

### 8. Backend (`main.py`)

Todos os endpoints relevantes agora aceitam `lang`:
- `GET /api/voices?lang=es`
- `GET /api/memhack/categories?lang=es`
- `POST /api/content` — body: `{..., lang: "es"}`
- `POST /api/correct` — body: `{..., lang: "es"}`
- `POST /api/tts` — body: `{..., lang: "es"}`
- `POST /api/stt` — query: `?lang=es`
- `POST /api/converse` — body: `{..., lang: "es"}`
- `POST /api/grammar` — body: `{..., lang: "es"}`
- `POST /api/memhack/next` — body: `{..., lang: "es"}`
- `POST /api/memhack/review` — body: `{..., lang: "es"}`

---

## O que ainda precisa ser implementado (passo a passo)

### ✅ Passo A: STT hardcoded no frontend (resolvido)

**Correção aplicada**:
1. `getSpeechRecognition(lang)` já era dinâmico (aceitava `lang` como parâmetro e mapeava para `es-ES`/`fr-FR`/`en-US`)
2. `browserSpeak(text)` hardcodeava `en-US` — corrigido para aceitar parâmetro `lang` e mapear para `es-ES`/`fr-FR`/`en-US`
3. `playTts()` agora passa `state.lang` para `browserSpeak()`

**Arquivo**: `frontend/app.js` (linhas ~29-60)

### ✅ Passo B/C: Listen/Read por idioma (resolvido)

**Arquivos criados**:
- `backend/listen_es.json` — frases de ditado em espanhol (3 níveis × 3 categorias × 8 frases)
- `backend/read_es.json` — textos de leitura em espanhol com glossário PT-BR
- `backend/listen_fr.json` — frases de ditado em francês (3 níveis × 3 categorias × 8 frases)
- `backend/read_fr.json` — textos de leitura em francês com glossário PT-BR

**Atualizações em `engine.py`**:
- Adicionados `_listen_file_for_lang()`, `_read_file_for_lang()`, `_load_listen_file()`, `_load_read_file()`
- Adicionados `_LISTEN_CACHE` e `_READ_CACHE` por idioma
- `_next_item()` agora aceita `lang` e carrega conteúdo do arquivo por idioma quando disponível
- `get_content()` passa `lang` para `_next_item()`
- `_CONTENT_QUEUES` agora inclui `lang` como quarta chave da tupla

### ✅ Passo D: Correção heuristics — limitação documentada

**Status**: Acceptable for initial phase. `heuristic_correct()` usa regex específicas de inglês; para ES/FR retorna fallback quando o LLM não está disponível. A correção real para ES/FR é feita pelo LLM via `correct()`.

### ✅ Passo E: Cache invalidation (resolvido)

**Problema**: `reload_grammar()` limpava `GRAMMAR_CACHE` mas não `_MEMHACK_CACHE`, `_LISTEN_CACHE` nem `_READ_CACHE`.

**Correção aplicada**:
- `reload_grammar(lang)` agora também invalida `_MEMHACK_CACHE`, `_LISTEN_CACHE` e `_READ_CACHE` para a linguagem específica
- `reload_grammar()` (sem `lang`) limpa todos os caches de conteúdo
- Limpeza de `_CONTENT_QUEUES` atualizada para filtrar por `lang` na tupla

### ✅ Passo F: STT multipart `lang` (resolvido)

**Problema**: O endpoint `POST /api/stt` usava `lang` como query parameter, o que pode não funcionar corretamente com FormData multipart no frontend.

**Correção aplicada**:
- Frontend (`app.js`): `lang` agora é enviado como campo FormData (`fd.append("lang", state.lang)`) em vez de query parameter
- Backend (`main.py`): endpoint STT agora usa `Form("en")` para ler `lang` do body do FormData
- Export `Form` adicionado aos imports do `fastapi` em `main.py`

### ✅ Passo G: Validação e testes (concluído)

Todos os testes passaram:
- Health check: OK
- Grammar por idioma (EN/ES/FR): OK
- MemHack por idioma (EN/ES/FR): OK (6 categorias cada)
- Listen/Read por idioma (EN/ES/FR): OK (conteúdo e glossário corretos)
- TTS por idioma (EN/ES/FR): OK
- Correct per language (EN/ES/FR): OK
- Frontend syntax (JS): OK
- Todos os JSON files validam: OK

---

## Arquivos modificados ate agora

| Arquivo | Alteracao |
|---------|-----------|
| `backend/engine.py` | Infraestrutura multi-idioma (LANG_META, LANG_VOICES, funcoes com `lang`), cache invalidation em `reload_grammar()`, suporte a Listen/Read per-language com `_LISTEN_CACHE`, `_READ_CACHE`, `_listen_file_for_lang()`, `_read_file_for_lang()`, `_load_listen_file()`, `_load_read_file()` |
| `backend/main.py` | Todos endpoints recebem `lang`; STT endpoint agora usa `Form("en")` para ler `lang` do body FormData; `Form` importado do fastapi |
| `backend/grammar_es.json` | Novo — grammar CEFR para espanhol |
| `backend/grammar_fr.json` | Novo — grammar CEFR para frances |
| `backend/memhack_es.json` | Novo — frases para espanhol |
| `backend/memhack_fr.json` | Novo — frases para frances |
| `backend/listen_es.json` | Novo — frases de ditado para espanhol (3 niveis × 3 categorias) |
| `backend/read_es.json` | Novo — textos de leitura para espanhol com glossario PT-BR |
| `backend/listen_fr.json` | Novo — frases de ditado para frances (3 niveis × 3 categorias) |
| `backend/read_fr.json` | Novo — textos de leitura para frances com glossario PT-BR |
| `frontend/app.js` | Envia `lang` em todas as chamadas API; recarrega vozes ao trocar idioma; `browserSpeak(text, lang)` agora usa codigo de idioma apropriado (es-ES/fr-FR/en-US); STT envia `lang` no body FormData em vez de query param |
| `frontend/index.html` | Flag FR corrigida (🇫🇷) |

---

> **Nota**: antes de cada implementacao, seguir o procedimento de backup da skill `backup-procedures`.

---

## Próximos passos — Conversa (Persona)

### Planejado: Remover Category selector e corrigir Persona na IA

**Problema atual**: O módulo Conversa tem um seletor de Categoria separado do seletor de Persona. A Categoria é redundante — cada Persona já define o contexto de conversa (ex.: `cafe` = conversa informal, `devops` = contexto técnico). A IA também não reconhece bem a escolha de Persona, porque o `persona` é enviado ao LLM mas o system prompt não reforça o papel associado à persona.

**O que será feito**:
1. Remover o seletor de Categoria da UI de Conversa (já está descontinuado no `app.js`)
2. Garantir que a Persona selecionada seja passada corretamente ao LLM no system prompt
3. Melhorar o system prompt do `converse()` para reforçar o papel da persona escolhida
4. Mapear cada persona para um nome de papel em português/inglês que a IA entenda

**Arquivos envolvidos**: `frontend/app.js`, `backend/engine.py`, `backend/main.py`

#### Detalhamento da Persona fix:

O `converse()` em `engine.py` usa o `PERSONAS` dict para o prefixo do prompt:
```python
persona_label = PERSONAS.get(persona, persona)
prompt = f"Voce e um {persona_label}. Responda em {lang_label}..."
```

O problema é que o `PERSONAS` dict tem valores em português que descrevem o papel ("amigo tomando café", "colega de DevOps"), mas o LLM não interpreta bem esse papel. A melhoria é usar nomes de papel mais explícitos e estruturados, e reforçar no system prompt que a IA DEVE adotar o papel da persona selecionada.

---

## Ordem de execução recomendada (próximos passos)

| Fase | Item | Esforco | Dependencia |
|------|------|---------|-------------|
| **1** | Remover Category selector da UI de Conversa | Baixo | Nenhuma |
| **2** | Melhorar system prompt de converse() com persona role explícito | Medio | Nenhuma |
| **3** | Mapear personas para nomes de papel claros (EN/ES/FR) | Baixo | Passo 2 |
| **4** | Testar e validar que a IA reconhece a persona escolhida | Medio | Fases 1-3 |