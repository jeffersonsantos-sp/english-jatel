const TRANSLATIONS = {
  app_title: { en: "JATEL IA", es: "JATEL IA", fr: "JATEL IA", pt: "JATEL IA" },
  app_subtitle: { en: "Learn by listening, speaking & conversing", es: "Aprende escuchando, hablando y conversando", fr: "Apprenez en écoutant, parlant et conversant", pt: "Aprenda ouvindo, falando & conversando" },
  lang_label: { en: "Language:", es: "Idioma:", fr: "Langue:", pt: "Idioma:" },
  level_label: { en: "Level:", es: "Nivel:", fr: "Niveau:", pt: "Nível:" },
  voice_label: { en: "AI Voice:", es: "Voz IA:", fr: "Voix IA:", pt: "Voz da IA:" },
  persona_label: { en: "Persona:", es: "Persona:", fr: "Personnage:", pt: "Persona (conversa):" },
  status_title: { en: "Connection status", es: "Estado de conexión", fr: "Statut de connexion", pt: "Status da conexão" },
  logout_btn: { en: "Logout", es: "Salir", fr: "Déconnexion", pt: "Sair" },
  change_pass_btn: { en: "Password", es: "Contraseña", fr: "Mot de passe", pt: "Senha" },
  users_btn: { en: "Users", es: "Usuarios", fr: "Utilisateurs", pt: "Usuários" },
  loading: { en: "Loading...", es: "Cargando...", fr: "Chargement...", pt: "Carregando..." },
  lang_en: { en: "English", es: "Inglés", fr: "Anglais", pt: "Inglês" },
  lang_es: { en: "Spanish", es: "Español", fr: "Espagnol", pt: "Espanhol" },
  lang_fr: { en: "French", es: "Francés", fr: "Français", pt: "Francês" },
  level_iniciante: { en: "Beginner", es: "Principiante", fr: "Débutant", pt: "Iniciante" },
  level_intermediario: { en: "Intermediate", es: "Intermedio", fr: "Intermédiaire", pt: "Intermediário" },
  level_avancado: { en: "Advanced", es: "Avanzado", fr: "Avancé", pt: "Avançado" },
  persona_cafe: { en: "Coffee", es: "Café", fr: "Café", pt: "Café" },
  persona_entrevistador: { en: "Interviewer", es: "Entrevistador", fr: "Interviewer", pt: "Entrevistador" },
  persona_negocios: { en: "Business", es: "Negocios", fr: "Affaires", pt: "Negócios" },
  persona_viagens: { en: "Travel", es: "Viajes", fr: "Voyages", pt: "Viagens" },
  persona_familia: { en: "Family", es: "Familia", fr: "Famille", pt: "Família" },
  persona_filmes: { en: "Movies", es: "Películas", fr: "Films", pt: "Filmes" },
  persona_series: { en: "Series", es: "Series", fr: "Séries", pt: "Séries" },
  persona_musicas: { en: "Music", es: "Música", fr: "Musique", pt: "Músicas" },
  persona_futebol: { en: "Soccer", es: "Fútbol", fr: "Football", pt: "Futebol" },
  persona_devops: { en: "DevOps", es: "DevOps", fr: "DevOps", pt: "DevOps" },
  listen_tab: { en: "Listen", es: "Escuchar", fr: "Écouter", pt: "Listen" },
  speak_tab: { en: "Speak", es: "Hablar", fr: "Parler", pt: "Speak" },
  write_tab: { en: "Write", es: "Escribir", fr: "Écrire", pt: "Write" },
  read_tab: { en: "Read", es: "Leer", fr: "Lire", pt: "Read" },
  converse_tab: { en: "Converse", es: "Conversar", fr: "Converser", pt: "Conversar" },
  grammar_tab: { en: "Grammar", es: "Gramática", fr: "Grammaire", pt: "Grammar" },
  memhack_tab: { en: "MemHack", es: "MemHack", fr: "MemHack", pt: "MemHack" },
  listen_title: { en: "Listen", es: "Escuchar", fr: "Écouter", pt: "Listen" },
  listen_subtitle: { en: "Listen to the sentence, write what you hear, then check.", es: "Escucha la frase, escribe lo que oyes y luego verifica.", fr: "Écoutez la phrase, écrivez ce que vous entendez, puis vérifiez.", pt: "Escute a frase, faça o ditado e confira depois." },
  listen_play: { en: "Listen", es: "Escuchar", fr: "Écouter", pt: "Ouvir frase" },
  listen_repeat: { en: "Repeat", es: "Repetir", fr: "Répéter", pt: "Repetir" },
  listen_next: { en: "Next", es: "Siguiente", fr: "Suivant", pt: "Próxima" },
  listen_check: { en: "Check", es: "Verificar", fr: "Vérifier", pt: "Verificar" },
  listen_label: { en: "Dictation (what you heard):", es: "Dictado (lo que oíste):", fr: "Dictée (ce que vous avez entendu):", pt: "Ditado (o que você ouviu):" },
  listen_placeholder: { en: "Type the sentence you heard", es: "Escribe la frase que oíste", fr: "Tapez la phrase entendue", pt: "Digite a frase ouvida" },
  speak_title: { en: "Speak", es: "Hablar", fr: "Parler", pt: "Speak" },
  speak_subtitle: { en: "Answer aloud (recording) or type — and hear the correction.", es: "Responde en voz alta (grabación) o escribe — y escucha la corrección.", fr: "Répondez à voix haute (enregistrement) ou tapez — et écoutez la correction.", pt: "Responda em voz alta (gravação) ou digite — e ouça a correção." },
  speak_hint_en: { en: 'Answer in English: "Tell me about your last weekend."', es: 'Responde en inglés: "Cuéntame sobre tu último fin de semana."', fr: 'Répondez en anglais: "Parle-moi de ton dernier week-end."', pt: 'Responda em inglês: "Tell me about your last weekend."' },
  speak_hint_es: { en: 'Answer in Spanish: "Cuéntame sobre tu último fin de semana."', es: 'Responde en español: "Cuéntame sobre tu último fin de semana."', fr: 'Répondez en espagnol: "Parle-moi de ton dernier week-end."', pt: 'Responda em espanhol: "Cuéntame sobre tu último fin de semana."' },
  speak_hint_fr: { en: 'Answer in French: "Parle-moi de ton dernier week-end."', es: 'Responde en francés: "Parle-moi de ton dernier week-end."', fr: 'Répondez en français: "Parle-moi de ton dernier week-end."', pt: 'Responda em francês: "Parle-moi de ton dernier week-end."' },
  speak_rec: { en: "Record", es: "Grabar", fr: "Enregistrer", pt: "Gravar" },
  speak_stop: { en: "Stop", es: "Parar", fr: "Arrêter", pt: "Parar" },
  speak_hear_transcript: { en: "Hear transcript", es: "Oír transcripción", fr: "Entendre transcription", pt: "Ouvir transcrição" },
  speak_hear_correction: { en: "Hear correction", es: "Oír corrección", fr: "Entendre correction", pt: "Ouvir correção" },
  speak_or_type: { en: "Or type your answer to correct:", es: "O escribe tu respuesta para corregir:", fr: "Ou tapez votre réponse à corriger:", pt: "Ou digite sua resposta para corrigir:" },
  speak_placeholder: { en: "Write in English...", es: "Escribe en inglés...", fr: "Écrivez en anglais...", pt: "Escreva em inglês..." },
  speak_correct_text: { en: "Correct text", es: "Corregir texto", fr: "Corriger le texte", pt: "Corrigir texto" },
  write_title: { en: "Write", es: "Escribir", fr: "Écrire", pt: "Write" },
  write_subtitle: { en: "Write a paragraph and receive a detailed correction.", es: "Escribe un párrafo y recibe una corrección detallada.", fr: "Écrivez un paragraphe et recevez une correction détaillée.", pt: "Escreva um parágrafo e receba uma correção detalhada." },
  write_label: { en: "Your text:", es: "Tu texto:", fr: "Votre texte:", pt: "Seu texto:" },
  write_placeholder: { en: "Write a paragraph in English...", es: "Escribe un párrafo en inglés...", fr: "Écrivez un paragraphe en anglais...", pt: "Escreva um parágrafo em inglês..." },
  write_check: { en: "Correct", es: "Corregir", fr: "Corriger", pt: "Corrigir" },
  read_title: { en: "Read", es: "Leer", fr: "Lire", pt: "Read" },
  read_subtitle: { en: "Read the text, check the glossary, and answer the question.", es: "Lee el texto, consulta el glosario y responde la pregunta.", fr: "Lisez le texte, consultez le glossaire et répondez à la question.", pt: "Leia o texto, consulte o glossário e responda à pergunta." },
  read_load: { en: "Load text", es: "Cargar texto", fr: "Charger le texte", pt: "Carregar texto" },
  read_next: { en: "Next", es: "Siguiente", fr: "Suivant", pt: "Próximo" },
  read_question: { en: "Comprehension question:", es: "Pregunta de comprensión:", fr: "Question de compréhension:", pt: "Pergunta de compreensão:" },
  read_placeholder: { en: "Your answer", es: "Tu respuesta", fr: "Votre réponse", pt: "Sua resposta" },
  read_check: { en: "Check", es: "Corregir", fr: "Vérifier", pt: "Corrigir" },
  converse_title: { en: "Chat with AI", es: "Conversar con IA", fr: "Discuter avec IA", pt: "Conversar com a IA" },
  converse_subtitle_en: { en: "Chat in English with your chosen persona.", es: "Charla en inglés con la persona elegida.", fr: "Discutez en anglais avec le personnage choisi.", pt: "Bate-papo em inglês com a persona escolhida." },
  converse_subtitle_es: { en: "Chat in Spanish with your chosen persona.", es: "Charla en español con la persona elegida.", fr: "Discutez en espagnol avec le personnage choisi.", pt: "Bate-papo em espanhol com a persona escolhida." },
  converse_subtitle_fr: { en: "Chat in French with your chosen persona.", es: "Charla en francés con la persona elegida.", fr: "Discutez en français avec le personnage choisi.", pt: "Bate-papo em francês com a persona escolhida." },
  conv_ai_start: { en: "AI speaks first", es: "IA habla primero", fr: "IA parle d'abord", pt: "IA fala primeiro" },
  conv_rec: { en: "Record", es: "Grabar", fr: "Enregistrer", pt: "Gravar" },
  conv_stop: { en: "Stop", es: "Parar", fr: "Arrêter", pt: "Parar" },
  conv_placeholder: { en: "Or type your message...", es: "O escribe tu mensaje...", fr: "Ou tapez votre message...", pt: "Ou digite sua mensagem..." },
  conv_send: { en: "Send", es: "Enviar", fr: "Envoyer", pt: "Enviar" },
  grammar_title: { en: "Grammar", es: "Gramática", fr: "Grammaire", pt: "Grammar" },
  grammar_subtitle_en: { en: "Learn English grammar by level (CEFR).", es: "Aprende gramática inglesa por nivel (MCER).", fr: "Apprenez la grammaire anglaise par niveau (CECR).", pt: "Aprenda gramática inglesa por nível (Quadro Europeu CEFR)." },
  grammar_subtitle_es: { en: "Learn Spanish grammar by level (CEFR).", es: "Aprende gramática española por nivel (MCER).", fr: "Apprenez la grammaire espagnole par niveau (CECR).", pt: "Aprenda gramática espanhola por nível (Quadro Europeu CEFR)." },
  grammar_subtitle_fr: { en: "Learn French grammar by level (CEFR).", es: "Aprende gramática francesa por nivel (MCER).", fr: "Apprenez la grammaire française par niveau (CECR).", pt: "Aprenda gramática francesa por nível (Quadro Europeu CEFR)." },
  grammar_cefr_label: { en: "CEFR Level:", es: "Nivel MCER:", fr: "Niveau CECR:", pt: "Nível CEFR:" },
  grammar_load: { en: "Load topic", es: "Cargar tema", fr: "Charger le sujet", pt: "Carregar tópico" },
  grammar_next: { en: "Next", es: "Siguiente", fr: "Suivant", pt: "Próximo" },
  memhack_title: { en: "MemHack", es: "MemHack", fr: "MemHack", pt: "MemHack" },
  memhack_subtitle: { en: "Memorize phrases with spaced repetition. Listen, practice, rate difficulty.", es: "Memoriza frases con repetición espaciada. Escucha, practica, clasifica.", fr: "Mémorisez des phrases avec répétition espacée. Écoutez, pratiquez, évaluez.", pt: "Memorize frases com repetição espaçada. Ouça, treine e classifique a dificuldade." },
  memhack_category_label: { en: "Category:", es: "Categoría:", fr: "Catégorie:", pt: "Categoria:" },
  memhack_play: { en: "Listen", es: "Escuchar", fr: "Écouter", pt: "Ouvir frase" },
  memhack_reveal: { en: "Translation", es: "Traducción", fr: "Traduction", pt: "Tradução" },
  memhack_easy: { en: "Easy", es: "Fácil", fr: "Facile", pt: "Fácil" },
  memhack_medium: { en: "Medium", es: "Medio", fr: "Moyen", pt: "Médio" },
  memhack_hard: { en: "Hard", es: "Difícil", fr: "Difficile", pt: "Difícil" },
  memhack_progress: { en: "Progress: {studied}/{total} phrases in training", es: "Progreso: {studied}/{total} frases en entrenamiento", fr: "Progrès: {studied}/{total} phrases en entraînement", pt: "Progresso: {studied}/{total} frases em treino" },
  memhack_done: { en: "Done for now. Come back later!", es: "Completado por ahora. ¡Vuelve más tarde!", fr: "Terminé pour l'instant. Revenez plus tard!", pt: "Concluído por enquanto. Volte mais tarde!" },
  glossary_label: { en: "Glossary:", es: "Glosario:", fr: "Glossaire:", pt: "Glossário:" },
  login_title: { en: "JATEL IA", es: "JATEL IA", fr: "JATEL IA", pt: "JATEL IA" },
  login_subtitle: { en: "Restricted access — log in to continue", es: "Acceso restringido — inicia sesión para continuar", fr: "Accès restreint — connectez-vous pour continuer", pt: "Acesso restrito — faça login para continuar" },
  login_user_label: { en: "Username", es: "Usuario", fr: "Utilisateur", pt: "Usuário" },
  login_pass_label: { en: "Password", es: "Contraseña", fr: "Mot de passe", pt: "Senha" },
  login_btn: { en: "Login", es: "Entrar", fr: "Connexion", pt: "Entrar" },
  change_pass_title: { en: "Change password", es: "Cambiar contraseña", fr: "Changer mot de passe", pt: "Trocar senha" },
  cp_current_label: { en: "Current password", es: "Contraseña actual", fr: "Mot de passe actuel", pt: "Senha atual" },
  cp_new_label: { en: "New password", es: "Nueva contraseña", fr: "Nouveau mot de passe", pt: "Nova senha" },
  cp_confirm_label: { en: "Confirm new password", es: "Confirmar nueva contraseña", fr: "Confirmer nouveau mot de passe", pt: "Confirmar nova senha" },
  cp_current_placeholder: { en: "current password", es: "contraseña actual", fr: "mot de passe actuel", pt: "senha atual" },
  cp_new_placeholder: { en: "min. 4 characters", es: "mín. 4 caracteres", fr: "min. 4 caractères", pt: "mín. 4 caracteres" },
  cp_confirm_placeholder: { en: "repeat new password", es: "repite la nueva contraseña", fr: "répétez le nouveau mot de passe", pt: "repita a nova senha" },
  cp_save: { en: "Save", es: "Guardar", fr: "Enregistrer", pt: "Salvar" },
  cp_cancel: { en: "Cancel", es: "Cancelar", fr: "Annuler", pt: "Cancelar" },
  users_title: { en: "Manage users", es: "Gestionar usuarios", fr: "Gérer utilisateurs", pt: "Gerenciar usuários" },
  users_new_label: { en: "New user", es: "Nuevo usuario", fr: "Nouvel utilisateur", pt: "Novo usuário" },
  users_username_placeholder: { en: "username", es: "nombre de usuario", fr: "nom d'utilisateur", pt: "nome de usuário" },
  users_pass_label: { en: "Password", es: "Contraseña", fr: "Mot de passe", pt: "Senha" },
  users_pass_placeholder: { en: "min. 4 characters", es: "mín. 4 caracteres", fr: "min. 4 caractères", pt: "mín. 4 caracteres" },
  users_confirm_label: { en: "Confirm password", es: "Confirmar contraseña", fr: "Confirmer mot de passe", pt: "Confirmar senha" },
  users_confirm_placeholder: { en: "repeat password", es: "repite la contraseña", fr: "répétez le mot de passe", pt: "repita a senha" },
  users_create: { en: "Create user", es: "Crear usuario", fr: "Créer utilisateur", pt: "Criar usuário" },
  users_existing: { en: "Existing users", es: "Usuarios existentes", fr: "Utilisateurs existants", pt: "Usuários existentes" },
  users_close: { en: "Close", es: "Cerrar", fr: "Fermer", pt: "Fechar" },
  footer_copyright: { en: "Copyright © 2026 JATEL IA produced by Jefferson Santos", es: "Copyright © 2026 JATEL IA producido por Jefferson Santos", fr: "Copyright © 2026 JATEL IA produit par Jefferson Santos", pt: "Copyright © 2026 JATEL IA produzido por Jefferson Santos" },
  grammar_listen_label: { en: "Listen to sentence in {lang}", es: "Escuchar frase en {lang}", fr: "Écouter la phrase en {lang}", pt: "Ouvir frase em {lang}" },
  grammar_lang_en: { en: "English", es: "inglés", fr: "anglais", pt: "inglês" },
  grammar_lang_es: { en: "Spanish", es: "español", fr: "espagnol", pt: "espanhol" },
  grammar_lang_fr: { en: "French", es: "francés", fr: "français", pt: "francês" },
};

function __t(key, replacements = {}) {
  const lang = window.__lang || "pt";
  let text = TRANSLATIONS[key]?.[lang] || TRANSLATIONS[key]?.pt || key;
  for (const [k, v] of Object.entries(replacements)) {
    text = text.replace(`{${k}}`, v);
  }
  return text;
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (!key) return;
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = __t(key);
    } else {
      el.textContent = __t(key);
    }
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (key) el.placeholder = __t(key);
  });
  document.querySelectorAll("[data-i18n-title]").forEach(el => {
    const key = el.dataset.i18nTitle;
    if (key) el.title = __t(key);
  });
}
