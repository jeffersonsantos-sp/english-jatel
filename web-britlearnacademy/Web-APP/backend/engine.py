"""Engine compartilhado do english-flow (correcao, TTS, STT, conversa, conteudo).

Modo demo roda sem dependencias externas (correcao heuristica + sem audio).
Com chave de LLM (OpenAI ou OpenRouter) usa o modelo para correcao/conversa.
TTS: prioriza Edge TTS (vozes neurais, sem chave), depois OpenAI tts-1,
depois pyttsx3. Se nada der certo, o frontend usa speechSynthesis.
"""

import os
import re
import asyncio
import subprocess
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

# --- Multi-idioma ---
SUPPORTED_LANGS = ("en", "es", "fr", "it", "de")
DEFAULT_LANG = "en"

LANG_META = {
    "en": {"label": "Inglês", "prompt_prefix": "professor de inglês", "stt_lang": "en-US"},
    "es": {"label": "Espanhol", "prompt_prefix": "profesor de español", "stt_lang": "es-ES"},
    "fr": {"label": "Francês", "prompt_prefix": "professeur de français", "stt_lang": "fr-FR"},
    "it": {"label": "Italiano", "prompt_prefix": "professore di italiano", "stt_lang": "it-IT"},
    "de": {"label": "Alemão", "prompt_prefix": "Deutschlehrer", "stt_lang": "de-DE"},
}

LANG_VOICES = {
    "en": os.getenv("EDGE_TTS_VOICE", "en-US-JennyNeural"),
    "es": os.getenv("EDGE_TTS_VOICE_ES", "es-ES-ElviraNeural"),
    "fr": os.getenv("EDGE_TTS_VOICE_FR", "fr-FR-DeniseNeural"),
    "it": os.getenv("EDGE_TTS_VOICE_IT", "it-IT-ElsaNeural"),
    "de": os.getenv("EDGE_TTS_VOICE_DE", "de-DE-KatjaNeural"),
}

def get_lang() -> str:
    return DEFAULT_LANG

def get_lang_meta(lang: str = DEFAULT_LANG) -> dict:
    return LANG_META.get(lang, LANG_META[DEFAULT_LANG])

def get_default_voice(lang: str = DEFAULT_LANG) -> str:
    return LANG_VOICES.get(lang, LANG_VOICES[DEFAULT_LANG])

# --- Autenticação (multi-usuário, persistido em arquivo) ---
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "J@Tel2026!!")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-prod")

import pathlib
DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data")))
USERS_FILE = DATA_DIR / "users.json"
_USERS_CACHE = None


def _hash_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex(), dk.hex()


def _load_users() -> dict:
    global _USERS_CACHE
    if _USERS_CACHE is not None:
        return _USERS_CACHE
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if USERS_FILE.exists():
        try:
            _USERS_CACHE = json.loads(USERS_FILE.read_text())
        except Exception:
            _USERS_CACHE = {}
    if not _USERS_CACHE:
        salt, h = _hash_password(ADMIN_PASS)
        _USERS_CACHE = {ADMIN_USER: {"salt": salt, "hash": h, "can_change_password": True}}
        _save_users(_USERS_CACHE)
    return _USERS_CACHE


def _save_users(users: dict) -> None:
    global _USERS_CACHE
    _USERS_CACHE = users
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))


def _seed_users() -> None:
    users = _load_users()
    seeds = {
        "jatel": {"password": "Update2026!", "can_change_password": True},
        "estudante": {"password": "Estudo@2026!", "can_change_password": False},
    }
    changed = False
    for uname, cfg in seeds.items():
        if uname not in users:
            salt, h = _hash_password(cfg["password"])
            users[uname] = {"salt": salt, "hash": h, "can_change_password": cfg["can_change_password"]}
            changed = True
    for uname in users:
        if "can_change_password" not in users[uname]:
            users[uname]["can_change_password"] = True
            changed = True
    if changed:
        _save_users(users)


def verify_user(username: str, password: str) -> bool:
    users = _load_users()
    u = users.get(username)
    if not u:
        return False
    salt = bytes.fromhex(u["salt"])
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk.hex(), u["hash"])


def add_user(username: str, password: str, can_change_password: bool = True) -> None:
    users = _load_users()
    if username in users:
        raise ValueError("usuário já existe")
    if len(password) < 4:
        raise ValueError("senha muito curta (mín. 4)")
    salt, h = _hash_password(password)
    users[username] = {"salt": salt, "hash": h, "can_change_password": can_change_password}
    _save_users(users)


def set_user_password(username: str, password: str) -> None:
    users = _load_users()
    if username not in users:
        raise ValueError("usuário não existe")
    if not users[username].get("can_change_password", True):
        raise ValueError("este usuario nao pode alterar a senha")
    salt, h = _hash_password(password)
    users[username] = {"salt": salt, "hash": h, "can_change_password": users[username].get("can_change_password", True)}
    _save_users(users)


def set_user_lang(username: str, lang: str) -> None:
    """Salva o idioma preferido do usuário (en, es, fr)."""
    if lang not in ("en", "es", "fr"):
        raise ValueError("Idioma não suportado")
    users = _load_users()
    if username not in users:
        raise ValueError("usuário não existe")
    # Ensure the user dict has the language field
    users[username]["lang"] = lang
    _save_users(users)


def get_user_lang(username: str) -> str:
    """Retorna o idioma salvo do usuário, padrão 'en'."""
    users = _load_users()
    user = users.get(username, {})
    return user.get("lang", "en")


def list_users() -> list:
    return sorted(_load_users().keys())


def username_from_token(token: str):
    try:
        payload_b64, _ = token.split(".")
        return json.loads(_b64d(payload_b64)).get("u")
    except Exception:
        return None


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

