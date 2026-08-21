const API = "/app";

const state = {
  lang: "en",
  level: "iniciante",
  persona: "cafe",
  voice: "",
  category: "all",
  listenText: "",
  history: [],
};
window.state = state;

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  const langSel = $("lang");
  if (langSel) langSel.className = "lang-" + state.lang;
});

function showError(el, msg) {
  if (el) el.textContent = "⚠️ " + (typeof t === "function" ? t("err-mic", { msg }) : "Erro: " + msg);
  console.error(msg);
}

async function api(path, opts) {
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function browserSpeak(text, lang) {
  try {
    const u = new SpeechSynthesisUtterance(text);
    const langMap = { es: "es-ES", fr: "fr-FR" };
    u.lang = langMap[lang] || "en-US";
    u.rate = 0.95;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  } catch (e) {
    console.warn("speechSynthesis indisponivel:", e);
  }
}

let ttsAudio = null;
async function playTts(text) {
  if (!text) return;
  try {
    const data = await api("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, level: state.level, voice: state.voice, lang: state.lang }),
    });
    if (!ttsAudio) ttsAudio = new Audio();
    ttsAudio.pause();
    ttsAudio.src = "data:audio/" + data.format + ";base64," + data.audio_b64;
    ttsAudio.load();
    const p = ttsAudio.play();
    if (p && typeof p.catch === "function") {
      await p.catch(() => browserSpeak(text, state.lang));
    }
  } catch (e) {
    console.warn("TTS backend indisponivel, usando voz do navegador:", e.message);
    browserSpeak(text, state.lang);
  }
}

/* ---------- Sidebar Navigation ---------- */
document.querySelectorAll(".sidebar-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sidebar-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $(btn.dataset.tab).classList.add("active");
  });
});

$("lang").addEventListener("change", async (e) => {
  state.lang = e.target.value;
  const langSel = $("lang");
  langSel.className = "lang-" + state.lang;
  if (typeof applyI18n === "function") applyI18n();
  try {
    await api("/api/set-lang", { method: "POST", body: JSON.stringify({ lang: state.lang }) });
  } catch (err) {
    console.warn("Lang set error:", err);
  }
  try {
    const data = await api("/api/voices?lang=" + encodeURIComponent(state.lang));
    const sel = $("voice");
    sel.innerHTML = "";
    data.voices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = v.name;
      sel.appendChild(o);
    });
    state.voice = sel.value;
  } catch (_) {}
  await loadMemhackCategories();
  await loadCalendarNumbers();
});

/* ---------- Vozes da IA ---------- */
(async () => {
  try {
    const lang = state.lang;
    const data = await api("/api/voices?lang=" + encodeURIComponent(lang));
    const sel = $("voice");
    sel.innerHTML = "";
    data.voices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = v.name;
      if (v.id === (lang === "es" ? "es-ES-ElviraNeural" : lang === "fr" ? "fr-FR-DeniseNeural" : "en-US-JennyNeural")) o.selected = true;
      sel.appendChild(o);
    });
    state.voice = sel.value;
  } catch (e) {
    console.warn("voices indisponivel:", e.message);
  }
})();
$("voice").addEventListener("change", (e) => (state.voice = e.target.value));

/* ---------- Health ---------- */
(async () => {
  try {
    const h = await api("/api/health");
    $("status").style.color = h.llm ? "#22c55e" : "#f59e0b";
    $("status").title = h.llm ? (typeof t === "function" ? t("status-active") : "LLM ativo") : (typeof t === "function" ? t("status-demo") : "Modo demo (sem LLM)");
  } catch {
    $("status").style.color = "#ef4444";
  }
})();

/* ---------- Listen ---------- */
function flashPlaying(btn, on) {
  if (!btn) return;
  btn.classList.toggle("playing", on);
}

$("listen-play").addEventListener("click", async () => {
  const btn = $("listen-play");
  flashPlaying(btn, true);
  try {
    const data = await api("/api/content", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: state.level, module: "listen", category: state.category, lang: state.lang }),
    });
    state.listenText = data.text;
    $("listen-sentence").textContent = data.text;
    $("listen-sentence").classList.add("hidden"); // escondida ate verificar
    $("listen-repeat").disabled = false;
    await playTts(data.text);
  } catch (e) {
    showError($("listen-result"), e.message);
  } finally {
    flashPlaying(btn, false);
  }
});

