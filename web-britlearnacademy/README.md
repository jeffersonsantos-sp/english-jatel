# Britlearn Academy

**Plataforma completa de ensino de ingles com Inteligencia Artificial**

Site institucional + Aplicativo de aprendizado de ingles com LLM, TTS/STT, deploy em Kubernetes (AKS) e containerizacao com Docker.

---

## Visao Geral

A Britlearn Academy e uma escola de ingles londrina que combina tecnologia moderna com ensino de qualidade. A plataforma inclui:

- **Site Institucional**: Paginas estaticas sobre a escola, cursos e contato
- **App de Aprendizado**: Aplicativo completo com IA para correcao, conversacao e praticas

---

## Stack Tecnologica

### Frontend
| Tecnologia | Uso |
|------------|-----|
| HTML5/CSS3 | Estrutura e estilo |
| JavaScript Vanilla | Logica do SPA |
| CSS Variables | Tema e cores customizaveis |
| i18n.js | Internacionalizacao (EN/ES/FR/IT/DE) |

### Backend
| Tecnologia | Uso |
|------------|-----|
| PHP 8.2 | Site institucional |
| Python 3.11 | API do App |
| FastAPI | Framework web assincrono |
| OpenRouter API | Integracao com LLM (GPT) |
| Edge TTS | Text-to-Speech neural (Microsoft) |
| Web Speech API | Speech-to-Text no navegador |
| ffmpeg | Conversao de audio |

### Infraestrutura
| Tecnologia | Uso |
|------------|-----|
| Docker | Containerizacao das aplicacoes |
| Kubernetes (AKS) | Orquestracao e deploy |
| Nginx Ingress | Roteamento HTTP/TLS |
| Let's Encrypt | Certificados SSL automaticos |
| Azure DNS | Resolucao de dominio |
| Terraform | Infraestrutura como codigo |

### Inteligencia Artificial
| Componente | Descricao |
|------------|-----------|
| LLM (GPT) | Correcao gramatical, conversacao, sugestoes |
| TTS (Edge) | Sintese de voz neural em multiplos idiomas |
| STT (Web Speech) | Reconhecimento de fala no navegador |
| Prompt Engineering | System prompts otimizados para ensino |

---

## Arquitetura

```
                    ┌─────────────────────────────────────┐
                    │         Azure Kubernetes (AKS)       │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
            ┌───────▼───────┐                   ┌───────▼───────┐
            │  britlearn-   │                   │  britlearn-   │
            │  academy-site │                   │  academy-app  │
            │  (PHP/Apache) │                   │  (FastAPI)    │
            └───────┬───────┘                   └───────┬───────┘
                    │                                   │
            ┌───────▼───────┐                   ┌───────▼───────┐
            │  Docker Image │                   │  Docker Image │
            │  :britlearn-  │                   │  :britlearn-  │
            │  academy-web  │                   │  app          │
            └───────────────┘                   └───────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                          ┌───────────▼───────────┐
                          │    Nginx Ingress       │
                          │    (Load Balancer)     │
                          └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │  britlearnacademy.     │
                          │  online                │
                          └───────────────────────┘
```

---

## URLs de Producao

| Servico | URL | Descricao |
|---------|-----|-----------|
| Site | https://britlearnacademy.online | Pagina institucional |
| App | https://britlearnacademy.online/app | Aplicativo de aprendizado |
| API | https://britlearnacademy.online/app/api/* | Endpoints da API |
| Admin | https://britlearnacademy.online/admin/ | Painel administrativo |

---

## Funcionalidades do App

### Modulos de Aprendizado
| Modulo | Descricao |
|--------|-----------|
| **Listen** | Exercicios de audicao com TTS + ditado |
| **Pronunciation** | Reconhecimento de fala (STT) + correcao |
| **Write** | Pratica de escrita com correcao detalhada |
| **Read** | Leitura com glossario e perguntas |
| **Conversation** | Chat conversacional com IA em ingles |
| **Grammar** | Correcao gramatical por nivel CEFR |
| **MemHack** | Repeticao espacada (SRS) para vocabulario |
| **Numbers** | Numeros, ordinais, meses e dias da semana |

### Recursos da IA
- **Correcao em tempo real**: Identifica erros e sugere correcoes
- **Explicacoes contextuais**: Regras gramaticais e sugestoes
- **Conversacao natural**: Chat como um professor nativo
- **Multiplos niveis**: A1 ate C2 (CEFR)
- **5 idiomas**: Ingles, Espanhol, Frances, Italiano, Alemao
- **9 personas**: Cafe, Entrevistador, Negocios, Viagens, Familia, Filmes, Musicas, Futebol, DevOps

### Internacionalizacao (i18n)
- Interface completa em 5 idiomas
- Sistema de traducao via `data-i18n` attributes
- Troca de idioma em tempo real

### Sistema de Auth
- Login com JWT (session-based)
- Cookie HttpOnly com SameSite=Lax
- Tokens assinados com HMAC-SHA256
- Seed de usuario admin para setup inicial
- Gerenciamento de usuarios (criar/novos usuarios)

---

## Estrutura do Repositorio