_seed_users()

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
    "cafe": {
        "en": "You are a friendly Brazilian chatting over coffee. Keep the conversation light and natural.",
        "es": "Eres un brasileño simpático charlando sobre un café. Mantén la conversación ligera y natural.",
        "fr": "Vous êtes un Brésilien sympathique discutant autour d'un café. Gardez la conversation légère et naturelle.",
    },
    "entrevistador": {
        "en": "You are a professional job interviewer. Ask clear questions and evaluate the student's responses.",
        "es": "Eres un entrevistador de trabajo profesional. Haz preguntas claras y evalúa las respuestas del estudiante.",
        "fr": "Vous êtes un recruteur professionnel. Posez des questions claires et évaluez les réponses de l'étudiant.",
    },
    "negocios": {
        "en": "You are a business colleague. Discuss professional topics using formal and business-appropriate language.",
        "es": "Eres un colega de negocios. Discute temas profesionales usando lenguaje formal y apropiado para los negocios.",
        "fr": "Vous êtes un collègue d'affaires. Discutez de sujets professionnels en utilisant un langage formel et approprié.",
    },
    "viagens": {
        "en": "You are an enthusiastic travel companion. Talk about destinations, experiences, and travel tips.",
        "es": "Eres un compañero de viaje entusiasta. Habla sobre destinos, experiencias y consejos de viaje.",
        "fr": "Vous êtes un compagnon de voyage enthousiaste. Parlez de destinations, d'expériences et de conseils de voyage.",
    },
    "familia": {
        "en": "You are a friendly family member. Have warm, casual conversations about family life and daily activities.",
        "es": "Eres un miembro de la familia amigable. Ten conversaciones cálidas y casuales sobre la vida familiar.",
        "fr": "Vous êtes un membre de la famille amical. Ayez des conversations chaleureuses et décontractées sur la vie de famille.",
    },
    "filmes": {
        "en": "You are a film enthusiast. Discuss movies, directors, actors, and cinema with passion and knowledge.",
        "es": "Eres un cinéfilo apasionado. Discute sobre películas, directores, actores y cine con entusiasmo.",
        "fr": "Vous êtes un passionné de cinéma. Discutez de films, de réalisateurs, d'acteurs et de cinéma avec passion.",
    },
    "musicas": {
        "en": "You are a music lover. Talk about genres, artists, concerts, and songs with enthusiasm.",
        "es": "Eres un amante de la música. Habla sobre géneros, artistas, conciertos y canciones con entusiasmo.",
        "fr": "Vous êtes un passionné de musique. Parlez de genres, d'artistes, de concerts et de chansons avec enthousiasme.",
    },
    "futebol": {
        "en": "You are a passionate football fan. Discuss matches, teams, players, and sports with energy.",
        "es": "Eres un hincha de fútbol apasionado. Discute sobre partidos, equipos, jugadores y deportes con energía.",
        "fr": "Vous êtes un fan de football passionné. Discutez des matchs, des équipes, des joueurs et du sport avec énergie.",
    },
    "devops": {
        "en": "You are a DevOps engineer and tech colleague. Discuss infrastructure, CI/CD, Kubernetes, and cloud with technical depth.",
        "es": "Eres un ingeniero DevOps y colega técnico. Discute sobre infraestructura, CI/CD, Kubernetes y nube con profundidad técnica.",
        "fr": "Vous êtes un ingénieur DevOps et collègue technique. Discutez de l'infrastructure, du CI/CD, de Kubernetes et du cloud avec une profondeur technique.",
    },
}

# --- Grammar: conteúdo por nível CEFR (A1..C2) ---
# Cada tópico: titulo, explicacao (pt-BR), exemplos (ingles — traducao).
GRAMMAR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

