# Guia do Usuário — English Flow

Aplicativo web para treinar inglês nas habilidades **Listen, Speak, Write, Read** e
**Conversar**, mais **Grammar** (gramática por nível CEFR) e **MemHack** (memorização com
repetição espaçada), com correção automática e conversação por IA.

## Acesso

1. No terminal, na pasta `backend`:
   ```bash
   pip install -r requirements.txt
   python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
2. Abra **http://localhost:8000** no navegador (Chrome recomendado para a voz).

> O backend serve tanto a API quanto a interface, num único endereço.

## Controles do topo

- **Nível**: Iniciante / Intermediário / Avançado — ajusta a dificuldade das frases e textos.
- **Voz da IA**: escolhe a voz neural do Edge TTS (ex.: Jenny feminina, Guy masculina, Sonia do Reino Unido).
- **Categoria**: Todas / Rotina / Trabalho / Viagem — filtra o conteúdo de Listen e Read.
- **Persona** (só na Conversa): Café / Entrevistador / Negócios — define o estilo da IA.

## Módulos

### Listen (ditado)
1. Clique **🔊 Ouvir frase** — a IA fala a frase (áudio), mas o texto **fica oculto**.
2. Digite no campo "Ditado" o que você ouviu.
3. Clique **Verificar** — a frase correta é revelada e mostra ✅ acerto ou ❌ o esperado vs. o que você escreveu.
4. **⏭ Próxima** puxa uma nova frase (sem repetir até esgotar o conjunto).

### Speak (fala)
1. Responda em inglês à pergunta exibida.
2. Clique **🎤 Gravar**, fale, e **⏹ Parar**.
3. A transcrição aparece e a IA corrige gramática/fluência.

### Write (escrita)
1. Escreva um parágrafo em inglês.
2. Clique **Corrigir** — recebe: `ERRO → CORREÇÃO → REGRA → SUGESTÃO`.

### Read (leitura)
1. Clique **📄 Carregar texto** para ver um texto do nível/categoria escolhidos, com glossário.
2. Responda à pergunta de compreensão em inglês e clique **Corrigir**.
3. **⏭ Próximo** troca o texto.

### Conversar (IA)
1. Clique **🤖 IA fala primeiro** para a IA iniciar, ou digite/envie sua mensagem.
2. Pode falar com **🎤 Gravar**; a IA transcreve, responde e fala de volta.
3. O histórico da conversa fica na tela.

### Grammar (gramática por nível CEFR)
1. Escolha o **Nível CEFR** (A1, A2, B1, B2, C1, C2) no seletor da aba.
2. Clique **📘 Carregar tópico** para ver um tópico: título, **estrutura** (fórmula), explicação e exemplos.
3. Cada exemplo tem 🔊 para ouvir a frase em inglês (TTS do navegador como fallback).
4. **⏭ Próximo** troca o tópico (sem repetir até esgotar o nível).

### MemHack (memorização com repetição espaçada)
1. Escolha a **Categoria** (Rotina, Trabalho, Escola, Família, Diversão, Esportes).
2. A frase em inglês aparece; clique **🔊 Ouvir frase** para treinar o ouvido e **👁 Tradução** para conferir.
3. Após treinar, classifique com **✅ Fácil**, **🟡 Médio** ou **🔴 Difícil**:
   - **Fácil** → sobe de "box" (revisa em intervalo maior: até 7 dias).
   - **Médio** → mantém o intervalo atual.
   - **Difícil** → desce de "box" (revisa em intervalo curto: 1–10 min).
4. O progresso de cada usuário é salvo; a próxima frase exibida é sempre a **vencida** (SRS estilo Leitner).
5. Quando tudo estiver em dia, a tela avisa para voltar mais tarde.

## Modo demo vs. com IA

- **Com `OPENROUTER_API_KEY`** (já configurada em `backend/.env`): correção e conversa usam o LLM; a voz usa Edge TTS (sem chave extra).
- **Sem chave**: correção heurística simples e voz do navegador (útil para testar a interface).

## Dicas

- Use fones de ouvido para o ditado (Listen) e fale sem ruído para o Speak.
- Troque a voz pela seleção no topo se a padrão não agradar.
- O botão "Próxima" garante treino variado sem frases repetidas.
