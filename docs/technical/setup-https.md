# Setup HTTPS — NGINX Ingress + Let's Encrypt no AKS

## Visão geral

Configura HTTPS completo em aplicações Kubernetes no Azure AKS:
```
DNS → NGINX Ingress (TLS termination) → Service ClusterIP → Pods
```

## Componentes

| Componente | Responsabilidade |
|---|---|
| NGINX Ingress Controller | Reverse proxy, TLS termination, routing |
| cert-manager | Gerencia certificados TLS automaticamente |
| Let's Encrypt | CA gratuita, emite certificados válidos por 90 dias |
| Azure DNS | Resolve domínio para IP do Ingress |
| Hostinger DNS | DNS externo (deve apontar para Azure DNS) |

## Fluxo de uma requisição HTTPS

```
1. Cliente resolve learn.jfs-devops.shop → IP_DO_INGRESS (via Terraform)
2. Conexão TCP na porta 443
3. TLS handshake (certificate Let's Encrypt)
4. NGINX recebe requisição HTTP interna
5. Roteamento via Ingress rules → Service → Pod
```

## Estrutura de arquivos

```
k8s/
├── cluster-issuer.yaml      # ClusterIssuer Let's Encrypt prod
├── ingress.yaml             # Ingress com TLS + ssl-redirect
├── certificate.yaml         # Certificate resource (opcional)
├── deployment-blue.yaml     # App deployment (slot blue)
├── service.yaml             # Service ClusterIP
├── configmap.yaml           # Configurações da app
├── secret.yaml              # Secrets (gitignored)
└── kustomization.yaml       # Agrega todos os manifests
```

## Sequência de deploy

```
1. Instalar NGINX Ingress (Helm)
2. Instalar cert-manager (Helm)
3. Criar ClusterIssuer
4. Criar Ingress com TLS
5. Atualizar DNS (Azure DNS + Hostinger)
6. Validar challenge Let's Encrypt
7. Confirmar HTTPS funcionando
```

## Problemas mais comuns

| # | Problema | Sintoma | Solução |
|---|---------|---------|---------|
| 1 | Backend pool vazio | `curl` timeout, pods OK | Reinstall NGINX Ingress |
| 2 | DNS conflitante | IP antigo em `dig` | Atualizar Hostinger |
| 3 | Challenge invalid | Let's Encrypt timeout | Verificar NSG + DNS |
| 4 | Probe HTTP falha | LB não roteia | Trocar probe para TCP |
| 5 | SSL redirect ativo | HTTP-01 falha | `ssl-redirect: "false"` |

## Comandos essenciais

```bash
# Status do certificado
kubectl get certificate,certificaterequest,challenge -n <NS>

# Logs do NGINX
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50

# Testar HTTPS
curl -sk https://learn.jfs-devops.shop/api/health

# Verificar DNS
dig @8.8.8.8 learn.jfs-devops.shop +short

# Verificar LB probe
az network lb probe list --resource-group MC_<RG> --lb-name kubernetes -o table
```

## Referências

- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager](https://cert-manager.io/docs/)
- [Let's Encrypt HTTP-01](https://letsencrypt.org/docs/challenge-types/http-01-challenge/)
- [Azure Load Balancer probes](https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-overview#probe)
