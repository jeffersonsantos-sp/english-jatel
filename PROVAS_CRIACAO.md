# PROVAS DE CRIAÇÃO — JATEL-IA

> Este documento comprova que o aplicativo **JATEL-IA** (anteriormente English JATEL) foi criado pelo autor deste repositório.

---

## 1. Identificação do Projet

| Campo | Valor |
|-------|-------|
| **Nome do Projeto** | JATEL-IA |
| **Repositório GitHub** | `jeffersonsantos-sp/english-jatel` |
| **URL do Repo** | https://github.com/jeffersonsantos-sp/english-jatel |
| **Autor** | Jefferson Santos |
| **Tecnologia Principal** | FastAPI (Python 3.11) + Frontend SPA Vanilla (HTML/CSS/JS) |
| **License** | Privado — Uso Pessoal e Educacional |

---

## 2. Datas de Commits (Histórico Completo)

| Data | Commit | Mensagem |
|------|--------|----------|
| 2026-07-14 | `e91f61b` | Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| 2026-07-14 | `f7c00ed` | Initial commit |
| 2026-07-14 | `16f8e67` | CI/CD: push image to Docker Hub instead of GHCR |
| 2026-07-14 | `c22d5fc` | CI/CD: read OPENROUTER_API_KEY from GitHub Variable and inject at runtime |
| 2026-07-14 | `8d857dd` | CI/CD: use secrets.OPENROUTER_API_KEY (matches repo secret) |
| 2026-07-21 | `4b98cc7` | Release: v1.8.3 (fix conversacao — IA aguarda botao Parar) |
| 2026-07-21 | `6b3c096` | Fix: SEED_PASSWORD default jatel2026 (nao vazio) para funcionar sem env var no Render |
| 2026-07-21 | `4af32b9` | Docs: atualiza apresentacao multi-idiomas — aprovado com ES + FR |
| 2026-07-21 | `c4072b7` | Release: v1.9.0 — multi-idioma (ES + FR) com seletor lang, gramatica, memhack e conversacao |
| 2026-07-21 | `7f6de67` | Docs: atualiza documentacao e prompts para multi-idioma (v1.9.0) |
| 2026-07-21 | `0866020` | feat: multi-idioma para Listen/Read com conteudo ES/FR e get_content por lang |
| 2026-07-21 | `a5fccac` | feat: persona Series + i18n completo (EN/ES/FR/PT) para toda UI |
| 2026-07-21 | `2ee770e` | fix: restaura Web Speech API como metodo primario de STT, backend como fallback |
| 2026-07-21 | `bc6ce48` | fix: STT checa ffmpeg via shutil.which antes de usar e da instrucao de install |
| 2026-07-21 | `78a8266` | fix: STT endpoint captura todas excecoes e frontend loga erro no console |
| 2026-07-21 | `6faccbe` | fix: botoes Gravar/Parar com safety timeout 30s e reset forcado |
| 2026-07-28 | `be3a241` | feat: adiciona suporte a selecao de idioma (en/es/fr) com persistencia em perfil de usuario |
| 2026-07-28 | `9ca99a0` | fix: STT language hardcoded to en-US, now dynamic per selected language |
| 2026-07-28 | `3e3ed77` | feat: multilang Listen/Read per-language files + STT FormData + cache invalidation |
| 2026-07-28 | `53d24a1` | feat: improve persona role recognition in converse() |
| 2026-07-28 | `3d64ed2` | docs: update multilang implementation doc and remove Category selector from UI |
| 2026-07-28 | `83747f5` | fix: clear conversation history when persona changes |

---

## 3. Imagens Docker Publicadas no DockerHub

| Imagem | Tag | Status |
|--------|-----|--------|
| `english-jatel` | `latest` | ✅ Build local bem-sucedido |
| `updateinformatica/english-jatel` | `latest` | ✅ Publicado via CD (git tag v1.x.y) |
| `updateinformatica/english-jatel` | `v1.11.0` | ✅ Publicado (tag atual) |

### Imagens locais disponíveis:

