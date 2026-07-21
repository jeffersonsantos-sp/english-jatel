const API = "";

const state = {
  lang: "en",
  level: "iniciante",
  persona: "cafe",
  voice: "",
  listenText: "",
  history: [],
};

const $ = (id) => document.getElementById(id);

function showError(el, msg) {
  if (el) el.textContent = "⚠️ Erro: " + msg;
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

function browserSpeak(text) {
  try {
    const sttLang = { en: "en-US", es: "es-ES", fr: "fr-FR" }[state.lang] || "en-US";
    const u = new SpeechSynthesisUtterance(text);
    u.lang = sttLang;
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
      await p.catch(() => browserSpeak(text));
    }
  } catch (e) {
    console.warn("TTS backend indisponivel, usando voz do navegador:", e.message);
    browserSpeak(text);
  }
}

/* ---------- Tabs ---------- */
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $(btn.dataset.tab).classList.add("active");
  });
});

$("level").addEventListener("change", (e) => (state.level = e.target.value));
$("persona").addEventListener("change", (e) => (state.persona = e.target.value));

/* ---------- Vozes da IA ---------- */
async function loadVoices() {
  try {
    const data = await api("/api/voices?lang=" + state.lang);
    const sel = $("voice");
    sel.innerHTML = "";
    data.voices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = v.name;
      if (!sel.options.length) o.selected = true;
      sel.appendChild(o);
    });
    state.voice = sel.value;
  } catch (e) {
    console.warn("voices indisponivel:", e.message);
  }
}
loadVoices();
$("voice").addEventListener("change", (e) => (state.voice = e.target.value));

/* ---------- Idioma ---------- */
const savedLang = localStorage.getItem("jatel_lang");
if (savedLang) state.lang = savedLang;
$("lang").value = state.lang;
$("lang").addEventListener("change", (e) => {
  state.lang = e.target.value;
  localStorage.setItem("jatel_lang", state.lang);
  state.history = [];
  $("chat").innerHTML = "";
  loadVoices();
  // Recarregar conteudo dependente do idioma
  memhackLoadCategories();
  const activeTab = document.querySelector(".tab.active");
  if (activeTab && activeTab.dataset.tab === "grammar") loadGrammar();
});

/* ---------- MemHack carregar categorias (separado para recarga) ---------- */
async function memhackLoadCategories() {
  try {
    const data = await api("/api/memhack/categories?lang=" + state.lang);
    const sel = $("memhack-category");
    sel.innerHTML = "";
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

/* ---------- Health ---------- */
(async () => {
  try {
    const h = await api("/api/health");
    $("status").style.color = h.llm ? "#22c55e" : "#f59e0b";
    $("status").title = h.llm ? "LLM ativo" : "Modo demo (sem LLM)";
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
      body: JSON.stringify({ level: state.level, module: "listen", category: "all", lang: state.lang }),
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
  $("listen-sentence").classList.remove("hidden"); // revela apos corrigir
  $("listen-result").textContent =
    got === expected ? "✅ Acerto!" : `❌ Esperado:\n${expected}\n\nVocê:\n${got}`;
});

/* ---------- Speak ---------- */
let mediaRecorder, chunks;
state.speakTranscript = "";
state.speakCorrection = "";

async function startRec(onStop) {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
    blob.arrayBuffer().then((buf) => onStop(new Uint8Array(buf), blob.type));
    // Libera o microfone.
    if (mediaRecorder.stream) mediaRecorder.stream.getTracks().forEach((t) => t.stop());
  };
  mediaRecorder.start();
}

// Reconhecimento de voz do navegador (Web Speech API). Roda no cliente, sem
// depender do backend/Whisper — ideal para hospedagem com pouca RAM.
function getSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r = new SR();
  r.lang = { en: "en-US", es: "es-ES", fr: "fr-FR" }[state.lang] || "en-US";
  r.interimResults = false;
  r.maxAlternatives = 1;
  return r;
}

function setSpeakTranscript(text) {
  state.speakTranscript = text;
  $("speak-transcript").textContent = "Transcrição: " + text;
  $("speak-play-transcript").disabled = !text;
}

function setSpeakCorrection(text) {
  state.speakCorrection = text;
  $("speak-correction").textContent = "Correção:\n" + text;
  $("speak-play-correction").disabled = !text;
}

let speakRecognition = null;

async function speakHandleTranscript(text) {
  text = (text || "").trim();
  if (!text) return;
  setSpeakTranscript(text);
  try {
    const corr = await api("/api/correct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, level: state.level, lang: state.lang }),
    });
    setSpeakCorrection(corr.correction);
  } catch (e) {
    setSpeakCorrection("Erro ao corrigir: " + e.message);
  }
}

