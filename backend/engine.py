"""Engine compartilhado do english-flow (correcao, TTS, STT, conversa, conteudo).

Modo demo roda sem dependencias externas (correcao heuristica + sem audio).
Com chave de LLM (OpenAI ou OpenRouter) usa o modelo para correcao/conversa.
TTS: prioriza Edge TTS (vozes neurais, sem chave), depois OpenAI tts-1,
depois pyttsx3. Se nada der certo, o frontend usa speechSynthesis.
"""

import os
import re
import asyncio
import tempfile
import pathlib
import hmac
import hashlib
import base64
import json
import time

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = OPENROUTER_API_KEY or OPENAI_API_KEY

BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
if OPENROUTER_API_KEY and "openrouter" not in BASE_URL:
    BASE_URL = "https://openrouter.ai/api/v1"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EDGE_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-JennyNeural")
IS_OPENROUTER = "openrouter" in BASE_URL

# --- Autenticação (admin) ---
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "mudar123")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-prod")

# Senha "viva" (pode ser alterada em runtime via /api/auth/change-password).
# Volta ao valor de ADMIN_PASS quando o container reinicia.
current_admin_pass = ADMIN_PASS


def set_admin_password(new_pass: str) -> None:
    global current_admin_pass
    current_admin_pass = new_pass


