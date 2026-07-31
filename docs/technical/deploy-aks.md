# Deploy Azure Kubernetes Service (AKS)

Guia completo para deploy do English JATEL no AKS com Terraform, NGINX Ingress e TLS.

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Cloud                          │
├─────────────────────────────────────────────────────────┤
│  Resource Group: rg-english-jatel                       │
│  Region: centralindia                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌─────────────────────────┐    │
│  │  Azure DNS      │    │  AKS Cluster            │    │
│  │  jfs-devops.shop│───▶│  aks-english-jatel      │    │
│  └─────────────────┘    │  v1.35.6                │    │
│                         │  B2als_v2 (2vCPU/4GB)   │    │
│                         └───────────┬─────────────┘    │
│                                     │                   │
│  ┌──────────────────────────────────▼────────────────┐  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  NGINX Ingress Controller                   │  │  │
│  │  │  IP: 4.247.210.38                           │  │  │
│  │  └─────────────────┬───────────────────────────┘  │  │
│  │                    │                              │  │
│  │  ┌─────────────────▼───────────────────────────┐  │  │
│  │  │  cert-manager + Let's Encrypt               │  │  │
│  │  │  TLS: learn.jfs-devops.shop                 │  │  │
│  │  └─────────────────┬───────────────────────────┘  │  │
│  │                    │                              │  │
│  │  ┌─────────────────▼───────────────────────────┐  │  │
│  │  │  Service: english-jatel                     │  │  │
│  │  │  ClusterIP: 10.0.28.149:80                  │  │  │
│  │  └─────────────────┬───────────────────────────┘  │  │
│  │                    │                              │  │
│  │  ┌─────────────────▼───────────────────────────┐  │  │
│  │  │  Deployment: english-jatel-blue             │  │  │
│  │  │  Image: updateinformatica/english-jatel:latest│ │  │
│  │  │  Port: 8000                                 │  │  │
│  │  └─────────────────┬───────────────────────────┘  │  │
│  │                    │                              │  │
│  │  ┌─────────────────▼───────────────────────────┐  │  │
│  │  │  PVC: english-jatel-data (1Gi)              │  │  │
│  │  │  Mount: /app/data                           │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Recursos Azure

| Recurso | Nome | Status |
|---|---|---|
| Resource Group | `rg-english-jatel` | ✅ Criado |
| AKS Cluster | `aks-english-jatel` | ✅ Rodando |
| DNS Zone | `jfs-devops.shop` | ✅ Criado |
| Public IP | `pip-ingress-english-jatel` | ✅ Criado |
| Role Assignment | Network Contributor | ✅ Atribuído |
| Role Assignment | DNS Zone Contributor | ✅ Atribuído |

## Configuração AKS

| Parâmetro | Valor |
|---|---|
| Região | `centralindia` |
| Kubernetes | `v1.35.6` |
| SKU Tier | `Free` |
| VM Size | `Standard_B2als_v2` |
| vCPU | 2 |
| RAM | 4GB |
| Disco OS | 30GB |
| Auto-scaling | ✅ (1-2 nodes) |
| Network Plugin | `kubenet` |
| Network Policy | `calico` |

## Segurança

### Pod Security
- `runAsNonRoot: true`
- `runAsUser: 10001` (appuser)
- `readOnlyRootFilesystem: true`
- `allowPrivilegeEscalation: false`
- Capabilities: `drop: ALL`

### Secrets Management (Dev)
- `kubectl create secret` para secrets em texto plano
- Arquivo: `k8s/secret.yaml`

### TLS/HTTPS
- cert-manager + Let's Encrypt
- Auto-renovação automática
- ClusterIssuer: `letsencrypt-prod`

## Blue/Green Deployment

### Estrutura

```
english-jatel-blue  (slot: blue)   ← ATIVO
english-jatel-green (slot: green)  ← STANDBY
```

### Promover Green

```bash
# 1. Atualizar imagem do green
kubectl set image deployment/english-jatel-green \
    english-jatel=updateinformatica/english-jatel:latest \
    -n english-jatel

# 2. Escalar green para 1
kubectl scale deployment/english-jatel-green --replicas=1 -n english-jatel

# 3. Aguardar ficar pronto
kubectl rollout status deployment/english-jatel-green -n english-jatel

# 4. Virar Service para green
kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"green"}}}'

# 5. Escalar blue para 0
kubectl scale deployment/english-jatel-blue --replicas=0 -n english-jatel
```

### Rollback

```bash
# Voltar para blue
kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"blue"}}}'

# Escalar blue para 1
kubectl scale deployment/english-jatel-blue --replicas=1 -n english-jatel
```

## Comandos Úteis

### Status
```bash
# Pods
kubectl get pods -n english-jatel

# Services
kubectl get svc -n english-jatel

# Ingress
kubectl get ingress -n english-jatel

# Certificates
kubectl get certificate -n english-jatel

# Nodes
kubectl get nodes

# All resources
kubectl get all -n english-jatel
```

### Logs
```bash
# App logs
kubectl logs -l app=english-jatel -n english-jatel

# Ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager
```

### Debug
```bash
# Describe pod
kubectl describe pod -l app=english-jatel -n english-jatel

# Describe ingress
kubectl describe ingress english-jatel-ingress -n english-jatel

# Describe certificate
kubectl describe certificate english-jatel-tls -n english-jatel

# Check events
kubectl get events -n english-jatel --sort-by='.lastTimestamp'
```

### Port Forward (acesso local)
```bash
# App
kubectl port-forward svc/english-jatel 8000:80 -n english-jatel

# Acessar
curl http://localhost:8000/api/health
```

## Troubleshooting

### Pod não inicia
```bash
kubectl describe pod -l app=english-jatel -n english-jatel
# Verificar: ImagePullBackOff, CrashLoopBackOff, OOMKilled
```

### Certificado não emite
```bash
kubectl describe certificate english-jatel-tls -n english-jatel
kubectl get challenge -n english-jatel
kubectl get order -n english-jatel
# Causa comum: DNS não configurado no registrador
```

### Ingress não acessível
```bash
kubectl get ingress -n english-jatel
kubectl describe ingress english-jatel-ingress -n english-jatel
# Verificar: ADDRESS, HOSTS, TLS
```

## DNS Configuration

### Name Servers (configurar no registrador)
```
ns1-05.azure-dns.com.
ns2-05.azure-dns.net.
ns3-05.azure-dns.org.
ns4-05.azure-dns.info.
```

### Records necessários
| Tipo | Nome | Valor |
|---|---|---|
| A | `learn` | `4.247.210.38` |
| CNAME | `www` | `learn.jfs-devops.shop` |

## Produção (futuro)

### Prometheus
```bash
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    -f k8s/production/prometheus/helm-values.yaml
```

### ArgoCD
```bash
helm upgrade --install argocd argo/argo-cd \
    --namespace argocd \
    --create-namespace \
    -f k8s/production/argocd/helm-values.yaml
```

## Estimativa de Custos

| Recurso | Custo Mensal |
|---|---|
| AKS Free Tier | $0 |
| Standard_B2als_v2 | ~$15 |
| Azure DNS Zone | $0.50 |
| Let's Encrypt | $0 |
| NGINX Ingress | $0 |
| cert-manager | $0 |
| **Total** | **~$15.50** |