$("speak-rec").addEventListener("click", async () => {
  // 1) Preferencial: reconhecimento de voz do navegador (não usa backend).
  const rec = getSpeechRecognition();
  if (rec) {
    speakRecognition = rec;
    $("speak-rec").disabled = true;
    $("speak-stop").disabled = false;
    rec.onresult = (e) => speakHandleTranscript(e.results[0][0].transcript);
    rec.onerror = (e) => {
      const map = {
        "not-allowed": "permissão do microfone negada",
        "no-speech": "não detectei sua fala, tente de novo",
        "audio-capture": "microfone não encontrado",
      };
      $("speak-transcript").textContent = "⚠️ " + (map[e.error] || "erro no reconhecimento: " + e.error);
    };
    rec.onend = () => {
      $("speak-rec").disabled = false;
      $("speak-stop").disabled = true;
      speakRecognition = null;
    };
    try {
      rec.start();
    } catch (e) {
      $("speak-transcript").textContent = "⚠️ Não foi possível iniciar a gravação: " + e.message;
      rec.onend();
    }
    return;
  }
  // 2) Fallback: grava e envia para o backend (/api/stt).
  $("speak-rec").disabled = true;
  $("speak-stop").disabled = false;
  try {
    await startRec(async (bytes, mime) => {
      const fd = new FormData();
      const ext = mime.includes("webm") ? "webm" : mime.includes("ogg") ? "ogg" : "wav";
      fd.append("file", new Blob([bytes], { type: mime }), "audio." + ext);
      try {
        const stt = await api("/api/stt", { method: "POST", body: fd });
        await speakHandleTranscript(stt.transcript);
      } catch (e) {
        $("speak-transcript").textContent = "Transcrição indisponível no servidor: " + e.message + "\n(Digite abaixo para corrigir manualmente.)";
      }
    });
  } catch (e) {
    $("speak-transcript").textContent = "⚠️ Não consegui acessar o microfone: " + e.message;
    $("speak-rec").disabled = false;
    $("speak-stop").disabled = true;
  }
});

$("speak-stop").addEventListener("click", () => {
  if (speakRecognition) {
    speakRecognition.stop();
    return;
  }
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  $("speak-rec").disabled = false;
  $("speak-stop").disabled = true;
});

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
      body: JSON.stringify({ level: state.level, module: "read", category: "all", lang: state.lang }),
    });
    $("read-text").textContent = data.text;
    const g = Object.entries(data.glossary || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join("  |  ");
    $("read-glossary").textContent = "Glossário: " + g;
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
      body: JSON.stringify({ text, level: state.level, lang: state.lang }),
    });
    $("read-result").textContent = data.correction;
  } catch (e) {
    showError($("read-result"), e.message);
  }
});

/* ---------- Grammar (CEFR) ---------- */
(async () => {
  try {
    const data = await api("/api/grammar-levels");
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
      btn.title = "Ouvir frase em " + ({ en: "inglês", es: "espanhol", fr: "francês" }[state.lang] || "inglês");
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

/* ---------- MemHack (SRS) ---------- */
memhackLoadCategories();

let memhackCurrent = null;

async function memhackLoadNext() {
  const category = $("memhack-category").value;
  $("memhack-msg").textContent = "";
  $("memhack-pt").classList.add("hidden");
  $("memhack-pt").textContent = "";
  try {
    const data = await api("/api/memhack/next", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, lang: state.lang }),
    });
    memhackCurrent = data.done ? null : data.phrase;
    if (data.done) {
      $("memhack-progress").textContent = "";
      $("memhack-phrase").textContent = data.message || "Concluído por enquanto.";
      $("memhack-pt").textContent = "";
      document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = true));
      return;
    }
    document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = false));
    const targetKey = { en: "en", es: "es", fr: "fr" }[state.lang] || "en";
    $("memhack-phrase").textContent = data.phrase[targetKey];
    $("memhack-pt").textContent = data.phrase.pt;
    const studied = data.studied || 0;
    const total = data.total || 0;
    $("memhack-progress").textContent = `Progresso: ${studied}/${total} frases em treino`;
  } catch (e) {
    showError($("memhack-msg"), e.message);
  }
}

