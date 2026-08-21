# Prompts - Britlearn Academy

## System Prompts para o App de Ensino

### 1. Grammar Correction (Correcao Gramatical)

```
Voce e um professor de ingles experiente e gentil. Corrija o texto abaixo considerando o nivel do aluno ({level}).

Formato da resposta:
- ERRO: [erro encontrado]
- CORRECAO: [texto corrigido]
- REGRA: [explicacao da regra gramatical]
- SUGESTAO: [dica para evitar o erro]

Seja preciso, didatico e encorajador. Destaque os acertos antes dos erros.
```

### 2. Conversation Partner (Parceiro de Conversacao)

```
You are a friendly and patient English teacher from London. You're chatting with a student who is learning English.

Your role:
- Speak naturally and engagingly
- Gently correct any mistakes the student makes
- Ask follow-up questions to keep the conversation going
- Use vocabulary appropriate for their level
- React naturally to what they say
- Always respond in English

Be encouraging and make the student feel comfortable practicing.
```

### 3. Persona Prompts

```python
# Personas disponiveis para conversacao:
PERSONAS = {
    "cafe": "Imagine you are a friendly barista in a London coffee shop...",
    "entrevistador": "You are a professional job interviewer...",
    "negocios": "You are a business executive in a meeting...",
    "viagens": "You are a travel guide showing someone around London...",
    "familia": "You are a family member having a casual chat...",
    "filmes": "You are discussing movies and TV shows...",
    "musicas": "You are talking about music and concerts...",
    "futebol": "You are a football fan discussing the Premier League...",
    "devops": "You are a DevOps engineer discussing cloud infrastructure...",
}
```

### 4. TTS Voice Configuration

```python
# Edge TTS voices disponiveis:
VOICES = {
    "en-US": "en-US-GuyNeural",        # Masculino americano
    "en-GB": "en-GB-RyanNeural",       # Masculino britanico
    "es-ES": "es-ES-AlvaroNeural",     # Masculino espanhol
    "fr-FR": "fr-FR-HenriNeural",      # Masculino frances
    "it-IT": "it-IT-DiegoNeural",      # Masculino italiano
    "de-DE": "de-DE-ConradNeural",     # Masculino alemao
}
```

### 5. Content Generation (Geracao de Conteudo)

```
Gere conteudo educativo para o nivel {level} de ingles.

Tema: {topic}
Tipo: {content_type} (grammar/listen/read/memhack)
Idioma: {language}

O conteudo deve ser:
- Apropriado para o nivel CEFR indicado
- Envolvente e relevante para o aluno
- Progressivo em dificuldade
- Incluir exemplos praticos
```

### 6. Numbers Content

```
Gere conteudo para a secao de numeros:
- Numeros cardinais (1-1000)
- Numeros ordinais (1st, 2nd, 3rd...)
- Meses do ano
- Dias da semana

Para cada item inclua:
- Palavra em ingles
- Pronuncia (IPA)
- Abreviacao (para ordinais, meses, dias)
```

---

## Prompts para Deploy e Infraestrutura

### 7. Docker Build

```bash
# Site
docker build -t updateinformatica/britlearnacademy-web:latest Web-Site/

# App
docker build -t updateinformatica/britlearn-app:latest Web-APP/
```

### 8. Kubernetes Secret Update

```bash
kubectl create secret generic britlearn-app-secrets \
  -n britlearn-academy-app \
  --from-literal=OPENROUTER_API_KEY="sk-or-v1-..." \
  --from-literal=SESSION_SECRET="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 9. Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: britlearn-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
  - host: britlearnacademy.online
    http:
      paths:
      - path: /app(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: britlearn-app-svc
            port:
              number: 80
```

---

## Prompts para Debug

### 10. Log Analysis

```bash
# Verificar logs do app
kubectl logs -n britlearn-academy-app -l app=britlearn-app,slot=blue --tail=50

# Verificar pods
kubectl get pods -n britlearn-academy-app -o wide

# Verificar ingress
kubectl describe ingress britlearn-app-ingress -n britlearn-academy-app
```

### 11. Health Check

```bash
# API health
curl -s https://britlearnacademy.online/app/api/health

# Site status
curl -sI https://britlearnacademy.online

# App status
curl -sI https://britlearnacademy.online/app
```

---

## Prompts para Git

### 12. Commit Messages

```
feat: [nova funcionalidade]
fix: [correcao de bug]
docs: [atualizacao de documentacao]
style: [mudanca de estilo/cor]
refactor: [refatoracao de codigo]
chore: [manutencao/tarefas]
i18n: [internacionalizacao]
```

### 13. Security Cleanup

```bash
# Remover secrets do historico
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret.yaml' \
  --prune-empty --tag-name-filter cat -- --all

git push origin main --force
```

---

## Prompts para i18n

### 14. Traducao de Interface

```javascript
// Adicionar nova traducao em i18n.js:
const I18N = {
  en: {
    "key": "English text",
  },
  es: {
    "key": "Texto en espanol",
  },
  fr: {
    "key": "Texte en francais",
  },
  it: {
    "key": "Testo in italiano",
  },
  de: {
    "key": "Text auf Deutsch",
  },
};
```

### 15. HTML com i18n

```html
<!-- Usar data-i18n para textos -->
<h1 data-i18n="titulo">Titulo</h1>

<!-- Usar data-i18n-placeholder para placeholders -->
<input data-i18n-placeholder="placeholder-chave" placeholder="Texto padrao">

<!-- Usar data-i18n-title para tooltips -->
<button data-i18n-title="tooltip-chave">Botao</button>
```
