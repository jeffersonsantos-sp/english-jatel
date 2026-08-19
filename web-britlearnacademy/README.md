# Britlearn Academy

Site institucional e aplicativo de aprendizado de inglês da Britlearn Academy.

## Estrutura

```
web-britlearnacademy/
├── Web-Site/          # Site institucional (PHP + Apache)
│   ├── includes/      # Header, footer, components PHP
│   ├── assets/        # CSS, imagens
│   ├── pages/         # Páginas PHP (home, story, contact)
│   └── index.html     # Landing page estática
└── Web-APP/           # Aplicativo de aprendizado (FastAPI + Python)
    ├── backend/       # API FastAPI, engine LLM, TTS/STT
    ├── frontend/      # SPA vanilla (HTML/CSS/JS)
    └── k8s/           # Manifestos Kubernetes
```

## Web-Site

Site institucional da Britlearn Academy com páginas sobre a escola, cursos e contato.

- **Stack**: PHP 8.2 + Apache
- **Deploy**: AKS namespace `britlearn-academy-site`
- **Imagem**: `updateinformatica/britlearnacademy-web:latest`

## Web-APP

Aplicativo de aprendizado de inglês com IA (LLM), correção de texto, conversação e pronúncia.

- **Stack**: FastAPI (Python 3.11) + Frontend vanilla JS
- **Deploy**: AKS namespace `britlearn-academy-app`
- **Imagem**: `updateinformatica/britlearn-app:latest`
- **Funcionalidades**:
  - Grammar (correção com LLM)
  - Conversation (chat com IA)
  - Listen, Read, Write, Pronunciation
  - MemHack (repetição espaçada)
  - TTS/STT (Edge TTS + Web Speech API)

## URLs

| Serviço | URL |
|---------|-----|
| Site | https://britlearnacademy.online |
| App | https://britlearnacademy.online/app |

## Deploy

```bash
# Build e push das imagens
docker build -t updateinformatica/britlearnacademy-web:latest Web-Site/
docker push updateinformatica/britlearnacademy-web:latest

docker build -t updateinformatica/britlearn-app:latest Web-APP/
docker push updateinformatica/britlearn-app:latest

# Reiniciar deployments
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site
kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app
```

## Configuração

- **OpenRouter API Key**: Secret `britlearn-app-secrets` no namespace `britlearn-academy-app`
- **DNS**: `britlearnacademy.online` apontando para IP do ingress `4.247.234.90`
- **Ingress**: Dois ingress compartilhando o mesmo host
  - Site: `path: /` (Prefix)
  - App: `path: /app(/|$)(.*)` (regex, rewrite para `/$2`)
