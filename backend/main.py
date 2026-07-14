"""API FastAPI do english-flow.

Endpoints:
  GET  /api/health
  GET  /api/levels
  GET  /api/personas
  GET  /api/voices
  POST /api/content      {level, module} -> {text, glossary?}
  POST /api/correct      {text, level} -> {correction}
  POST /api/tts          {text, voice?} -> audio/* (bytes)
  POST /api/stt          multipart audio -> {transcript}
  POST /api/converse     {level, persona, history, message} -> {reply}
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import base64
import os

import engine

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = FastAPI(title="English Flow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContentReq(BaseModel):
    level: str
    module: str
    category: str = "all"


class TtsReq(BaseModel):
    text: str
    voice: str = None


class CorrectReq(BaseModel):
    text: str
    level: str = "iniciante"


class ConverseReq(BaseModel):
    level: str = "iniciante"
    persona: str = "cafe"
    history: List[Dict[str, str]] = []
    message: str = ""


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm": bool(engine.API_KEY),
        "provider": "openrouter" if engine.IS_OPENROUTER else ("openai" if engine.API_KEY else "demo"),
    }


@app.get("/api/levels")
def levels():
    return {"levels": engine.LEVELS}


@app.get("/api/personas")
def personas():
    return {"personas": list(engine.PERSONAS.keys())}


@app.get("/api/categories")
def categories():
    return {"categories": engine.CATEGORIES}


@app.post("/api/content")
def content(req: ContentReq):
    return engine.get_content(req.level, req.module, req.category)


@app.post("/api/correct")
def correct(req: CorrectReq):
    return {"correction": engine.correct(req.text, req.level)}


@app.get("/api/voices")
def voices():
    return {"voices": engine.list_voices()}


@app.post("/api/tts")
async def tts(req: TtsReq):
    audio = engine.tts_bytes(req.text, req.voice)
    if not audio:
        raise HTTPException(status_code=501, detail="TTS indisponivel")
    b64 = base64.b64encode(audio).decode()
    return {"audio_b64": b64, "format": "mp3"}


@app.post("/api/stt")
async def stt(file: UploadFile = File(...)):
    data = await file.read()
    suffix = "." + (file.filename.split(".")[-1] if file.filename and "." in file.filename else "webm")
    try:
        transcript = engine.stt_transcribe(data, suffix)
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"transcript": transcript}


@app.post("/api/converse")
def converse(req: ConverseReq):
    reply = engine.converse(req.level, req.persona, req.history, req.message)
    return {"reply": reply}


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
