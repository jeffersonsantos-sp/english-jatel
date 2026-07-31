# AKS Deploy Skill

Deploy English JATEL to Azure Kubernetes Service (AKS) using Terraform + K8s manifests.

## Trigger

Use when the user asks to:
- Deploy to AKS/Azure Kubernetes
- Provision infrastructure with Terraform
- Setup HTTPS/TLS on AKS
- Configure Ingress on Azure
- Manage AKS clusters
- Blue/Green deployment on AKS

## Prerequisites

- Azure CLI (`az`) logged in
- Terraform >= 1.5.0
- kubectl configured
- Helm 3 installed
- Domain configured (or Azure DNS Zone)

## Architecture

```
┌─────────────────────────────────────┐
│  Azure DNS Zone                     │
│  jfs-devops.shop                    │
├─────────────────────────────────────┤
│  AKS Cluster (centralindia)         │
│  Standard_B2als_v2 (2vCPU/4GB)      │
├─────────────────────────────────────┤
│  NGINX Ingress + cert-manager       │
│  english-jatel (blue/green)         │
│  PVC 1Gi                            │
└─────────────────────────────────────┘
```

## Workflow

### 1. Provision Infrastructure (Terraform)

```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Resources created:
- `azurerm_resource_group` - Resource group
- `azurerm_kubernetes_cluster` - AKS cluster (Free tier)
- `azurerm_dns_zone` - DNS zone for domain
- `azurerm_public_ip` - Public IP for Ingress
- `azurerm_role_assignment` - Network + DNS Contributor

### 2. Configure kubectl

```bash
az aks get-credentials --resource-group rg-english-jatel --name aks-english-jatel
```

### 3. Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer
```

### 4. Install cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true
```

### 5. Configure Secrets

Edit `k8s/secret.yaml` with real values:
- `OPENROUTER_API_KEY` - From ~/.bashrc
- `SESSION_SECRET` - Generate with `openssl rand -hex 32`
- `ADMIN_USER` - Admin username
- `ADMIN_PASS` - Admin password

### 6. Deploy Application

```bash
kubectl apply -k k8s/
```

### 7. Configure DNS

Update name servers at domain registrar:
```
ns1-05.azure-dns.com.
ns2-05.azure-dns.net.
ns3-05.azure-dns.org.
ns4-05.azure-dns.info.
```

### 8. Verify

```bash
# Check pods
kubectl get pods -n english-jatel

# Check ingress
kubectl get ingress -n english-jatel

# Check certificate
kubectl get certificate -n english-jatel

# Check app health
curl https://learn.jfs-devops.shop/api/health
```

## Blue/Green Deployment

### Promote Green to Active

```bash
# 1. Update green deployment with new image
kubectl set image deployment/english-jatel-green \
    english-jatel=updateinformatica/english-jatel:latest \
    -n english-jatel

# 2. Scale green to 1
kubectl scale deployment/english-jatel-green --replicas=1 -n english-jatel

# 3. Wait for green to be ready
kubectl rollout status deployment/english-jatel-green -n english-jatel

# 4. Switch service to green
kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"green"}}}'

# 5. Scale down blue
kubectl scale deployment/english-jatel-blue --replicas=0 -n english-jatel
```

### Rollback

```bash
# Switch back to blue
kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"blue"}}}'

# Scale up blue
kubectl scale deployment/english-jatel-blue --replicas=1 -n english-jatel
```

## Production Add-ons

### Prometheus (Monitoring)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    -f k8s/production/prometheus/helm-values.yaml
```

### ArgoCD (GitOps)

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm upgrade --install argocd argo/argo-cd \
    --namespace argocd \
    --create-namespace \
    -f k8s/production/argocd/helm-values.yaml
```

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -l app=english-jatel -n english-jatel
kubectl logs -l app=english-jatel -n english-jatel
```

### Certificate not issued
```bash
kubectl describe certificate english-jatel-tls -n english-jatel
kubectl get challenge -n english-jatel
kubectl get order -n english-jatel
```

### Ingress not accessible
```bash
kubectl get ingress -n english-jatel
kubectl describe ingress english-jatel-ingress -n english-jatel
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Files

```
terraform/
├── providers.tf      # Terraform providers
├── variables.tf      # Configurable variables
├── main.tf          # AKS, DNS, IP, Roles
└── outputs.tf       # Cluster info, IP, URL

k8s/
├── namespace.yaml
├── configmap.yaml
├── pvc.yaml
├── deployment-blue.yaml
├── deployment-green.yaml
├── service.yaml
├── ingress.yaml
├── cluster-issuer.yaml
├── secret.yaml
└── kustomization.yaml

k8s/production/
├── prometheus/
│   ├── namespace.yaml
│   ├── helm-values.yaml
│   └── alerting-rules.yaml
└── argocd/
    ├── namespace.yaml
    ├── helm-values.yaml
    └── app-manifest.yaml
```

## Cost Estimate

| Resource | Cost |
|---|---|
| AKS Free Tier | $0/month |
| Standard_B2als_v2 | ~$15/month |
| Azure DNS Zone | $0.50/month |
| Let's Encrypt | $0 (gratuito) |
| NGINX Ingress | $0 (open source) |
| **Total** | **~$15.50/month** |
