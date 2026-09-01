#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[SETUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

AZURE_SUBSCRIPTION="${AZURE_SUBSCRIPTION:-0a2d7603-ccc0-4bb9-9c70-0794abca2a6d}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SETUP NOVA CONTA AZURE - JATEL-IA     ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Subscription: $AZURE_SUBSCRIPTION"
echo ""

# 1. Verificar pré-requisitos
log "Verificando pré-requisitos..."
command -v terraform >/dev/null 2>&1 || error "Terraform não encontrado"
command -v az >/dev/null 2>&1 || error "Azure CLI não encontrado"
command -v kubectl >/dev/null 2>&1 || error "kubectl não encontrado"
command -v helm >/dev/null 2>&1 || error "Helm não encontrado"
log "Pré-requisitos OK"

# 2. Verificar login Azure
log "Verificando login Azure..."
az account show >/dev/null 2>&1 || error "Não está logado no Azure. Execute: az login"

current_sub=$(az account show --query "id" -o tsv)
if [ "$current_sub" != "$AZURE_SUBSCRIPTION" ]; then
    warn "Trocando para a subscription correta..."
    az account set --subscription "$AZURE_SUBSCRIPTION"
fi

sub_name=$(az account show --query "name" -o tsv)
log "Logado como: $sub_name ($AZURE_SUBSCRIPTION)"

# 3. Verificar se já existem recursos
log "Verificando se já existem recursos..."
existing_rg=$(az group list --query "[?name=='rg-english-jatel'].name" -o tsv)
if [ -n "$existing_rg" ]; then
    warn "Resource Group 'rg-english-jatel' já existe!"
    warn "Isso pode causar conflitos com o Terraform."
    read -p "Deseja continuar mesmo assim? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        error "Setup cancelado pelo usuário"
    fi
fi

# 4. Inicializar Terraform
log "Inicializando Terraform..."
cd "$PROJECT_ROOT/terraform"
terraform init

# 5. Criar infraestrutura
log "Criando infraestrutura Azure..."
terraform apply -auto-approve -var="subscription_id=$AZURE_SUBSCRIPTION"

# 6. Configurar kubectl
log "Configurando kubectl..."
eval $(terraform output -raw kube_config_command)
log "kubectl configurado"

# 7. Instalar NGINX Ingress
log "Instalando NGINX Ingress Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"="rg-english-jatel"

log "Aguardando NGINX Ingress ficar pronto..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=300s

# 8. Instalar cert-manager
log "Instalando cert-manager..."
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true

log "Aguardando cert-manager ficar pronto..."
kubectl wait --namespace cert-manager \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=webhook \
    --timeout=300s

# 9. Verificar secrets
log "Verificando secrets..."
cd "$PROJECT_ROOT"

if [ ! -f "k8s/secret.yaml" ]; then
    warn "k8s/secret.yaml não encontrado!"
    warn "Copie k8s/secret.yaml.example para k8s/secret.yaml e preencha os valores"
fi

if [ ! -f "web-britlearnacademy/Web-Site/k8s/secret.yaml" ]; then
    warn "web-britlearnacademy/Web-Site/k8s/secret.yaml não encontrado!"
    warn "Copie o secret.example e preencha os valores"
fi

if [ ! -f "web-britlearnacademy/Web-APP/k8s/secret.yaml" ]; then
    warn "web-britlearnacademy/Web-APP/k8s/secret.yaml não encontrado!"
    warn "Copie o secret.example e preencha os valores"
fi

# 10. Aplicar manifests K8s
log "Aplicando manifests English JATEL..."
kubectl apply -k k8s/

log "Aplicando manifests Britlearn Site..."
kubectl apply -k web-britlearnacademy/Web-Site/k8s/

log "Aplicando manifests Britlearn App..."
kubectl apply -k web-britlearnacademy/Web-APP/k8s/

# 11. Aguardar pods
log "Aguardando pods ficarem prontos..."
kubectl wait --namespace english-jatel \
    --for=condition=ready pod \
    --selector=app=english-jatel \
    --timeout=300s

kubectl wait --namespace britlearn-academy-site \
    --for=condition=ready pod \
    --selector=app=britlearn-site \
    --timeout=300s

kubectl wait --namespace britlearn-academy-app \
    --for=condition=ready pod \
    --selector=app=britlearn-app \
    --timeout=300s

# 12. Mostrar status
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SETUP CONCLUÍDO COM SUCESSO!          ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

log "IP Público do Ingress:"
terraform output public_ip_address

echo ""
log "Name servers (jfs-devops.shop) - configurar no registrador:"
terraform output dns_zone_name_servers

echo ""
log "Name servers (britlearnacademy.online) - configurar no registrador:"
terraform output britlearn_dns_zone_name_servers

echo ""
log "URLs da aplicação:"
log "  English JATEL: https://learn.jfs-devops.shop"
log "  Britlearn Academy: https://britlearnacademy.online"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PRÓXIMOS PASSOS:                      ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "1. Configure os nameservers no registrador de domínio"
echo "2. Aguarde a propagação do DNS (pode levar até 48h)"
echo "3. Verifique os certificados TLS:"
echo "   kubectl get certificate -A"
echo "4. Verifique o status do deploy:"
echo "   ./scripts/deploy-aks.sh k8s-status"
echo ""
