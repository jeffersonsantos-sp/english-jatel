/* i18n — UI internationalization for EN / ES / FR */

const I18N = {
  en: {
    // topbar
    tagline: "Learn by listening, speaking & conversing",
    "label-level": "Level:",
    "opt-iniciante": "Beginner",
    "opt-intermediario": "Intermediate",
    "opt-avancado": "Advanced",
    "label-voice": "AI Voice:",
    "label-lang": "Language:",
    "opt-en": "English",
    "opt-es": "Spanish",
    "opt-fr": "French",
    "label-persona": "Persona (chat):",
    "btn-logout": "Logout",
    "btn-pass": "Password",
    "btn-users": "Users",

    // tabs
    "tab-listen": "Listen",
    "tab-speak": "Pronunciation",
    "tab-write": "Write",
    "tab-read": "Read",
    "tab-converse": "Conversation",
    "tab-grammar": "Grammar",
    "tab-memhack": "MemHack",
    "tab-numbers": "Numbers",

    // listen
    "listen-title": "Listen",
    "listen-sub": "Listen to the sentence, type what you hear, then check.",
    "listen-play": "Listen to sentence",
    "listen-repeat": "Repeat",
    "listen-next": "Next",
    "listen-label": "Dictation (what you heard):",
    "listen-placeholder": "Type the sentence you heard",
    "listen-check": "Check",
    // listen results (JS)
    "listen-correct": "Correct!",
    "listen-wrong": "Expected:\n{expected}\n\nYours:\n{got}",

    // speak
    "speak-title": "Pronunciation",
    "speak-sub": "Practice pronunciation: record a sentence and hear the correction.",
    "speak-hint": "Answer in English: \"Tell me about your last weekend.\"",
    "speak-rec": "Record",
    "speak-recording": "Recording...",
    "speak-stop": "Stop",
    "speak-play-transcript": "Listen to transcript",
    "speak-play-correction": "Listen to correction",
    "speak-label": "Or type your answer to correct:",
    "speak-placeholder": "Write in English...",
    "speak-correct-text": "Correct text",

    // write
    "write-title": "Write",
    "write-sub": "Write a paragraph and receive a detailed correction.",
    "write-label": "Your text:",
    "write-placeholder": "Write a paragraph in English...",
    "write-check": "Correct",

    // read
    "read-title": "Read",
    "read-sub": "Read the text, check the glossary and answer the question.",
    "read-load": "Load text",
    "read-next": "Next",
    "read-label": "Comprehension question (in English):",
    "read-placeholder": "Your answer",
    "read-check": "Correct",

    // converse
    "converse-title": "Chat with AI",
    "converse-sub": "Chat in English with the chosen persona.",
    "converse-ai-start": "AI speaks first",
    "converse-rec": "Record",
    "converse-recording": "Recording...",
    "converse-stop": "Stop",
    "converse-placeholder": "Or type your message...",
    "converse-send": "Send",

    // grammar
    "grammar-title": "Grammar",
    "grammar-sub": "Learn English grammar by level (CEFR Framework).",
    "grammar-level": "CEFR Level:",
    "grammar-load": "Load topic",
    "grammar-next": "Next",

    // memhack
    "memhack-title": "MemHack",
    "memhack-sub": "Memorize phrases with spaced repetition. Listen, train and rate difficulty.",
    "memhack-category": "Category:",
    "memhack-play": "Listen to phrase",
    "memhack-reveal": "Translation",
    "memhack-easy": "Easy",
    "memhack-medium": "Medium",
    "memhack-hard": "Hard",

    // change password modal
    "cp-title": "Change password",
    "cp-current": "Current password",
    "cp-new": "New password",
    "cp-confirm": "Confirm new password",
    "cp-save": "Save",
    "cp-cancel": "Cancel",

    // users modal
    "users-title": "Manage users",
    "users-username": "New user",
    "users-password": "Password",
    "users-confirm": "Confirm password",
    "users-add": "Create user",
    "users-existing": "Existing users",
    "users-close": "Close",

    // login
    "login-subtitle": "Restricted access — login to continue",
    "login-user-label": "Username",
    "login-pass-label": "Password",
    "login-btn": "Login",
    "login-error-invalid": "Invalid username or password",
    "login-error-connect": "Connection error",

    // errors
    "err-mic": "Microphone error: {msg}",
    "err-recording": "Could not start recording: {msg}",
    "err-mic-not-allowed": "Microphone permission denied",
    "err-no-speech": "No speech detected, try again",
    "err-audio-capture": "Microphone not found",
    "err-recording-cancelled": "Recording cancelled (30s limit). Try again.",
    "err-recording-timeout": "Recording cancelled (30s limit).",
    "err-stt-empty": "(empty audio)",
    "err-stt-network": "Could not transcribe audio",

    // misc
    "transcript-label": "Transcript: ",
    "correction-label": "Correction:\n",
    "glossary-label": "Glossary: ",
    "progress-label": "Progress: {studied}/{total} phrases in training",
    "memhack-done": "Done for now.",
    "memhack-scheduled": "Review scheduled. Come back later!",
    "status-active": "LLM active",
    "status-demo": "Demo mode (no LLM)",

    // numbers
    "calendar-numbers-title": "Numbers",
    "calendar-numbers-sub": "Learn numbers, ordinal numbers, months, and days of the week.",
    "subtab-numbers": "Numbers",
    "subtab-ordinals": "Ordinal Numbers",
    "subtab-months": "Months",
    "subtab-days": "Days of the Week",
  },

  es: {
    // topbar
    tagline: "Aprende escuchando, hablando y conversando",
    "label-level": "Nivel:",
    "opt-iniciante": "Principiante",
    "opt-intermediario": "Intermedio",
    "opt-avancado": "Avanzado",
    "label-voice": "Voz de IA:",
    "label-lang": "Idioma:",
    "opt-en": "Inglés",
    "opt-es": "Español",
    "opt-fr": "Francés",
    "label-persona": "Persona (chat):",
    "btn-logout": "Salir",
    "btn-pass": "Contraseña",
    "btn-users": "Usuarios",

    // tabs
    "tab-listen": "Escuchar",
    "tab-speak": "Pronunciación",
    "tab-write": "Escribir",
    "tab-read": "Leer",
    "tab-converse": "Conversar",
    "tab-grammar": "Gramática",
    "tab-memhack": "MemHack",
    "tab-numbers": "Números",

    // listen
    "listen-title": "Escuchar",
    "listen-sub": "Escucha la frase, escribe lo que oigas y luego comprueba.",
    "listen-play": "Escuchar frase",
    "listen-repeat": "Repetir",
    "listen-next": "Siguiente",
    "listen-label": "Dictado (lo que escuchaste):",
    "listen-placeholder": "Escribe la frase que escuchaste",
    "listen-check": "Comprobar",
    "listen-correct": "¡Correcto!",
    "listen-wrong": "Esperado:\n{expected}\n\nTu respuesta:\n{got}",

    // speak
    "speak-title": "Pronunciación",
    "speak-sub": "Practica la pronunciación: graba una frase y escucha la corrección.",
    "speak-hint": "Responde en inglés: \"Tell me about your last weekend.\"",
    "speak-rec": "Grabar",
    "speak-recording": "Grabando...",
    "speak-stop": "Parar",
    "speak-play-transcript": "Escuchar transcripción",
    "speak-play-correction": "Escuchar corrección",
    "speak-label": "O escribe tu respuesta para corregir:",
    "speak-placeholder": "Escribe en inglés...",
    "speak-correct-text": "Corregir texto",

    // write
    "write-title": "Escribir",
    "write-sub": "Escribe un párrafo y recibe una corrección detallada.",
    "write-label": "Tu texto:",
    "write-placeholder": "Escribe un párrafo en inglés...",
    "write-check": "Corregir",

    // read
    "read-title": "Leer",
    "read-sub": "Lee el texto, consulta el glosario y responde la pregunta.",
    "read-load": "Cargar texto",
    "read-next": "Siguiente",
    "read-label": "Pregunta de comprensión (en inglés):",
    "read-placeholder": "Tu respuesta",
    "read-check": "Corregir",

    // converse
    "converse-title": "Chatear con IA",
    "converse-sub": "Conversa en inglés con la persona elegida.",
    "converse-ai-start": "IA habla primero",
    "converse-rec": "Grabar",
    "converse-recording": "Grabando...",
    "converse-stop": "Parar",
    "converse-placeholder": "O escribe tu mensaje...",
    "converse-send": "Enviar",

    // grammar
    "grammar-title": "Gramática",
    "grammar-sub": "Aprende gramática inglesa por nivel (Marco CEFR).",
    "grammar-level": "Nivel CEFR:",
    "grammar-load": "Cargar tema",
    "grammar-next": "Siguiente",

    // memhack
    "memhack-title": "MemHack",
    "memhack-sub": "Memoriza frases con repetición espaciada. Escucha, entrena y clasifica la dificultad.",
    "memhack-category": "Categoría:",
    "memhack-play": "Escuchar frase",
    "memhack-reveal": "Traducción",
    "memhack-easy": "Fácil",
    "memhack-medium": "Medio",
    "memhack-hard": "Difícil",

    // change password modal
    "cp-title": "Cambiar contraseña",
    "cp-current": "Contraseña actual",
    "cp-new": "Nueva contraseña",
    "cp-confirm": "Confirmar nueva contraseña",
    "cp-save": "Guardar",
    "cp-cancel": "Cancelar",

    // users modal
    "users-title": "Gestionar usuarios",
    "users-username": "Nuevo usuario",
    "users-password": "Contraseña",
    "users-confirm": "Confirmar contraseña",
    "users-add": "Crear usuario",
    "users-existing": "Usuarios existentes",
    "users-close": "Cerrar",

    // login
    "login-subtitle": "Acceso restringido — inicia sesión para continuar",
    "login-user-label": "Usuario",
    "login-pass-label": "Contraseña",
    "login-btn": "Entrar",
    "login-error-invalid": "Usuario o contraseña inválidos",
    "login-error-connect": "Error de conexión",

    // errors
    "err-mic": "Error de micrófono: {msg}",
    "err-recording": "No se pudo iniciar la grabación: {msg}",
    "err-mic-not-allowed": "Permiso de micrófono denegado",
    "err-no-speech": "No se detectó tu voz, intenta de nuevo",
    "err-audio-capture": "Micrófono no encontrado",
    "err-recording-cancelled": "Grabación cancelada (límite de 30s). Intenta de nuevo.",
    "err-recording-timeout": "Grabación cancelada (límite de 30s).",
    "err-stt-empty": "(audio vacío)",
    "err-stt-network": "No se pudo transcribir el audio",

    // misc
    "transcript-label": "Transcripción: ",
    "correction-label": "Corrección:\n",
    "glossary-label": "Glosario: ",
    "progress-label": "Progreso: {studied}/{total} frases en entrenamiento",
    "memhack-done": "Terminado por ahora.",
    "memhack-scheduled": "Revisión programada. ¡Vuelve más tarde!",
    "status-active": "LLM activo",
    "status-demo": "Modo demo (sin LLM)",

    // numbers
    "calendar-numbers-title": "Números",
    "calendar-numbers-sub": "Aprende números, ordinales, meses y días de la semana.",
    "subtab-numbers": "Números",
    "subtab-ordinals": "Números Ordinales",
    "subtab-months": "Meses",
    "subtab-days": "Días de la Semana",
  },

  fr: {
    // topbar
    tagline: "Apprenez en écoutant, parlant et conversant",
    "label-level": "Niveau :",
    "opt-iniciante": "Débutant",
    "opt-intermediario": "Intermédiaire",
    "opt-avancado": "Avancé",
    "label-voice": "Voix de l'IA :",
    "label-lang": "Langue :",
    "opt-en": "Anglais",
    "opt-es": "Espagnol",
    "opt-fr": "Français",
    "label-persona": "Persona (chat) :",
    "btn-logout": "Déconnexion",
    "btn-pass": "Mot de passe",
    "btn-users": "Utilisateurs",

    // tabs
    "tab-listen": "Écouter",
    "tab-speak": "Prononciation",
    "tab-write": "Écrire",
    "tab-read": "Lire",
    "tab-converse": "Conversation",
    "tab-grammar": "Grammaire",
    "tab-memhack": "MemHack",
    "tab-numbers": "Nombres",

    // listen
    "listen-title": "Écouter",
    "listen-sub": "Écoutez la phrase, tapez ce que vous entendez, puis vérifiez.",
    "listen-play": "Écouter la phrase",
    "listen-repeat": "Répéter",
    "listen-next": "Suivant",
    "listen-label": "Dictée (ce que vous avez entendu) :",
    "listen-placeholder": "Tapez la phrase entendue",
    "listen-check": "Vérifier",
    "listen-correct": "Correct !",
    "listen-wrong": "Attendu :\n{expected}\n\nVotre réponse :\n{got}",

    // speak
    "speak-title": "Prononciation",
    "speak-sub": "Entraînez votre prononciation : enregistrez une phrase et écoutez la correction.",
    "speak-hint": "Répondez en anglais : \"Tell me about your last weekend.\"",
    "speak-rec": "Enregistrer",
    "speak-recording": "Enregistrement...",
    "speak-stop": "Arrêter",
    "speak-play-transcript": "Écouter la transcription",
    "speak-play-correction": "Écouter la correction",
    "speak-label": "Ou tapez votre réponse à corriger :",
    "speak-placeholder": "Écrivez en anglais...",
    "speak-correct-text": "Corriger le texte",

    // write
    "write-title": "Écrire",
    "write-sub": "Écrivez un paragraphe et recevez une correction détaillée.",
    "write-label": "Votre texte :",
    "write-placeholder": "Écrivez un paragraphe en anglais...",
    "write-check": "Corriger",

    // read
    "read-title": "Lire",
    "read-sub": "Lisez le texte, consultez le glossaire et répondez à la question.",
    "read-load": "Charger le texte",
    "read-next": "Suivant",
    "read-label": "Question de compréhension (en anglais) :",
    "read-placeholder": "Votre réponse",
    "read-check": "Corriger",

    // converse
    "converse-title": "Discuter avec l'IA",
    "converse-sub": "Discutez en anglais avec la persona choisie.",
    "converse-ai-start": "L'IA parle en premier",
    "converse-rec": "Enregistrer",
    "converse-recording": "Enregistrement...",
    "converse-stop": "Arrêter",
    "converse-placeholder": "Ou tapez votre message...",
    "converse-send": "Envoyer",

    // grammar
    "grammar-title": "Grammaire",
    "grammar-sub": "Apprenez la grammaire anglaise par niveau (Cadre CEFR).",
    "grammar-level": "Niveau CEFR :",
    "grammar-load": "Charger le sujet",
    "grammar-next": "Suivant",

    // memhack
    "memhack-title": "MemHack",
    "memhack-sub": "Mémorisez des phrases avec la répétition espacée. Écoutez, entraînez et évaluez la difficulté.",
    "memhack-category": "Catégorie :",
    "memhack-play": "Écouter la phrase",
    "memhack-reveal": "Traduction",
    "memhack-easy": "Facile",
    "memhack-medium": "Moyen",
    "memhack-hard": "Difficile",

    // change password modal
    "cp-title": "Changer le mot de passe",
    "cp-current": "Mot de passe actuel",
    "cp-new": "Nouveau mot de passe",
    "cp-confirm": "Confirmer le nouveau mot de passe",
    "cp-save": "Enregistrer",
    "cp-cancel": "Annuler",

    // users modal
    "users-title": "Gérer les utilisateurs",
    "users-username": "Nouvel utilisateur",
    "users-password": "Mot de passe",
    "users-confirm": "Confirmer le mot de passe",
    "users-add": "Créer l'utilisateur",
    "users-existing": "Utilisateurs existants",
    "users-close": "Fermer",

    // login
    "login-subtitle": "Accès restreint — connectez-vous pour continuer",
    "login-user-label": "Nom d'utilisateur",
    "login-pass-label": "Mot de passe",
    "login-btn": "Connexion",
    "login-error-invalid": "Nom d'utilisateur ou mot de passe invalide",
    "login-error-connect": "Erreur de connexion",

    // errors
    "err-mic": "Erreur de microphone : {msg}",
    "err-recording": "Impossible de démarrer l'enregistrement : {msg}",
    "err-mic-not-allowed": "Permission du microphone refusée",
    "err-no-speech": "Aucune parole détectée, réessayez",
    "err-audio-capture": "Microphone non trouvé",
    "err-recording-cancelled": "Enregistrement annulé (limite de 30s). Réessayez.",
    "err-recording-timeout": "Enregistrement annulé (limite de 30s).",
    "err-stt-empty": "(audio vide)",
    "err-stt-network": "Impossible de transcrire l'audio",

    // misc
    "transcript-label": "Transcription : ",
    "correction-label": "Correction :\n",
    "glossary-label": "Glossaire : ",
    "progress-label": "Progrès : {studied}/{total} phrases en entraînement",
    "memhack-done": "Terminé pour l'instant.",
    "memhack-scheduled": "Révision programmée. Revenez plus tard !",
    "status-active": "LLM actif",
    "status-demo": "Mode démo (sans LLM)",

    // numbers
    "calendar-numbers-title": "Nombres",
    "calendar-numbers-sub": "Apprenez les nombres, les ordinaux, les mois et les jours de la semaine.",
    "subtab-numbers": "Nombres",
    "subtab-ordinals": "Nombres Ordinaux",
    "subtab-months": "Mois",
    "subtab-days": "Jours de la Semaine",
  },

  it: {
    // topbar
    tagline: "Impara ascoltando, parlando e conversando",
    "label-level": "Livello:",
    "opt-iniciante": "Principiante",
    "opt-intermediario": "Intermedio",
    "opt-avancado": "Avanzato",
    "label-voice": "Voce IA:",
    "label-lang": "Lingua:",
    "opt-en": "Inglese",
    "opt-es": "Spagnolo",
    "opt-fr": "Francese",
    "opt-it": "Italiano",
    "opt-de": "Tedesco",
    "label-persona": "Persona (chat):",
    "btn-logout": "Esci",
    "btn-pass": "Password",
    "btn-users": "Utenti",

    // tabs
    "tab-listen": "Ascolta",
    "tab-speak": "Pronuncia",
    "tab-write": "Scrivi",
    "tab-read": "Leggi",
    "tab-converse": "Conversazione",
    "tab-grammar": "Grammatica",
    "tab-memhack": "MemHack",
    "tab-numbers": "Numeri",

    // listen
    "listen-title": "Ascolta",
    "listen-sub": "Ascolta la frase, scrivi ciò che senti e poi verifica.",
    "listen-play": "Ascolta frase",
    "listen-repeat": "Ripeti",
    "listen-next": "Successivo",
    "listen-label": "Dettato (quello che hai sentito):",
    "listen-placeholder": "Scrivi la frase sentita",
    "listen-check": "Verifica",
    "listen-correct": "Corretto!",
    "listen-wrong": "Atteso:\n{expected}\n\nLa tua risposta:\n{got}",

    // speak
    "speak-title": "Pronuncia",
    "speak-sub": "Esercita la pronuncia: registra una frase e ascolta la correzione.",
    "speak-hint": "Rispondi in inglese: \"Tell me about your last weekend.\"",
    "speak-rec": "Registra",
    "speak-recording": "Registrazione...",
    "speak-stop": "Ferma",
    "speak-play-transcript": "Ascolta trascrizione",
    "speak-play-correction": "Ascolta correzione",
    "speak-label": "Oppure scrivi la tua risposta da correggere:",
    "speak-placeholder": "Scrivi in inglese...",
    "speak-correct-text": "Correggi testo",

    // write
    "write-title": "Scrivi",
    "write-sub": "Scrivi un paragrafo e ricevi una correzione dettagliata.",
    "write-label": "Il tuo testo:",
    "write-placeholder": "Scrivi un paragrafo in inglese...",
    "write-check": "Correggi",

    // read
    "read-title": "Leggi",
    "read-sub": "Leggi il testo, consulta il glossario e rispondi alla domanda.",
    "read-load": "Carica testo",
    "read-next": "Successivo",
    "read-label": "Domanda di comprensione (in inglese):",
    "read-placeholder": "La tua risposta",
    "read-check": "Correggi",

    // converse
    "converse-title": "Chatta con l'IA",
    "converse-sub": "Conversa in inglese con la persona scelta.",
    "converse-ai-start": "L'IA parla prima",
    "converse-rec": "Registra",
    "converse-recording": "Registrazione...",
    "converse-stop": "Ferma",
    "converse-placeholder": "Oppure scrivi il tuo messaggio...",
    "converse-send": "Invia",

    // grammar
    "grammar-title": "Grammatica",
    "grammar-sub": "Impara la grammatica inglese per livello (Quadro CEFR).",
    "grammar-level": "Livello CEFR:",
    "grammar-load": "Carica argomento",
    "grammar-next": "Successivo",

    // memhack
    "memhack-title": "MemHack",
    "memhack-sub": "Memorizza frasi con ripetizione dilazionata. Ascolta, esercita e valuta la difficoltà.",
    "memhack-category": "Categoria:",
    "memhack-play": "Ascolta frase",
    "memhack-reveal": "Traduzione",
    "memhack-easy": "Facile",
    "memhack-medium": "Medio",
    "memhack-hard": "Difficile",

    // change password modal
    "cp-title": "Cambia password",
    "cp-current": "Password attuale",
    "cp-new": "Nuova password",
    "cp-confirm": "Conferma nuova password",
    "cp-save": "Salva",
    "cp-cancel": "Annulla",

    // users modal
    "users-title": "Gestisci utenti",
    "users-username": "Nuovo utente",
    "users-password": "Password",
    "users-confirm": "Conferma password",
    "users-add": "Crea utente",
    "users-existing": "Utenti esistenti",
    "users-close": "Chiudi",

    // login
    "login-subtitle": "Accesso riservato — accedi per continuare",
    "login-user-label": "Nome utente",
    "login-pass-label": "Password",
    "login-btn": "Accedi",
    "login-error-invalid": "Nome utente o password non validi",
    "login-error-connect": "Errore di connessione",

    // errors
    "err-mic": "Errore microfono: {msg}",
    "err-recording": "Impossibile avviare la registrazione: {msg}",
    "err-mic-not-allowed": "Permesso microfono negato",
    "err-no-speech": "Nessun parlato rilevato, riprova",
    "err-audio-capture": "Microfono non trovato",
    "err-recording-cancelled": "Registrazione annullata (limite 30s). Riprova.",
    "err-recording-timeout": "Registrazione annullata (limite 30s).",
    "err-stt-empty": "(audio vuoto)",
    "err-stt-network": "Impossibile trascrivere l'audio",

    // misc
    "transcript-label": "Trascrizione: ",
    "correction-label": "Correzione:\n",
    "glossary-label": "Glossario: ",
    "progress-label": "Progresso: {studied}/{total} frasi in allenamento",
    "memhack-done": "Finito per ora.",
    "memhack-scheduled": "Revisione programmata. Torna più tardi!",
    "status-active": "LLM attivo",
    "status-demo": "Modalità demo (senza LLM)",

    // numbers
    "calendar-numbers-title": "Numeri",
    "calendar-numbers-sub": "Impara numeri, ordinali, mesi e giorni della settimana.",
    "subtab-numbers": "Numeri",
    "subtab-ordinals": "Numeri Ordinali",
    "subtab-months": "Mesi",
    "subtab-days": "Giorni della Settimana",
  },

  de: {
    // topbar
    tagline: "Lernen durch Zuhören, Sprechen und Konversation",
    "label-level": "Niveau:",
    "opt-iniciante": "Anfänger",
    "opt-intermediario": "Mittelstufe",
    "opt-avancado": "Fortgeschritten",
    "label-voice": "KI-Stimme:",
    "label-lang": "Sprache:",
    "opt-en": "Englisch",
    "opt-es": "Spanisch",
    "opt-fr": "Französisch",
    "opt-it": "Italienisch",
    "opt-de": "Deutsch",
    "label-persona": "Persona (Chat):",
    "btn-logout": "Abmelden",
    "btn-pass": "Passwort",
    "btn-users": "Benutzer",

    // tabs
    "tab-listen": "Hören",
    "tab-speak": "Aussprache",
    "tab-write": "Schreiben",
    "tab-read": "Lesen",
    "tab-converse": "Unterhaltung",
    "tab-grammar": "Grammatik",
    "tab-memhack": "MemHack",
    "tab-numbers": "Zahlen",

    // listen
    "listen-title": "Hören",
    "listen-sub": "Höre den Satz, schreibe auf, was du hörst, und überprüfe dann.",
    "listen-play": "Satz anhören",
    "listen-repeat": "Wiederholen",
    "listen-next": "Weiter",
    "listen-label": "Diktat (was du gehört hast):",
    "listen-placeholder": "Schreibe den gehörten Satz",
    "listen-check": "Überprüfen",
    "listen-correct": "Richtig!",
    "listen-wrong": "Erwartet:\n{expected}\n\nDeine Antwort:\n{got}",

    // speak
    "speak-title": "Aussprache",
    "speak-sub": "Übe die Aussprache: zeichne einen Satz auf und höre die Korrektur.",
    "speak-hint": "Antworte auf Englisch: \"Tell me about your last weekend.\"",
    "speak-rec": "Aufnehmen",
    "speak-recording": "Aufnahme...",
    "speak-stop": "Stopp",
    "speak-play-transcript": "Transkript anhören",
    "speak-play-correction": "Korrektur anhören",
    "speak-label": "Oder schreibe deine Antwort zur Korrektur:",
    "speak-placeholder": "Schreibe auf Englisch...",
    "speak-correct-text": "Text korrigieren",

    // write
    "write-title": "Schreiben",
    "write-sub": "Schreibe einen Absatz und erhalte eine detaillierte Korrektur.",
    "write-label": "Dein Text:",
    "write-placeholder": "Schreibe einen Absatz auf Englisch...",
    "write-check": "Korrigieren",

    // read
    "read-title": "Lesen",
    "read-sub": "Lies den Text, konsultiere das Glossar und beantworte die Frage.",
    "read-load": "Text laden",
    "read-next": "Weiter",
    "read-label": "Verstehensfrage (auf Englisch):",
    "read-placeholder": "Deine Antwort",
    "read-check": "Korrigieren",

    // converse
    "converse-title": "Mit KI chatten",
    "converse-sub": "Unterhalte dich auf Englisch mit der gewählten Persona.",
    "converse-ai-start": "KI spricht zuerst",
    "converse-rec": "Aufnehmen",
    "converse-recording": "Aufnahme...",
    "converse-stop": "Stopp",
    "converse-placeholder": "Oder schreibe deine Nachricht...",
    "converse-send": "Senden",

    // grammar
    "grammar-title": "Grammatik",
    "grammar-sub": "Lerne Englisch-Grammatik nach Niveau (CEFR-Rahmen).",
    "grammar-level": "CEFR-Niveau:",
    "grammar-load": "Thema laden",
    "grammar-next": "Weiter",

    // memhack
    "memhack-title": "MemHack",
    "memhack-sub": "Merke dir Sätze mit verteiltem Wiederholen. Höre übe und bewerte den Schwierigkeitsgrad.",
    "memhack-category": "Kategorie:",
    "memhack-play": "Satz anhören",
    "memhack-reveal": "Übersetzung",
    "memhack-easy": "Leicht",
    "memhack-medium": "Mittel",
    "memhack-hard": "Schwer",

    // change password modal
    "cp-title": "Passwort ändern",
    "cp-current": "Aktuelles Passwort",
    "cp-new": "Neues Passwort",
    "cp-confirm": "Neues Passwort bestätigen",
    "cp-save": "Speichern",
    "cp-cancel": "Abbrechen",

    // users modal
    "users-title": "Benutzer verwalten",
    "users-username": "Neuer Benutzer",
    "users-password": "Passwort",
    "users-confirm": "Passwort bestätigen",
    "users-add": "Benutzer erstellen",
    "users-existing": "Bestehende Benutzer",
    "users-close": "Schließen",

    // login
    "login-subtitle": "Zugang beschränkt — melde dich an, um fortzufahren",
    "login-user-label": "Benutzername",
    "login-pass-label": "Passwort",
    "login-btn": "Anmelden",
    "login-error-invalid": "Ungültiger Benutzername oder Passwort",
    "login-error-connect": "Verbindungsfehler",

    // errors
    "err-mic": "Mikrofonfehler: {msg}",
    "err-recording": "Aufnahme konnte nicht gestartet werden: {msg}",
    "err-mic-not-allowed": "Mikrofonzugriff verweigert",
    "err-no-speech": "Keine Sprache erkannt, versuche es erneut",
    "err-audio-capture": "Mikrofon nicht gefunden",
    "err-recording-cancelled": "Aufnahme abgebrochen (30s Limit). Versuche es erneut.",
    "err-recording-timeout": "Aufnahme abgebrochen (30s Limit).",
    "err-stt-empty": "(leere Audiodatei)",
    "err-stt-network": "Audio konnte nicht transkribiert werden",

    // misc
    "transcript-label": "Transkript: ",
    "correction-label": "Korrektur:\n",
    "glossary-label": "Glossar: ",
    "progress-label": "Fortschritt: {studied}/{total} Sätze im Training",
    "memhack-done": "Fertig für jetzt.",
    "memhack-scheduled": "Überprüfung geplant. Komm später zurück!",
    "status-active": "LLM aktiv",
    "status-demo": "Demo-Modus (ohne LLM)",

    // numbers
    "calendar-numbers-title": "Zahlen",
    "calendar-numbers-sub": "Lerne Zahlen, Ordnungszahlen, Monate und Wochentage.",
    "subtab-numbers": "Zahlen",
    "subtab-ordinals": "Ordnungszahlen",
    "subtab-months": "Monate",
    "subtab-days": "Wochentage",
  },
};

function t(key, replacements) {
  const lang = (window.state && window.state.lang) || "en";
  let str = (I18N[lang] && I18N[lang][key]) || (I18N.en && I18N.en[key]) || key;
  if (replacements) {
    Object.entries(replacements).forEach(([k, v]) => {
      str = str.replace("{" + k + "}", v);
    });
  }
  return str;
}

function applyI18n() {
  const lang = (window.state && window.state.lang) || "en";

  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const translations = I18N[lang] || I18N.en;
    if (translations && translations[key] !== undefined) {
      el.textContent = translations[key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    const translations = I18N[lang] || I18N.en;
    if (translations && translations[key] !== undefined) {
      el.placeholder = translations[key];
    }
  });

  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title");
    const translations = I18N[lang] || I18N.en;
    if (translations && translations[key] !== undefined) {
      el.title = translations[key];
    }
  });
}

window.I18N = I18N;
window.t = t;
window.applyI18n = applyI18n;
