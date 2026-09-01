#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BACKUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_ROOT/repo-backup/$TIMESTAMP"

usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  full      - Backup completo (terraform, k8s, web-britlearnacademy)"
    echo "  terraform - Backup apenas do Terraform"
    echo "  k8s       - Backup apenas dos manifests Kubernetes"
    echo "  list      - Listar backups existentes"
    echo "  clean     - Remover backups antigos (mantém últimos 5)"
    exit 1
}

backup_full() {
    log "Criando backup completo..."
    mkdir -p "$BACKUP_DIR/terraform"
    mkdir -p "$BACKUP_DIR/k8s"
    mkdir -p "$BACKUP_DIR/web-britlearnacademy"
    mkdir -p "$BACKUP_DIR/scripts"
    
    # Terraform
    cp -r "$PROJECT_ROOT/terraform/"* "$BACKUP_DIR/terraform/" 2>/dev/null || warn "Nenhum arquivo Terraform encontrado"
    
    # Kubernetes
    cp -r "$PROJECT_ROOT/k8s/"* "$BACKUP_DIR/k8s/" 2>/dev/null || warn "Nenhum manifesto K8s encontrado"
    
    # Web Britlearn Academy
    cp -r "$PROJECT_ROOT/web-britlearnacademy/"* "$BACKUP_DIR/web-britlearnacademy/" 2>/dev/null || warn "Nenhum arquivo Britlearn encontrado"
    
    # Scripts
    cp -r "$PROJECT_ROOT/scripts/"* "$BACKUP_DIR/scripts/" 2>/dev/null || warn "Nenhum script encontrado"
    
    log "Backup completo criado em: $BACKUP_DIR"
}

backup_terraform() {
    log "Criando backup do Terraform..."
    mkdir -p "$BACKUP_DIR/terraform"
    cp -r "$PROJECT_ROOT/terraform/"* "$BACKUP_DIR/terraform/" 2>/dev/null || warn "Nenhum arquivo Terraform encontrado"
    log "Backup do Terraform criado em: $BACKUP_DIR/terraform"
}

backup_k8s() {
    log "Criando backup dos manifests Kubernetes..."
    mkdir -p "$BACKUP_DIR/k8s"
    cp -r "$PROJECT_ROOT/k8s/"* "$BACKUP_DIR/k8s/" 2>/dev/null || warn "Nenhum manifesto K8s encontrado"
    log "Backup dos manifests K8s criado em: $BACKUP_DIR/k8s"
}

list_backups() {
    log "Backups existentes:"
    ls -la "$PROJECT_ROOT/repo-backup/" 2>/dev/null || warn "Nenhum backup encontrado"
}

clean_backups() {
    log "Limpando backups antigos..."
    cd "$PROJECT_ROOT/repo-backup/"
    ls -t | tail -n +6 | xargs -r rm -rf
    log "Backups antigos removidos (mantidos os 5 mais recentes)"
}

case "${1:-}" in
    full)      backup_full ;;
    terraform) backup_terraform ;;
    k8s)       backup_k8s ;;
    list)      list_backups ;;
    clean)     clean_backups ;;
    *)         usage ;;
esac
