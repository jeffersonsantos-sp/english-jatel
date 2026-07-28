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
| STT (fala → texto) | ⚠️ **Parcial** | Idioma correto no backend, mas frontend hardcoded `en-US` |
| Listen (ditado) | ❌ **Inglês apenas** | Conteúdo `LISTEN` e `READ` em `engine.py` são hardcoded em inglês |
| Read (leitura) | ❌ **Inglês apenas** | Conteúdo `READ` em `engine.py` é hardcoded em inglês |
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

### ❌ Passo A: STT hardcoded no frontend (urgente)

**Problema**: `app.js` linha 208 tem `r.lang = "en-US"` hardcoded. Quando o usuario seleciona Espanhol ou Frances, o STT continua usando `en-US`.

**O que fazer**: Ajustar `getSpeechRecognition()` para usar `LANG_META[lang].stt_lang` dinamicamente.

**Arquivo**: `frontend/app.js`, linha ~208

**Solução**: Passar `state.lang` para `getSpeechRecognition()` e mapear o código STT.

```javascript
function getSpeechRecognition(lang) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r = new SR();
  const sttLang = lang === "es" ? "es-ES" : lang === "fr" ? "fr-FR" : "en-US";
  r.lang = sttLang;
  r.interimResults = false;
  r.maxAlternatives = 1;
  return r;
}
```

Depois atualizar todas as chamadas: `getSpeechRecognition(state.lang)`.

---

### ❌ Passo B: Listen — conteúdo por idioma (fase 2)

**Problema**: `LISTEN` e `READ` em `engine.py` são dicts hardcoded em inglês. Não há arquivos de conteúdo Listen/Read para ES/FR.

**O que fazer**:

#### Opção B1: Per-language files (recomendado)
Criar `listen_es.json`, `read_es.json`, `listen_fr.json`, `read_fr.json` com a mesma estrutura dos dicts em `engine.py`:

```json
{
  "iniciante": {
    "rotina": [
      "Me levanto temprano cada mañana.",
      "Me cepillo los dientes después del desayuno."
    ],
    "trabajo": [...],
    "viagem": [...]
  },
  "intermediario": { ... },
  "avancado": { ... }
}
```

Depois atualizar `engine.py` para carregar Listen/Read por idioma:

```python
def _listen_file_for_lang(lang: str) -> str:
    if lang == DEFAULT_LANG:
        return None  # usa dict embutido
    alt = os.path.join(os.path.dirname(__file__), f"listen_{lang}.json")
    return alt if os.path.exists(alt) else None

def _read_file_for_lang(lang: str) -> str:
    if lang == DEFAULT_LANG:
        return None
    alt = os.path.join(os.path.dirname(__file__), f"read_{lang}.json")
    return alt if os.path.exists(alt) else None

def _load_listen(lang: str = DEFAULT_LANG):
    # ... similar a _load_memhack
    pass

def _load_read(lang: str = DEFAULT_LANG):
    # ... similar a _load_memhack
    pass
```

E modificar `_next_item(level, module, category, lang)` para usar a source correta.

#### Opção B2: Expandir os dicts embutidos
Adicionar listas ES/FR dentro dos próprios dicts `LISTEN` e `READ` em `engine.py`.

Mais simples, mas polui o código. Menos recomendado.

---

### ❌ Passo C: Read — conteúdo com glossário por idioma

**Problema**: Igual ao Listen — `READ` dict é hardcoded em inglês e inclui glossário PT-BR.

**Requisitos para os arquivos por idioma**:
- Cada entrada precisa de `text` (no idioma alvo) e `glossary` (traducoes PT-BR)
- Exemplo para ES: `{"text": "Ana se despierta a las siete...", "glossary": {"despierta": "acorda", ...}}`

**Implementação**: Igual ao Passo B, usando por-language files ou expandindo os dicts.

---

### ⚠️ Passo D: Correcao heuristics — apenas ingles

**Problema**: A funcao `heuristic_correct()` (engine.py) detecta erros de conjugacao em ingles (3ª pessoa singular -s, etc.). Nao funciona para ES ou FR porque usa regex especifico de ingles.

**O que fazer**: Para FR/ES, o `heuristic_correct()` retorna "Sem erros obvios" (o fallback atual). Isso é aceitavel para a fase inicial. O LLM fara a correcao real nos outros idiomas.

**Melhora futura**: Adaptar `heuristic_correct()` para espanhol e frances, ou remover e depender do LLM em todos os idiomas.

---

### ⚠️ Passo E: Caching de grammar/memhack por idioma