GRAMMAR = {
    "A1": [
        {
            "topic": "Verbo to be (ser / estar)",
            "structure": "Subject + am / is / are (+ not) + complement",
            "explanation": "Usamos am (eu), is (ele/ela/isto), are (você/nós/eles) para identidade, idade, profissão, origem e estado. Na negativa, acrescenta-se not (isn't / aren't / 'm not). Nas perguntas, o verbo vem antes do sujeito.",
            "examples": [
                "I am a student. — Eu sou estudante.",
                "She is from Brazil. — Ela é do Brasil.",
                "They are not at home. — Eles não estão em casa.",
                "Is he your brother? — Ele é seu irmão?",
            ],
        },
        {
            "topic": "Pronomes pessoais e sujeito",
            "structure": "I / you / he / she / it / we / they + verbo",
            "explanation": "O pronome define a forma do verbo. he, she e it exigem -s na 3ª pessoa do singular nos tempos simples. it refere-se a coisas, animais ou ideias.",
            "examples": [
                "He speaks English. — Ele fala inglês.",
                "We live in São Paulo. — Nós moramos em São Paulo.",
                "It is a book. — Isto é um livro.",
                "They work on Monday. — Eles trabalham na segunda.",
            ],
        },
        {
            "topic": "Artigos a / an / the",
            "structure": "a + consoante | an + vogal | the (definido)",
            "explanation": "a antes de som de consoante, an antes de som de vogal (an hour, a university). the aponta algo já conhecido. Sem artigo para plural genérico (I like cats) ou nomes próprios.",
            "examples": [
                "I have a cat. — Eu tenho um gato.",
                "She ate an orange. — Ela comeu uma laranja.",
                "The book is on the table. — O livro está sobre a mesa.",
                "Dogs are friendly. — Cães são amigáveis.",
            ],
        },
        {
            "topic": "Plural de substantivos",
            "structure": "substantivo + s / es / (irregular)",
            "explanation": "Geralmente + s (cats). Terminando em s, x, ch, sh ou o consoante: + es (boxes). Terminando em consoante + y: troca y por ies. Muitos irregulares: child→children, man→men, foot→feet.",
            "examples": [
                "one dog, two dogs. — um cão, dois cães.",
                "one box, three boxes. — uma caixa, três caixas.",
                "one man, many men. — um homem, muitos homens.",
                "one child, two children. — uma criança, duas crianças.",
            ],
        },
        {
            "topic": "Present Simple (afirmativo)",
            "structure": "Subject + verb(base) / -s (he/she/it)",
            "explanation": "Expressa fatos, rotinas e hábitos. He/She/It leva -s (works) ou -es (goes, watches). have vira has na 3ª pessoa. Outras pessoas usam o verbo na base.",
            "examples": [
                "I work every day. — Eu trabalho todo dia.",
                "He goes to school. — Ele vai à escola.",
                "We like coffee. — Nós gostamos de café.",
                "She has a red car. — Ela tem um carro vermelho.",
            ],
        },
        {
            "topic": "Adjetivos possessivos",
            "structure": "my / your / his / her / its / our / their + nome",
            "explanation": "Indicam posse e concordam com o dono, não com o objeto. my, your, his, her, its, our, their. Não usam artigo junto (my car, não the my car).",
            "examples": [
                "This is my phone. — Este é meu telefone.",
                "His name is John. — O nome dele é John.",
                "We love our city. — Nós amamos nossa cidade.",
                "Their house is big. — A casa deles é grande.",
            ],
        },
        {
            "topic": "Demonstrativos this / that / these / those",
            "structure": "this/that (sing.) | these/those (pl.)",
            "explanation": "this/these = perto de quem fala; that/those = longe. this book (este livro), that car (aquele carro), these dogs (estes cães), those houses (aquelas casas).",
            "examples": [
                "This is my chair. — Esta é minha cadeira.",
                "That is a tall building. — Aquela é um prédio alto.",
                "These apples are fresh. — Estas maçãs estão frescas.",
                "Those shoes are expensive. — Aqueles sapatos são caros.",
            ],
        },
        {
            "topic": "Preposições de lugar",
            "structure": "in / on / under / next to / between",
            "explanation": "in (dentro), on (sobre superfície), under (embaixo), next to (ao lado de), between (entre dois). Indispensáveis para descrever posição.",
            "examples": [
                "The cat is in the box. — O gato está na caixa.",
                "The book is on the table. — O livro está sobre a mesa.",
                "The ball is under the bed. — A bola está debaixo da cama.",
                "She sits between Tom and Mary. — Ela senta entre Tom e Mary.",
            ],
        },
    ],
    "A2": [
        {
            "topic": "Present Simple (negativo e interrogativo)",
            "structure": "do/does + not + verb(base) | Do/Does + Subject + verb?",
            "explanation": "Usa-se o auxiliar do/does. Negativo: don't/doesn't + verbo base (sem -s). Interrogativo: Do/Does + sujeito + verbo base. He/She/It usa does, mas o verbo principal perde o -s.",
            "examples": [
                "I don't like tea. — Eu não gosto de chá.",
                "Does she speak French? — Ela fala francês?",
                "They don't live here. — Eles não moram aqui.",
                "Don't we have class today? — Não temos aula hoje?",
            ],
        },
        {
            "topic": "Past Simple",
            "structure": "verb + ed (regular) | irregular (went, ate)",
            "explanation": "Ações concluídas no passado. Regulares: + ed (played, studied). Irregulares comuns: go→went, eat→ate, see→saw, buy→bought. Negativo/interrogativo com did + base.",
            "examples": [
                "I visited my grandmother. — Eu visitei minha avó.",
                "He went to the market. — Ele foi ao mercado.",
                "We didn't watch TV. — Nós não assistimos TV.",
                "Did you buy the tickets? — Você comprou os ingressos?",
            ],
        },
        {
            "topic": "Preposições de tempo in / on / at",
            "structure": "in + período | on + dia | at + hora",
            "explanation": "in + meses/anos/estações (in July, in 2020, in summer). on + dias e datas (on Monday, on July 4th). at + horas e momentos (at 7 o'clock, at night, at the weekend no RU).",
            "examples": [
                "The party is in December. — A festa é em dezembro.",
                "We meet on Friday. — Nós nos encontramos na sexta.",
                "The bus leaves at nine. — O ônibus sai às nove.",
                "She was born on March 2nd. — Ela nasceu em 2 de março.",
            ],
        },
        {
            "topic": "There is / There are",
            "structure": "There is (sing.) / There are (pl.) (+ not)",
            "explanation": "Para dizer que algo existe ou está presente. there is (singular/indescritível), there are (plural). Negativo: isn't / aren't. Interrogativo: Is/Are there...?",
            "examples": [
                "There is a park near my house. — Há um parque perto de casa.",
                "There are two cats. — Há dois gatos.",
                "There isn't any milk. — Não há leite nenhum.",
                "Are there students in the room? — Há alunos na sala?",
            ],
        },
        {
            "topic": "Can / Can't (habilidade e permissão)",
            "structure": "can + verb(base) | can't + verb(base)",
            "explanation": "can indica capacidade ou permissão; não varia com o sujeito e é seguido do verbo na base. Negativo: can't. Interrogativo: Can + sujeito + base. Passado: could.",
            "examples": [
                "I can swim. — Eu sei nadar.",
                "She can't drive. — Ela não sabe dirigir.",
                "Can you help me? — Você pode me ajudar?",
                "We could see the stars. — Nós conseguíamos ver as estrelas.",
            ],
        },
        {
            "topic": "Comparativos e superlativos",
            "structure": "adj + er / more + adj | the + adj + est / most",
            "explanation": "Comparativo: -er (taller) ou more + adj longo (more beautiful), com than. Superlativo: -est (tallest) ou most + adj, com the. Irregulares: good→better→best, bad→worse→worst.",
            "examples": [
                "He is taller than me. — Ele é mais alto que eu.",
                "This book is more interesting. — Este livro é mais interessante.",
                "She is the best student. — Ela é a melhor aluna.",
                "That was the worst day. — Aquele foi o pior dia.",
            ],
        },
        {
            "topic": "Pronomes objetos",
            "structure": "me / you / him / her / it / us / them",
            "explanation": "Substituem o objeto da ação (recebedor). me, you, him, her, it, us, them. Vêm após verbos ou preposições (I saw him / with them).",
            "examples": [
                "She called me yesterday. — Ela me ligou ontem.",
                "We invited them to the party. — Nós os convidamos para a festa.",
                "He gave her a gift. — Ele deu um presente a ela.",
                "Talk to us later. — Converse conosco mais tarde.",
            ],
        },
        {
            "topic": "Quantificadores some / any / much / many",
            "structure": "some (afir.) | any (neg./interrog.) | much/many",
            "explanation": "some em afirmativas e ofertas; any em negativas e perguntas. much com incontáveis (much water); many com contáveis (many friends). a lot of serve para ambos.",
            "examples": [
                "I have some money. — Eu tenho algum dinheiro.",
                "Do you have any questions? — Você tem alguma pergunta?",
                "There isn't much time. — Não há muito tempo.",
                "How many students are there? — Quantos alunos há?",
            ],
        },
    ],
    "B1": [
        {
            "topic": "Present Continuous",
            "structure": "am/is/are + verb-ing",
            "explanation": "Ações em progresso no momento ou temporárias. Frequentemente com now, at the moment, today. also para hábitos irritantes (He is always complaining).",
            "examples": [
                "I am reading a book now. — Estou lendo um livro agora.",
                "She is working today. — Ela está trabalhando hoje.",
                "They are not sleeping. — Eles não estão dormindo.",
                "What are you doing? — O que você está fazendo?",
            ],
        },
        {
            "topic": "Past Continuous",
            "structure": "was/were + verb-ing",
            "explanation": "Ação em progresso no passado, muitas vezes interrompida por outra (when + Past Simple). Também para cenários de fundo (It was raining).",
            "examples": [
                "I was taking a shower when you called. — Eu tomava banho quando você ligou.",
                "They were playing football. — Eles estavam jogando futebol.",
                "It was raining, so we stayed in. — Chovia, então ficamos em casa.",
                "She was studying all night. — Ela estava estudando a noite toda.",
            ],
        },
        {
            "topic": "Present Perfect",
            "structure": "have/has + past participle",
            "explanation": "Experiências de vida (I have been), mudanças recentes e estados que começaram no passado e continuam (for/since). Ligação passado→presente; não diz quando.",
            "examples": [
                "I have been to London. — Eu estive em Londres (já fui).",
                "She has finished her homework. — Ela terminou a lição.",
                "We have lived here for years. — Moramos aqui há anos.",
                "Has he ever eaten sushi? — Ele já comeu sushi alguma vez?",
            ],
        },
        {
            "topic": "Futuro: will / going to",
            "structure": "will + base | am/is/are going to + base",
            "explanation": "will para decisões no momento, ofertas e previsões sem prova. going to para planos já decididos e previsões com sinais no presente (Look at the sky!).",
            "examples": [
                "I will help you. — Eu vou te ajudar (agora decidi).",
                "Look at the sky! It's going to rain. — Olhe o céu! Vai chover.",
                "We are going to travel in July. — Vamos viajar em julho.",
                "I think she will like it. — Acho que ela vai gostar.",
            ],
        },
        {
            "topic": "First Conditional",
            "structure": "if + Present Simple, will + base",
            "explanation": "Resultados prováveis no futuro a partir de uma condição real. if-clause na base; resultado com will (ou outro futuro/imperativo). if não leva will.",
            "examples": [
                "If it rains, we will stay home. — Se chover, ficaremos em casa.",
                "If you study, you will pass. — Se você estudar, passará.",
                "If he calls, I will tell him. — Se ele ligar, eu direi a ele.",
                "If you are late, take a taxi. — Se você se atrasar, pegue um táxi.",
            ],
        },
        {
            "topic": "Pronomes relativos who / which / that",
            "structure": "Subject + verb + who/which/that + ...",
            "explanation": "who para pessoas, which para coisas, that para ambos (informais). Conectam orações e evitam repetir o substantivo. Sempre o livro que comprei.",
            "examples": [
                "The man who called you is my uncle. — O homem que te ligou é meu tio.",
                "This is the book which I bought. — Este é o livro que comprei.",
                "She likes music that is relaxing. — Ela gosta de música que é relaxante.",
                "We met the teacher who teaches math. — Conhecemos o professor que ensina matemática.",
            ],
        },
        {
            "topic": "Passado de modais (could / would / should)",
            "structure": "could / would / should + have + participle",
            "explanation": "could (habilidade no passado), would (preferência/educação), should (conselho). would like = gostaria. No passado: could have, would have, should have.",
            "examples": [
                "When I was young I could run fast. — Quando era jovem, conseguia correr rápido.",
                "I would like some water. — Eu gostaria de um pouco de água.",
                "You should see a doctor. — Você deveria ver um médico.",
                "He could have won. — Ele poderia ter vencido.",
            ],
        },
        {
            "topic": "Tag questions",
            "structure": "afirmativa, + negativa? | negativa, + afirmativa?",
            "explanation": "Perguntas de confirmação no final da frase. O auxiliar repete invertido: afirmativa→tag negativa (You like it, don't you?), negativa→tag afirmativa (You don't, do you?).",
            "examples": [
                "You speak English, don't you? — Você fala inglês, não fala?",
                "She isn't here, is she? — Ela não está aqui, está?",
                "We can go, can't we? — Nós podemos ir, não podemos?",
                "It's cold, isn't it? — Está frio, não está?",
            ],
        },
    ],
    "B2": [
        {
            "topic": "Present Perfect Continuous",
            "structure": "have/has been + verb-ing",
            "explanation": "Ação que começou no passado e continua ou tem resultado visível agora. Foca na duração. for/since frequentes. I have been waiting for an hour.",
            "examples": [
                "I have been waiting for an hour. — Estou esperando há uma hora.",
                "She has been working all day. — Ela está trabalhando o dia todo.",
                "It has been raining since morning. — Chove desde de manhã.",
                "We have been learning grammar. — Temos estudado gramática.",
            ],
        },
        {
            "topic": "Second Conditional",
            "structure": "if + Past Simple, would + base",
            "explanation": "Situações hipotéticas ou irreais no presente/futuro. if + passado simples; resultado com would (ou could/might). If I won, I would travel.",
            "examples": [
                "If I won the lottery, I would travel. — Se eu ganhasse na loteria, viajaria.",
                "If she knew, she would tell us. — Se ela soubesse, nos diria.",
                "What would you do? — O que você faria?",
                "If I were you, I would apologize. — Se eu fosse você, pediria desculpas.",
            ],
        },
        {
            "topic": "Voz passiva",
            "structure": "be + past participle (+ by agent)",
            "explanation": "Foco na ação/objeto, não no agente. Active: They built the house → Passive: The house was built (by them). Tempos mudam o be (is/are/was/were/been).",
            "examples": [
                "The letter was written by Tom. — A carta foi escrita pelo Tom.",
                "English is spoken worldwide. — O inglês é falado no mundo todo.",
                "The cake has been eaten. — O bolo foi comido.",
                "The road is being repaired. — A estrada está sendo consertada.",
            ],
        },
        {
            "topic": "Reported Speech (discurso indireto)",
            "structure": "say/tell + que + tempo recuado",
            "explanation": "Repete o que foi dito com recuo de tempo: present→past, will→would, am/is→was, have→had. Perguntas viram if/whether ou se já têm wh-.",
            "examples": [
                "He said he was tired. — Ele disse que estava cansado.",
                "She told me she would come. — Ela me disse que viria.",
                "They said they liked it. — Eles disseram que gostaram.",
                "He asked if I was ready. — Ele perguntou se eu estava pronto.",
            ],
        },
        {
            "topic": "Modais de dedução",
            "structure": "must / can't / could / might + base",
            "explanation": "Certeza afirmativa (must), certeza negativa (can't), possibilidade (could/might). Dedução sobre o presente; para o passado: must have, can't have.",
            "examples": [
                "He must be at home. — Ele deve estar em casa.",
                "That can't be true. — Isso não pode ser verdade.",
                "She might be busy. — Ela pode estar ocupada.",
                "They must have left already. — Eles devem ter saído já.",
            ],
        },
        {
            "topic": "Used to / Would (hábitos passados)",
            "structure": "used to + base | would + base (passado)",
            "explanation": "used to descreve hábitos e estados do passado que não existem mais (I used to smoke). would descreve ações repetidas no passado (narrativa), não estados.",
            "examples": [
                "I used to live in Rio. — Eu costumava morar no Rio.",
                "She used to play the piano. — Ela tocava piano antigamente.",
                "Every summer we would visit grandma. — Cada verão visitávamos a vovó.",
                "He didn't use to like coffee. — Ele não costumava gostar de café.",
            ],
        },
        {
            "topic": "Phrasal verbs comuns",
            "structure": "verbo + partícula (sentido novo)",
            "explanation": "Combinações de verbo + preposição/advérbio com significado próprio. Separáveis (turn off the light / turn the light off) ou inseparáveis (look after).",
            "examples": [
                "Please turn off the light. — Por favor, apague a luz.",
                "She looks after her brother. — Ela cuida do irmão.",
                "We ran out of milk. — Acabou o leite (ficamos sem).",
                "He gave up smoking. — Ele desistiu de fumar.",
            ],
        },
        {
            "topic": "Artigo zero com genéricos",
            "structure": "Ø + substantivo plural/contável genérico",
            "explanation": "Sem artigo para espécies/classes em geral (Dogs are loyal), refeições (breakfast), idiomas (English), esportes (football). Contrasta com the para específicos.",
            "examples": [
                "Dogs are loyal animals. — Cães são animais leais.",
                "I eat breakfast at 7. — Eu tomo café da manhã às 7.",
                "She speaks English fluently. — Ela fala inglês fluentemente.",
                "The dogs in the yard are loud. — Os cães no quintal são barulhentos.",
            ],
        },
    ],
    "C1": [
        {
            "topic": "Third Conditional",
            "structure": "if + Past Perfect, would have + participle",
            "explanation": "Situações hipotéticas sobre o passado (não mudáveis). if + had done; resultado com would/could/might have done. If I had studied, I would have passed.",
            "examples": [
                "If I had studied, I would have passed. — Se eu tivesse estudado, teria passado.",
                "If she had left earlier, she wouldn't have missed it. — Se tivesse saído cedo, não teria perdido.",
                "We would have helped if we had known. — Teríamos ajudado se soubéssemos.",
                "If they had invited me, I could have gone. — Se tivessem me convidado, eu poderia ter ido.",
            ],
        },
        {
            "topic": "Inversão após negativos",
            "structure": "Never/Seldom/Not only + aux + Subject + ...",
            "explanation": "Advérbios negativos no início da frase exigem inversão sujeito-verbo (auxiliar antes do sujeito). Enfatiza e é típico de registro formal/escrito.",
            "examples": [
                "Never have I seen such a thing. — Nunca vi tal coisa.",
                "Seldom does he complain. — Raramente ele reclama.",
                "Not only did she win, but she broke the record. — Ela não só venceu, como quebrou o recorde.",
                "Rarely do we get such a chance. — Raramente temos tal chance.",
            ],
        },
        {
            "topic": "Wish / If only",
            "structure": "wish/if only + Past (present) / Past Perf. (passado)",
            "explanation": "Desejos. Sobre o presente/irreal: Past Simple (I wish I spoke). Sobre o passado arrependido: Past Perfect (I wish I had studied). if only é mais enfático.",
            "examples": [
                "I wish I spoke French. — Quem me dera falar francês.",
                "I wish I had studied more. — Queria ter estudado mais.",
                "If only we knew! — Se ao menos soubéssemos!",
                "She wishes it were easier. — Ela deseja que fosse mais fácil.",
            ],
        },
        {
            "topic": "Passiva com modais e causativo",
            "structure": "modal + be + participle | have + object + participle",
            "explanation": "Passiva com modais: must be done. Causativo have something done = mandar que façam algo para você (I had my hair cut = cortei o cabelo [no salão]).",
            "examples": [
                "The work must be finished today. — O trabalho deve ser terminado hoje.",
                "He had his car repaired. — Ele mandou consertar o carro.",
                "The report is being written. — O relatório está sendo escrito.",
                "It should have been delivered. — Deveria ter sido entregue.",
            ],
        },
        {
            "topic": "Colocações avançadas",
            "structure": "palavras que combinam naturalmente",
            "explanation": "Combinações fixas nativas (make a decision, take action, raise a question, pay attention, break the news). Aprender o par, não só a tradução isolada.",
            "examples": [
                "We made a decision. — Nós tomamos uma decisão.",
                "Please pay attention. — Por favor, preste atenção.",
                "They raised an interesting point. — Eles levantaram um ponto interessante.",
                "She broke the news gently. — Ela deu a notícia delicadamente.",
            ],
        },
        {
            "topic": "Discurso indireto com tempos perfeitos",
            "structure": "said + that + Past Perfect / would have",
            "explanation": "Em relatos longos, o recuo vai além: present→past→past perfect; will→would→would have. Mantém a perspectiva temporal do locutor original.",
            "examples": [
                "He said he had already finished. — Ele disse que já tinha terminado.",
                "She claimed she would have helped. — Ela alegou que teria ajudado.",
                "They explained they had been waiting. — Eles explicaram que estiveram esperando.",
                "He mentioned he had never seen it. — Ele mencionou que nunca tinha visto.",
            ],
        },
        {
            "topic": "Estruturas de preferência (would rather / it's time)",
            "structure": "would rather + base | it's time + Past",
            "explanation": "would rather + verbo base (I'd rather go). it's time / it's high time + Past Simple para algo urgente (It's time we left). Difere de preferência comum.",
            "examples": [
                "I would rather stay home. — Eu prefiro ficar em casa.",
                "She'd rather not discuss it. — Ela prefere não discutir isso.",
                "It's time we left. — É hora de irmos.",
                "It's high time you studied. — Já passou da hora de você estudar.",
            ],
        },
    ],
    "C2": [
        {
            "topic": "Cleft sentences (ênfase)",
            "structure": "It was/were + foco + that/who + ...",
            "explanation": "Desloca o foco para um elemento da frase. It was John who called (não Maria). What-clause também enfatiza: What I need is time.",
            "examples": [
                "It was the manager who approved it. — Foi o gerente quem aprovou.",
                "It is grammar that we are studying. — É gramática que estamos estudando.",
                "It wasn't me that said that. — Não fui eu que disse isso.",
                "What surprised me was his reaction. — O que me surpreendeu foi a reação dele.",
            ],
        },
        {
            "topic": "Discurso indireto complexo",
            "structure": "said + recuo de tempos e deíticos",
            "explanation": "Relatos longos exigem cuidado com tempos e deíticos: here→there, now→then, today→that day, this→that. here/now viram there/then no discurso indireto.",
            "examples": [
                "He said he had been there the week before. — Ele disse que estivera lá na semana anterior.",
                "She explained that she would leave the next day. — Ela explicou que partiria no dia seguinte.",
                "They claimed they had never met him. — Eles alegaram nunca tê-lo conhecido.",
                "He told me this morning he was busy. — Ele me disse hoje cedo que estava ocupado.",
            ],
        },
        {
            "topic": "Conectivos discursivos sofisticados",
            "structure": "Nevertheless / Furthermore / thereby / Albeit",
            "explanation": "Coesão em texto formal. nevertheless (todavia), furthermore (além disso), thereby (assim), albeit (embora), notwithstanding. Elevam o registro acadêmico.",
            "examples": [
                "He was tired; nevertheless, he continued. — Ele estava cansado; todavia, continuou.",
                "She left, thereby ending the dispute. — Ela saiu, terminando assim a disputa.",
                "Albeit small, the team was effective. — Embora pequena, a equipe foi eficaz.",
                "Furthermore, the data supports our claim. — Além disso, os dados apoiam nossa tese.",
            ],
        },
        {
            "topic": "Preposições idiomáticas",
            "structure": "combinações fixas com preposição",
            "explanation": "Pares fixos: in charge of, by means of, on behalf of, with regard to, at risk of, on the grounds that. Preposição não é livre; decorar o par.",
            "examples": [
                "She is in charge of the project. — Ela está a cargo do projeto.",
                "On behalf of the team, thank you. — Em nome da equipe, obrigado.",
                "With regard to your request... — Com relação ao seu pedido...",
                "He is at risk of failing. — Ele corre risco de reprovar.",
            ],
        },
        {
            "topic": "Registro e nuances de tom",
            "structure": "formal vs. informal / mitigadores",
            "explanation": "Escolha de tom: I would appreciate it if (formal) vs. Can you... (direto). Mitigadores como I was wondering if, if you wouldn't mind, needless to say.",
            "examples": [
                "I would appreciate your feedback. — Agradeceria seu retorno (formal).",
                "I was wondering if you could help. — Gostaria de saber se poderia ajudar.",
                "Needless to say, we agree. — Escusado será dizer que concordamos.",
                "If you wouldn't mind closing the door. — Se não se importasse de fechar a porta.",
            ],
        },
        {
            "topic": "Fronting e ênfase com advérbios",
            "structure": "Advérbio + aux + Subject + ...",
            "explanation": "Antecipar um complemento para dar ênfase (Only after the war did he return). Similar à inversão negativa, mas com advérbios de tempo/ponto (only, not until, hardly).",
            "examples": [
                "Only then did I understand. — Só então eu entendi.",
                "Not until midnight did she arrive. — Só à meia-noite ela chegou.",
                "Hardly had we left when it rained. — Mal havíamos saído quando choveu.",
                "So tired was he that he fell asleep. — Tão cansado ele estava que dormiu.",
            ],
        },
        {
            "topic": "Ellipsis e estruturas compactas",
            "structure": "omissão de termos recuperáveis",
            "explanation": "Omitir palavras subentendidas para concisão (I will if I can). Parallelismo: She likes tea, and he coffee. Típico de C2 para fluidez e sofisticação.",
            "examples": [
                "I will go if you do. — Irei se você for.",
                "She likes tea, and he coffee. — Ela gosta de chá, e ele de café.",
                "He works harder than I. — Ele trabalha mais que eu.",
                "Some came by train, others by car. — Alguns vieram de trem, outros de carro.",
            ],
        },
    ],
}

