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

# --- Autenticação (multi-usuário, persistido em arquivo) ---
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "mudar123")
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
        _USERS_CACHE = {ADMIN_USER: {"salt": salt, "hash": h}}
        _save_users(_USERS_CACHE)
    return _USERS_CACHE


def _save_users(users: dict) -> None:
    global _USERS_CACHE
    _USERS_CACHE = users
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))


def verify_user(username: str, password: str) -> bool:
    users = _load_users()
    u = users.get(username)
    if not u:
        return False
    salt = bytes.fromhex(u["salt"])
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk.hex(), u["hash"])


def add_user(username: str, password: str) -> None:
    users = _load_users()
    if username in users:
        raise ValueError("usuário já existe")
    if len(password) < 4:
        raise ValueError("senha muito curta (mín. 4)")
    salt, h = _hash_password(password)
    users[username] = {"salt": salt, "hash": h}
    _save_users(users)


def set_user_password(username: str, password: str) -> None:
    users = _load_users()
    if username not in users:
        raise ValueError("usuário não existe")
    salt, h = _hash_password(password)
    users[username] = {"salt": salt, "hash": h}
    _save_users(users)


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

# --- Grammar: conteúdo por nível CEFR (A1..C2) ---
# Cada tópico: titulo, explicacao (pt-BR), exemplos (ingles — traducao).
GRAMMAR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