$("listen-repeat").addEventListener("click", async () => {
  if (!state.listenText) return;
  const btn = $("listen-repeat");
  flashPlaying(btn, true);
  try {
    await playTts(state.listenText);
  } catch (e) {
    showError($("listen-result"), e.message);
  } finally {
    flashPlaying(btn, false);
  }
});

function loadListen() {
  $("listen-answer").value = "";
  $("listen-result").textContent = "";
  $("listen-play").click();
}
$("listen-next").addEventListener("click", loadListen);

$("listen-check").addEventListener("click", () => {
  const expected = (state.listenText || "").trim().toLowerCase();
  const got = $("listen-answer").value.trim().toLowerCase();
  $("listen-sentence").classList.remove("hidden");
  if (got === expected) {
    $("listen-result").textContent = typeof t === "function" ? t("listen-correct") : "✅ Acerto!";
  } else {
    $("listen-result").textContent = (typeof t === "function" ? t("listen-wrong", { expected, got }) : `❌ Esperado:\n${expected}\n\nVocê:\n${got}`);
  }
});

/* ---------- Speak ---------- */
let mediaRecorder, chunks, mediaStream;
let speakRecognition = null;
let speakSafetyTimer = null;
state.speakTranscript = "";

function speakStopRecording() {
  if (speakSafetyTimer) { clearTimeout(speakSafetyTimer); speakSafetyTimer = null; }
  if (speakRecognition) {
    try { speakRecognition.stop(); } catch (_) {}
    speakRecognition = null;
  }
  if (mediaRecorder && mediaRecorder.state === "recording") {
    try { mediaRecorder.stop(); } catch (_) {}
  }
  $("speak-rec").disabled = false;
  $("speak-rec").textContent = typeof t === "function" ? "🎤 " + t("speak-rec") : "🎤 Gravar";
  $("speak-stop").disabled = true;
}state.speakCorrection = "";

async function startBackendSTT() {
  $("speak-rec").disabled = true;
  $("speak-rec").textContent = typeof t === "function" ? "🎤 " + t("speak-recording") : "🎤 Gravando...";
  $("speak-stop").disabled = false;
  try {
    await startRec(async (bytes, mime) => {
      $("speak-rec").disabled = false;
      $("speak-rec").textContent = typeof t === "function" ? "🎤 " + t("speak-rec") : "🎤 Gravar";
      $("speak-stop").disabled = true;
      const fd = new FormData();
      const ext = mime.includes("webm") ? "webm" : mime.includes("ogg") ? "ogg" : "wav";
      fd.append("file", new Blob([bytes], { type: mime }), "audio." + ext);
      fd.append("lang", state.lang);
      try {
        const stt = await api("/api/stt", { method: "POST", body: fd });
        setSpeakTranscript(stt.transcript || (typeof t === "function" ? t("err-stt-empty") : "(audio vazio)"));
        if (stt.transcript) {
          const corr = await api("/api/correct", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: stt.transcript, level: state.level, lang: state.lang }),
          });
          setSpeakCorrection(corr.correction);
        }
      } catch (e) {
        console.error("STT error:", e);
        $("speak-transcript").textContent = "🎤 (" + (typeof t === "function" ? t("err-stt-network") : "erro") + ": " + (e.message || e) + ")\n(" + (typeof t === "function" ? t("speak-label") : "Digite abaixo para corrigir manualmente.") + ")";
      }
    });
  } catch (e) {
    $("speak-rec").disabled = false;
    $("speak-rec").textContent = typeof t === "function" ? "🎤 " + t("speak-rec") : "🎤 Gravar";
    $("speak-stop").disabled = true;
    $("speak-transcript").textContent = typeof t === "function" ? t("err-mic", { msg: e.message }) : "Erro microfone: " + e.message;
  }
}

