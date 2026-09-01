#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

AZURE_SUBSCRIPTION="${AZURE_SUBSCRIPTION:-0a2d7603-ccc0-4bb9-9c70-0794abca2a6d}"

usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  terraform-init    - Inicializa Terraform"
    echo "  terraform-plan    - Plano de execução"
    echo "  terraform-apply   - Aplica infraestrutura"
    echo "  terraform-destroy - Destroi infraestrutura"
    echo "  k8s-deploy        - Deploy dos manifests K8s (todas as apps)"
    echo "  k8s-status        - Status do deploy"
    echo "  setup-completo    - Setup completo (Terraform + K8s)"
    echo "  setup-new-account - Setup completo para nova conta Azure"
    exit 1
}

check_prereqs() {
    command -v terraform >/dev/null 2>&1 || error "Terraform não encontrado. Instale: https://developer.hashicorp.com/terraform/install"
    command -v az >/dev/null 2>&1 || error "Azure CLI não encontrado. Instale: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    command -v kubectl >/dev/null 2>&1 || error "kubectl não encontrado. Instale: https://kubernetes.io/docs/tasks/tools/"
    command -v helm >/dev/null 2>&1 || error "Helm não encontrado. Instale: https://helm.sh/docs/intro/install/"
    log "Prerequisites OK"
}

check_azure_login() {
    az account show >/dev/null 2>&1 || error "Não está logado no Azure. Execute: az login"
    local current_sub=$(az account show --query "id" -o tsv)
    if [ "$current_sub" != "$AZURE_SUBSCRIPTION" ]; then
        warn "Subscription atual: $current_sub"
        warn "Subscription esperada: $AZURE_SUBSCRIPTION"
        warn "Trocando para a subscription correta..."
        az account set --subscription "$AZURE_SUBSCRIPTION"
    fi
    log "Azure login OK (subscription: $AZURE_SUBSCRIPTION)"
}

terraform_init() {
    log "Inicializando Terraform..."
    cd "$PROJECT_ROOT/terraform"
    terraform init
    log "Terraform init completo"
}

terraform_plan() {
    log "Rodando terraform plan..."
    cd "$PROJECT_ROOT/terraform"
    terraform plan -var="subscription_id=$AZURE_SUBSCRIPTION"
}

terraform_apply() {
    log "Aplicando infraestrutura..."
    cd "$PROJECT_ROOT/terraform"
    terraform apply -auto-approve -var="subscription_id=$AZURE_SUBSCRIPTION"
    log "Infraestrutura criada!"
    
    log "Configurando kubectl..."
    eval $(terraform output -raw kube_config_command)
    log "kubectl configurado"
    
    echo ""
    log "Name servers para configurar no registrador (jfs-devops.shop):"
    terraform output dns_zone_name_servers
    echo ""
    log "Name servers para configurar no registrador (britlearnacademy.online):"
    terraform output britlearn_dns_zone_name_servers
}

terraform_destroy() {
    warn "Destruindo infraestrutura..."
    cd "$PROJECT_ROOT/terraform"
    terraform destroy -auto-approve -var="subscription_id=$AZURE_SUBSCRIPTION"
    log "Infraestrutura destruída"
}

install_ingress() {
    log "Instalando NGINX Ingress Controller..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"=$(az group list --query "[?starts_with(name,'rg-english-jatel')].name" -o tsv)
    log "NGINX Ingress instalado"
    
    log "Aguardando IP externo..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    log "Ingress Controller pronto"
}

install_cert_manager() {
    log "Instalando cert-manager..."
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    helm upgrade --install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true
    log "cert-manager instalado"
    
    log "Aguardando cert-manager ficar pronto..."
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=webhook \
        --timeout=300s
    log "cert-manager pronto"
}

k8s_deploy() {
    log "Instalando dependências..."
    install_ingress
    install_cert_manager
    
    log "Verificando secrets..."
    warn "ATENÇÃO: Certifique-se de que os secrets estão criados!"
    warn "Para English JATEL: kubectl apply -f k8s/secret.yaml"
    warn "Para Britlearn Site: kubectl apply -f web-britlearnacademy/Web-Site/k8s/secret.yaml"
    warn "Para Britlearn App: kubectl apply -f web-britlearnacademy/Web-APP/k8s/secret.yaml"
    
    log "Aplicando manifests English JATEL..."
    cd "$PROJECT_ROOT"
    kubectl apply -k k8s/
    log "English JATEL aplicado"
    
    log "Aplicando manifests Britlearn Academy..."
    kubectl apply -k web-britlearnacademy/Web-Site/k8s/
    kubectl apply -k web-britlearnacademy/Web-APP/k8s/
    log "Britlearn Academy aplicado"
    
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
    log "Todos os pods prontos"
    
    log "Verificando certificados TLS..."
    kubectl get certificate -n english-jatel
    kubectl get certificate -n britlearn-academy-site
    kubectl get certificate -n britlearn-academy-app
}

k8s_status() {
    echo ""
    log "=== English JATEL (learn.jfs-devops.shop) ==="
    kubectl get all -n english-jatel
    kubectl get ingress -n english-jatel
    kubectl get certificate -n english-jatel
    
    echo ""
    log "=== Britlearn Site (britlearnacademy.online) ==="
    kubectl get all -n britlearn-academy-site
    kubectl get ingress -n britlearn-academy-site
    kubectl get certificate -n britlearn-academy-site
    
    echo ""
    log "=== Britlearn App (britlearnacademy.online/app) ==="
    kubectl get all -n britlearn-academy-app
    kubectl get ingress -n britlearn-academy-app
    kubectl get certificate -n britlearn-academy-app
    
    echo ""
    log "=== NGINX Ingress ==="
    kubectl get svc -n ingress-nginx
    
    echo ""
    log "=== Cert Manager ==="
    kubectl get pods -n cert-manager
}

setup_completo() {
    terraform_init
    terraform_apply
    k8s_deploy
    echo ""
    log "Setup completo!"
    log "English JATEL: https://learn.jfs-devops.shop"
    log "Britlearn Academy: https://britlearnacademy.online"
}

setup_new_account() {
    log "=== SETUP PARA NOVA CONTA AZURE ==="
    echo ""
    check_azure_login
    setup_completo
    echo ""
    log "=== IMPORTANTE ==="
    log "1. Atualize os nameservers no registrador de domínio"
    log "2. Aguarde a propagação do DNS (pode levar até 48h)"
    log "3. Verifique os certificados TLS: kubectl get certificate -A"
}

case "${1:-}" in
    terraform-init)    check_prereqs; terraform_init ;;
    terraform-plan)    check_prereqs; terraform_plan ;;
    terraform-apply)   check_prereqs; check_azure_login; terraform_apply ;;
    terraform-destroy) check_prereqs; check_azure_login; terraform_destroy ;;
    k8s-deploy)        check_prereqs; k8s_deploy ;;
    k8s-status)        check_prereqs; k8s_status ;;
    setup-completo)    check_prereqs; setup_completo ;;
    setup-new-account) check_prereqs; setup_new_account ;;
    *)                 usage ;;
esac
