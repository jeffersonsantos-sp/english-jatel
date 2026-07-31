---
name: setup-https
description: >
  Configura HTTPS em aplicações Kubernetes no Azure AKS usando NGINX Ingress Controller +
  cert-manager + Let's Encrypt. cobre: instalação via Helm, ClusterIssuers, Ingress com TLS,
  DNS (Azure DNS + Hostinger), health probe do Azure LB, validação de certificado, troubleshooting
  de backend pool vazio, e re-instalação do NGINX Ingress (mudança de IP). Use quando o usuário
  mencionar HTTPS, TLS, SSL, certificado, Let's Encrypt, Ingress, domínio com HTTPS, ou quiser
  expor a aplicação com segurança.
---

# Setup HTTPS — NGINX Ingress + cert-manager + Let's Encrypt (Azure AKS)

## Visão geral do que será feito

```
Antes:  DNS → IP antigo (LoadBalancer direto) → pods  [HTTP :80]
Depois: DNS → IP do Ingress → NGINX Ingress (TLS) → Service ClusterIP → pods  [HTTP + HTTPS]
```

## Pré-requisitos

- `kubectl` configurado com contexto AKS
- `helm` disponível — `export PATH="$HOME/bin:$PATH"`
- `az` CLI autenticado
- Domínio com acesso ao painel DNS (Hostinger, Azure DNS, etc.)
- Repos Helm:

```bash
export PATH="$HOME/bin:$PATH"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

---

## Fluxo principal (ordem importa)

### Passo 1 — Reduzir TTL do DNS ANTES de tudo

No painel DNS (Hostinger), reduza o TTL para **60 segundos**. Aguarde o TTL atual expirar.

### Passo 2 — Instalar NGINX Ingress Controller

```bash
export PATH="$HOME/bin:$PATH"
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.externalTrafficPolicy=Local \
  --set controller.watchIngressWithoutClass=true \
  --set controller.allowSnippetAnnotations=true \
  --wait --timeout=5m
```

Capture o IP do Ingress:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Passo 3 — Instalar cert-manager

```bash
export PATH="$HOME/bin:$PATH"
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true \
  --wait --timeout=5m
```

### Passo 4 — Criar ClusterIssuer (produção)

Crie `k8s/cluster-issuer.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: SEU_EMAIL@dominio.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            ingressClassName: nginx
```

Aplique:
```bash
kubectl apply -f k8s/cluster-issuer.yaml
kubectl get clusterissuers
```

### Passo 5 — Criar Ingress com TLS

Crie `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: english-jatel-ingress
  namespace: english-jatel
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - learn.jfs-devops.shop
      secretName: english-jatel-tls
  rules:
    - host: learn.jfs-devops.shop
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: english-jatel
                port:
                  number: 80
```

> **IMPORTANTE:** `ssl-redirect: "false"` é OBRIGATÓRIO para que o desafio HTTP-01 funcione. O Let's Encrypt acessa via HTTP na porta 80. Se redirecionar para HTTPS, o challenge falha.

Aplique:
```bash
kubectl apply -f k8s/ingress.yaml
```

### Passo 6 — Atualizar DNS

Registros necessários:
- **Azure DNS** (zona `jfs-devops.shop`): Registro A `learn` → IP do Ingress
- **Hostinger**: A `learn` → IP do Ingress (TTL 60)

```bash
# Atualizar Azure DNS
az network dns record-set a update \
  -g rg-english-jatel \
  -z jfs-devops.shop \
  -n learn \
  --set aRecords[0].ipv4Address=NOVO_IP \
  --set TTL=60
```

Verificar propagação:
```bash
dig @ns1-05.azure-dns.com learn.jfs-devops.shop +short
dig @8.8.8.8 learn.jfs-devops.shop +short
```

### Passo 7 — Validar certificado

```bash
kubectl get certificate,certificaterequest,challenge -n english-jatel
```

O challenge deve ir para `valid` e o Certificate para `READY=True`.

### Passo 8 — Validar HTTPS

```bash
curl -sk https://learn.jfs-devops.shop/api/health
# Esperado: {"status":"ok","llm":true,...}

echo | openssl s_client -connect learn.jfs-devops.shop:443 -servername learn.jfs-devops.shop 2>/dev/null | openssl x509 -noout -subject -issuer -dates
# Esperado: issuer Let's Encrypt, válido por 90 dias
```

---

## Problemas conhecidos e soluções

### 1. Backend Pool vazio (problema mais comum)

**Sintoma:** Ingress mostra IP correto, pods rodando, mas `curl` externo dá timeout.

**Causa:** Modificações manuais no Load Balancer do AKS (regras, probes, frontend IPs) quebram a associação automática do cloud controller. O backend pool fica sem IPs dos nós.

**Diagnóstico:**
```bash
az network lb address-pool show \
  --resource-group MC_<RG>_AKS_<CLUSTER>_<REGIAO> \
  --lb-name kubernetes \
  --name kubernetes \
  -o json | python3 -c "
