# MCP (Model Context Protocol) - Britlearn Academy

## Visao Geral

O MCP permite integrar as capacidades do Britlearn Academy com ferramentas de IA externas (IDEs, agents, etc).

---

## MCP Server Configuration

### Configuracao para IDEs (Cursor, VS Code, etc)

```json
{
  "mcpServers": {
    "britlearn": {
      "command": "python",
      "args": ["-m", "mcp_server_britlearn"],
      "env": {
        "BRITLEARN_API_URL": "https://britlearnacademy.online/app/api",
        "BRITLEARN_API_KEY": "sua-chave-aqui"
      }
    }
  }
}
```

---

## Ferramentas MCP Disponiveis

### 1. grammar_check
**Descricao**: Verifica gramatica de texto

**Parametros**:
```json
{
  "text": "I goes to school every day",
  "level": "A1",
  "language": "en"
}
```

**Resposta**:
```json
{
  "corrections": [
    {
      "error": "goes",
      "correction": "go",
      "rule": "Subject-verb agreement: I + go (not goes)",
      "suggestion": "Remember: I/you/we/they + go, he/she/it + goes"
    }
  ],
  "score": 0.85
}
```

---

### 2. conversation_start
**Descricao**: Inicia uma conversa com IA

**Parametros**:
```json
{
  "topic": "daily_routines",
  "level": "B1",
  "language": "en"
}
```

**Resposta**:
```json
{
  "response": "Hello! I'd love to chat about daily routines. What does a typical day look like for you?",
  "suggestions": ["I usually wake up at...", "My morning routine is..."]
}
```

---

### 3. tts_generate
**Descricao**: Gera audio a partir de texto

**Parametros**:
```json
{
  "text": "Hello, how are you today?",
  "voice": "en-GB-RyanNeural",
  "rate": "+0%",
  "pitch": "+0Hz"
}
```

**Resposta**:
```json
{
  "audio_base64": "UklGRi...",
  "duration_ms": 3200,
  "format": "mp3"
}
```

---

### 4. content_list
**Descricao**: Lista conteudo disponivel

**Parametros**:
```json
{
  "module": "grammar",
  "level": "A1",
  "language": "en"
}
```

**Resposta**:
```json
{
  "items": [
    {
      "id": "present_simple",
      "title": "Present Simple",
      "description": "Basic verb conjugation",
      "difficulty": 1
    }
  ],
  "total": 15
}
```

---

## Integração com Agents

### Exemplo: Claude Code / OpenCode

```python
# Adicionar ao AGENTS.md
## MCP Integration
- Use britlearn MCP server for grammar checks
- Tool: britlearn:grammar_check
- Tool: britlearn:conversation_start
- Tool: britlearn:tts_generate
```

### Exemplo: Custom Agent

```python
import httpx

class BritlearnAgent:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def check_grammar(self, text: str, level: str = "B1"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/grammar",
                json={"text": text, "level": level},
                headers=self.headers
            )
            return response.json()
    
    async def start_conversation(self, topic: str, level: str = "A2"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/conversation",
                json={"topic": topic, "level": level},
                headers=self.headers
            )
            return response.json()
```

---

## Endpoints da API (MCP-compatible)

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| `/api/health` | GET | Health check |
| `/api/grammar` | POST | Correcao gramatical |
| `/api/conversation` | POST | Chat com IA |
| `/api/tts` | POST | Text-to-Speech |
| `/api/stt` | POST | Speech-to-Text |
| `/api/content/{module}` | GET | Listar conteudo |
| `/api/auth/login` | POST | Login |

---

## Seguranca

- API keys via headers `Authorization: Bearer <key>`
- Rate limiting por IP
- CORS configurado para dominios especificos
- HTTPS obrigatorio em producao
