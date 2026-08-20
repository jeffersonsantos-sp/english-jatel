# Skills - Britlearn Academy

## Skills de Deploy

### Skill: britlearn-deploy-site
**Descricao**: Deploy do site institucional no AKS

**Uso**:
```bash
# Build
docker build -t updateinformatica/britlearnacademy-web:latest Web-Site/
docker push updateinformatica/britlearnacademy-web:latest

# Deploy
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site

# Verificar
kubectl get pods -n britlearn-academy-site
curl -sI https://britlearnacademy.online
```

---

### Skill: britlearn-deploy-app
**Descricao**: Deploy do app de aprendizado no AKS

**Uso**:
```bash
# Build
docker build -t updateinformatica/britlearn-app:latest Web-APP/
docker push updateinformatica/britlearn-app:latest

# Deploy
kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app

# Verificar
kubectl get pods -n britlearn-academy-app
curl -s https://britlearnacademy.online/app/api/health
```

---

### Skill: britlearn-secret-update
**Descricao**: Atualizar secrets no Kubernetes

**Uso**:
```bash
kubectl create secret generic britlearn-app-secrets \
  -n britlearn-academy-app \
  --from-literal=OPENROUTER_API_KEY="NOVA_KEY" \
  --from-literal=SESSION_SECRET="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app
```

---

## Skills de Desenvolvimento

### Skill: britlearn-add-module
**Descricao**: Adicionar novo modulo de aprendizado

**Estrutura**:
```
Web-APP/backend/{module_name}.json
Web-APP/frontend/ (atualizar app.js)
```

**Template JSON**:
```json
{
  "module": "nome_modulo",
  "levels": {
    "A1": [...],
    "A2": [...],
    "B1": [...],
    "B2": [...],
    "C1": [...],
    "C2": [...]
  }
}
```

---

### Skill: britlearn-add-language
**Descricao**: Adicionar novo idioma ao app

**Arquivos necessarios**:
```bash
# Conteudo
Web-APP/backend/grammar_{lang}.json
Web-APP/backend/memhack_{lang}.json
Web-APP/backend/listen_{lang}.json
Web-APP/backend/read_{lang}.json
Web-APP/backend/calendar_numbers_{lang}.json

# Frontend
Web-APP/frontend/i18n.js (adicionar traducoes)
```

**Idiomas suportados**: en, es, fr, it, de

---

## Skills de Manutencao

### Skill: britlearn-backup
**Descricao**: Backup dos arquivos antes de alteracoes

**Uso**:
```bash
mkdir -p repo-backup/$(date +%Y%m%d_%H%M)
cp -r Web-Site/ repo-backup/$(date +%Y%m%d_%H%M)/
cp -r Web-APP/ repo-backup/$(date +%Y%m%d_%H%M)/
```

---

### Skill: britlearn-rollback
**Descricao**: Rollback para versao anterior

**Uso**:
```bash
# Rollout anterior
kubectl rollout undo deployment/britlearn-app-blue -n britlearn-academy-app

# Verificar
kubectl rollout status deployment/britlearn-app-blue -n britlearn-academy-app
```

---

### Skill: britlearn-logs
**Descricao**: Analise de logs e debug

**Uso**:
```bash
# Logs do app
kubectl logs -n britlearn-academy-app -l app=britlearn-app,slot=blue --tail=100

# Logs do site
kubectl logs -n britlearn-academy-site -l app=britlearn-site,slot=blue --tail=100

# Erros
kubectl logs -n britlearn-academy-app -l app=britlearn-app,slot=blue --tail=100 | grep -i error
```

---

## Skills de IA

### Skill: britlearn-prompt-grammar
**Descricao**: Prompt para correcao gramatical

**Template**:
```
Voce e um professor de {language} experiente. Corrija o texto abaixo (nivel {level}).

Formato: ERRO -> CORRECAO -> REGRA -> SUGESTAO

Texto: {text}
```

---

### Skill: britlearn-prompt-conversation
**Descricao**: Prompt para conversacao

**Template**:
```
You are a friendly English teacher from London.
Student level: {level}
Topic: {topic}

React naturally, correct mistakes gently, and keep the conversation engaging.
Always respond in English.
```

---

### Skill: britlearn-tts-config
**Descricao**: Configuracao de voz TTS

**Vozes disponiveis**:
| Idioma | Voz | Genero |
|--------|-----|--------|
| en-US | en-US-GuyNeural | M |
| en-GB | en-GB-RyanNeural | M |
| es-ES | es-ES-AlvaroNeural | M |
| fr-FR | fr-FR-HenriNeural | M |
| it-IT | it-IT-DiegoNeural | M |
| de-DE | de-DE-ConradNeural | M |

**Uso**:
```bash
export EDGE_TTS_VOICE=en-GB-RyanNeural
```
