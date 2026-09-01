# Prompt: Migração Azure JATEL-IA

> **Versão:** 1.0  
> **Última atualização:** 2026-09-01  
> **Uso:** Migração mensal da infraestrutura Azure para nova conta

---

## Contexto

Você é um assistente especializado em migração de infraestrutura Azure. O projeto JATEL-IA precisa ser migrado para uma nova conta Azure a cada 30 dias devido às limitações da Free tier.

## Tarefa

Realizar a migração completa da infraestrutura Azure JATEL-IA para uma nova conta, garantindo:
1. Todos os recursos sejam criados corretamente
2. As aplicações continuem acessíveis
3. Os certificates TLS sejam renovados
4. O DNS seja atualizado

## Informações Necessárias

Antes de iniciar, colete as seguintes informações:

```
1. Subscription ID da nova conta Azure
2. OPENROUTER_API_KEY (para LLM)
3. SESSION_SECRET (para autenticação)
4. Confirmar que os secrets já existem
```

## Fluxo de Execução

### Passo 1: Verificar Login

```bash
# Verificar login atual
az account show

# Se não estiver logado, fazer login
az login

# Trocar subscription
az account set --subscription <SUBSCRIPTION_ID>
```

### Passo 2: Backup

```bash
# Criar backup
./scripts/backup-azure.sh
```

### Passo 3: Limpar Estado Terraform

```bash
# IMPORTANTE: O state está vinculado à subscription antiga
cd terraform
rm -f terraform.tfstate terraform.tfstate.backup
rm -rf .terraform
```

### Passo 4: Executar Setup

```bash
# Executar setup completo
./scripts/setup-new-account.sh
```

### Passo 5: Configurar DNS

```bash
# Obter IP público
IP=$(cd terraform && terraform output -raw public_ip_address)

# Criar records DNS
az network dns record-set a add-record -g rg-english-jatel -z jfs-devops.shop -n learn -a $IP
az network dns record-set a add-record -g rg-english-jatel -z britlearnacademy.online -n @ -a $IP
```

### Passo 6: Verificar Status

```bash
# Verificar status completo
./scripts/deploy-aks.sh k8s-status

# Verificar certificates
kubectl get certificate -A

# Verificar pods
kubectl get pods -A | grep -E "(english-jatel|britlearn)"
```

## Validação

Após a migração, verifique:

- [ ] Todos os pods estão rodando
- [ ] Certificates TLS estão prontos (READY=True)
- [ ] DNS está resolvendo corretamente
- [ ] URLs de acesso estão funcionais
- [ ] IP público está correto

## URLs de Acesso

| Aplicação | URL |
|---|---|
| English JATEL | https://learn.jfs-devops.shop |
| Britlearn Academy | https://britlearnacademy.online |

## Troubleshooting

### NGINX Ingress não obtém IP

```bash
# Verificar role assignments
PRINCIPAL_ID=$(az aks show --resource-group rg-english-jatel --name aks-english-jatel --query "identity.principalId" -o tsv)
az role assignment list --assignee $PRINCIPAL_ID

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

### Certificate TLS não provisiona

```bash
# Verificar DNS
dig @ns1-01.azure-dns.com learn.jfs-devops.shop +short

# Verificar challenges
kubectl get challenges -A
kubectl describe challenge -n english-jatel <CHALLENGE_NAME>
```

## Referências

- **Documentação completa:** `docs/technical/azure-migration.md`
- **Skill:** `.opencode/skills/azure-migration/SKILL.md`
- **Scripts:** `scripts/setup-new-account.sh`, `scripts/deploy-aks.sh`
