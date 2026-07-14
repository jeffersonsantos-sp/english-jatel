#!/usr/bin/env python3
"""english-flow: app de ensino de ingles (listen/speak/write/read + conversacao IA).

Modo demo: roda sem API keys (texto + correcao heuristica).
Com OPENAI_API_KEY: usa LLM para correcao/conversa, TTS openai e Whisper para fala.
"""

import os
import re
import sys
from typing import List, Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LEVELS = ["iniciante", "intermediario", "avancado"]

CONTENT = {
    "iniciante": {
        "listen": "Hello, my name is Anna and I like coffee.",
        "read": "Tom is a student. He lives in Brazil. He studies English every day.",
        "glossary": {"student": "estudante", "lives": "vive/mora", "studies": "estuda"},
    },
    "intermediario": {
        "listen": "Although it was raining, we decided to walk to the museum.",
        "read": "She has been working remotely since the pandemic started, which changed her routine.",
        "glossary": {"remotely": "remotamente", "routine": "rotina", "pandemic": "pandemica"},
    },
    "avancado": {
        "listen": "Notwithstanding the complexities, the negotiation yielded a mutually beneficial outcome.",
        "read": "The proliferation of automation has precipitated a paradigm shift in labor markets worldwide.",
        "glossary": {"proliferation": "proliferacao", "precipitated": "precipitou", "paradigm": "paradigma"},
    },
}


def get_level() -> str:
    print("Escolha o nivel:", ", ".join(LEVELS))
    lv = input("> ").strip().lower()
    return lv if lv in LEVELS else "iniciante"


def llm_correct(text: str, level: str) -> str:
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            prompt = (
                f"Voce e um professor de ingles. Corrija o texto abaixo (nivel {level}). "
                f"Formato: ERRO -> CORRECAO -> REGRA -> SUGESTAO.\n\n{text}"
            )
            r = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM indisponivel: {e}]\n" + heuristic_correct(text)
    return heuristic_correct(text)


def heuristic_correct(text: str) -> str:
    fixes = []
    t = text
    if re.search(r"\bi am\b", t, re.I) and re.search(r"\bhe (am|are)\b", t, re.I):
        fixes.append("ERRO -> 'he am/are' | CORRECAO -> 'he is' | REGRA -> 3a pessoa singular usa 'is' | SUGESTAO -> 'He is a student.'")
    if re.search(r"\bhave went\b", t, re.I):
        fixes.append("ERRO -> 'have went' | CORRECAO -> 'have gone' | REGRA -> particípio de 'go' e 'gone' | SUGESTAO -> 'I have gone home.'")
    m = re.match(r"\b(he|she|it)\s+([a-z]+)\b", t, re.I)
    if m and m.group(2) not in {"is", "was", "has", "does", "goes", "likes", "lives", "studies"}:
        third = "goes" if m.group(2) == "go" else m.group(2) + "s"
        fixes.append(f"ERRO -> '{m.group(1)} {m.group(2)}' | CORRECAO -> '{m.group(1)} {third}' | REGRA -> 3a pessoa singular leva -s (go->goes) | SUGESTAO -> '{m.group(1)} {third}.'")
    if not fixes:
        fixes.append("Sem erros gramaticais obvios detectados (correcao heuristica limitada).")
    return "\n".join(fixes)


def speak_text(text: str) -> None:
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            r = client.audio.speech.create(model="tts-1", voice="nova", input=text)
            import tempfile, subprocess, pathlib
            p = pathlib.Path(tempfile.mktemp(suffix=".mp3"))
            p.write_bytes(r.content)
            subprocess.run(["xdg-open", str(p)], stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
    try:
        import pyttsx3
        pyttsx3.speak(text)
        return
    except Exception:
        pass
    print(f"[TTS] {text}")


def listen_input(prompt: str = "Voce: ") -> str:
    if OPENAI_API_KEY and os.getenv("USE_WHISPER"):
        try:
            import whisper, tempfile, sounddevice, scipy.io.wavfile
            print("(gravando 5s...)")
            fs = 16000
            rec = sounddevice.rec(int(5 * fs), samplerate=fs, channels=1)
            sounddevice.wait()
            tmp = tempfile.mktemp(suffix=".wav")
            scipy.io.wavfile.write(tmp, fs, rec)
            model = whisper.load_model("base")
            return model.transcribe(tmp)["text"].strip()
        except Exception as e:
            print(f"[Whisper indisponivel: {e}] digite o texto.")
    return input(prompt).strip()


def mod_listen(level: str) -> None:
    sent = CONTENT[level]["listen"]
    print(f"\n[Listen] Ouça a frase (nivel {level}):")
    speak_text(sent)
    ans = input("Digite o que ouviu (ditado): ").strip()
    ok = ans.lower() == sent.lower()
    print("Resultado:", "ACERTO" if ok else f"Esperado: {sent}\nVoce: {ans}")


def mod_speak(level: str) -> None:
    print(f"\n[Speak] Responda em ingles (nivel {level}):")
    q = "Tell me about your last weekend."
    print("Pergunta:", q)
    ans = listen_input("Sua resposta: ")
    print("\nTranscricao:", ans)
    print("\nCorrecao:\n", llm_correct(ans, level))


def mod_write(level: str) -> None:
    print(f"\n[Write] Escreva um paragrafo em ingles (nivel {level}):")
    text = input("Seu texto: ").strip()
    print("\nCorrecao:\n", llm_correct(text, level))


def mod_read(level: str) -> None:
    data = CONTENT[level]
    print(f"\n[Read] Leia o texto (nivel {level}):\n{data['read']}")
    print("\nGlossario:", data["glossary"])
    q = input("Pergunta de compreensao (responda em ingles): ").strip()
    print("\nCorrecao:\n", llm_correct(q, level))


def mod_converse(level: str) -> None:
    print(f"\n[Converse] Conversa com a IA (nivel {level}). 'sair' encerra.")
    personas = {"1": "entrevistador de emprego", "2": "amigo tomando cafe", "3": "colega de negocios"}
    print("Persona:", ", ".join(f"{k}={v}" for k, v in personas.items()))
    persona = personas.get(input("> ").strip(), "amigo tomando cafe")
    history = [{"role": "system", "content": f"Voce e um professor de ingles atuando como {persona}. Converse em ingles (nivel {level}), reaja, faca perguntas e corrija erros do aluno."}]
    while True:
        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
                ai = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=history).choices[0].message.content.strip()
            except Exception as e:
                ai = f"[LLM indisponivel: {e}] How are you today?"
        else:
            ai = "Hello! Tell me something about yourself."
        print("\nIA:", ai)
        speak_text(ai)
        history.append({"role": "assistant", "content": ai})
        user = listen_input("Voce: ")
        if user.lower() in {"sair", "exit", "quit"}:
            break
        history.append({"role": "user", "content": user})


MENU = {
    "1": ("Listen", mod_listen),
    "2": ("Speak", mod_speak),
    "3": ("Write", mod_write),
    "4": ("Read", mod_read),
    "5": ("Conversar com IA", mod_converse),
}


def main() -> None:
    print("=== English Flow ===")
    if not OPENAI_API_KEY:
        print("(modo demo: sem OPENAI_API_KEY, correcao heuristica + TTS opcional)\n")
    level = get_level()
    while True:
        print("\nModulos: 1 Listen | 2 Speak | 3 Write | 4 Read | 5 Conversar | 0 Sair")
        choice = input("> ").strip()
        if choice == "0":
            break
        if choice in MENU:
            MENU[choice][1](level)
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
