# Azure Migration Guide - JATEL-IA

> **Tipo:** Documentação Técnica  
> **Última atualização:** 2026-09-01  
> **Revisão:** 1.0

---

## Visão Geral

Este guia documenta o processo completo de migração da infraestrutura Azure JATEL-IA para uma nova conta Azure. Devido às limitações da Free tier, é necessário criar uma nova conta a cada 30 dias e migrar todos os recursos.

---

## Pré-requisitos

### Conta Azure
- Nova conta Azure criada
- Subscription ID anotado
- Acesso `az login` configurado

### Ferramentas
- Azure CLI (`az`)
- Terraform >= 1.5.0
- kubectl
- Helm >= 3.0

### Informações Necessárias
- **Subscription ID** da nova conta
- **OPENROUTER_API_KEY** (para LLM)
- **SESSION_SECRET** (para autenticação)

---

## Estrutura de Arquivos

```
projeto-aiops/
├── terraform/
│   ├── main.tf              # Recursos Azure principais
│   ├── variables.tf         # Variáveis (inclui subscription_id)
│   ├── providers.tf         # Providers Terraform
│   └── outputs.tf           # Outputs (IP, DNS, URLs)
├── k8s/
│   ├── secret.yaml          # Secrets English JATEL
│   └── ...                  # Outros manifests
├── web-britlearnacademy/
│   ├── Web-Site/k8s/
│   │   └── secret.yaml      # Secrets Britlearn Site
│   └── Web-APP/k8s/
│       └── secret.yaml      # Secrets Britlearn App
└── scripts/
    ├── deploy-aks.sh        # Script de deploy principal
    └── setup-new-account.sh # Script completo de setup
```

---

## Processo de Migração

### Passo 1: Login na Nova Conta

```bash
# Fazer login
az login

# Verificar subscription
az account show

# Trocar para subscription correta
az account set --subscription <SUBSCRIPTION_ID>
```

### Passo 2: Backup do Estado Atual

```bash
# Criar backup
mkdir -p repo-backup
cp -r terraform/ repo-backup/
cp -r k8s/ repo-backup/
cp -r web-britlearnacademy/ repo-backup/
```

### Passo 3: Limpar Estado Terraform

```bash
# IMPORTANTE: O state do Terraform está vinculado à subscription antiga
cd terraform
rm -f terraform.tfstate terraform.tfstate.backup
rm -rf .terraform
```

### Passo 4: Executar Setup Completo

```bash
# Opção 1: Script automatizado
./scripts/setup-new-account.sh

# Opção 2: Passo a passo manual
cd terraform
terraform init
terraform apply -var="subscription_id=<SUBSCRIPTION_ID>"

# Configurar kubectl
az aks get-credentials --resource-group rg-english-jatel --name aks-english-jatel

# Instalar componentes
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"="rg-english-jatel"

helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true
```

### Passo 5: Criar Secrets

```bash
# English JATEL
kubectl apply -f k8s/secret.yaml

# Britlearn Site
kubectl apply -f web-britlearnacademy/Web-Site/k8s/secret.yaml

# Britlearn App
kubectl apply -f web-britlearnacademy/Web-APP/k8s/secret.yaml
```

### Passo 6: Deploy das Aplicações

```bash
# English JATEL
kubectl apply -k k8s/

# Britlearn Site
kubectl apply -k web-britlearnacademy/Web-Site/k8s/

# Britlearn App
kubectl apply -k web-britlearnacademy/Web-APP/k8s/
```

### Passo 7: Configurar DNS

```bash
# Obter IP público
IP=$(terraform output -raw public_ip_address)

# Criar records DNS
az network dns record-set a add-record -g rg-english-jatel -z jfs-devops.shop -n learn -a $IP
az network dns record-set a add-record -g rg-english-jatel -z britlearnacademy.online -n @ -a $IP
```

### Passo 8: Configurar Role Assignments

```bash
# Obter principal_id do AKS
PRINCIPAL_ID=$(az aks show --resource-group rg-english-jatel --name aks-english-jatel --query "identity.principalId" -o tsv)

# Criar role assignments
az role assignment create --assignee $PRINCIPAL_ID --role "Network Contributor" --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-english-jatel

DNS_ZONE_ID=$(az network dns zone show --resource-group rg-english-jatel --name jfs-devops.shop --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "DNS Zone Contributor" --scope $DNS_ZONE_ID

DNS_ZONE_ID=$(az network dns zone show --resource-group rg-english-jatel --name britlearnacademy.online --query "id" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "DNS Zone Contributor" --scope $DNS_ZONE_ID
```

