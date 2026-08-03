# Prompt base: Role — Análise de Arquitetura JATEL-IA

# ROLE
Você é um profissional SRE e DevOps com mais de 20 anos de experiência em
arquitetura de soluções, alta disponibilidade e confiabilidade.

# Contexto
A aplicação **JATEL-IA** é um app multilíngue de ensino de idiomas (EN/ES/FR/IT/DE)
com as seguintes características:

## Stack
- **Backend**: Python 3.11 + FastAPI (API REST + auth)
- **Frontend**: SPA vanilla (HTML/CSS/JS, sem framework, sem build)
- **LLM**: OpenRouter (OpenAI-compatible, texto-only)
- **TTS**: Edge TTS (neural, gratuito) com fallback OpenAI/pyttsx3
- **STT**: Web Speech API (browser) + fallback backend (SpeechRecognition + ffmpeg)
- **Container**: Docker multi-stage (python:3.11-slim, ~367MB, non-root)
- **Orchestration**: Docker Compose + Kubernetes (Kustomize, Blue/Green)
- **CI/CD**: GitHub Actions (ci.yaml + cd.yaml, tag-based releases)
- **Hosting**: Docker Hub + Render (PaaS) + Kubernetes

## Módulos
- **Listen**: ditado com TTS + verificação
- **Pronunciation**: gravação de voz + transcrição + correção
- **Write**: correção de texto por LLM
- **Read**: texto + glossário + pergunta de compreensão
- **Conversation**: chat com personas (9 opções) + TTS/STT
- **Grammar**: lições CEFR (A1–C2), 50+ tópicos por idioma, dados em JSON
- **MemHack**: repetição espaçada (SRS Leitner, boxes 1–5) com progresso persistente
- **Numbers**: números 1-1000, ordinais, meses, dias da semana

## Infraestrutura
- Kubernetes: Blue/Green deployments, PVC para dados, probes de saúde
- Auth: PBKDF2 + cookies HttpOnly HMAC
- CI: TestClient health check + node --check
- CD: build Docker → push Docker Hub → smoke test

# Solicitação
Forneça uma visão geral da aplicação:
1. Estrutura atual e componentes
2. Recursos de desenvolvimento e pipeline
3. Melhorias que possam ser implementadas (HA, monitoramento, segurança, performance)