```
web-britlearnacademy/
├── README.md                    # Esta documentacao
├── .gitignore                   # Arquivos ignorados pelo Git
│
├── Web-Site/                    # Site Institucional
│   ├── Dockerfile               # Build image PHP/Apache
│   ├── docker-compose.yml       # Deploy local
│   ├── config/config.php        # Configuracoes do site
│   ├── includes/                # Componentes PHP
│   │   ├── header.php           # Navbar com BritLearn-APP
│   │   ├── footer.php           # Footer
│   │   └── functions.php        # Funcoes auxiliares
│   ├── pages/                   # Paginas PHP
│   │   ├── home.php             # Pagina inicial
│   │   ├── story.php            # Nossa historia
│   │   └── contact.php          # Contato (form + telefones)
│   ├── assets/css/style.css     # Estilos do site
│   └── k8s/                     # Manifestos Kubernetes
│
└── Web-APP/                     # Aplicativo de Aprendizado
    ├── Dockerfile               # Build image Python
    ├── docker-compose.yml       # Deploy local
    ├── backend/
    │   ├── main.py              # FastAPI - rotas e middleware
    │   ├── engine.py            # Engine LLM + TTS/STT
    │   ├── requirements.txt     # Dependencias Python
    │   └── *.json               # Conteudo (grammar, memhack, etc)
    ├── frontend/
    │   ├── index.html           # SPA principal
    │   ├── login.html           # Pagina de login
    │   ├── app.js               # Logica principal
    │   ├── auth.js              # Autenticacao
    │   ├── i18n.js              # Internacionalizacao (EN/ES/FR/IT/DE)
    │   └── style.css            # Estilos (tema Navy/Vermelho/Dourado)
    └── k8s/                     # Manifestos Kubernetes
        ├── namespace.yaml
        ├── deployment-blue.yaml
        ├── deployment-green.yaml
        ├── service.yaml
        ├── ingress.yaml
        ├── configmap.yaml
        ├── secret.yaml
        └── pvc.yaml

docs/                            # Documentacao
├── README.md                    # Indice da documentacao
├── prompts/prompts.md           # Prompts de IA
├── skills/skills.md             # Skills e workflows
├── mcp/mcp.md                   # Model Context Protocol
└── brainstorm/                  # Ideias e roadmap
    ├── brainstorm.md            # Planejamento futuro
    └── mockup-login-*.html      # Mockups de design
```

---

## Deploy

### Build e Push das Imagens

```bash
# Site
cd web-britlearnacademy/Web-Site
docker build -t updateinformatica/britlearnacademy-web:latest .
docker push updateinformatica/britlearnacademy-web:latest

# App
cd web-britlearnacademy/Web-APP
docker build -t updateinformatica/britlearn-app:latest .
docker push updateinformatica/britlearn-app:latest
```

### Reiniciar Deployments

```bash
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site
kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app
```

### Verificar Status

```bash
kubectl get pods -n britlearn-academy-site
kubectl get pods -n britlearn-academy-app
kubectl logs -n britlearn-academy-app -l app=britlearn-app,slot=blue --tail=20
```

---

## Configuracao

### Secrets (Kubernetes)

```bash
# Atualizar secret do App
kubectl create secret generic britlearn-app-secrets -n britlearn-academy-app \
  --from-literal=OPENROUTER_API_KEY="sua-chave-aqui" \
  --from-literal=SESSION_SECRET="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Variaveis de Ambiente

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `OPENROUTER_API_KEY` | Chave da API OpenRouter | `sk-or-v1-...` |
| `OPENAI_MODEL` | Modelo LLM a usar | `openai/gpt-4o-mini` |
| `EDGE_TTS_VOICE` | Voz do TTS | `en-US-GuyNeural` |
| `SESSION_SECRET` | Chave para sessoes | `(hex 64 chars)` |
| `ADMIN_USER` | Usuario admin | `admin` |
| `SEED_PASSWORD` | Senha do seed | `CHANGE_ME` |

### Ingress

- **Host**: `britlearnacademy.online`
- **Site**: `path: /` (Prefix)
- **App**: `path: /app(/|$)(.*)` (regex, rewrite para `/$2`)
- **TLS**: Let's Encrypt via cert-manager
- **IP**: `4.247.234.90`

---

## Desenvolvimento Local

### Site

```bash
cd Web-Site
docker-compose up -d
# Acesse: http://localhost:8080
```

### App

```bash
cd Web-APP
pip install -r backend/requirements.txt
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
# Acesse: http://localhost:8000
```

---

## Seguranca

- Secrets **nunca** sao committados no Git
- `.gitignore` protege `.env` e `secret.yaml`
- Cookies HttpOnly + SameSite=Lax
- Headers de seguranca (XSS, CSRF, nosniff)
- Rate limiting no formulario de contato
- Senhas hasheadas com bcrypt
- Git history limpa com filter-branch

---

## Contato

| Canal | Valor |
|-------|-------|
| **Email** | contact@britlearnacademy.online |
| **Telefone 1** | +44 7363 065270 |
| **Telefone 2** | +44 7363 065262 |
| **Site** | https://britlearnacademy.online |
| **App** | https://britlearnacademy.online/app |

---

## Roadmap

### Q1 2026
- [x] Lancamento do site
- [x] Lancamento do app basico
- [x] Modulos: Listen, Pronunciation, Write, Read, Conversation, Grammar, MemHack, Numbers
- [x] i18n em 5 idiomas

### Q2 2026 (Planejado)
- [ ] Gamificacao (XP, badges, streak)
- [ ] PWA (Progressive Web App)
- [ ] Analytics dashboard
- [ ] Conteudo Business English

---

## Licenca

Proprietario - Britlearn Academy 2026