// Reconhecimento de voz do navegador (Web Speech API). Roda no cliente, sem
// depender do backend/ffmpeg/whisper.
function getSpeechRecognition(lang) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r = new SR();
  r.lang = lang === "es" ? "es-ES" : lang === "fr" ? "fr-FR" : "en-US";
  r.interimResults = false;
  r.maxAlternatives = 1;
  return r;
}

async function startRec(onStop) {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
    ? "audio/webm;codecs=opus"
    : MediaRecorder.isTypeSupported("audio/webm")
    ? "audio/webm"
    : "audio/ogg;codecs=opus";
  mediaRecorder = new MediaRecorder(mediaStream, mime ? { mimeType: mime } : undefined);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunks.push(e.data);
  };
  mediaRecorder.onstop = () => {
    if (mediaStream) mediaStream.getTracks().forEach((t) => t.stop());
    if (chunks.length === 0) return;
    const blob = new Blob(chunks, { type: mediaRecorder.mimeType || "audio/webm" });
    blob.arrayBuffer().then((buf) => onStop(new Uint8Array(buf), blob.type));
  };
  mediaRecorder.start();
}

function setSpeakTranscript(text) {
  state.speakTranscript = text;
  $("speak-transcript").textContent = (typeof t === "function" ? t("transcript-label") : "Transcrição: ") + text;
  $("speak-play-transcript").disabled = !text;
}

function setSpeakCorrection(text) {
  state.speakCorrection = text;
  $("speak-correction").textContent = (typeof t === "function" ? t("correction-label") : "Correção:\n") + text;
  $("speak-play-correction").disabled = !text;
}

$("speak-rec").addEventListener("click", async () => {
  // 1) Preferencial: Web Speech API do navegador
  const rec = getSpeechRecognition(state.lang);
  if (rec) {
    speakRecognition = rec;
    $("speak-rec").disabled = true;
    $("speak-rec").textContent = typeof t === "function" ? "🎤 " + t("speak-recording") : "🎤 Gravando...";
    $("speak-stop").disabled = false;
    rec.onresult = (e) => {
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const text = (e.results[i][0].transcript || "").trim();
        if (text && e.results[i].isFinal) setSpeakTranscript(text);
      }
    };
    rec.onerror = (e) => {
      if (e.error === "network") {
        speakStopRecording();
        startBackendSTT();
        return;
      }
      const errMap = {
        "not-allowed": typeof t === "function" ? t("err-mic-not-allowed") : "permissão do microfone negada",
        "no-speech": typeof t === "function" ? t("err-no-speech") : "não detectei sua fala",
        "audio-capture": typeof t === "function" ? t("err-audio-capture") : "microfone não encontrado",
      };
      $("speak-transcript").textContent = "⚠️ " + (errMap[e.error] || (typeof t === "function" ? t("err-mic", { msg: e.error }) : "erro: " + e.error));
      speakStopRecording();
    };
    rec.onend = async () => {
      speakStopRecording();
      const text = state.speakTranscript;
      if (text) {
        try {
          const corr = await api("/api/correct", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, level: state.level }),
          });
          setSpeakCorrection(corr.correction);
        } catch (e) {
          $("speak-correction").textContent = "⚠️ " + e.message;
        }
      }
    };
    speakSafetyTimer = setTimeout(() => {
      $("speak-transcript").textContent = "⚠️ " + (typeof t === "function" ? t("err-recording-timeout") : "Gravação cancelada (limite de 30s).");
      speakStopRecording();
    }, 30000);
    try { rec.start(); } catch (e) {
      $("speak-transcript").textContent = "⚠️ " + (typeof t === "function" ? t("err-recording", { msg: e.message }) : e.message);
      speakStopRecording();
      startBackendSTT();
    }
    return;
  }
  // 2) Fallback: grava e envia para o backend (/api/stt).
  startBackendSTT();
});

$("speak-stop").addEventListener("click", speakStopRecording);

$("speak-play-transcript").addEventListener("click", async () => {
  if (state.speakTranscript) await playTts(state.speakTranscript);
});

$("speak-play-correction").addEventListener("click", async () => {
  if (state.speakCorrection) await playTts(state.speakCorrection);
});