GRAMMAR = {
    "A1": [
        {
            "topic": "Verbo to be (ser / estar)",
            "explanation": "Usamos am (eu), is (ele/ela/isto), are (você/nós/eles) para identidade, idade, profissão e estado. Na negativa, acrescenta-se not (isn't / aren't).",
            "examples": [
                "I am a student. — Eu sou estudante.",
                "She is from Brazil. — Ela é do Brasil.",
                "They are not at home. — Eles não estão em casa.",
            ],
        },
        {
            "topic": "Pronomes pessoais",
            "explanation": "I (eu), you (você), he (ele), she (ela), it (isto), we (nós), they (eles/elas). O pronome define a forma do verbo.",
            "examples": [
                "He speaks English. — Ele fala inglês.",
                "We live in São Paulo. — Nós moramos em São Paulo.",
                "It is a book. — Isto é um livro.",
            ],
        },
        {
            "topic": "Artigos a / an / the",
            "explanation": "a antes de consoante, an antes de vogal (a dog, an apple). the define algo já conhecido. Sem artigo para plural geral (I like cats).",
            "examples": [
                "I have a cat. — Eu tenho um gato.",
                "She ate an orange. — Ela comeu uma laranja.",
                "The book is on the table. — O livro está sobre a mesa.",
            ],
        },
        {
            "topic": "Plural de substantivos",
            "explanation": "Geralmente + s (cat -> cats). Terminando em s, x, ch, sh ou o consonante: + es. Muitos irregulares (child -> children).",
            "examples": [
                "one dog, two dogs. — um cão, dois cães.",
                "one box, three boxes. — uma caixa, três caixas.",
                "one man, many men. — um homem, muitos homens.",
            ],
        },
        {
            "topic": "Present Simple (afirmativo)",
            "explanation": "Fatos e rotinas. He/She/It leva -s no verbo (works, goes). Outras pessoas usam o verbo na base.",
            "examples": [
                "I work every day. — Eu trabalho todo dia.",
                "He goes to school. — Ele vai à escola.",
                "We like coffee. — Nós gostamos de café.",
            ],
        },
    ],
    "A2": [
        {
            "topic": "Present Simple (negativo e interrogativo)",
            "explanation": "Usa-se o auxiliar do/does. Negativo: don't/doesn't + verbo base. Interrogativo: Do/Does + sujeito + verbo base.",
            "examples": [
                "I don't like tea. — Eu não gosto de chá.",
                "Does she speak French? — Ela fala francês?",
                "They don't live here. — Eles não moram aqui.",
            ],
        },
        {
            "topic": "Past Simple",
            "explanation": "Ações concluídas no passado. Regulares: + ed (played). Irregulares comuns: go->went, eat->ate, see->saw. Negativo/interrogativo com did.",
            "examples": [
                "I visited my grandmother. — Eu visitei minha avó.",
                "He went to the market. — Ele foi ao mercado.",
                "We didn't watch TV. — Nós não assistimos TV.",
            ],
        },
        {
            "topic": "Preposições de tempo in / on / at",
            "explanation": "in + meses/anos (in July, in 2020). on + dias (on Monday, on Sunday). at + horas (at 7 o'clock, at night).",
            "examples": [
                "The party is in December. — A festa é em dezembro.",
                "We meet on Friday. — Nós nos encontramos na sexta.",
                "The bus leaves at nine. — O ônibus sai às nove.",
            ],
        },
        {
            "topic": "There is / There are",
            "explanation": "Para dizer que algo existe. there is (singular), there are (plural). Na negativa: isn't / aren't.",
            "examples": [
                "There is a park near my house. — Há um parque perto de casa.",
                "There are two cats. — Há dois gatos.",
                "There isn't any milk. — Não há leite nenhum.",
            ],
        },
        {
            "topic": "Can / Can't (habilidade)",
            "explanation": "can + verbo base indica capacidade ou permissão. Negativo: can't. Interrogativo: Can + sujeito + verbo base.",
            "examples": [
                "I can swim. — Eu sei nadar.",
                "She can't drive. — Ela não sabe dirigir.",
                "Can you help me? — Você pode me ajudar?",
            ],
        },
    ],
    "B1": [
        {
            "topic": "Present Continuous",
            "explanation": "am/is/are + verbo-ing para ações no momento ou temporárias. Often com now / at the moment.",
            "examples": [
                "I am reading a book now. — Estou lendo um livro agora.",
                "She is working today. — Ela está trabalhando hoje.",
                "They are not sleeping. — Eles não estão dormindo.",
            ],
        },
        {
            "topic": "Past Continuous",
            "explanation": "was/were + verbo-ing para ação em progresso no passado, muitas vezes interrompida por outra (when).",
            "examples": [
                "I was taking a shower when you called. — Eu tomava banho quando você ligou.",
                "They were playing football. — Eles estavam jogando futebol.",
                "She was studying all night. — Ela estava estudando a noite toda.",
            ],
        },
        {
            "topic": "Present Perfect",
            "explanation": "have/has + particípio para experiências, mudanças recentes e algo que começou no passado e continua. have been / has gone.",
            "examples": [
                "I have been to London. — Eu estive em Londres (já fui).",
                "She has finished her homework. — Ela terminou a lição.",
                "We have lived here for years. — Moramos aqui há anos.",
            ],
        },
        {
            "topic": "Futuro: will / going to",
            "explanation": "will para decisões no momento e previsões. going to para planos e intenções já decididas ou sinais no presente.",
            "examples": [
                "I will help you. — Eu vou te ajudar (agora decidi).",
                "Look at the sky! It's going to rain. — Olhe o céu! Vai chover.",
                "We are going to travel in July. — Vamos viajar em julho.",
            ],
        },
        {
            "topic": "First Conditional",
            "explanation": "if + Present Simple, will + base. Para resultados prováveis no futuro.",
            "examples": [
                "If it rains, we will stay home. — Se chover, ficaremos em casa.",
                "If you study, you will pass. — Se você estudar, passará.",
                "If he calls, I will tell him. — Se ele ligar, eu direi a ele.",
            ],
        },
    ],
    "B2": [
        {
            "topic": "Present Perfect Continuous",
            "explanation": "have/has been + verbo-ing para ação que começou no passado e continua ou tem resultado visível agora.",
            "examples": [
                "I have been waiting for an hour. — Estou esperando há uma hora.",
                "She has been working all day. — Ela está trabalhando o dia todo.",
                "It has been raining since morning. — Chove desde de manhã.",
            ],
        },
        {
            "topic": "Second Conditional",
            "explanation": "if + Past Simple, would + base. Para situações hipotéticas ou irreais no presente/futuro.",
            "examples": [
                "If I won the lottery, I would travel. — Se eu ganhasse na loteria, viajaria.",
                "If she knew, she would tell us. — Se ela soubesse, nos diria.",
                "What would you do? — O que você faria?",
            ],
        },
        {
            "topic": "Voz passiva",
            "explanation": "be + particípio. O foco vai para a ação/objeto. Active: They built the house -> Passive: The house was built.",
            "examples": [
                "The letter was written by Tom. — A carta foi escrita pelo Tom.",
                "English is spoken worldwide. — O inglês é falado no mundo todo.",
                "The cake has been eaten. — O bolo foi comido.",
            ],
        },
        {
            "topic": "Reported Speech (introdução)",
            "explanation": "Repete o que foi dito com mudança de tempo (say/tell + que). present -> past, will -> would, am/is -> was.",
            "examples": [
                "He said he was tired. — Ele disse que estava cansado.",
                "She told me she would come. — Ela me disse que viria.",
                "They said they liked it. — Eles disseram que gostaram.",
            ],
        },
        {
            "topic": "Modais de dedução",
            "explanation": "must (certeza afirmativa), can't (certeza negativa), could/might (possibilidade).",
            "examples": [
                "He must be at home. — Ele deve estar em casa.",
                "That can't be true. — Isso não pode ser verdade.",
                "She might be busy. — Ela pode estar ocupada.",
            ],
        },
    ],
    "C1": [
        {
            "topic": "Third Conditional",
            "explanation": "if + Past Perfect, would have + particípio. Situações hipotéticas sobre o passado (não mudáveis).",
            "examples": [
                "If I had studied, I would have passed. — Se eu tivesse estudado, teria passado.",
                "If she had left earlier, she wouldn't have missed it. — Se tivesse saído cedo, não teria perdido.",
                "We would have helped if we had known. — Teríamos ajudado se soubéssemos.",
            ],
        },
        {
            "topic": "Inversão após negativos",
            "explanation": "Advérbios negativos no início (never, hardly, seldom, not only) exigem inversão sujeito-verbo (auxiliar antes do sujeito).",
            "examples": [
                "Never have I seen such a thing. — Nunca vi tal coisa.",
                "Seldom does he complain. — Raramente ele reclama.",
                "Not only did she win, but she broke the record. — Ela não só venceu, como quebrou o recorde.",
            ],
        },
        {
            "topic": "Wish / If only",
            "explanation": "Desejos sobre presente (Past Simple) ou passado (Past Perfect). I wish I were / I wish I had done.",
            "examples": [
                "I wish I spoke French. — Quem me dera falar francês.",
                "I wish I had studied more. — Queria ter estudado mais.",
                "If only we knew! — Se ao menos soubéssemos!",
            ],
        },
        {
            "topic": "Passiva com modais e perífrasis",
            "explanation": "modal + be + particípio (must be done); ou have something done (something is done for you).",
            "examples": [
                "The work must be finished today. — O trabalho deve ser terminado hoje.",
                "He had his car repaired. — Ele mandou consertar o carro.",
                "The report is being written. — O relatório está sendo escrito.",
            ],
        },
        {
            "topic": "Colocações avançadas",
            "explanation": "Palavras que combinam naturalmente (make a decision, take action, raise a question, pay attention).",
            "examples": [
                "We made a decision. — Nós tomamos uma decisão.",
                "Please pay attention. — Por favor, preste atenção.",
                "They raised an interesting point. — Eles levantaram um ponto interessante.",
            ],
        },
    ],
    "C2": [
        {
            "topic": "Cleft sentences (ênfase)",
            "explanation": "It was/were + foco + that/who para dar ênfase a um elemento da frase. It was John who called.",
            "examples": [
                "It was the manager who approved it. — Foi o gerente quem aprovou.",
                "It is grammar that we are studying. — É gramática que estamos estudando.",
                "It wasn't me that said that. — Não fui eu que disse isso.",
            ],
        },
        {
            "topic": "Discurso indireto complexo",
            "explanation": "Mudança de tempos e deicticos em relatos longos; cuidado com would/could e expressões de tempo (here->there, now->then).",
            "examples": [
                "He said he had been there the week before. — Ele disse que estivera lá na semana anterior.",
                "She explained that she would leave the next day. — Ela explicou que partiria no dia seguinte.",
                "They claimed they had never met him. — Eles alegaram nunca tê-lo conhecido.",
            ],
        },
        {
            "topic": "Conectivos discursivos sofisticados",
            "explanation": "Nevertheless, furthermore, thereby, albeit, notwithstanding, on the grounds that — para Coesão em texto formal.",
            "examples": [
                "He was tired; nevertheless, he continued. — Ele estava cansado; todavia, continuou.",
                "She left, thereby ending the dispute. — Ela saiu, terminando assim a disputa.",
                "Albeit small, the team was effective. — Embora pequena, a equipe foi eficaz.",
            ],
        },
        {
            "topic": "Preposições idiomáticas",
            "explanation": "Combinações fixas (in charge of, by means of, on behalf of, with regard to, at risk of).",
            "examples": [
                "She is in charge of the project. — Ela está a cargo do projeto.",
                "On behalf of the team, thank you. — Em nome da equipe, obrigado.",
                "With regard to your request... — Com relação ao seu pedido...",
            ],
        },
        {
            "topic": "Registro e nuances de tom",
            "explanation": "Escolha entre formal/informal e construtores compactos para precisão (I would appreciate it if / I was wondering if).",
            "examples": [
                "I would appreciate your feedback. — Agradeceria seu retorno (formal).",
                "I was wondering if you could help. — Gostaria de saber se poderia ajudar.",
                "Needless to say, we agree. — Escusado será dizer que concordamos.",
            ],
        },
    ],
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


def normalize_cefr(level: str) -> str:
    return level if level in GRAMMAR_LEVELS else "A1"


def _next_grammar(level: str):
    topics = GRAMMAR.get(normalize_cefr(level), [])
    key = ("grammar", normalize_cefr(level))
    q = _CONTENT_QUEUES.get(key)
    if not q:
        q = topics[:]
        random.shuffle(q)
        _CONTENT_QUEUES[key] = q
    if not q:
        return None
    return q.pop(0)


def get_grammar(level: str) -> dict:
    topic = _next_grammar(level)
    if not topic:
        return {"topic": "", "explanation": "", "examples": []}
    return {
        "topic": topic["topic"],
        "explanation": topic["explanation"],
        "examples": topic["examples"][:],
    }


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