# --- Grammar orientado a dados (arquivo externo) ---
# Conteudo carregado de GRAMMAR_FILE (padrao: grammar.json ao lado deste modulo).
# O dicionario GRAMMAR embutido acima e usado apenas como fallback caso o
# arquivo nao exista ou seja invalido. Edite grammar.json para adicionar
# topicos/exemplos sem mexer no codigo; use o endpoint /api/admin/reload-grammar
# (admin) para recarregar em tempo de execucao.
GRAMMAR_FILE = os.getenv("GRAMMAR_FILE", os.path.join(os.path.dirname(__file__), "grammar.json"))

def _grammar_file_for_lang(lang: str) -> str:
    if lang == DEFAULT_LANG:
        return GRAMMAR_FILE
    alt = os.path.join(os.path.dirname(__file__), f"grammar_{lang}.json")
    if os.path.exists(alt):
        return alt
    return GRAMMAR_FILE

def _listen_file_for_lang(lang: str) -> str | None:
    if lang == DEFAULT_LANG:
        return None
    alt = os.path.join(os.path.dirname(__file__), f"listen_{lang}.json")
    return alt if os.path.exists(alt) else None

def _read_file_for_lang(lang: str) -> str | None:
    if lang == DEFAULT_LANG:
        return None
    alt = os.path.join(os.path.dirname(__file__), f"read_{lang}.json")
    return alt if os.path.exists(alt) else None