def _b64(b: bytes) -> str:
    # remove padding '=' (causes Starlette to quote the cookie value)
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(user: str) -> str:
    payload = _b64(json.dumps({"u": user, "exp": int(time.time()) + 604800}).encode())
    sig = _b64(hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def verify_token(token: str) -> bool:
    try:
        payload_b64, sig_b64 = token.split(".")
        payload = _b64d(payload_b64)
        sig = _b64d(sig_b64)
        expected = hmac.new(SESSION_SECRET.encode(), payload_b64.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return False
        return json.loads(payload).get("exp", 0) > int(time.time())
    except Exception:
        return False

LEVELS = ["iniciante", "intermediario", "avancado"]

# Banco de frases/textos por nivel e categoria.
# Listen = frases curtas para ditado. Read = textos com glossario.
CATEGORIES = ["rotina", "trabalho", "viagem"]

LISTEN = {
    "iniciante": {
        "rotina": [
            "I wake up early every morning.",
            "She brushes her teeth before breakfast.",
            "We eat lunch at twelve o'clock.",
            "He watches television in the evening.",
            "They go to bed at ten at night.",
            "My mother makes coffee in the morning.",
            "The cat sleeps on my bed.",
            "I walk to school with my friends.",
        ],
        "trabalho": [
            "He works in an office downtown.",
            "She answers emails all day long.",
            "We have a meeting at three pm.",
            "They are busy this week.",
            "I finish work at six o'clock.",
            "My boss is very friendly.",
            "She writes reports for the company.",
            "We eat lunch together at the office.",
        ],
        "viagem": [
            "We travel by train to the city.",
            "She buys a ticket at the station.",
            "He carries a small suitcase.",
            "They visit the museum on holiday.",
            "I like to take photos of the beach.",
            "We book a room in a hotel.",
            "The airport is far from here.",
            "She speaks a little Spanish when she travels.",
        ],
    },
    "intermediario": {
        "rotina": [
            "Although I prefer tea, I drink coffee in the mornings.",
            "She usually goes for a run before heading to the office.",
            "We tend to cook at home rather than order takeout.",
            "He rarely stays up later than midnight.",
            "They enjoy reading before going to sleep.",
            "I have gotten into the habit of journaling daily.",
            "She finds it relaxing to listen to music while cleaning.",
            "We often meet friends for brunch on weekends.",
        ],
        "trabalho": [
            "She has been leading the project since last spring.",
            "We should delegate this task to the new intern.",
            "He pointed out a few flaws in the presentation.",
            "The client requested a revised timeline.",
            "I will circulate the minutes after the meeting.",
            "They agreed to postpone the launch by a week.",
            "She negotiated better terms with the supplier.",
            "We are expected to hit the deadline next month.",
        ],
        "viagem": [
            "We booked a guided tour of the old town.",
            "She misplaced her passport at the hotel.",
            "He managed to catch the connecting flight just in time.",
            "They rented a car to explore the countryside.",
            "I exchanged some money at the airport kiosk.",
            "We wandered through the local market for hours.",
            "She struggled to communicate in the foreign language.",
            "The flight was delayed due to bad weather.",
        ],
    },
    "avancado": {
        "rotina": [
            "Notwithstanding her hectic schedule, she maintains a rigorous fitness regimen.",
            "He has cultivated a morning routine predicated on mindfulness and stillness.",
            "The deliberate sequestration of screens at dinner has bolstered familial cohesion.",
            "She invariably rebuts the temptation to succumb to digital distraction.",
            "His predilection for nocturnal productivity often undermines his circadian rhythm.",
            "We have systematically curated habits that attenuate cumulative stress.",
            "The incremental optimization of his workflow yielded disproportionate gains.",
            "She espouses a philosophy of measured, incremental self-improvement.",
        ],
        "trabalho": [
            "The incumbent paradigm of hierarchical oversight is being incrementally dismantled.",
            "Her incisive delineation of the risks galvanized the stakeholders.",
            "We must reconcile diverging incentives to avert operational friction.",
            "The proposal's ostensibly benign premises obfuscate latent liabilities.",
            "He architected a contingency framework resilient to exogenous shocks.",
            "The board ratified the restructuring notwithstanding internal dissent.",
            "Such unequivocal delineation of accountability mitigated subsequent ambiguity.",
            "We ascertained that the bottleneck emanated from fragmented ownership.",
        ],
        "viagem": [
            "The itinerary was meticulously calibrated to preclude logistical friction.",
            "She navigated the bureaucratic labyrinth with remarkable aplomb.",
            "The serendipitous encounter at the remote village proved transformative.",
            "His insatiable wanderlust frequently jeopardizes his domestic stability.",
            "We reconciled the divergent itineraries into a cohesive plan.",
            "The ostensibly austere locale belied an undercurrent of vibrant culture.",
            "She endeavored to immerse herself in the vernacular rather than tourist enclaves.",
            "The expedition's success was predicated on empirical preparation.",
        ],
    },
}

READ = {
    "iniciante": {
        "rotina": [
            {"text": "Ana wakes up at seven. She brushes her teeth and eats breakfast. Then she goes to school by bus. In the evening she does her homework.",
             "glossary": {"wakes up": "acorda", "brushes": "escova", "breakfast": "café da manhã", "homework": "lição de casa", "evening": "noite"}},
            {"text": "My family has dinner at seven. We talk about our day. After dinner, my father washes the dishes and my mother reads a book.",
             "glossary": {"dinner": "jantar", "dishes": "pratos/loiça", "washes": "lava", "reads": "lê", "after": "depois"}},
            {"text": "On saturdays I clean my room and play with my dog. We go to the park and run near the lake.",
             "glossary": {"clean": "limpar", "room": "quarto", "park": "parque", "lake": "lago", "near": "perto"}},
        ],
        "trabalho": [
            {"text": "Pedro works in a hospital. He is a nurse. He helps sick people every day. His shift starts at eight in the morning.",
             "glossary": {"hospital": "hospital", "nurse": "enfermeiro", "sick": "doente", "shift": "turno", "morning": "manhã"}},
            {"text": "Maria is a teacher. She teaches math to children. The students like her classes because they are fun and clear.",
             "glossary": {"teacher": "professora", "math": "matemática", "students": "alunos", "classes": "aulas", "clear": "claras"}},
            {"text": "The office is open from nine to six. Employees drink coffee and answer the phone. They use computers all day.",
             "glossary": {"office": "escritório", "employees": "funcionários", "phone": "telefone", "computers": "computadores", "open": "aberto"}},
        ],
        "viagem": [
            {"text": "We traveled to Rio de Janeiro last summer. We visited the beach and ate local food. The trip was amazing and cheap.",
             "glossary": {"traveled": "viajou", "summer": "verão", "local": "local", "trip": "viagem", "cheap": "barato"}},
            {"text": "My friend booked a flight to Europe. She packed two suitcases and took many photos. The weather was cold there.",
             "glossary": {"booked": "reservou", "flight": "voo", "suitcases": "malas", "photos": "fotos", "cold": "frio"}},
            {"text": "At the hotel, we left our bags and went for a walk. The city was busy and the people were friendly.",
             "glossary": {"hotel": "hotel", "bags": "malas", "walk": "caminhada", "busy": "movimentada", "friendly": "amigáveis"}},
        ],
    },
    "intermediario": {
        "rotina": [
            {"text": "Although Maria dislikes mornings, she wakes up early to exercise. She believes a healthy routine improves her focus at work.",
             "glossary": {"dislikes": "desgosta", "exercise": "exercita", "healthy": "saudável", "routine": "rotina", "focus": "foco"}},
            {"text": "We have gradually replaced screen time with reading. This small change has noticeably improved our sleep quality.",
             "glossary": {"gradually": "gradativamente", "replaced": "substituiu", "screen time": "tempo de tela", "quality": "qualidade", "sleep": "sono"}},
            {"text": "He schedules his tasks the night before. By planning ahead, he avoids the stress of a chaotic morning.",
             "glossary": {"schedules": "agenda", "tasks": "tarefas", "planning": "planejando", "avoids": "evita", "chaotic": "caótico"}},
        ],
        "trabalho": [
            {"text": "The team held a retrospective to analyze what went wrong. They identified communication gaps and proposed concrete fixes.",
             "glossary": {"retrospective": "retrospectiva", "analyze": "analisar", "gaps": "lacunas", "proposed": "propôs", "concrete": "concretas"}},
            {"text": "She presented the quarterly results to the board. Although nervous, she answered every question with clarity and confidence.",
             "glossary": {"presented": "apresentou", "quarterly": "trimestral", "board": "conselho", "clarity": "clareza", "confidence": "confiança"}},
            {"text": "Our department adopted a flexible schedule. Employees can choose their hours as long as they attend the daily standup.",
             "glossary": {"department": "departamento", "flexible": "flexível", "schedule": "horário", "attend": "participam", "standup": "reunião diária"}},
        ],
        "viagem": [
            {"text": "After missing our train, we booked a last-minute bus. The delay was annoying, yet the scenery along the road was stunning.",
             "glossary": {"missing": "perdendo", "last-minute": "última hora", "delay": "atraso", "scenery": "paisagem", "stunning": "deslumbrante"}},
            {"text": "We relied on a translation app during the trip. It helped us read menus and ask for directions in a foreign language.",
             "glossary": {"relied": "dependemos", "translation": "tradução", "menus": "cardápios", "directions": "direções", "foreign": "estrangeira"}},
            {"text": "The hostel was basic but clean. We met travelers from five countries and exchanged tips about affordable places to visit.",
             "glossary": {"hostel": "albergue", "basic": "básico", "travelers": "viajantes", "affordable": "acessível", "places": "lugares"}},
        ],
    },
    "avancado": {
        "rotina": [
            {"text": "Notwithstanding a demanding schedule, she preserves a disciplined morning ritual anchored in solitude and reflection.",
             "glossary": {"demanding": "exigente", "preserves": "preserva", "ritual": "ritual", "solitude": "solidão", "reflection": "reflexão"}},
            {"text": "The deliberate curation of daily habits, however modest, compounds into transformative long-term outcomes.",
             "glossary": {"curation": "curadoria", "modest": "modestas", "compounds": "acumula", "transformative": "transformadoras", "outcomes": "resultados"}},
            {"text": "He scrutinizes his routines meticulously, pruning activities that detract from cognitive restoration.",
             "glossary": {"scrutinizes": "analisa", "pruning": "poda", "detract": "detraem", "cognitive": "cognitiva", "restoration": "restauração"}},
        ],
        "trabalho": [
            {"text": "The incumbent paradigm of hierarchical oversight is being incrementally dismantled in favor of distributed autonomy.",
             "glossary": {"incumbent": "incumbente", "oversight": "supervisão", "dismantled": "desmantelado", "distributed": "distribuída", "autonomy": "autonomia"}},
            {"text": "Her incisive delineation of latent risks galvanized stakeholders to preempt a potentially ruinous escalation.",
             "glossary": {"incisive": "incisiva", "delineation": "delineamento", "galvanized": "galvanizou", "preempt": "prevenir", "escalation": "escalada"}},
            {"text": "We must reconcile diverging incentives, lest operational friction metastasize into systemic fragility.",
             "glossary": {"reconcile": "reconciliar", "diverging": "divergentes", "incentives": "incentivos", "friction": "fricção", "systemic": "sistêmica"}},
        ],
        "viagem": [
            {"text": "The itinerary was meticulously calibrated to preclude logistical friction, yet serendipity supplied the most memorable moments.",
             "glossary": {"itinerary": "itinerário", "calibrated": "calibrado", "preclude": "evitar", "serendipity": "serendipidade", "memorable": "memoráveis"}},
            {"text": "She navigated the bureaucratic labyrinth with aplomb, leveraging localized knowledge to circumvent procedural delays.",
             "glossary": {"navigated": "navegou", "labyrinth": "labirinto", "aplomb": "segurança", "circumvent": "contornar", "delays": "atrasos"}},
            {"text": "The ostensibly austere locale belied an undercurrent of vibrant culture that only revealed itself to the patient observer.",
             "glossary": {"ostensibly": "aparentemente", "austere": "austero", "undercurrent": "corrente oculta", "vibrant": "vibrante", "observer": "observador"}},
        ],
    },
}

PERSONAS = {
    "entrevistador": "entrevistador de emprego formal",
    "cafe": "amigo tomando cafe",
    "negocios": "colega de negocios",
}

import random

_CONTENT_QUEUES = {}


def _next_item(level: str, module: str, category: str):
    pool = (READ[level] if module == "read" else LISTEN[level])
    if category and category != "all":
        items = pool.get(category, [])
    else:
        items = [x for cat in pool.values() for x in cat]
    if not items:
        items = [x for cat in pool.values() for x in cat]
    key = (level, module, category)
    q = _CONTENT_QUEUES.get(key)
    if not q:
        q = items[:]
        random.shuffle(q)
        _CONTENT_QUEUES[key] = q
    return q.pop(0)


def normalize_level(level: str) -> str:
    return level if level in LEVELS else "iniciante"


def get_content(level: str, module: str, category: str = "all") -> dict:
    level = normalize_level(level)
    if module == "read":
        item = _next_item(level, "read", category)
        return {"text": item["text"], "glossary": item["glossary"]}
    return {"text": _next_item(level, "listen", category)}


def heuristic_correct(text: str) -> str:
    fixes = []
    t = text
    m = re.match(r"\b(he|she|it)\s+([a-z]+)\b", t, re.I)
    if m and m.group(2) not in {"is", "was", "has", "does", "goes", "likes", "lives", "studies"}:
        third = "goes" if m.group(2) == "go" else m.group(2) + "s"
        fixes.append(f"ERRO -> '{m.group(1)} {m.group(2)}' | CORRECAO -> '{m.group(1)} {third}' | REGRA -> 3a pessoa singular leva -s (go->goes) | SUGESTAO -> '{m.group(1)} {third}.'")
    if re.search(r"\bi am\b", t, re.I) and re.search(r"\bhe (am|are)\b", t, re.I):
        fixes.append("ERRO -> 'he am/are' | CORRECAO -> 'he is' | REGRA -> 3a pessoa singular usa 'is' | SUGESTAO -> 'He is a student.'")
    if re.search(r"\bhave went\b", t, re.I):
        fixes.append("ERRO -> 'have went' | CORRECAO -> 'have gone' | REGRA -> particípio de 'go' é 'gone' | SUGESTAO -> 'I have gone home.'")
    if not fixes:
        fixes.append("Sem erros gramaticais obvios detectados (correcao heuristica limitada).")
    return "\n".join(fixes)


def _client():
    from openai import OpenAI
    headers = {}
    if IS_OPENROUTER:
        headers["HTTP-Referer"] = os.getenv("OPENROUTER_REFERER", "http://localhost")
        headers["X-Title"] = os.getenv("OPENROUTER_TITLE", "English Flow")
    return OpenAI(api_key=API_KEY, base_url=BASE_URL, default_headers=headers)


def correct(text: str, level: str) -> str:
    if API_KEY:
        try:
            client = _client()
            prompt = (
                f"Voce e um professor de ingles. Corrija o texto abaixo (nivel {level}). "
                f"Formato: ERRO -> CORRECAO -> REGRA -> SUGESTAO.\n\n{text}"
            )
            r = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM indisponivel: {e}]\n" + heuristic_correct(text)
    return heuristic_correct(text)


def _run_async(coro):
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(coro)).result()


