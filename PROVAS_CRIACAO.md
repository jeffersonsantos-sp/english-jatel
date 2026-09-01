# PROVAS DE CRIACAO — JATEL-IA

> Este documento comprova que o aplicativo **JATEL-IA** foi criado e e mantido pelo autor deste repositorio.
> Ultima atualizacao: **31/07/2026** — versao `v1.12.3`.

---

## 1. Identificacao do Projeto

| Campo | Valor |
|-------|-------|
| **Nome do Projeto** | JATEL-IA |
| **Repositorio GitHub** | `jeffersonsantos-sp/english-jatel` |
| **URL do Repo** | https://github.com/jeffersonsantos-sp/english-jatel |
| **Autor** | Jefferson Santos — DevOps |
| **Stack** | FastAPI (Python 3.11) + SPA Vanilla (HTML/CSS/JS) |
| **Docker Hub** | `updateinformatica/english-jatel` |
| **Versao Atual** | `v1.12.3` |
| **License** | Privado — Uso Pessoal e Educacional |

---

## 2. URLs de Producao

| URL | Provider | Uso |
|-----|----------|-----|
| **https://learn.jfs-devops.shop** | Azure AKS (Kubernetes) | Producao principal + demonstracao DevOps |
| **https://english-jatel.onrender.com** | Render (PaaS) | Deploy automatizado no push ao `main` |

### Stack Cloud (Azure AKS)

| Componente | Detalhe |
|------------|---------|
| **AKS Cluster** | `aks-english-jatel` (Free Tier, Central India) |
| **Kubernetes** | v1.35.6 |
| **VM Size** | Standard_B2als_v2 (2 vCPU, 4GB RAM) |
| **Terraform** | Infraestrutura como codigo (AKS, DNS, RBAC) |
| **NGINX Ingress** | Reverse proxy + TLS termination |
| **cert-manager** | Let's Encrypt (auto-renovacao a cada 90 dias) |
| **Azure DNS** | `jfs-devops.shop` (zona DNS gerenciada) |
| **Public IP** | (dynamic via Terraform) |
| **Custo mensal** | ~$15.50 (AKS + DNS) |

---

## 3. Cronologia do Projeto

| Marco | Data | Detalhe |
|-------|------|---------|
| **Primeiro commit** | 2026-07-14 | `e91f61b` — Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| **Primeiro deploy Docker** | 2026-07-14 | Imagem `updateinformatica/english-jatel` publicada no Docker Hub |
| **CI/CD pipeline** | 2026-07-14 | `ci.yaml` + `cd.yaml` configurados com GitHub Actions |
| **Multi-idioma (EN/ES/FR)** | 2026-07-21 | v1.9.0 — seletor de idioma, Listen/Read ES/FR, Grammar ES/FR |
| **Kubernetes Blue/Green** | 2026-07-28 | Manifestos k8s com deployment blue/green e Kustomize |
| **Full i18n UI** | 2026-07-29 | v1.12.0 — traducao completa da interface (120+ chaves EN/ES/FR) |
| **Azure AKS + Terraform** | 2026-07-30 | Deploy na cloud com Terraform, NGINX Ingress, Let's Encrypt |
| **Setup HTTPS skill** | 2026-07-31 | Skill para configuracao HTTPS/TLS no AKS |
| **Dual URL production** | 2026-07-31 | Azure AKS + Render simultaneamente |
| **Tags publicadas** | 2026-07-31 | v1.0.0 ate v1.12.3 (14+ releases) |

---

## 4. Historico de Commits (selecao representativa)

| Data | Hash | Mensagem |
|------|------|----------|
| 2026-07-14 | `e91f61b` | Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| 2026-07-14 | `16f8e67` | CI/CD: push image to Docker Hub instead of GHCR |
| 2026-07-14 | `8d857dd` | CI/CD: use secrets.OPENROUTER_API_KEY (matches repo secret) |
| 2026-07-21 | `4b98cc7` | Release: v1.8.3 (fix conversacao — IA aguarda botao Parar) |
| 2026-07-21 | `c4072b7` | Release: v1.9.0 — multi-idioma (ES + FR) com seletor lang |
| 2026-07-21 | `0866020` | feat: multi-idioma para Listen/Read com conteudo ES/FR |
| 2026-07-21 | `a5fccac` | feat: persona Series + i18n completo (EN/ES/FR/PT) para toda UI |
| 2026-07-28 | `be3a241` | feat: suporte a selecao de idioma (en/es/fr) com persistencia |
| 2026-07-29 | `b53cc92` | feat: implement full UI i18n (EN/ES/FR) for all tabs, buttons |
| 2026-07-29 | `fdd2aa2` | feat: move Persona selector to Conversation section header |
| 2026-07-29 | `4ba1f4f` | feat: rename Speak tab to Pronunciation (EN/ES/FR) |
| 2026-07-30 | `bd69239` | feat: Add AKS deployment with Terraform, NGINX Ingress, and TLS |
| 2026-07-31 | `a62bcd4` | fix: Remove secrets from git and add security guidelines |
| 2026-07-31 | `5a05d5b` | feat: Add setup-https skill, docs, and update README with dual URLs |
| 2026-07-31 | `e3ef4ac` | feat: Update author to DevOps, add LinkedIn post with dual URLs |
| 2026-07-31 | `04a4613` | chore: Clean up .gitignore (remove duplicate entries) |