def _load_listen_file(filepath: str) -> dict | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception as e:
        print(f"[listen] falha ao ler {filepath}: {e}")
        return None

def _load_read_file(filepath: str) -> dict | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception as e:
        print(f"[read] falha ao ler {filepath}: {e}")
        return None

GRAMMAR_CACHE = {}
_LISTEN_CACHE = {}
_READ_CACHE = {}

def load_grammar_data(lang: str = DEFAULT_LANG):
    global GRAMMAR, GRAMMAR_LEVELS
    filepath = _grammar_file_for_lang(lang)
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[grammar] falha ao ler {filepath}: {e}; usando conteudo embutido")
        return
    grammar = data.get("grammar")
    levels = data.get("levels")
    if not isinstance(grammar, dict) or not grammar:
        print(f"[grammar] {filepath} sem 'grammar' valido; usando embutido")
        return
    if not levels:
        levels = [lv for lv in GRAMMAR_LEVELS if lv in grammar] + [lv for lv in grammar if lv not in GRAMMAR_LEVELS]
    GRAMMAR_CACHE[lang] = {lv: grammar[lv] for lv in levels if lv in grammar}
    GRAMMAR_LEVELS = levels
    print(f"[grammar] carregado de {filepath}: {len(levels)} niveis (lang={lang})")