def tts_bytes(text: str, voice: str = None) -> bytes:
    voice = voice or EDGE_VOICE
    # 1) Edge TTS: vozes neurais de alta qualidade, sem chave (recomendado).
    try:
        import edge_tts

        async def _say():
            p = pathlib.Path(tempfile.mktemp(suffix=".mp3"))
            await edge_tts.Communicate(text, voice).save(str(p))
            return p.read_bytes()

        return _run_async(_say())
    except Exception:
        pass
    # 2) OpenAI tts-1 (precisa de OPENAI_API_KEY).
    if API_KEY and not IS_OPENROUTER:
        try:
            client = _client()
            r = client.audio.speech.create(model="tts-1", voice="nova", input=text)
            return r.content
        except Exception:
            pass
    # 3) pyttsx3 offline.
    try:
        import pyttsx3
        p = pathlib.Path(tempfile.mktemp(suffix=".wav"))
        eng = pyttsx3.init()
        eng.save_to_file(text, str(p))
        eng.runAndWait()
        return p.read_bytes()
    except Exception:
        pass
    return b""


_VOICES_CACHE = None


def list_voices() -> list:
    global _VOICES_CACHE
    if _VOICES_CACHE is not None:
        return _VOICES_CACHE
    voices = []
    try:
        import edge_tts

        async def _list():
            return await edge_tts.list_voices()

        all_voices = _run_async(_list())
        for v in all_voices:
            if v["ShortName"].startswith("en-"):  # só ingles
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
    except Exception:
        voices = [{"id": "en-US-JennyNeural", "name": "Jenny (US, female)"},
                  {"id": "en-US-GuyNeural", "name": "Guy (US, male)"},
                  {"id": "en-GB-SoniaNeural", "name": "Sonia (UK, female)"},
                  {"id": "en-AU-NatashaNeural", "name": "Natasha (AU, female)"}]
    _VOICES_CACHE = voices
    return voices


def stt_transcribe(audio_bytes: bytes, suffix: str = ".webm") -> str:
    try:
        import whisper
        p = pathlib.Path(tempfile.mktemp(suffix=suffix))
        p.write_bytes(audio_bytes)
        model = whisper.load_model("base")
        return model.transcribe(str(p))["text"].strip()
    except Exception as e:
        raise RuntimeError(f"STT indisponivel (instale whisper): {e}")


def converse(level: str, persona: str, history: list, user_message: str) -> str:
    persona_desc = PERSONAS.get(persona, "amigo tomando cafe")
    system = f"Voce e um professor de ingles atuando como {persona_desc}. Converse em ingles (nivel {level}), reaja, faca perguntas e corrija erros do aluno de forma gentil."
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user_message}]
    if API_KEY:
        try:
            client = _client()
            r = client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM indisponivel: {e}] Hello! Tell me more about that."
    return "Hello! That's interesting. Can you tell me more?"
