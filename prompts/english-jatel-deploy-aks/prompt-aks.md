# Prompt: Deploy English JATEL no AKS

## Contexto

O English JATEL é um app de aprendizado de idiomas multilíngue (EN/ES/FR/IT/DE) construído com FastAPI + frontend vanilla. O app precisa ser deployado no Azure Kubernetes Service (AKS) usando Terraform para provisionamento de infraestrutura e manifests K8s para o app.

## Arquitetura

- **Região**: centralindia (mais barata)
- **VM**: Standard_B2als_v2 (2vCPU, 4GB RAM)
- **Ingress**: NGINX Ingress Controller
- **TLS**: cert-manager + Let's Encrypt
- **Domínio**: learn.jfs-devops.shop
- **Blue/Green**: Deploy com rotação entre slots

## Arquivos

```
terraform/
├── providers.tf      # Providers Azure, K8s, Helm
├── variables.tf      # Variáveis configuráveis
├── main.tf          # AKS, DNS Zone, IP, Roles
└── outputs.tf       # Saídas (kubeconfig, IP, URL)

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
```

## Comandos de Deploy

### 1. Provisionar Infraestrutura
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 2. Configurar kubectl
```bash
az aks get-credentials --resource-group rg-english-jatel --name aks-english-jatel
```

### 3. Instalar NGINX Ingress
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer
```

### 4. Instalar cert-manager
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true
```

### 5. Configurar Secrets
```bash
# Editar k8s/secret.yaml com valores reais
vim k8s/secret.yaml
```

### 6. Deploy do App
```bash
kubectl apply -k k8s/
```

### 7. Configurar DNS
```bash
# Atualizar name servers no registrador do domínio
az network dns zone show --resource-group rg-english-jatel --name jfs-devops.shop --query "nameServers" -o tsv
```

## Blue/Green Deployment

### Promover Green
```bash
kubectl set image deployment/english-jatel-green \
    english-jatel=updateinformatica/english-jatel:latest \
    -n english-jatel

kubectl scale deployment/english-jatel-green --replicas=1 -n english-jatel

kubectl rollout status deployment/english-jatel-green -n english-jatel

kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"green"}}}'

kubectl scale deployment/english-jatel-blue --replicas=0 -n english-jatel
```

### Rollback
```bash
kubectl patch service english-jatel -n english-jatel \
    -p '{"spec":{"selector":{"slot":"blue"}}}'

kubectl scale deployment/english-jatel-blue --replicas=1 -n english-jatel
```

## Verificação

```bash
# Status geral
kubectl get all -n english-jatel

# Pods
kubectl get pods -n english-jatel

# Ingress
kubectl get ingress -n english-jatel

# Certificado
kubectl get certificate -n english-jatel

# Health check
curl https://learn.jfs-devops.shop/api/health
```

## Troubleshooting

### Pod não inicia
```bash
kubectl describe pod -l app=english-jatel -n english-jatel
kubectl logs -l app=english-jatel -n english-jatel
```

### Certificado não emite
```bash
kubectl describe certificate english-jatel-tls -n english-jatel
kubectl get challenge -n english-jatel
kubectl get order -n english-jatel
```

### Ingress não acessível
```bash
kubectl describe ingress english-jatel-ingress -n english-jatel
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```
