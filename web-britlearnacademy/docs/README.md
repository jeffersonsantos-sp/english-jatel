# Documentacao - Britlearn Academy

## Indice

| Documento | Descricao |
|-----------|-----------|
| [README](../README.md) | Visao geral do projeto |
| [Prompts](prompts/prompts.md) | Prompts de IA e comandos |
| [Skills](skills/skills.md) | Habilidades e workflows |
| [MCP](mcp/mcp.md) | Integracao Model Context Protocol |
| [Brainstorm](brainstorm/brainstorm.md) | Ideias e roadmap futuro |

---

## Resumo do Projeto

A **Britlearn Academy** e uma plataforma completa de ensino de ingles que combina:

### Tecnologias Principais
- **Docker** - Containerizacao
- **Kubernetes (AKS)** - Orquestracao
- **FastAPI** - Backend assincrono
- **PHP** - Site institucional
- **OpenRouter/GPT** - Inteligencia Artificial
- **Edge TTS** - Text-to-Speech neural
- **Web Speech API** - Speech-to-Text

### Funcionalidades
- **7 modulos** de aprendizado (Grammar, Conversation, Listen, Read, Write, Pronunciation, MemHack)
- **5 idiomas** (Ingles, Espanhol, Frances, Italiano, Alemao)
- **6 niveis CEFR** (A1 ate C2)
- **IA para correcao** em tempo real
- **TTS/STT** para pronuncia

### Infraestrutura
- **2 namespaces** no AKS (site + app)
- **2 imagens Docker** (PHP + Python)
- **Nginx Ingress** com TLS
- **Blue/Green deployment**

---

## Guia Rapido

### Deploy
```bash
# Site
docker build -t updateinformatica/britlearnacademy-web:latest Web-Site/
docker push updateinformatica/britlearnacademy-web:latest
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site

# App
docker build -t updateinformatica/britlearn-app:latest Web-APP/
docker push updateinformatica/britlearn-app:latest
kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app
```

### URLs
- Site: https://britlearnacademy.online
- App: https://britlearnacademy.online/app

### Contato
- Email: updateinformatica2023@gmail.com
- Telefone: +44 7363 065270 / +44 7363 065262

---

## Stack Completa

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEIRAS                           │
├─────────────────────────────────────────────────────────┤
│  HTML5 │ CSS3 │ JavaScript │ React (futuro)            │
├─────────────────────────────────────────────────────────┤
│                    APLICACAO                           │
├─────────────────────────────────────────────────────────┤
│  FastAPI │ PHP 8.2 │ Python 3.11 │ OpenAI SDK          │
├─────────────────────────────────────────────────────────┤
│                    DADOS                               │
├─────────────────────────────────────────────────────────┤
│  JSON Files │ Kubernetes Secrets │ PVC                 │
├─────────────────────────────────────────────────────────┤
│                    INFRAESTRUTURA                      │
├─────────────────────────────────────────────────────────┤
│  Docker │ Kubernetes │ Nginx Ingress │ Let's Encrypt   │
├─────────────────────────────────────────────────────────┤
│                    CLOUD                               │
├─────────────────────────────────────────────────────────┤
│  Azure AKS │ Azure DNS │ Azure Monitor                 │
└─────────────────────────────────────────────────────────┘
```
