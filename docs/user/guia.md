# Guia do Usuário — JATEL-IA

Aplicativo web para treinar **inglês, espanhol, francês, italiano e alemão** nas habilidades
**Listen, Pronunciation, Write, Read** e **Conversar**, mais **Grammar** (gramática por
nível CEFR), **MemHack** (memorização com repetição espaçada) e **Numbers** (números,
ordinais, meses, dias da semana), com correção automática e conversação por IA.
Selecione o idioma na sidebar — toda a interface é traduzida.

## Acesso

1. No terminal, na pasta `backend`:
   ```bash
   pip install -r requirements.txt
   python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
2. Abra **http://localhost:8000** no navegador (Chrome recomendado para voz).
3. Faça login: `admin` / `mudar123`

> O backend serve tanto a API quanto a interface, num único endereço.

## Controles da sidebar

- **Nível**: Iniciante / Intermediário / Avançado — ajusta a dificuldade das frases e textos.
- **Voz da IA**: escolhe a voz neural do Edge TTS (ex.: Jenny feminina, Guy masculina).
- **Idioma**: 🇺🇸 Inglês / 🇪🇸 Espanhol / 🇫🇷 Francês / 🇮🇹 Italiano / 🇩🇪 Alemão — troca todo o conteúdo E a interface.

## Módulos

### Listen (ditado)
1. Clique **🔊 Ouvir frase** — a IA fala a frase (áudio), mas o texto **fica oculto**.
2. Digite no campo "Ditado" o que você ouviu.
3. Clique **Verificar** — a frase correta é revelada e mostra ✅ acerto ou ❌ o esperado.
4. **⏭ Próxima** puxa uma nova frase (sem repetir até esgotar o conjunto).

### Pronunciation (fala)
1. Responda à pergunta exibida (ou use o campo de texto).
2. Clique **🎤 Gravar**, fale, e **⏹ Parar**.
3. A transcrição aparece e a IA corrige gramática/fluência.
4. Ouça a transcrição e a correção com os botões de áudio.

### Write (escrita)
1. Escreva um parágrafo no idioma selecionado.
2. Clique **Corrigir** — recebe correção detalhada com erros, regras e sugestões.

### Read (leitura)
1. Clique **📄 Carregar texto** para ver um texto do nível/categoria escolhidos, com glossário.
2. Responda à pergunta de compreensão e clique **Corrigir**.
3. **⏭ Próximo** troca o texto.

### Conversation (chat com IA)
1. Escolha a **Persona** ao lado do título: Café, Entrevistador, Negócios, Viagens, Família, Filmes, Músicas, Futebol, DevOps.
2. Clique **🤖 IA fala primeiro** para a IA iniciar, ou digite/envie sua mensagem.
3. Pode falar com **🎤 Gravar** — a IA transcreve, responde e fala de volta.
4. O histórico da conversa fica na tela.

### Grammar (gramática por nível CEFR)
1. Escolha o **Nível CEFR** (A1, A2, B1, B2, C1, C2).
2. Clique **📘 Carregar tópico** para ver título, estrutura, explicação e exemplos.
3. Cada exemplo tem 🔊 para ouvir a frase.
4. **⏭ Próximo** troca o tópico (sem repetir até esgotar o nível).

### MemHack (memorização com repetição espaçada)
1. Escolha a **Categoria** (Rotina, Trabalho, Escola, Família, Diversão, Esportes).
2. A frase aparece; clique **🔊 Ouvir frase** e **👁 Tradução** para conferir.
3. Classifique com **✅ Fácil**, **🟡 Médio** ou **🔴 Difícil**:
   - **Fácil** → revisa em intervalo maior (até 7 dias).
   - **Médio** → mantém o intervalo.
   - **Difícil** → revisa em intervalo curto (1–10 min).
4. O progresso é salvo por usuário e idioma.

### Numbers (números, ordinais, meses, dias)
1. Clique na aba **Numbers** na sidebar.
2. Escolha uma sub-aba: **Números** (1-100 + centenas), **Ordinais** (1-100), **Meses** ou **Dias da Semana**.
3. Veja a lista no idioma selecionado com TTS para cada item.
4. Troque o idioma para ver os números, ordinais, meses e dias em inglês, espanhol, francês, italiano ou alemão.

## Modo demo vs. com IA

- **Com `OPENROUTER_API_KEY`**: correção e conversa usam o LLM; voz usa Edge TTS.
- **Sem chave**: correção heurística simples e voz do navegador.

## Dicas

- Use fones de ouvido para o ditado (Listen) e fale sem ruído para Pronunciation.
- Troque a voz pela seleção na sidebar se a padrão não agradar.
- O botão "Próxima" garante treino variado sem repetição.
- Troque o idioma para praticar inglês, espanhol, francês, italiano ou alemão — toda a UI acompanha.