**Problema**: `GRAMMAR_CACHE` e `_MEMHACK_CACHE` usam `lang` como chave, mas os caches nao sao invalidados quando o `reload_grammar(lang)` e chamado. O `_MEMHACK_CACHE` precisa de invalidacao similar.

**O que fazer**: Adicionar invalidacao de cache para `_load_memhack(lang)`:

```python
def _load_memhack(lang: str = DEFAULT_LANG):
    if lang in _MEMHACK_CACHE and _MEMHACK_CACHE[lang] is not None:
        return _MEMHACK_CACHE[lang]
    # ... carregar do arquivo
```

E atualizar `reload_grammar()` para invalidar ambos os caches.

---

### ⚠️ Passo F: Upload de audio — `lang` no multipart

**Problema**: O endpoint `POST /api/stt` usa `lang` como query parameter, mas o frontend `app.js` faz `fetch` com `FormData` via `api()` que nao suporta query params bem no multipart. Verificar se `lang` chega ao backend.

**O que fazer**: Testar manualmente enviando audio para `/api/stt?lang=es` e verificar se a transcrição sai em espanhol. Se nao funcionar, mudar para enviar `lang` no body do FormData em vez de query param.

---

### 📋 Passo G: Validação e testes

Apos cada implementacao, rodar:

```bash
# 1. Health check
python3 -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); print(c.get('/api/health').json())"

# 2. Grammar por idioma
python3 -c "
from fastapi.testclient import TestClient
import main as m
c = TestClient(m.app)
# login
c.post('/api/auth/login', json={'user':'admin','password':'mudar123'})
for lang in ['en','es','fr']:
    r = c.post('/api/grammar', json={'level':'A1','lang':lang})
    print(lang, r.json().get('topic','N/A')[:50])
"

# 3. MemHack por idioma
python3 -c "
from fastapi.testclient import TestClient
import main as m
c = TestClient(m.app)
c.post('/api/auth/login', json={'user':'admin','password':'mudar123'})
for lang in ['en','es','fr']:
    r = c.get(f'/api/memhack/categories?lang={lang}')
    print(lang, len(r.json().get('categories',[])))
"

# 4. Frontend syntax
node --check frontend/app.js
node --check frontend/auth.js

# 5. JSON validation
python3 -m json.tool backend/grammar_es.json > /dev/null
python3 -m json.tool backend/grammar_fr.json > /dev/null
python3 -m json.tool backend/memhack_es.json > /dev/null
python3 -m json.tool backend/memhack_fr.json > /dev/null
```

---

## Roadmap Recomendado

| Fase | Item | Esforco | Dependencia |
|------|------|---------|-------------|
| **1** | Fix STT hardcoded `en-US` no frontend | Baixo | Nenhuma |
| **2** | Listen/Read per-language files (EN/ES/FR) | Medio-Alto | Passo A |
| **3** | Correcao heuristics para ES/FR | Medio | Passo A |
| **4** | Cache invalidation para grammar/memhack | Baixo | Nenhuma |
| **5** | STT multipart `lang` fix | Medio | Passo A |
| **6** | Validacao e testes completos | Medio | Todos |

### Ordem de execucao recomendada:
1. **Passo A** (STT hardcoded) — 15 min, fixa o mais urgente
2. **Passo G** (Validacao) — 30 min, garante qualidade
3. **Passo E** (Cache invalidation) — 20 min, corrige potencial bug
4. **Passo F** (STT multipart) — 30 min, garante STT funcional para ES/FR
5. **Passo B/C** (Listen/Read per-language) — 4-6h, maior impacto
6. **Passo D** (Correcao heuristics ES/FR) — 2h, nice-to-have
7. **Passo G** final (testes completos) — 30 min

---

## Arquivos modificados ate agora

| Arquivo | Alteracao |
|---------|-----------|
| `backend/engine.py` | Infraestrutura multi-idioma (LANG_META, LANG_VOICES, funcoes com `lang`) |
| `backend/main.py` | Todos endpoints recebem `lang` |
| `backend/grammar_es.json` | Novo — grammar CEFR para espanhol |
| `backend/grammar_fr.json` | Novo — grammar CEFR para frances |
| `backend/memhack_es.json` | Novo — frases para espanhol |
| `backend/memhack_fr.json` | Novo — frases para frances |
| `frontend/app.js` | Envia `lang` em todas as chamadas API, recarrega vozes ao trocar idioma |
| `frontend/index.html` | Flag FR corrigida (🇫🇷) |

---

> **Nota**: antes de cada implementacao, seguir o procedimento de backup da skill `backup-procedures`.