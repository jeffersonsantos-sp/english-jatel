# Post LinkedIn — JATEL-IA (DevOps + AI Focus)

---

## Post

---

💡 **De "quero praticar inglês" a uma plataforma full-stack com IA + DevOps completo — em 15 dias**

Criei o **JATEL-IA** — uma plataforma multilíngue que treina Inglês, Espanhol e Francês com inteligência artificial. Mas o que me orgulha mesmo não é o app em si — é **como ele foi construído e entregue**.

**🤖 Ferramentas de IA que usei:**

- **OpenRouter** — LLM para correção gramatical em tempo real (GPT-4o-mini). O aluno escreve, a IA corrige explicando o erro, a regra e sugerindo a forma correta.
- **Edge TTS** — vozes neurais da Microsoft, gratuitas, sem API key. Cada idioma tem sua voz (inglês americano, espanhol, francês).
- **Web Speech API** — reconhecimento de voz nativo do navegador. O aluno fala, o app transcreve e corrige. Fallback para backend quando o navegador não suporta.
- **GitHub Copilot / Claude** — assistência no desenvolvimento, debugging e arquitetura.

**🔧 Stack DevOps completa:**

- **Docker** — imagem multi-stage (python:3.11-slim), ~367MB, rodando como non-root com user 10001
- **Docker Compose** — ambiente local com um comando: `docker compose up -d --build`
- **Kubernetes** — manifests com Kustomize, deploy **Blue/Green** para zero downtime
- **Blue/Green Deployment** — dois slots (azul/verde), Promotion via Service selector
- **Health Probes** — readiness + liveness em `/api/health`
- **PVC** — persistência de dados (usuários + progresso SRS)
- **GitHub Actions CI** — TestClient no backend + `node --check` no frontend
- **GitHub Actions CD** — triggered por git tag `v*` → build → push Docker Hub → smoke test
- **14+ releases** versionados com tags semânticas (v1.0.0 → v1.12.3)

**☁️ Cloud + Infraestrutura como Código:**

- **Azure AKS** — cluster Kubernetes gerenciado (Free Tier, Central India)
- **Terraform** — infraestrutura como código: AKS, DNS Zone, Public IP, RBAC
- **NGINX Ingress Controller** — reverse proxy + TLS termination
- **cert-manager + Let's Encrypt** — certificados TLS automáticos, renovação a cada 90 dias
- **Azure DNS** — resolução de domínio `learn.jfs-devops.shop`
- **Render** — deploy PaaS com auto-deploy a cada push na branch main

**📐 Arquitetura que aprendi a desenhar:**

- Backend FastAPI + frontend SPA vanilla num **único servidor** (sem build step)
- **i18n completo**: 120+ chaves traduzidas — ao trocar o idioma, toda a UI muda (abas, botões, labels, mensagens, placeholders)
- **Conteúdo data-driven**: gramática e frases em JSON. Para adicionar uma lição, edita o arquivo — não mexe no código
- **SRS (Spaced Repetition)**: sistema Leitner com 5 boxes e intervalos crescentes (1min → 7dias), progresso por usuário
- **Auth**: PBKDF2 + cookies HttpOnly HMAC. Multi-usuário com roles admin/comum

**🎯 O que isso me ensinou:**

Não basta saber programar. O valor está em **entregar software** — com CI/CD, containerização, deploy automatizado, monitoramento e segurança. Em **15 dias**, saí do "código que roda na minha máquina" para "sistema em produção com pipeline completo, 14 releases e deploy automatizado".

**🌐 Duas URLs em produção:**

| URL | Ambiente |
|-----|----------|
| 🔗 https://learn.jfs-devops.shop | Azure AKS (Kubernetes + Terraform + TLS) |
| 🔗 https://english-jatel.onrender.com | Render (PaaS, deploy automático) |

**Stack:** Python · FastAPI · Docker · Kubernetes · Terraform · Azure AKS · NGINX · Let's Encrypt · GitHub Actions · OpenRouter · Edge TTS

🔗 GitHub: https://github.com/jeffersonsantos-sp/english-jatel
🐳 Docker Hub: https://hub.docker.com/r/updateinformatica/english-jatel
☁️ Azure AKS: https://learn.jfs-devops.shop
🚀 Render: https://english-jatel.onrender.com

Se você trabalha com DevOps, Arquitetura de Soluções ou quer trocar uma ideia sobre como unir IA + infraestrutura, me conecte! 👇

#devops #docker #kubernetes #terraform #azure #aks #nginx #letsencrypt #tls #https #certmanager #ci_cd #python #fastapi #ai #machinelearning #cloud #githubactions #infrastructureascode #iac #bluegreen #sre #site Reliability #linux #bash #yaml #kustomize #render #paas #saas #edtech #educationtech #languages #multilingual #learnenglish #english #spanish #french #spacedrepetition #aiassisted #llm #openrouter #speechrecognition #texttospeech #fullstack #backend #frontend #api #microservices #containerization #devopslife #cloudcomputing #microsoftazure #azurekubernetes #kubernetescluster #devopstools #automation #cicdpipeline #continuousintegration #continuousdeployment #infrastructure #monitoring #security #secretsmanagement #productionready #scalability #highavailability #disasterrecovery #loadbalancer #dns #ssl #certificate #renewal #auto #zero downtime #deployment #microservices #architecture #microservicesarchitecture #softwareengineering #softwaredevelopment #programming #developer #tech #technology #innovation #learning #education #languages #polyglot #multilingual #accessibility #ux #ui #userexperience #userinterface #webapp #webdevelopment #opensource #community #networking #career #growth #learning #portfolio #project #showcase #buildinginpublic #buildinpublic #100daysofcode #30daychallenge #devopsjourney #cloudjourney #techjourney #learningbydoing #hands on #practical #realworld #production #enterprise #business #solution #consulting #freelance #remotework #remoteworking #digitalnomad #techlife #devopsengineer #cloudengineer #sreengineer #platformengineer #infrastructureengineer #softwarearchitect #solutionarchitect #cloudarchitect #devopsarchitect

---

## Dicas para postar

1. **Adicione 1–2 screenshots** (front-en.png mostra o app funcional + diagrama de arquitetura)
2. **Poste entre 8h–10h** ou **18h–20h** (horários de maior engajamento no LinkedIn)
3. **Comente no próprio post** nos primeiros 30 min (dica do algoritmo)
4. **Marque 2–3 pessoas** de DevOps/Cloud/Python
5. **Responda todos os comentários** nas primeiras 2 horas

---

*Documento pessoal — não versionar no Git.*