---

## Recursos Criados

### Azure Resources

| Recurso | Nome | Propósito |
|---|---|---|
| Resource Group | `rg-english-jatel` | Container lógico |
| AKS Cluster | `aks-english-jatel` | Orquestração de containers |
| Public IP | `pip-ingress-jatel-*` | IP estático para Ingress |
| DNS Zone | `jfs-devops.shop` | Domínio principal |
| DNS Zone | `britlearnacademy.online` | Domínio secundário |

### Kubernetes Namespaces

| Namespace | Aplicação |
|---|---|
| `english-jatel` | English JATEL |
| `britlearn-academy-site` | Britlearn Academy Site |
| `britlearn-academy-app` | Britlearn Academy App |
| `ingress-nginx` | NGINX Ingress Controller |
| `cert-manager` | cert-manager |

### URLs de Acesso

| Aplicação | URL |
|---|---|
| English JATEL | https://learn.jfs-devops.shop |
| Britlearn Academy | https://britlearnacademy.online |
| Britlearn App | https://britlearnacademy.online/app |

---

## Troubleshooting

### Problema: NGINX Ingress não obtém IP externo

**Causa:** Role assignment incorreto ou IP público com nome duplicado

**Solução:**
```bash
# Verificar role assignments
az role assignment list --assignee <PRINCIPAL_ID>

# Recriar service com IP específico
kubectl delete svc -n ingress-nginx ingress-nginx-controller
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-resource-group: rg-english-jatel
    service.beta.kubernetes.io/azure-load-balancer-ipv4: <IP_ADDRESS>
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: https
      port: 443
      targetPort: https
EOF
```

### Problema: Certificate TLS não provisiona

**Causa:** DNS não apontando para IP correto

**Solução:**
```bash
# Verificar resolução DNS
dig @ns1-01.azure-dns.com learn.jfs-devops.shop +short

# Criar record se necessário
az network dns record-set a add-record -g rg-english-jatel -z jfs-devops.shop -n learn -a <IP_ADDRESS>

# Verificar challenges
kubectl get challenges -A
kubectl describe challenge -n english-jatel <CHALLENGE_NAME>
```

### Problema: Erro "AuthorizationFailed" no AKS

**Causa:** Role assignment não propagado

**Solução:**
```bash
# Aguardar propagação (pode levar até 5 minutos)
sleep 300

# Verificar role assignments
az role assignment list --assignee <PRINCIPAL_ID> --query "[].{Role:roleDefinitionName, Scope:scope}"
```

---

## Comandos Úteis

### Status do Cluster

```bash
# Verificar pods
kubectl get pods -A | grep -E "(english-jatel|britlearn)"

# Verificar services
kubectl get svc -A | grep -E "(english-jatel|britlearn)"

# Verificar ingresses
kubectl get ingress -A

# Verificar certificates
kubectl get certificate -A
```

### Logs

```bash
# Logs English JATEL
kubectl logs -n english-jatel deployment/english-jatel-blue

# Logs NGINX Ingress
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Logs cert-manager
kubectl logs -n cert-manager deployment/cert-manager
```

### Reiniciar Aplicações

```bash
# Reiniciar English JATEL
kubectl rollout restart deployment/english-jatel-blue -n english-jatel

# Reiniciar Britlearn Site
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site

# Reiniciar Britlearn App
kubectl rollout restart deployment/britlearn-app-blue -n britlearn-academy-app
```

---

## Custos Estimados

| Recurso | Custo Mensal (Free Tier) |
|---|---|
| AKS Cluster | $0 (Free Tier) |
| DNS Zone | ~$1/mês |
| Public IP | ~$4/mês |
| **Total** | **~$5/mês** |

> **Nota:** Na Free tier do Azure, o AKS é gratuito por 12 meses. Após isso, o custo aumenta para ~$15/mês.

---

## Checklist de Migração

- [ ] Criar nova conta Azure
- [ ] Fazer `az login`
- [ ] Anotar Subscription ID
- [ ] Limpar estado Terraform
- [ ] Executar `setup-new-account.sh`
- [ ] Criar secrets (k8s/secret.yaml)
- [ ] Verificar pods rodando
- [ ] Verificar certificates TLS
- [ ] Testar acesso às URLs
- [ ] Documentar novo IP e DNS nameservers
