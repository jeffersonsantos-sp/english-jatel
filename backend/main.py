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


class NewUserReq(BaseModel):
    username: str
    password: str


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
    if engine.verify_user(req.user, req.password):
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
    token = request.cookies.get("session", "")
    if not engine.verify_token(token):
        raise HTTPException(status_code=401, detail="nao autenticado")
    user = engine.username_from_token(token)
    return {"user": user, "is_admin": user == engine.ADMIN_USER}


@app.post("/api/auth/change-password")
def change_password(req: ChangePassReq, request: Request, response: Response):
    token = request.cookies.get("session", "")
    if not engine.verify_token(token):
        raise HTTPException(status_code=401, detail="nao autenticado")
    user = engine.username_from_token(token)
    if not user or not engine.verify_user(user, req.current_password):
        raise HTTPException(status_code=400, detail="senha atual incorreta")
    if len(req.new_password) < 4:
        raise HTTPException(status_code=400, detail="nova senha muito curta (min 4)")
    engine.set_user_password(user, req.new_password)
    new_token = engine.make_token(user)
    response.set_cookie(
        "session", new_token, httponly=True, samesite="lax", path="/", max_age=604800
    )
    return {"ok": True}


def _require_admin(request: Request) -> str:
    token = request.cookies.get("session", "")
    if not engine.verify_token(token):
        raise HTTPException(status_code=401, detail="nao autenticado")
    user = engine.username_from_token(token)
    if user != engine.ADMIN_USER:
        raise HTTPException(status_code=403, detail="apenas admin")
    return user


def _require_user(request: Request) -> str:
    token = request.cookies.get("session", "")
    if not engine.verify_token(token):
        raise HTTPException(status_code=401, detail="nao autenticado")
    return engine.username_from_token(token)


@app.post("/api/auth/register")
def register(req: NewUserReq, request: Request):
    _require_admin(request)
    if not req.username or len(req.username) < 2:
        raise HTTPException(status_code=400, detail="usuario muito curto (min 2)")
    try:
        engine.add_user(req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


@app.get("/api/auth/users")
def users_list(request: Request):
    _require_admin(request)
    return {"users": engine.list_users()}


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


@app.get("/api/grammar-levels")
def grammar_levels():
    return {"levels": engine.GRAMMAR_LEVELS}


class GrammarReq(BaseModel):
    level: str = "A1"


@app.post("/api/grammar")
def grammar(req: GrammarReq):
    return engine.get_grammar(req.level)


@app.post("/api/admin/reload-grammar")
def reload_grammar(request: Request):
    _require_admin(request)
    engine.reload_grammar()
    counts = {lv: len(engine.GRAMMAR.get(lv, [])) for lv in engine.GRAMMAR_LEVELS}
    return {"ok": True, "levels": engine.GRAMMAR_LEVELS, "counts": counts, "source": engine.GRAMMAR_FILE}


# ---- MemHack (memorizacao com repeticao espacada) ----
class MemHackNextReq(BaseModel):
    category: str


@app.get("/api/memhack/categories")
def memhack_categories():
    return {"categories": engine.get_memhack_categories()}


@app.post("/api/memhack/next")
def memhack_next(req: MemHackNextReq, request: Request):
    user = _require_user(request)
    return engine.get_memhack_next(user, req.category)


class MemHackReviewReq(BaseModel):
    category: str
    phrase_id: str
    difficulty: str


@app.post("/api/memhack/review")
def memhack_review(req: MemHackReviewReq, request: Request):
    user = _require_user(request)
    result = engine.review_memhack(user, req.category, req.phrase_id, req.difficulty)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


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
    import traceback
    try:
        transcript = engine.stt_transcribe(data, suffix)
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"STT interno: {type(e).__name__}: {e}")
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