def _load_grammar(lang: str = DEFAULT_LANG):
    if lang not in GRAMMAR_CACHE:
        load_grammar_data(lang)
    return GRAMMAR_CACHE.get(lang, GRAMMAR)


def reload_grammar(lang: str | None = None):
    global GRAMMAR_CACHE
    if lang:
        GRAMMAR_CACHE.pop(lang, None)
        _MEMHACK_CACHE.pop(lang, None)
        _LISTEN_CACHE.pop(lang, None)
        _READ_CACHE.pop(lang, None)
        load_grammar_data(lang)
        for k in list(_CONTENT_QUEUES):
            if isinstance(k, tuple) and len(k) == 4 and k[3] == lang:
                _CONTENT_QUEUES.pop(k, None)
    else:
        GRAMMAR_CACHE.clear()
        _MEMHACK_CACHE.clear()
        _LISTEN_CACHE.clear()
        _READ_CACHE.clear()
        load_grammar_data()
        for k in list(_CONTENT_QUEUES):
            if isinstance(k, tuple):
                _CONTENT_QUEUES.pop(k, None)


load_grammar_data()

import random

_CONTENT_QUEUES = {}


def _next_item(level: str, module: str, category: str, lang: str = DEFAULT_LANG):
    listen_data = LISTEN
    read_data = READ
    if lang != DEFAULT_LANG:
        if lang not in _LISTEN_CACHE:
            lf = _listen_file_for_lang(lang)
            if lf:
                d = _load_listen_file(lf)
                if d:
                    _LISTEN_CACHE[lang] = d
        if lang not in _READ_CACHE:
            rf = _read_file_for_lang(lang)
            if rf:
                d = _load_read_file(rf)
                if d:
                    _READ_CACHE[lang] = d
        if lang in _LISTEN_CACHE:
            listen_data = _LISTEN_CACHE[lang]
        if lang in _READ_CACHE:
            read_data = _READ_CACHE[lang]
    pool = (read_data[level] if module == "read" else listen_data[level])
    if category and category != "all":
        items = pool.get(category, [])
    else:
        items = [x for cat in pool.values() for x in cat]
    if not items:
        items = [x for cat in pool.values() for x in cat]
    key = (level, module, category, lang)
    q = _CONTENT_QUEUES.get(key)
    if not q:
        q = items[:]
        random.shuffle(q)
        _CONTENT_QUEUES[key] = q
    return q.pop(0)