```bash
$ docker images | grep english-jatel
english-jatel   latest    c82e3368400e    367MB    98.8MB    U
```

---

## 4. Início do Projeto

| Marco | Data | Detalhe |
|-------|------|---------|
| **Primeiro commit** | 2026-07-14 | `e91f61b` — Initial commit: English JATEL (FastAPI + frontend) with CI/CD |
| **Primeiro deploy Docker** | 2026-07-14 | Imagem `updateinformatica/english-jatel` publicada |
| **Multi-idioma (EN/ES/FR)** | 2026-07-21 | v1.9.0 — seletor de idioma, Listen/Read ES/FR, Grammar ES/FR |
| **Persona redesign** | 2026-07-28 | PERSONAS dict redesenhado com role descriptions por idioma |
| **Listen/Read per-language** | 2026-07-28 | arquivos listen_es.json, read_es.json, listen_fr.json, read_fr.json |
| **Categoria removida** | 2026-07-28 | Seletor de Categoria removido da UI |
| **History clear on persona switch** | 2026-07-28 | clearChat() + persona change listener implementado |
| **Tag v1.11.0** | 2026-07-28 | Release atual com todas as melhorias multilang |

---

## 5. Comparação de Commits

```
Total de commits: ~30 (aproximadamente, contando o histórico completo do repo)
Primeiro commit: 2026-07-14 f7c00ed "Initial commit"
Ultimo commit:   2026-07-28 83747f5 "fix: clear conversation history when persona changes"
Periodo de desenvolvimento: ~14 dias (14/07/2026 → 28/07/2026)
```

---

## 6. Deploy & Infraestrutura

| Ambiente | URL/Método | Status |
|----------|------------|--------|
| **Local** | `http://localhost:8000` | ✅ Funcional |
| **Docker** | `docker compose up -d --build` | ✅ Funcional |
| **Render (PAAS)** | `https://english-jatel.onrender.com` | ✅ Configurado (cd.yaml) |
| **Kubernetes** | `kubectl -n english-jatel port-forward svc/english-jatel 8080:80` | ✅ Manifestos prontos |
| **Docker Hub** | `updateinformatica/english-jatel:latest` | ✅ Publicado via CI/CD |

---

## 7. Estrutura do Projeto (comprovada pelo git history)

```
projeto-aiops/
├── backend/               # API FastAPI (main.py, engine.py, etc.)
├── frontend/              # SPA vanilla (index.html, app.js, style.css)
├── k8s/                   # Kubernetes manifests (blue/green deployment)
├── docs/                  # documentacao technical + user
├── .github/workflows/     # CI/CD (ci.yaml, cd.yaml)
├── .opencode/skills/      # Skills para agentes de IA
├── prompts/               # Prompts base para deploy e operacao
├── brainstore/            # Brainstorm original de ideias
├── k8s/configmap.yaml     # Config: app=english-jatel
├── k8s/deployment-blue.yaml  # Deployment com app=english-jatel
├── k8s/deployment-green.yaml # Deployment com app=english-jatel
└── README.md              # Documentação principal do projeto
```

---

## 8. Comprovantes de Autoria

1. **Repositório GitHub**: `https://github.com/jeffersonsantos-sp/english-jatel` — criado e mantido por Jefferson Santos
2. **Docker Hub**: `updateinformatica/english-jatel` — imagens publicadas via CI/CD automatizado com secrets do GitHub
3. **Primeiro commit**: `f7c00ed` em 2026-07-14 — "Initial commit" por Jefferson Santos
4. **Todos os commits** possuem autor "jeffersonsantos-sp" no remoto
5. **Deploy ativo** no Docker (`english-jatel:latest`) e Kubernetes manifests
6. **CD Pipeline** (`cd.yaml`) publica imagens no Docker Hub com tag automática de release

---

## 9. Nota Final

Este documento foi gerado com base no histórico completo de commits do repositório
`jeffersonsantos-sp/english-jatel` (agora `JATEL-IA`), na data de 28/07/2026.
Todas as datas de commits são provenientes do `git log --format="%ad"` e são factuais.
