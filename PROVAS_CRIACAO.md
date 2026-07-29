# PROVAS DE CRIAÇÃO — JATEL-IA

> Este documento comprova que o aplicativo **JATEL-IA** foi criado e é mantido pelo autor deste repositório.
> Última atualização: **29/07/2026** — versão `v1.12.2`.

---

## 1. Identificação do Projeto

| Campo | Valor |
|-------|-------|
| **Nome do Projeto** | JATEL-IA |
| **Repositório GitHub** | `jeffersonsantos-sp/english-jatel` |
| **URL do Repo** | https://github.com/jeffersonsantos-sp/english-jatel |
| **Autor** | Jefferson Santos |
| **Stack** | FastAPI (Python 3.11) + SPA Vanilla (HTML/CSS/JS) |
| **Docker Hub** | `updateinformatica/english-jatel` |
| **Versão Atual** | `v1.12.2` |
| **License** | Privado — Uso Pessoal e Educacional |

---

## 2. Cronologia do Projeto

| Marco | Data | Detalhe |
|-------|------|---------|
| **Primeiro commit** | 2026-07-14 | `e91f61b` — Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| **Primeiro deploy Docker** | 2026-07-14 | Imagem `updateinformatica/english-jatel` publicada no Docker Hub |
| **CI/CD pipeline** | 2026-07-14 | `ci.yaml` + `cd.yaml` configurados com GitHub Actions |
| **Multi-idioma (EN/ES/FR)** | 2026-07-21 | v1.9.0 — seletor de idioma, Listen/Read ES/FR, Grammar ES/FR |
| **Persona redesign** | 2026-07-28 | PERSONAS dict redesenhado com role descriptions por idioma |
| **Kubernetes Blue/Green** | 2026-07-28 | Manifestos k8s com deployment blue/green e Kustomize |
| **Full i18n UI** | 2026-07-29 | v1.12.0 — tradução completa da interface (120+ chaves EN/ES/FR) |
| **Persona move** | 2026-07-29 | v1.12.1 — seletor de Persona movido para aba Conversation |
| **Speak → Pronunciation** | 2026-07-29 | v1.12.2 — aba renomeada para clareza UX |
| **Tags publicadas** | 2026-07-29 | v1.0.0 até v1.12.2 (14+ releases) |

---

## 3. Histórico de Commits (seleção representativa)

| Data | Hash | Mensagem |
|------|------|----------|
| 2026-07-14 | `e91f61b` | Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| 2026-07-14 | `16f8e67` | CI/CD: push image to Docker Hub instead of GHCR |
| 2026-07-14 | `8d857dd` | CI/CD: use secrets.OPENROUTER_API_KEY (matches repo secret) |
| 2026-07-21 | `4b98cc7` | Release: v1.8.3 (fix conversacao — IA aguarda botao Parar) |
| 2026-07-21 | `c4072b7` | Release: v1.9.0 — multi-idioma (ES + FR) com seletor lang |
| 2026-07-21 | `0866020` | feat: multi-idioma para Listen/Read com conteudo ES/FR |
| 2026-07-21 | `a5fccac` | feat: persona Series + i18n completo (EN/ES/FR/PT) para toda UI |
| 2026-07-21 | `2ee770e` | fix: restaura Web Speech API como metodo primario de STT |
| 2026-07-28 | `be3a241` | feat: suporte a selecao de idioma (en/es/fr) com persistencia |
| 2026-07-28 | `3e3ed77` | feat: multilang Listen/Read per-language files + STT FormData |
| 2026-07-28 | `83747f5` | fix: clear conversation history when persona changes |
| 2026-07-29 | `5159cb5` | feat: translate Grammar ES/FR content and bump manifests to v1.11.3 |
| 2026-07-29 | `b53cc92` | feat: implement full UI i18n (EN/ES/FR) for all tabs, buttons, labels |
| 2026-07-29 | `fdd2aa2` | feat: move Persona selector to Conversation section header |
| 2026-07-29 | `4ba1f4f` | feat: rename Speak tab to Pronunciation (EN/ES/FR) |

**Total de commits**: 40+ | **Período**: 14/07/2026 → 29/07/2026 (15 dias)

---

## 4. Imagens Docker