def normalize_level(level: str) -> str:
    return level if level in LEVELS else "iniciante"


def get_content(level: str, module: str, category: str = "all", lang: str = DEFAULT_LANG) -> dict:
    level = normalize_level(level)
    if module == "read":
        item = _next_item(level, "read", category, lang)
        return {"text": item["text"], "glossary": item["glossary"]}
    return {"text": _next_item(level, "listen", category, lang)}


def normalize_cefr(level: str) -> str:
    return level if level in GRAMMAR_LEVELS else "A1"


def _next_grammar(level: str, lang: str = DEFAULT_LANG):
    grammar_data = _load_grammar(lang)
    topics = grammar_data.get(normalize_cefr(level), [])
    key = ("grammar", normalize_cefr(level), lang)
    q = _CONTENT_QUEUES.get(key)
    if not q:
        q = topics[:]
        random.shuffle(q)
        _CONTENT_QUEUES[key] = q
    if not q:
        return None
    return q.pop(0)


def get_grammar(level: str, lang: str = DEFAULT_LANG) -> dict:
    topic = _next_grammar(level, lang)
    if not topic:
        return {"topic": "", "explanation": "", "structure": "", "examples": []}
    return {
        "topic": topic["topic"],
        "structure": topic.get("structure", ""),
        "explanation": topic["explanation"],
        "examples": topic["examples"][:],
    }


# --- MemHack: memorizacao com repeticao espacada (SRS estilo Leitner) ---
# Frases em backend/memhack.json (compartilhado). O progresso de cada usuario
# (box + proxima revisao) fica em DATA_DIR/memhack_progress.json.
MEMHACK_FILE = os.getenv("MEMHACK_FILE", os.path.join(os.path.dirname(__file__), "memhack.json"))
MEMHACK_PROGRESS_FILE = pathlib.Path(os.getenv("MEMHACK_PROGRESS", os.path.join(DATA_DIR, "memhack_progress.json")))

def _memhack_file_for_lang(lang: str) -> str:
    if lang == DEFAULT_LANG:
        return MEMHACK_FILE
    alt = os.path.join(os.path.dirname(__file__), f"memhack_{lang}.json")
    if os.path.exists(alt):
        return alt
    return MEMHACK_FILE

# Intervalos (segundos) por box: 1min, 10min, 1h, 1 dia, 7 dias.
MEMHACK_BOX_INTERVALS = {1: 60, 2: 600, 3: 3600, 4: 86400, 5: 604800}
MEMHACK_MAX_BOX = 5
MEMHACK_NEW_BOX = 1

_MEMHACK_CACHE = {}


def _load_memhack(lang: str = DEFAULT_LANG):
    if lang in _MEMHACK_CACHE and _MEMHACK_CACHE[lang] is not None:
        return _MEMHACK_CACHE[lang]
    filepath = _memhack_file_for_lang(lang)
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[memhack] falha ao ler {filepath}: {e}")
        data = {"categories": [], "labels": {}, "phrases": {}}
    _MEMHACK_CACHE[lang] = data
    return data


def _memhack_progress_key(user: str, lang: str) -> str:
    return f"{user}::{lang}"


def _load_memhack_progress() -> dict:
    if MEMHACK_PROGRESS_FILE.exists():
        try:
            return json.loads(MEMHACK_PROGRESS_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_memhack_progress(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEMHACK_PROGRESS_FILE.write_text(json.dumps(data, indent=2))


def get_memhack_categories(lang: str = DEFAULT_LANG) -> list:
    d = _load_memhack(lang)
    labels = d.get("labels", {})
    return [{"id": c, "label": labels.get(c, c)} for c in d.get("categories", [])]


def _memhack_phrase(category: str, pid: str, lang: str = DEFAULT_LANG):
    for p in _load_memhack(lang).get("phrases", {}).get(category, []):
        if p.get("id") == pid:
            return p
    return None


def get_memhack_next(user: str, category: str, lang: str = DEFAULT_LANG) -> dict:
    d = _load_memhack(lang)
    phrases = d.get("phrases", {}).get(category, [])
    if not phrases:
        return {"done": True, "message": "Sem frases nesta categoria."}
    progress_key = _memhack_progress_key(user, lang)
    progress = _load_memhack_progress().get(progress_key, {}).get(category, {})
    now = time.time()
    candidates = [p for p in phrases if progress.get(p["id"], {}).get("due", 0) <= now]
    if not candidates:
        soonest = min(
            (progress[p["id"]]["due"] for p in phrases if p["id"] in progress),
            default=now,
        )
        return {
            "done": True,
            "message": "Tudo em dia! Proxima revisao agendada.",
            "next_due": soonest,
            "total": len(phrases),
            "studied": len(progress),
        }
    candidates.sort(
        key=lambda p: (
            progress.get(p["id"], {}).get("due", 0),
            -progress.get(p["id"], {}).get("box", 0),
        )
    )
    phrase = candidates[0]
    return {
        "done": False,
        "phrase": phrase,
        "total": len(phrases),
        "studied": len(progress),
    }


def review_memhack(user: str, category: str, phrase_id: str, difficulty: str, lang: str = DEFAULT_LANG) -> dict:
    if difficulty not in ("facil", "medio", "dificil"):
        return {"error": "dificuldade invalida (use facil/medio/dificil)"}
    if not _memhack_phrase(category, phrase_id, lang):
        return {"error": "frase nao encontrada"}
    progress_all = _load_memhack_progress()
    progress_key = _memhack_progress_key(user, lang)
    cat_prog = progress_all.setdefault(progress_key, {}).setdefault(category, {})
    box = cat_prog.get(phrase_id, {}).get("box", MEMHACK_NEW_BOX)
    if difficulty == "facil":
        box = min(MEMHACK_MAX_BOX, box + 1)
    elif difficulty == "dificil":
        box = max(1, box - 1)
    interval = MEMHACK_BOX_INTERVALS.get(box, MEMHACK_BOX_INTERVALS[MEMHACK_MAX_BOX])
    cat_prog[phrase_id] = {"box": box, "due": time.time() + interval}
    _save_memhack_progress(progress_all)
    return get_memhack_next(user, category, lang)


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


def correct(text: str, level: str, lang: str = DEFAULT_LANG) -> str:
    meta = get_lang_meta(lang)
    prompt_prefix = meta["prompt_prefix"]
    if API_KEY:
        try:
            client = _client()
            prompt = (
                f"Voce e um professor de {prompt_prefix}. Corrija o texto abaixo (nivel {level}). "
                f"Formato: ERRO -> CORRECAO -> REGRA -> SUGESTAO.\n\n{text}"
            )
            r = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM indisponivel: {e}]\n" + heuristic_correct(text)
    return heuristic_correct(text)


def _run_async(coro):
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(coro)).result()