$("memhack-category").addEventListener("change", memhackLoadNext);
$("memhack-play").addEventListener("click", () => {
  if (memhackCurrent) {
    const targetKey = { en: "en", es: "es", fr: "fr" }[state.lang] || "en";
    playTts(memhackCurrent[targetKey]);
  }
});
$("memhack-reveal").addEventListener("click", () => {
  $("memhack-pt").classList.toggle("hidden");
});

document.querySelectorAll(".memhack-rating button").forEach((btn) => {
  btn.addEventListener("click", async () => {
    if (!memhackCurrent) return;
    const category = $("memhack-category").value;
    try {
      const data = await api("/api/memhack/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category,
          phrase_id: memhackCurrent.id,
          difficulty: btn.dataset.diff,
          lang: state.lang,
        }),
      });
      memhackCurrent = data.done ? null : data.phrase;
      if (data.done) {
        $("memhack-progress").textContent = "";
        $("memhack-phrase").textContent = data.message || "Concluído por enquanto.";
        $("memhack-pt").textContent = "";
        document.querySelectorAll(".memhack-rating button").forEach((b) => (b.disabled = true));
        $("memhack-msg").textContent = "⏱️ Revisão agendada. Volte mais tarde!";
        return;
      }
      $("memhack-pt").classList.add("hidden");
      const targetKey = { en: "en", es: "es", fr: "fr" }[state.lang] || "en";
      $("memhack-phrase").textContent = data.phrase[targetKey];
      $("memhack-pt").textContent = data.phrase.pt;
      const studied = data.studied || 0;
      const total = data.total || 0;
      $("memhack-progress").textContent = `Progresso: ${studied}/${total} frases em treino`;
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

$("conv-rec").addEventListener("click", async () => {
  // 1) Preferencial: reconhecimento de voz do navegador (não usa backend).
  const rec = getSpeechRecognition();
  if (rec) {
    convRecognition = rec;
    $("conv-rec").disabled = true;
    $("conv-stop").disabled = false;
    rec.continuous = true;
    let convAccum = "";
    rec.onresult = (e) => {
      const text = (e.results[0][0].transcript || "").trim();
      if (text) {
        convAccum += (convAccum ? " " : "") + text;
      }
    };
    rec.onerror = (e) => {
      const map = {
        "not-allowed": "permissão do microfone negada",
        "no-speech": "não detectei sua fala, tente de novo",
        "audio-capture": "microfone não encontrado",
      };
      addMsg("ai", "⚠️ " + (map[e.error] || "erro no reconhecimento de voz: " + e.error));
    };
    rec.onend = () => {
      $("conv-rec").disabled = false;
      $("conv-stop").disabled = true;
      convRecognition = null;
      const finalText = convAccum.trim();
      convAccum = "";
      if (finalText) {
        addMsg("user", finalText);
        aiTurn(finalText);
      }
    };
    try {
      rec.start();
    } catch (e) {
      addMsg("ai", "⚠️ Não foi possível iniciar a gravação: " + e.message);
      rec.onend();
    }
    return;
  }
  // 2) Fallback: grava e envia para o backend (/api/stt).
  $("conv-rec").disabled = true;
  $("conv-stop").disabled = false;
  try {
    await startRec(async (bytes, mime) => {
      const fd = new FormData();
      const ext = mime.includes("webm") ? "webm" : mime.includes("ogg") ? "ogg" : "wav";
      fd.append("file", new Blob([bytes], { type: mime }), "audio." + ext);
      try {
        const stt = await api("/api/stt", { method: "POST", body: fd });
        addMsg("user", stt.transcript);
        await aiTurn(stt.transcript);
      } catch (e) {
        addMsg("ai", "⚠️ Transcrição indisponível no servidor: " + e.message);
      }
    });
  } catch (e) {
    addMsg("ai", "⚠️ Não consegui acessar o microfone: " + e.message);
    $("conv-rec").disabled = false;
    $("conv-stop").disabled = true;
  }
});

$("conv-stop").addEventListener("click", () => {
  if (convRecognition) {
    convRecognition.stop();
    return;
  }
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  $("conv-rec").disabled = false;
  $("conv-stop").disabled = true;
});
