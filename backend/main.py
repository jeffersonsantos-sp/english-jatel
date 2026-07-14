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

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import base64
import os
import hmac

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


class LoginReq(BaseModel):
    user: str
    password: str


class ChangePassReq(BaseModel):
    current_password: str
    new_password: str


# ---- Auth guard: protege "/" e "/api/*" (exceto rotas públicas) ----
PUBLIC_API = {"/api/auth/login", "/api/auth/logout", "/api/auth/me", "/api/health"}


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_API or path in ("/login", "/login.html"):
        return await call_next(request)
    is_api = path.startswith("/api/")
    is_root = path == "/"
    if not (is_api or is_root):  # assets estáticos (css/js/img) são públicos
        return await call_next(request)
    if engine.verify_token(request.cookies.get("session", "")):
        return await call_next(request)
    if is_api:
        return JSONResponse(status_code=401, content={"detail": "nao autenticado"})
    return RedirectResponse("/login", status_code=307)


@app.post("/api/auth/login")
def login(req: LoginReq, response: Response):
    if req.user == engine.ADMIN_USER and hmac.compare_digest(req.password, engine.current_admin_pass):
        token = engine.make_token(req.user)
        response.set_cookie(
            "session", token, httponly=True, samesite="lax", path="/", max_age=604800
        )
        return {"ok": True}
    raise HTTPException(status_code=401, detail="usuario ou senha invalidos")


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"ok": True}


@app.get("/api/auth/me")
def me(request: Request):
    if engine.verify_token(request.cookies.get("session", "")):
        return {"user": engine.ADMIN_USER}
    raise HTTPException(status_code=401, detail="nao autenticado")


@app.post("/api/auth/change-password")
def change_password(req: ChangePassReq, request: Request, response: Response):
    if not engine.verify_token(request.cookies.get("session", "")):
        raise HTTPException(status_code=401, detail="nao autenticado")
    if not hmac.compare_digest(req.current_password, engine.current_admin_pass):
        raise HTTPException(status_code=400, detail="senha atual incorreta")
    if len(req.new_password) < 4:
        raise HTTPException(status_code=400, detail="nova senha muito curta (min 4)")
    engine.set_admin_password(req.new_password)
    # re-emite o cookie para manter a sessao valida
    token = engine.make_token(engine.ADMIN_USER)
    response.set_cookie(
        "session", token, httponly=True, samesite="lax", path="/", max_age=604800
    )
    return {"ok": True}


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


@app.get("/login")
def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