def tts_bytes(text: str, voice: str = None, lang: str = DEFAULT_LANG) -> bytes:
    voice = voice or get_default_voice(lang)
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


_VOICES_CACHE = {}


def list_voices(lang: str = DEFAULT_LANG) -> list:
    if lang in _VOICES_CACHE:
        return _VOICES_CACHE[lang]
    voices = []
    prefix = LANG_VOICES.get(lang, LANG_VOICES[DEFAULT_LANG]).split("-")[0]
    try:
        import edge_tts

        async def _list():
            return await edge_tts.list_voices()

        all_voices = _run_async(_list())
        for v in all_voices:
            if lang == "en" and v["ShortName"].startswith("en-"):
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
            elif lang == "es" and v["ShortName"].startswith("es-"):
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
            elif lang == "fr" and v["ShortName"].startswith("fr-"):
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
            elif lang == "it" and v["ShortName"].startswith("it-"):
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
            elif lang == "de" and v["ShortName"].startswith("de-"):
                voices.append({"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"])})
    except Exception:
        if lang == "en":
            voices = [{"id": "en-US-JennyNeural", "name": "Jenny (US, female)"},
                      {"id": "en-US-GuyNeural", "name": "Guy (US, male)"},
                      {"id": "en-GB-SoniaNeural", "name": "Sonia (UK, female)"},
                      {"id": "en-AU-NatashaNeural", "name": "Natasha (AU, female)"}]
        elif lang == "es":
            voices = [{"id": "es-ES-ElviraNeural", "name": "Elvira (ES, female)"},
                      {"id": "es-MX-DaliaNeural", "name": "Dalia (MX, female)"}]
        elif lang == "fr":
            voices = [{"id": "fr-FR-DeniseNeural", "name": "Denise (FR, female)"},
                      {"id": "fr-FR-HenriNeural", "name": "Henri (FR, male)"}]
        elif lang == "it":
            voices = [{"id": "it-IT-ElsaNeural", "name": "Elsa (IT, female)"},
                      {"id": "it-IT-DiegoNeural", "name": "Diego (IT, male)"}]
        elif lang == "de":
            voices = [{"id": "de-DE-KatjaNeural", "name": "Katja (DE, female)"},
                      {"id": "de-DE-ConradNeural", "name": "Conrad (DE, male)"}]
        else:
            voices = [{"id": LANG_VOICES.get(lang, LANG_VOICES[DEFAULT_LANG]), "name": "Default"}]
    _VOICES_CACHE[lang] = voices
    return voices


def stt_transcribe(audio_bytes: bytes, suffix: str = ".webm", lang: str = DEFAULT_LANG) -> str:
    import speech_recognition as sr
    import shutil
    meta = get_lang_meta(lang)
    stt_lang = meta["stt_lang"]
    r = sr.Recognizer()
    src = pathlib.Path(tempfile.mktemp(suffix=suffix))
    wav = src.with_suffix(".wav")
    src.write_bytes(audio_bytes)
    try:
        if suffix.lower() != ".wav":
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                raise RuntimeError(
                    "ffmpeg nao encontrado. Instale com:\n"
                    "  Ubuntu/Debian: sudo apt install ffmpeg\n"
                    "  macOS: brew install ffmpeg\n"
                    "  Windows: https://ffmpeg.org/download.html"
                )
            subprocess.run(
                [ffmpeg_path, "-y", "-i", str(src), "-ar", "16000", "-ac", "1",
                 "-f", "wav", str(wav)],
                capture_output=True, check=True)
            audio_path = wav
        else:
            audio_path = src
        with sr.AudioFile(str(audio_path)) as audio_src:
            audio = r.record(audio_src)
        return r.recognize_google(audio, language=stt_lang)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise RuntimeError(f"STT indisponivel (Google Speech API): {e}")
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="replace")[:200] if e.stderr else str(e)
        raise RuntimeError(f"STT: falha no ffmpeg: {msg}")
    finally:
        src.unlink(missing_ok=True)
        wav.unlink(missing_ok=True)


def converse(level: str, persona: str, history: list, user_message: str, lang: str = DEFAULT_LANG) -> str:
    meta = get_lang_meta(lang)
    prompt_prefix = meta["prompt_prefix"]
    persona_roles = PERSONAS.get(persona, {})
    persona_role = persona_roles.get(lang, persona_roles.get("en", "a helpful conversation partner"))
    lang_label = meta["label"]
    system = (
        f"You are a language teacher of {prompt_prefix}. "
        f"Your role: {persona_role}. "
        f"Converse in {lang_label} (nivel {level}). "
        f"Be engaging, ask follow-up questions, react naturally, and gently correct any mistakes the student makes. "
        f"Always respond in the target language."
    )
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user_message}]
    if API_KEY:
        try:
            client = _client()
            r = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, max_tokens=1024)
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM indisponivel: {e}] Hello! Tell me more about that."
    return "Hello! That's interesting. Can you tell me more?"


# --- Calendar & Numbers ---
CALENDAR_NUMBERS_CACHE = {}

def _calendar_numbers_file_for_lang(lang: str) -> str:
    if lang == DEFAULT_LANG:
        return os.path.join(os.path.dirname(__file__), "calendar_numbers_en.json")
    alt = os.path.join(os.path.dirname(__file__), f"calendar_numbers_{lang}.json")
    if os.path.exists(alt):
        return alt
    return os.path.join(os.path.dirname(__file__), "calendar_numbers_en.json")

def _load_calendar_numbers(lang: str = DEFAULT_LANG) -> dict:
    if lang in CALENDAR_NUMBERS_CACHE and CALENDAR_NUMBERS_CACHE[lang] is not None:
        return CALENDAR_NUMBERS_CACHE[lang]
    filepath = _calendar_numbers_file_for_lang(lang)
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[calendar_numbers] falha ao ler {filepath}: {e}")
        data = {"sections": {}}
    CALENDAR_NUMBERS_CACHE[lang] = data
    return data

def get_calendar_numbers(lang: str = DEFAULT_LANG, section: str = "all") -> dict:
    data = _load_calendar_numbers(lang)
    sections = data.get("sections", {})
    if section == "all":
        return sections
    if section in sections:
        return {section: sections[section]}
    return {"sections": list(sections.keys())}
