#!/usr/bin/env python3
"""Servidor MCP minimo do english-flow.

Expe as capacidades do backend como ferramentas MCP, reaproveitando
`backend/engine.py` (sem reimplementar logica). Roda em transporte stdio
(padrao do FastMCP), entao pode ser conectado a um agente/IDE via MCP.

Uso:
  python mcp/server.py
Ou, para expor a um cliente MCP:
  uvx / mcp-client apontando para este script.

Dependencias: mcp (SDK), + backend/requirements.txt (openai, edge-tts, ...).
"""

import os
import sys
import base64

# Garante que o backend (engine.py) seja importavel a partir daqui.
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mcp.server.fastmcp import FastMCP  # type: ignore

import engine  # carrega backend/.env e banco de frases

mcp = FastMCP("english-flow-mcp")


@mcp.tool()
def correct_text(text: str, level: str = "iniciante") -> str:
    """Corrige um texto em ingles (nivel: iniciante|intermediario|avancado).
    Retorna correcao no formato ERRO -> CORRECAO -> REGRA -> SUGESTAO."""
    return engine.correct(text, level)


@mcp.tool()
def generate_tts(text: str, voice: str = None) -> str:
    """Gera audio (MP3 base64) da frase usando Edge TTS (voz neural, sem chave).
    `voice` opcional (ex.: en-US-JennyNeural, en-US-GuyNeural). Retorna string
    base64 vazia se o TTS estiver indisponivel."""
    audio = engine.tts_bytes(text, voice)
    return base64.b64encode(audio).decode() if audio else ""


@mcp.tool()
def converse(level: str = "iniciante", persona: str = "cafe",
             history: list = None, message: str = "") -> str:
    """Turno de conversa com a IA (nivel + persona: cafe|entrevistador|negocios).
    `history` e a lista de mensagens anteriores [{role, content}]."""
    history = history or []
    return engine.converse(level, persona, history, message)


@mcp.tool()
def get_content(level: str = "iniciante", module: str = "listen",
                category: str = "all") -> dict:
    """Retorna uma frase/texto de treino (module: listen|read) por nivel e
    categoria (rotina|trabalho|viagem|all). Sem repetir ate esgotar o conjunto."""
    return engine.get_content(level, module, category)


if __name__ == "__main__":
    mcp.run()