import json,sys
d=json.load(sys.stdin)
ips = d.get('backendIpConfigurations', [])
print(f'Backend IPs: {len(ips)}')
"
```

**Correção (reinstall NGINX Ingress):**
```bash
# 1. Salvar IP atual (se precisar manter)
CURRENT_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "IP atual: $CURRENT_IP"

# 2. Desinstalar
helm uninstall ingress-nginx -n ingress-nginx

# 3. Aguardar limpeza
sleep 15

# 4. Reinstalar
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.service.type=LoadBalancer \
  --set controller.service.externalTrafficPolicy=Local \
  --wait --timeout=5m

# 5. Capturar NOVO IP (pode ser diferente!)
NEW_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "NOVO IP: $NEW_IP"

# 6. Atualizar DNS para o novo IP
az network dns record-set a update -g <RG> -z <ZONE> -n learn \
  --set aRecords[0].ipv4Address=$NEW_IP --set TTL=60
```

> **ATENÇÃO:** Reinstall do NGINX Ingress gera um NOVO IP público. Atualize TODOS os registros DNS e configure Hostinger.

### 2. DNS conflitante (Hostinger vs Azure DNS)

**Sintoma:** `dig @ns1-05.azure-dns.com` retorna IP correto, mas `dig learn.jfs-devops.shop` retorna IP antigo.

**Causa:** Hostinger tem registro A apontando para IP antigo, sobrescrevendo Azure DNS.

**Correção:** Atualizar o registro A no painel da Hostinger para o novo IP do Ingress.

### 3. Let's Encrypt challenge `invalid` com erro "Timeout during connect"

**Sintoma:** Challenge fica `invalid` com erro:
```
Timeout during connect (likely firewall problem)
```

**Causas possíveis:**
1. Backend pool vazio (ver Problema 1)
2. DNS apontando para IP errado (ver Problema 2)
3. NSG bloqueando porta 80

**Verificar NSG:**
```bash
az network nsg rule list \
  --resource-group MC_<RG>_AKS_<CLUSTER>_<REGIAO> \
  --nsg-name <NSG_NAME> \
  -o json | python3 -c "
import json,sys
for r in sorted(json.load(sys.stdin), key=lambda x: x['priority']):
    if r['direction']=='Inbound' and r['access']=='Allow':
        ports = r.get('destinationPortRange', r.get('destinationPortRanges',[]))
        print(f'P{r[\"priority\"]:3d} Allow {r[\"protocol\"]:4s} {ports}')
"
```

Deve incluir:
```
P500 Allow Tcp  [80, 443]   (do AKS)
```

### 4. Probe HTTP do Azure LB

**Sintoma:** Pods OK, DNS correto, mas tráfego externo cai.

**Diagnóstico:**
```bash
az network lb probe list \
  --resource-group MC_<RG>_AKS_<CLUSTER>_<REGIAO> \
  --lb-name kubernetes \
  -o json | python3 -c "
import json,sys
for p in json.load(sys.stdin):
    print(f\"{p['name']}: {p['protocol']}:{p['port']} {p.get('requestPath','N/A')}\")
"
```

**Correção:**
```bash
# Trocar probe HTTP para TCP
az network lb probe update \
  --resource-group MC_<RG>_AKS_<CLUSTER>_<REGIAO> \
  --lb-name kubernetes \
  --name NOME_DO_PROBE \
  --protocol Tcp \
  --port 80 \
  --path ""
```

### 5. Certificado não renovando

```bash
# Forçar renew
kubectl delete secret <SECRET_NAME> -n <NAMESPACE>
kubectl delete certificaterequest --all -n <NAMESPACE>
# cert-manager recria automaticamente
```

---

## Compatibilidade com Blue-Green

O mecanismo Blue-Green **não é afetado**. O Ingress aponta para o Service, e o selector controla qual slot recebe tráfego:

```
Ingress → Service (selector: app=english-jatel, slot=blue|green) → pods
```

---

## Arquivos gerados por esta skill

| Arquivo | Descrição |
|---|---|
| `k8s/cluster-issuer.yaml` | ClusterIssuer Let's Encrypt prod |
| `k8s/ingress.yaml` | Ingress com TLS |
| `k8s/certificate.yaml` | Certificate resource (opcional) |

## Helm releases

| Release | Namespace | Chart |
|---|---|---|
| `ingress-nginx` | `ingress-nginx` | `ingress-nginx/ingress-nginx` |
| `cert-manager` | `cert-manager` | `jetstack/cert-manager` |

---

## Checklist de deploy

- [ ] TTL DNS reduzido para 60s
- [ ] NGINX Ingress instalado
- [ ] cert-manager instalado
- [ ] ClusterIssuer criado
- [ ] Ingress com TLS e `ssl-redirect: "false"`
- [ ] DNS atualizado (Azure DNS + Hostinger)
- [ ] Propagação DNS verificada (`dig @8.8.8.8`)
- [ ] Challenge Let's Encrypt `valid`
- [ ] Certificate `READY=True`
- [ ] HTTPS funcionando (`curl -sk https://dominio/api/health`)
- [ ] SSL redirect ativado (opcional, após validação)
