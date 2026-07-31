# Prompt: Setup HTTPS no AKS

## Contexto

Você está configurando HTTPS para uma aplicação Kubernetes no Azure AKS. A aplicação já está rodando internamente e acessível via HTTP. Agora precisa adicionar TLS com Let's Encrypt via NGINX Ingress Controller.

## Dados do ambiente

- **Domínio**: `learn.jfs-devops.shop`
- **Região AKS**: `centralindia`
- **Resource Group**: `rg-english-jatel`
- **AKS Cluster**: `aks-english-jatel`
- **Namespace da app**: `english-jatel`
- **Service da app**: `english-jatel` (porta 80 → targetPort 8000)

## Instruções passo a passo

### 1. Instalar NGINX Ingress Controller

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.externalTrafficPolicy=Local \
  --set controller.watchIngressWithoutClass=true \
  --set controller.allowSnippetAnnotations=true \
  --wait --timeout=5m
```

### 2. Capturar IP do Ingress

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

**IMPORTANTE:** Anote este IP. Você vai precisar para DNS.

### 3. Instalar cert-manager

```bash
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true \
  --wait --timeout=5m
```

### 4. Criar ClusterIssuer

Crie `k8s/cluster-issuer.yaml` com o email correto e aplique.

### 5. Criar Ingress com TLS

Crie `k8s/ingress.yaml` com:
- `cert-manager.io/cluster-issuer: letsencrypt-prod`
- `nginx.ingress.kubernetes.io/ssl-redirect: "false"` (OBRIGATÓRIO para HTTP-01)
- TLS hosts apontando para o domínio
- Backend apontando para o Service da app

### 6. Atualizar DNS

- **Azure DNS**: Registro A `learn` → IP do Ingress (TTL 60)
- **Hostinger**: A `learn` → mesmo IP (TTL 60)

### 7. Validar

```bash
# Status
kubectl get certificate,certificaterequest,challenge -n english-jatel

# HTTPS
curl -sk https://learn.jfs-devops.shop/api/health
```

## Troubleshooting

### Se o challenge ficar `invalid`:

1. Verificar DNS: `dig @8.8.8.8 learn.jfs-devops.shop +short`
2. Verificar NSG: porta 80 e 443 abertas
3. Verificar LB probe: `az network lb probe list ...`
4. Verificar backend pool: `az network lb address-pool show ...`

### Se o site ficar inacessível:

1. Verificar pods: `kubectl get pods -n english-jatel`
2. Verificar ingress: `kubectl get ingress -n english-jatel`
3. Verificar serviço: `kubectl get svc -n ingress-nginx`
4. Verificar IP: `kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`

### Se o IP mudou após reinstall:

1. Atualizar Azure DNS
2. Atualizar Hostinger
3. Aguardar propagação (TTL 60s)
4. Limpar cache DNS local: `sudo systemd-resolve --flush-caches`

## Referências

- Skill: `.opencode/setup-https/SKILL.md`
- Docs: `docs/technical/setup-https.md`
- Deploy AKS: `docs/technical/deploy-aks.md`
