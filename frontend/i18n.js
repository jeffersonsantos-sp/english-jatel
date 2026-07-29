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
    "tab-speak": "Speak",
    "tab-write": "Write",
    "tab-read": "Read",
    "tab-converse": "Conversation",
    "tab-grammar": "Grammar",
    "tab-memhack": "MemHack",

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
    "speak-title": "Speak",
    "speak-sub": "Answer aloud (recording) or type — and hear the correction.",
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
    "tab-speak": "Hablar",
    "tab-write": "Escribir",
    "tab-read": "Leer",
    "tab-converse": "Conversar",
    "tab-grammar": "Gramática",
    "tab-memhack": "MemHack",

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
    "speak-title": "Hablar",
    "speak-sub": "Responde en voz alta (grabación) o escribe — y escucha la corrección.",
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
    "tab-speak": "Parler",
    "tab-write": "Écrire",
    "tab-read": "Lire",
    "tab-converse": "Conversation",
    "tab-grammar": "Grammaire",
    "tab-memhack": "MemHack",

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
    "speak-title": "Parler",
    "speak-sub": "Répondez à voix haute (enregistrement) ou tapez — et écoutez la correction.",
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

  document.documentElement.lang = lang === "en" ? "en" : lang === "es" ? "es" : "fr";

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
