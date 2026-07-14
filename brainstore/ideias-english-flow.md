# Ideias para Brainstore

## Habilidade Proposta
- Nome sugerido: "english-flow"
- Objetivo: Aplicativo de ensino de inglês que treina listening, speaking, writing e reading, com correções automáticas e conversação por IA (voz com voz).

## Contexto do Usuário
- O usuário quer aprender inglês praticando as 4 habilidades (ouvir, falar, escrever, ler)
- Quer correções detalhadas em cada exercício (erro -> correcao -> regra -> sugestao)
- Quer treinar conversacao com a IA: a IA fala com ele e ele fala com a IA (loop de voz)
- Precisa de ajuste de nivel (iniciante, intermediario, avancado) e historico de erros para revisao

## Modulos / Fluxo de Trabalho Sugerido
1. Listen: gerar audio (TTS) de frases/textos por nivel; exercicios de ditado e multipla escolha
2. Speak: capturar fala do usuario (STT), transcrever, avaliar pronuncia/fluencia e corrigir
3. Write: redacao livre ou guiada; IA corrige gramatica, vocabulario e estilo com explicacoes
4. Read: textos por nivel com glossario e perguntas de compreensao
5. Conversacao IA: IA fala (TTS) -> usuario responde (STT) -> IA reage, corrige e mantem contexto; personas/roles (entrevista, cafe, negocios)
6. Correcoes (transversal): feedback granular + historico de erros recorrentes para revisao (spaced repetition)

## Variáveis Sem Definição
- Plataforma: web, mobile (iOS/Android) ou desktop?
- Idioma da interface: portugues, ingles ou bilíngue?
- Provedor de TTS/STT: Whisper + gTTS/elevenlabs ou nativo do SO?
- Modelo de IA: qual LLM para correcao e conversacao?
- Monetizacao: freemium, assinatura ou gratuito?
- Nivel inicial do usuario: definido por teste ou escolha manual?

## Stack Sugerida
- Backend: Python ou Node.js
- LLM: API de modelo de linguagem (correcao + conversacao)
- Voz: Whisper (STT) + gTTS/elevenlabs (TTS)
- Frontend: React/React Native ou similar
