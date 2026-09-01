---
description: Migração automatizada da infraestrutura Azure JATEL-IA para nova conta. Setup completo com Terraform, Kubernetes, DNS e certificates TLS. USE PARA: migrar Azure, nova conta Azure, setup Azure, recriar infraestrutura, mudar subscription, atualizar IP público. DO NOT USE PARA: deploy de aplicações (use aks-deploy), configuração de HTTPS (use setup-https).
---

# Azure Migration Skill

## Visão Geral

Esta skill automatiza o processo de migração da infraestrutura Azure JATEL-IA para uma nova conta Azure. Projetada para migrações mensais devido às limitações da Free tier.

## Quando Usar

- Criar nova conta Azure e migrar infraestrutura
- Atualizar IP público após criação de nova conta
- Recriar recursos Azure do zero
- Trocar de subscription Azure

## Fluxo de Trabalho

### 1. Preparação

```bash
# Verificar login atual
az account show

# Fazer login na nova conta (se necessário)
az login

# Definir subscription
az account set --subscription <SUBSCRIPTION_ID>
```

### 2. Backup

```bash
# Criar backup do estado atual
./scripts/backup-azure.sh
```

### 3. Limpar Estado Terraform

```bash
# IMPORTANTE: O state está vinculado à subscription antiga
cd terraform
rm -f terraform.tfstate terraform.tfstate.backup
rm -rf .terraform
```

### 4. Executar Setup

```bash
# Opção completa (recomendado)
./scripts/setup-new-account.sh

# Ou passo a passo
./scripts/deploy-aks.sh setup-completo
```

### 5. Criar Secrets

```bash
# Verificar se secrets existem
ls -la k8s/secret.yaml
ls -la web-britlearnacademy/Web-Site/k8s/secret.yaml
ls -la web-britlearnacademy/Web-APP/k8s/secret.yaml

# Se não existirem, criar a partir dos examples
cp k8s/secret.yaml.example k8s/secret.yaml
# Editar com valores reais
```

### 6. Configurar DNS

```bash
# Obter IP público
IP=$(cd terraform && terraform output -raw public_ip_address)

# Criar records DNS
az network dns record-set a add-record -g rg-english-jatel -z jfs-devops.shop -n learn -a $IP
az network dns record-set a add-record -g rg-english-jatel -z britlearnacademy.online -n @ -a $IP
```

### 7. Verificar Status

```bash
# Verificar todos os componentes
./scripts/deploy-aks.sh k8s-status
```

## Arquivos Importantes

| Arquivo | Propósito |
|---|---|
| `terraform/variables.tf` | Variável `subscription_id` |
| `terraform/main.tf` | Recursos Azure |
| `scripts/setup-new-account.sh` | Script de setup completo |
| `scripts/deploy-aks.sh` | Script de deploy |
| `k8s/secret.yaml` | Secrets English JATEL |
| `web-britlearnacademy/*/k8s/secret.yaml` | Secrets Britlearn |

## Comandos Rápidos

```bash
# Status completo
./scripts/deploy-aks.sh k8s-status

# Verificar certificates
kubectl get certificate -A

# Verificar DNS
dig @ns1-01.azure-dns.com learn.jfs-devops.shop +short

# Verificar pods
kubectl get pods -A | grep -E "(english-jatel|britlearn)"
```

## Troubleshooting

### NGINX Ingress não obtém IP

```bash
# Verificar role assignments
PRINCIPAL_ID=$(az aks show --resource-group rg-english-jatel --name aks-english-jatel --query "identity.principalId" -o tsv)
az role assignment list --assignee $PRINCIPAL_ID
```

### Certificate TLS não provisiona

```bash
# Verificar DNS
dig @ns1-01.azure-dns.com learn.jfs-devops.shop +short

# Verificar challenges
kubectl get challenges -A
```

### Erro de autorização

```bash
# Recriar role assignments
PRINCIPAL_ID=$(az aks show --resource-group rg-english-jatel --name aks-english-jatel --query "identity.principalId" -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --role "Network Contributor" --scope /subscriptions/<SUB_ID>/resourceGroups/rg-english-jatel
```

## URLs de Produção

| Aplicação | URL |
|---|---|
| English JATEL | https://learn.jfs-devops.shop |
| Britlearn Academy | https://britlearnacademy.online |

## Referências

- **Documentação completa:** `docs/technical/azure-migration.md`
- **Script principal:** `scripts/setup-new-account.sh`
- **Terraform:** `terraform/`
