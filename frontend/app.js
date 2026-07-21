const API = "";

const state = {
  level: "iniciante",
  persona: "cafe",
  voice: "",
  category: "all",
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
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
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
      body: JSON.stringify({ text, level: state.level, voice: state.voice }),
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
$("category").addEventListener("change", (e) => (state.category = e.target.value));

/* ---------- Vozes da IA ---------- */
(async () => {
  try {
    const data = await api("/api/voices");
    const sel = $("voice");
    sel.innerHTML = "";
    data.voices.forEach((v) => {
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = v.name;
      if (v.id === "en-US-JennyNeural") o.selected = true;
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
      body: JSON.stringify({ level: state.level, module: "listen", category: state.category }),
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
let mediaRecorder, chunks, mediaStream;
state.speakTranscript = "";
state.speakCorrection = "";

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
  $("speak-transcript").textContent = "Transcrição: " + text;
  $("speak-play-transcript").disabled = !text;
}

function setSpeakCorrection(text) {
  state.speakCorrection = text;
  $("speak-correction").textContent = "Correção:\n" + text;
  $("speak-play-correction").disabled = !text;
}

$("speak-rec").addEventListener("click", async () => {
  $("speak-rec").disabled = true;
  $("speak-rec").textContent = "🎤 Gravando...";
  $("speak-stop").disabled = false;
  try {
    await startRec(async (bytes, mime) => {
      $("speak-rec").disabled = false;
      $("speak-rec").textContent = "🎤 Gravar";
      $("speak-stop").disabled = true;
      const fd = new FormData();
      const ext = mime.includes("webm") ? "webm" : mime.includes("ogg") ? "ogg" : "wav";
      fd.append("file", new Blob([bytes], { type: mime }), "audio." + ext);
      try {
        const stt = await api("/api/stt", { method: "POST", body: fd });
        setSpeakTranscript(stt.transcript || "(audio vazio)");
        if (stt.transcript) {
          const corr = await api("/api/correct", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: stt.transcript, level: state.level }),
          });
          setSpeakCorrection(corr.correction);
        }
      } catch (e) {
        console.error("STT error:", e);
        $("speak-transcript").textContent = "🎤 (erro: " + (e.message || e) + ")\n(Digite abaixo para corrigir manualmente.)";
      }
    });
  } catch (e) {
    $("speak-rec").disabled = false;
    $("speak-rec").textContent = "🎤 Gravar";
    $("speak-stop").disabled = true;
    $("speak-transcript").textContent = "Erro microfone: " + e.message;
  }
});

$("speak-stop").addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  $("speak-rec").disabled = false;
  $("speak-rec").textContent = "🎤 Gravar";
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
      body: JSON.stringify({ text, level: state.level }),
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
      body: JSON.stringify({ text, level: state.level }),
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
      body: JSON.stringify({ level: state.level, module: "read", category: state.category }),
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
      body: JSON.stringify({ level: $("grammar-level").value }),
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
      btn.title = "Ouvir frase em inglês";
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
(async () => {
  try {
    const data = await api("/api/memhack/categories");
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
})();

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
      body: JSON.stringify({ category }),
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
    $("memhack-phrase").textContent = data.phrase.en;
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
  if (memhackCurrent) playTts(memhackCurrent.en);
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
      $("memhack-phrase").textContent = data.phrase.en;
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

$("conv-rec").addEventListener("click", async () => {
  $("conv-rec").disabled = true;
  $("conv-rec").textContent = "🎤 Gravando...";
  $("conv-stop").disabled = false;
  try {
    await startRec(async (bytes, mime) => {
      $("conv-rec").disabled = false;
      $("conv-rec").textContent = "🎤 Gravar";
      $("conv-stop").disabled = true;
      const fd = new FormData();
      const ext = mime.includes("webm") ? "webm" : mime.includes("ogg") ? "ogg" : "wav";
      fd.append("file", new Blob([bytes], { type: mime }), "audio." + ext);
      try {
        const stt = await api("/api/stt", { method: "POST", body: fd });
        if (stt.transcript) {
          addMsg("user", stt.transcript);
          await aiTurn(stt.transcript);
        } else {
          addMsg("user", "(STT: audio vazio ou inaudivel)");
        }
      } catch (e) {
        console.error("STT error:", e);
        addMsg("user", "🎤 (erro: " + (e.message || e) + ")");
      }
    });
  } catch (e) {
    $("conv-rec").disabled = false;
    $("conv-rec").textContent = "🎤 Gravar";
    $("conv-stop").disabled = true;
    addMsg("user", "(erro microfone: " + e.message + ")");
  }
});

$("conv-stop").addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  $("conv-rec").disabled = false;
  $("conv-rec").textContent = "🎤 Gravar";
  $("conv-stop").disabled = true;
});