**Total de commits**: 50+ | **Periodo**: 14/07/2026 → 31/07/2026 (17 dias)

---

## 5. Imagens Docker

| Imagem | Tags | Tamanho | Status |
|--------|------|---------|--------|
| `updateinformatica/english-jatel` | `latest`, `v1.12.3` | ~367MB | Publicado via CD |

---

## 6. Deploy & Infraestrutura

| Ambiente | URL / Metodo | Status |
|----------|-------------|--------|
| **Azure AKS** | https://learn.jfs-devops.shop | Producao (demonstracao DevOps) |
| **Render (PaaS)** | https://english-jatel.onrender.com | Producao (deploy automatico) |
| **Docker Hub** | `updateinformatica/english-jatel:latest` | Publicado |
| **Kubernetes** | `kubectl apply -k k8s/` (Blue/Green) | Manifestos prontos |
| **Local** | `docker compose up` ou `uvicorn` | Funcional |

---

## 7. Funcionalidades Implementadas

| Modulo | EN | ES | FR | i18n UI |
|--------|----|----|-----|---------|
| Listen (ditado) | Sim | Sim | Sim | Sim |
| Pronunciation (fala) | Sim | Sim | Sim | Sim |
| Write (escrita) | Sim | Sim | Sim | Sim |
| Read (leitura) | Sim | Sim | Sim | Sim |
| Conversation (chat IA) | Sim | Sim | Sim | Sim |
| Grammar (CEFR A1-C2) | 46 topicos | 46 topicos | 47 topicos | Sim |
| MemHack (SRS) | 6 cat. x 8 frases | 6 cat. x 8 frases | 6 cat. x 8 frases | Sim |
| TTS (Edge neural) | Sim | Sim | Sim | — |
| STT (Web Speech + fallback) | Sim | Sim | Sim | — |
| Auth (PBKDF2 + sessions) | Sim | — | — | Sim |
| CI/CD (GitHub Actions) | Sim | — | — | — |
| Kubernetes Blue/Green | Sim | — | — | — |
| Docker multi-stage | Sim | — | — | — |

---

## 8. Stack Tecnico

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
| Ingress | NGINX Ingress Controller |
| TLS | cert-manager + Let's Encrypt |
| IaC | Terraform (AKS, DNS, RBAC) |
| Cloud | Azure AKS, Render |
| CI/CD | GitHub Actions |
| Hosting | Docker Hub, Azure AKS, Render |

---

## 9. Comprovantes de Autoria

1. **Repositorio GitHub**: `jeffersonsantos-sp/english-jatel` — criado e mantido por Jefferson Santos
2. **Docker Hub**: `updateinformatica/english-jatel` — imagens publicadas via CI/CD automatizado
3. **Primeiro commit**: `e91f61b` em 2026-07-14 — "Initial commit" por Jefferson Santos
4. **Todos os commits** possuem autor `jeffersonsantos-sp` no remoto
5. **Tags Git**: v1.0.0 ate v1.12.3 criadas e enviadas pelo autor
6. **CD Pipeline**: `cd.yaml` dispara em tags `v*`, publica imagens automaticamente
7. **Azure AKS**: Cluster criado via Terraform pelo autor
8. **Render**: Deploy configurado via GitHub Actions pelo autor

---

## 10. Estrutura do Repositorio

```
projeto-aiops/
├── backend/                  # API FastAPI (main.py, engine.py, conteudo JSON)
├── frontend/                 # SPA vanilla (index.html, app.js, i18n.js, style.css)
├── terraform/                # Infraestrutura Azure (AKS, DNS, RBAC)
├── k8s/                      # Kubernetes manifests (Blue/Green + Kustomize)
├── k8s/production/           # Prometheus, ArgoCD
├── .opencode/                # Skills do agente IA
│   ├── setup-https/          # Skill HTTPS/TLS
│   └── skills/aks-deploy/    # Skill deploy AKS
├── .github/workflows/        # CI/CD (ci.yaml, cd.yaml)
├── docs/                     # Documentacao tecnica + usuario
├── prompts/                  # Templates de prompts para agentes IA
├── skills/                   # Skills para agentes IA
├── Dockerfile                # Build multi-stage
├── docker-compose.yaml       # Desenvolvimento local
├── AGENTS.md                 # Configuracao do agente
├── PROVAS_CRIACAO.md         # Este documento
└── README.md                 # Documentacao principal
```

---

## 11. Custos Azure (enquanto ativo)

| Recurso | Custo Mensal |
|---------|-------------|
| AKS Free Tier | $0 |
| Standard_B2als_v2 | ~$15 |
| Azure DNS Zone | $0.50 |
| Let's Encrypt + NGINX + cert-manager | $0 |
| **Total** | **~$15.50** |

> **Nota**: Infraestrutura Azure sera desativada em breve. O deploy continua disponivel via Render.

---

Documento gerado em 31/07/2026 com base no historico completo de commits do repositorio.