$("speak-correct-text").addEventListener("click", async () => {
  const text = $("speak-text").value.trim();
  if (!text) return;
  try {
    const corr = await api("/api/correct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, level: state.level, lang: state.lang }),
    });
    setSpeakCorrection(corr.correction);
  } catch (e) {
    showError($("speak-correction"), e.message);
  }
});

/* ---------- Write ---------- */
$("write-check").addEventListener("click", async () => {
  const text = $("write-text").value.trim();
  if (!text) return;
  try {
    const data = await api("/api/correct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, level: state.level, lang: state.lang }),
    });
    $("write-result").textContent = data.correction;
  } catch (e) {
    showError($("write-result"), e.message);
  }
});

/* ---------- Read ---------- */
$("read-load").addEventListener("click", async () => {
  try {
    const data = await api("/api/content", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: state.level, module: "read", category: state.category, lang: state.lang }),
    });
    $("read-text").textContent = data.text;
    const g = Object.entries(data.glossary || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join("  |  ");
    $("read-glossary").textContent = (typeof t === "function" ? t("glossary-label") : "Glossário: ") + g;
  } catch (e) {
    showError($("read-glossary"), e.message);
  }
});

$("read-next").addEventListener("click", () => $("read-load").click());

$("read-check").addEventListener("click", async () => {
  const text = $("read-answer").value.trim();
  if (!text) return;
  try {
    const data = await api("/api/correct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, level: state.level }),
    });
    $("read-result").textContent = data.correction;
  } catch (e) {
    showError($("read-result"), e.message);
  }
});

/* ---------- Grammar (CEFR) ---------- */
(async () => {
  try {
    const lang = state.lang;
    const data = await api("/api/grammar-levels?lang=" + encodeURIComponent(lang));
    const sel = $("grammar-level");
    sel.innerHTML = "";
    data.levels.forEach((lv) => {
      const o = document.createElement("option");
      o.value = lv;
      o.textContent = lv;
      sel.appendChild(o);
    });
  } catch (e) {
    console.warn("grammar-levels indisponivel:", e.message);
  }
})();

function grammarEnglishPart(example) {
  return example.split(" — ")[0].trim();
}

async function loadGrammar() {
  $("grammar-result").textContent = "";
  try {
    const data = await api("/api/grammar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: $("grammar-level").value, lang: state.lang }),
    });
    $("grammar-topic").textContent = data.topic || "";
    $("grammar-structure").textContent = data.structure || "";
    $("grammar-explanation").textContent = data.explanation || "";
    const list = $("grammar-examples");
    list.innerHTML = "";
    (data.examples || []).forEach((ex) => {
      const li = document.createElement("li");
      const span = document.createElement("span");
      span.textContent = ex;
      const btn = document.createElement("button");
      btn.className = "btn ghost grammar-play";
      btn.textContent = "🔊";
      btn.title = typeof t === "function" ? t("speak-play-transcript") : "Ouvir frase em ingles";
      btn.addEventListener("click", () => playTts(grammarEnglishPart(ex)));
      li.appendChild(span);
      li.appendChild(btn);
      list.appendChild(li);
    });
  } catch (e) {
    showError($("grammar-result"), e.message);
  }
}

$("grammar-load").addEventListener("click", loadGrammar);
$("grammar-next").addEventListener("click", loadGrammar);
$("grammar-level").addEventListener("change", loadGrammar);

async function loadMemhackCategories() {
  const lang = state.lang;
  const sel = $("memhack-category");
  sel.innerHTML = "";
  try {
    const data = await api("/api/memhack/categories?lang=" + encodeURIComponent(lang));
    data.categories.forEach((c) => {
      const o = document.createElement("option");
      o.value = c.id;
      o.textContent = c.label;
      sel.appendChild(o);
    });
    memhackLoadNext();
  } catch (e) {
    console.warn("memhack/categories indisponivel:", e.message);
  }
}

/* ---------- MemHack (SRS) ---------- */
(async () => {
  await loadMemhackCategories();
})();

let memhackCurrent = null;

