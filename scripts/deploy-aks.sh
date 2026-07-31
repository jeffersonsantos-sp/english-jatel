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

usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  terraform-init    - Inicializa Terraform"
    echo "  terraform-plan    - Plano de execução"
    echo "  terraform-apply   - Aplica infraestrutura"
    echo "  terraform-destroy - Destroi infraestrutura"
    echo "  k8s-deploy        - Deploy dos manifests K8s"
    echo "  k8s-status        - Status do deploy"
    echo "  setup-completo    - Setup completo (Terraform + K8s)"
    exit 1
}

check_prereqs() {
    command -v terraform >/dev/null 2>&1 || error "Terraform não encontrado. Instale: https://developer.hashicorp.com/terraform/install"
    command -v az >/dev/null 2>&1 || error "Azure CLI não encontrado. Instale: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    command -v kubectl >/dev/null 2>&1 || error "kubectl não encontrado. Instale: https://kubernetes.io/docs/tasks/tools/"
    command -v helm >/dev/null 2>&1 || error "Helm não encontrado. Instale: https://helm.sh/docs/intro/install/"
    log "Prerequisites OK"
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
    terraform plan
}

terraform_apply() {
    log "Aplicando infraestrutura..."
    cd "$PROJECT_ROOT/terraform"
    terraform apply -auto-approve
    log "Infraestrutura criada!"
    
    log "Configurando kubectl..."
    eval $(terraform output -raw kube_config_command)
    log "kubectl configurado"
    
    log "Name servers para configurar no registrador:"
    terraform output dns_zone_name_servers
}

terraform_destroy() {
    warn "Destruindo infraestrutura..."
    cd "$PROJECT_ROOT/terraform"
    terraform destroy -auto-approve
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
    
    log "Aplicando secrets..."
    warn "ATENÇÃO: Edite k8s/secret.yaml com seus valores reais antes de aplicar!"
    warn "Execute: kubectl apply -f k8s/secret.yaml"
    
    log "Aplicando manifests K8s..."
    cd "$PROJECT_ROOT"
    kubectl apply -k k8s/
    log "Manifests aplicados"
    
    log "Aguardando pods ficarem prontos..."
    kubectl wait --namespace english-jatel \
        --for=condition=ready pod \
        --selector=app=english-jatel \
        --timeout=300s
    log "Pods prontos"
    
    log "Verificando certificado TLS..."
    kubectl get certificate -n english-jatel
}

k8s_status() {
    log "Status do namespace english-jatel:"
    kubectl get all -n english-jatel
    
    log "Ingress:"
    kubectl get ingress -n english-jatel
    
    log "Certificates:"
    kubectl get certificate -n english-jatel
    
    log "Pods prontos:"
    kubectl get pods -n english-jatel -o wide
}

setup_completo() {
    terraform_init
    terraform_apply
    k8s_deploy
    log "Setup completo! Acesse: https://learn.jfs-devops.shop"
}

case "${1:-}" in
    terraform-init)    check_prereqs; terraform_init ;;
    terraform-plan)    check_prereqs; terraform_plan ;;
    terraform-apply)   check_prereqs; terraform_apply ;;
    terraform-destroy) check_prereqs; terraform_destroy ;;
    k8s-deploy)        check_prereqs; k8s_deploy ;;
    k8s-status)        check_prereqs; k8s_status ;;
    setup-completo)    check_prereqs; setup_completo ;;
    *)                 usage ;;
esac