| Imagem | Tags | Tamanho | Status |
|--------|------|---------|--------|
| `updateinformatica/english-jatel` | `latest`, `v1.12.2` | ~367MB | ✅ Publicado via CD |

```bash
$ docker images | grep english-jatel
updateinformatica/english-jatel   latest   <hash>   367MB
updateinformatica/english-jatel   v1.12.2  <hash>   367MB
```

---

## 5. Deploy & Infraestrutura

| Ambiente | URL / Método | Status |
|----------|-------------|--------|
| **Docker Hub** | `updateinformatica/english-jatel:latest` | ✅ Publicado |
| **Kubernetes** | `kubectl apply -k k8s/` (Blue/Green) | ✅ Manifestos prontos |
| **Render (PaaS)** | `https://english-jatel.onrender.com` | ✅ Configurado |
| **Local** | `docker compose up` ou `uvicorn` | ✅ Funcional |

---

## 6. Funcionalidades Implementadas

| Módulo | EN | ES | FR | i18n UI |
|--------|----|----|-----|---------|
| Listen (ditado) | ✅ | ✅ | ✅ | ✅ |
| Pronunciation (fala) | ✅ | ✅ | ✅ | ✅ |
| Write (escrita) | ✅ | ✅ | ✅ | ✅ |
| Read (leitura) | ✅ | ✅ | ✅ | ✅ |
| Conversation (chat IA) | ✅ | ✅ | ✅ | ✅ |
| Grammar (CEFR A1–C2) | ✅ 46 tópicos | ✅ 46 tópicos | ✅ 47 tópicos | ✅ |
| MemHack (SRS) | ✅ 6 cat. × 8 frases | ✅ 6 cat. × 8 frases | ✅ 6 cat. × 8 frases | ✅ |
| TTS (Edge neural) | ✅ | ✅ | ✅ | — |
| STT (Web Speech + fallback) | ✅ | ✅ | ✅ | — |
| Auth (PBKDF2 + sessions) | ✅ | — | — | ✅ |
| CI/CD (GitHub Actions) | ✅ | — | — | — |
| Kubernetes Blue/Green | ✅ | — | — | — |
| Docker multi-stage | ✅ | — | — | — |

---

## 7. Stack Técnico

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Frontend | Vanilla HTML/CSS/JS (SPA, sem build) |
| LLM | OpenRouter (OpenAI-compatible) |
| TTS | Edge TTS (neural, gratuito) |
| STT | Web Speech API + SpeechRecognition fallback |
| Auth | HMAC cookies + PBKDF2 |
| Container | Docker multi-stage (python:3.11-slim) |
| Orchestration | Docker Compose, Kubernetes (Kustomize) |
| CI/CD | GitHub Actions |
| Hosting | Docker Hub, Render, Kubernetes |

---

## 8. Comprovantes de Autoria

1. **Repositório GitHub**: `jeffersonsantos-sp/english-jatel` — criado e mantido por Jefferson Santos
2. **Docker Hub**: `updateinformatica/english-jatel` — imagens publicadas via CI/CD automatizado
3. **Primeiro commit**: `e91f61b` em 2026-07-14 — "Initial commit" por Jefferson Santos
4. **Todos os commits** possuem autor `jeffersonsantos-sp` no remoto
5. **Tags Git**: v1.0.0 até v1.12.2 criadas e enviadas pelo autor
6. **CD Pipeline**: `cd.yaml` dispara em tags `v*`, publica imagens automaticamente

---

## 9. Estrutura do Repositório

```
projeto-aiops/
├── backend/                  # API FastAPI (main.py, engine.py, conteúdo JSON)
├── frontend/                 # SPA vanilla (index.html, app.js, i18n.js, style.css)
├── k8s/                      # Kubernetes manifests (Blue/Green + Kustomize)
├── mcp/                      # MCP stdio server
├── .github/workflows/        # CI/CD (ci.yaml, cd.yaml)
├── docs/                     # Documentação técnica + usuário
├── prompts/                  # Templates de prompts para agentes IA
├── skills/                   # Skills para agentes IA
├── brainstore/               # Notas de brainstorm
├── Dockerfile                # Build multi-stage
├── docker-compose.yaml       # Desenvolvimento local
├── PROVAS_CRIACAO.md         # Este documento
└── README.md                 # Documentação principal
```

---

Documento gerado em 29/07/2026 com base no histórico completo de commits do repositório.