async function memhackLoadNext() {
  const category = $("memhack-category").value;
  const lang = state.lang;
  $("memhack-msg").textContent = "";
  $("memhack-pt").classList.add("hidden");
  $("memhack-pt").textContent = "";
  try {
    const data = await api("/api/memhack/next", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, lang }),
    });
    memhackCurrent = data.done ? null : data.phrase;
    if (data.done) {
      $("memhack-progress").textContent = "";
      $("memhack-phrase").textContent = data.message || (typeof t === "function" ? t("memhack-done") : "Concluido por enquanto.");
      $("memhack-pt").textContent = "";
      document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = true));
      return;
    }
    document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = false));
     $("memhack-phrase").textContent = data.phrase[lang];
     $("memhack-pt").textContent = data.phrase.pt;
    const studied = data.studied || 0;
    const total = data.total || 0;
    $("memhack-progress").textContent = typeof t === "function" ? t("progress-label", { studied, total }) : `Progresso: ${studied}/${total} frases em treino`;
  } catch (e) {
    showError($("memhack-msg"), e.message);
  }
}

$("memhack-category").addEventListener("change", memhackLoadNext);
$("memhack-play").addEventListener("click", () => {
  if (memhackCurrent) playTts(memhackCurrent[state.lang]);
});
$("memhack-reveal").addEventListener("click", () => {
  $("memhack-pt").classList.toggle("hidden");
});

document.querySelectorAll(".memhack-rating button").forEach((btn) => {
  btn.addEventListener("click", async () => {
    if (!memhackCurrent) return;
    const category = $("memhack-category").value;
    const lang = state.lang;
    try {
      const data = await api("/api/memhack/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category,
          phrase_id: memhackCurrent.id,
          difficulty: btn.dataset.diff,
          lang,
        }),
      });
      memhackCurrent = data.done ? null : data.phrase;
      if (data.done) {
        $("memhack-progress").textContent = "";
        $("memhack-phrase").textContent = data.message || (typeof t === "function" ? t("memhack-done") : "Concluido por enquanto.");
        $("memhack-pt").textContent = "";
        document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = true));
        $("memhack-msg").textContent = typeof t === "function" ? t("memhack-scheduled") : "⏱ Revisao agendada. Volte mais tarde!";
        return;
      }
       $("memhack-pt").classList.add("hidden");
       $("memhack-phrase").textContent = data.phrase[lang];
       $("memhack-pt").textContent = data.phrase.pt;
       const studied = data.studied || 0;
       const total = data.total || 0;
       $("memhack-progress").textContent = typeof t === "function" ? t("progress-label", { studied, total }) : `Progresso: ${studied}/${total} frases em treino`;
     } catch (e) {
      showError($("memhack-msg"), e.message);
    }
  });
});

/* ---------- Converse ---------- */
function addMsg(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  $("chat").appendChild(div);
  $("chat").scrollTop = $("chat").scrollHeight;
}

function clearChat() {
  $("chat").innerHTML = "";
  state.history = [];
}

$("persona").addEventListener("change", (e) => {
  state.persona = e.target.value;
  clearChat();
});

async function aiTurn(message) {
  try {
    const data = await api("/api/converse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        level: state.level,
        persona: state.persona,
        history: state.history,
        message,
        lang: state.lang,
      }),
    });
    state.history.push({ role: "user", content: message });
    state.history.push({ role: "assistant", content: data.reply });
    addMsg("ai", data.reply);
    await playTts(data.reply);
  } catch (e) {
    addMsg("ai", "⚠️ Erro: " + e.message);
  }
}

$("conv-ai-start").addEventListener("click", () => aiTurn("start"));

$("conv-send").addEventListener("click", () => {
  const text = $("conv-text").value.trim();
  if (!text) return;
  addMsg("user", text);
  $("conv-text").value = "";
  aiTurn(text);
});

let convRecognition = null;
let convSafetyTimer = null;

function convStopRecording() {
  if (convSafetyTimer) { clearTimeout(convSafetyTimer); convSafetyTimer = null; }
  if (convRecognition) {
    try { convRecognition.stop(); } catch (_) {}
    convRecognition = null;
  }
  if (mediaRecorder && mediaRecorder.state === "recording") {
    try { mediaRecorder.stop(); } catch (_) {}
  }
  $("conv-rec").disabled = false;
  $("conv-rec").textContent = typeof t === "function" ? "🎤 " + t("converse-rec") : "🎤 Gravar";
  $("conv-stop").disabled = true;
}

$("conv-rec").addEventListener("click", async () => {
  // 1) Preferencial: Web Speech API do navegador (não usa backend).
  const rec = getSpeechRecognition(state.lang);
  if (rec) {
    convRecognition = rec;
    $("conv-rec").disabled = true;
    $("conv-rec").textContent = typeof t === "function" ? "🎤 " + t("converse-recording") : "🎤 Gravando...";
    $("conv-stop").disabled = false;
    let convAccum = "";
    rec.onresult = (e) => {
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const text = (e.results[i][0].transcript || "").trim();
        if (text && e.results[i].isFinal) convAccum += (convAccum ? " " : "") + text;
      }
    };
    rec.onerror = (e) => {
      if (e.error === "network") {
        convStopRecording();
        startBackendSTT();
        return;
      }
      const map = {
        "not-allowed": typeof t === "function" ? t("err-mic-not-allowed") : "permissão do microfone negada",
        "no-speech": typeof t === "function" ? t("err-no-speech") : "não detectei sua fala, tente de novo",
        "audio-capture": typeof t === "function" ? t("err-audio-capture") : "microfone não encontrado",
      };
      addMsg("ai", "⚠️ " + (map[e.error] || e.error));
      convStopRecording();
    };
    rec.onend = () => {
      convStopRecording();
      const finalText = convAccum.trim();
      convAccum = "";
      if (finalText) {
        addMsg("user", finalText);
        aiTurn(finalText);
      }
    };
    convSafetyTimer = setTimeout(() => {
      addMsg("ai", "⚠️ " + (typeof t === "function" ? t("err-recording-cancelled") : "Gravação cancelada (limite de 30s). Tente novamente."));
      convStopRecording();
    }, 30000);
    try { rec.start(); } catch (e) {
      addMsg("ai", "⚠️ " + (typeof t === "function" ? t("err-recording", { msg: e.message }) : "Não foi possível iniciar a gravação: " + e.message));
      convStopRecording();
      startBackendSTT();
    }
    return;
  }
  // 2) Fallback: grava e envia para o backend (/api/stt).
  startBackendSTT();
});

$("conv-stop").addEventListener("click", convStopRecording);

/* ---------- Apply i18n on load ---------- */
if (typeof applyI18n === "function") applyI18n();

/* ---------- Numbers (Calendar & Numbers) ---------- */
let calendarData = {};

async function loadCalendarNumbers() {
  try {
    const data = await api("/api/calendar-numbers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: state.lang, section: "all" }),
    });
    calendarData = data;
    renderCalendarSection("numbers");
    renderCalendarSection("ordinals");
    renderCalendarSection("months");
    renderCalendarSection("days");
  } catch (e) {
    console.warn("Numbers load error:", e.message);
  }
}

function renderCalendarSection(section) {
  const container = $(section + "-grid");
  if (!container || !calendarData[section]) return;
  const items = calendarData[section].items || [];
  container.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "calendar-card";
    let word = item.word;
    let extra = "";
    if (section === "numbers") {
      extra = `<span class="calendar-value">${item.value}</span>`;
    } else if (section === "ordinals") {
      extra = `<span class="calendar-value">${item.ordinal}</span>`;
    } else if (section === "months") {
      extra = `<span class="calendar-value">${item.abbreviation || ""}</span>`;
    } else if (section === "days") {
      extra = `<span class="calendar-value">${item.abbreviation || ""}</span>`;
    }
    card.innerHTML = `
      <div class="calendar-word">${word}</div>
      <div class="calendar-pronunciation">${item[" pronunciation"] || ""}</div>
      ${extra}
      <button class="btn ghost calendar-speak" data-text="${word}">🔊</button>
    `;
    container.appendChild(card);
  });
  container.querySelectorAll(".calendar-speak").forEach((btn) => {
    btn.addEventListener("click", () => playTts(btn.dataset.text));
  });
}

document.querySelectorAll(".sub-tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sub-tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".subtab-content").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $("subtab-" + btn.dataset.subtab).classList.add("active");
  });
});

loadCalendarNumbers();
