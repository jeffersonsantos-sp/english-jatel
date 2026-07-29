# Deploy no Kubernetes

Manifestos em `k8s/` para implantar a imagem `updateinformatica/english-jatel` no Kubernetes.
Validados com `kubectl apply --dry-run=client`.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `k8s/namespace.yaml` | namespace `english-jatel` |
| `k8s/configmap.yaml` | config não-sensível: `ADMIN_USER`, `EDGE_TTS_VOICE`, `DATA_DIR`, imagem |
| `k8s/pvc.yaml` | `PersistentVolumeClaim` de 1Gi montado em `/app/data` (usuários + progresso MemHack) |
| `k8s/deployment-blue.yaml` | Deployment do slot **ativo** (`slot: blue`, 1 réplica) |
| `k8s/deployment-green.yaml` | Deployment do slot **standby** (`slot: green`, 0 réplicas) |
| `k8s/service.yaml` | Service `ClusterIP` na porta 80 → 8000, seleciona pelo `slot` ativo |
| `k8s/kustomization.yaml` | aplica todos de uma vez (`kubectl apply -k k8s/`) |

## Aplicar

```bash
kubectl apply -k k8s/
```

Acompanhe:

```bash
kubectl -n english-jatel get pods
kubectl -n english-jatel logs deploy/english-jatel-blue
```

## Blue/Green (deploy sem downtime e rollback instantâneo)

Dois Deployments compartilham o rótulo `app: english-jatel`, diferenciados por
`slot: blue` (ativo) e `slot: green` (standby, 0 réplicas). O Service roteia para
o slot indicado em `spec.selector.slot` (começa em `blue`).

### Promover uma nova versão (green)
```bash
# 1. Aponte o green para a nova imagem e suba 1 réplica
kubectl -n english-jatel set image deploy/english-jatel-green \
  english-jatel=updateinformatica/english-jatel:v1.12.1
kubectl -n english-jatel scale deploy/english-jatel-green --replicas=1

# 2. Aguarde o green ficar Ready/saudavel
kubectl -n english-jatel rollout status deploy/english-jatel-green

# 3. Vire o Service para o green (trafego 100% para a nova versao)
kubectl -n english-jatel patch svc english-jatel \
  -p '{"spec":{"selector":{"app":"english-jatel","slot":"green"}}}'

# 4. (opcional) encoste o blue para evitar escritas simultaneas no volume
kubectl -n english-jatel scale deploy/english-jatel-blue --replicas=0
```

### Rollback (voltar para o blue)
```bash
kubectl -n english-jatel patch svc english-jatel \
  -p '{"spec":{"selector":{"app":"english-jatel","slot":"blue"}}}'
kubectl -n english-jatel scale deploy/english-jatel-blue --replicas=1
kubectl -n english-jatel scale deploy/english-jatel-green --replicas=0
```

> **Volume compartilhado**: ambos os slots montam o mesmo PVC (`/app/data`).
> Durante a sobreposição (antes de escalar o blue para 0) ambos podem escrever
> `users.json`/`memhack_progress.json`; para tráfego baixo é aceitável. Em
> produção de maior risco, prefira manter apenas um slot ativo por vez.

## Acesso

O Service é `ClusterIP`. Para acessar localmente, use port-forward:

```bash
kubectl -n english-jatel port-forward svc/english-jatel 8080:80
# abra http://localhost:8080
```

> A porta `8000` pode já estar em uso no host (ex.: proxy do kind); use `8080` ou outra livre.

### Expor no cluster

- **Nuvem (LB)**: troque `type: ClusterIP` por `type: LoadBalancer` em `k8s/service.yaml`.
- **On-prem / kind**: use `type: NodePort` e acesse pela porta do node.
- **Ingress**: adicione um `Ingress` apontando para `svc/english-jatel` (requer ingress controller).

## Variáveis de ambiente e segredos

O container usa os **defaults embutidos** do app (`ADMIN_PASS=mudar123`,
`SESSION_SECRET=change-me-in-prod`) — por isso não há Secret comitado. Recomenda-se
sobrescrever em produção.

### Habilitar o LLM (correção/conversa)

Sem `OPENROUTER_API_KEY` no pod, o app roda em **modo demo** (TTS funciona; correção/conversa
ficam heurísticas). O deploy atual já injeta a chave via **Secret** `english-jatel-secrets`
(referenciado por `secretKeyRef` nos Deployments blue/green). Para recriar/habilitar:

```bash
kubectl -n english-jatel create secret generic english-jatel-secrets \
  --from-literal=OPENROUTER_API_KEY=<sua_key>
```

Alternativamente: `kubectl -n english-jatel set env deploy/english-jatel-blue OPENROUTER_API_KEY=<sua_key>`.
Se o deploy for feito pelo pipeline (`cd.yaml`), prefira um step que crie o Secret a partir de
`${{ secrets.OPENROUTER_API_KEY }}` em vez de comitar a chave.

### Senhas de admin

Para alterar `ADMIN_PASS`/`SESSION_SECRET` sem rebuild, use:

```bash
kubectl -n english-jatel set env deploy/english-jatel ADMIN_PASS=<forte> SESSION_SECRET=<rand>
```

## Persistência

`/app/data` é um `emptyDir`? Não — é um `PersistentVolumeClaim` (`english-jatel-data`, 1Gi,
`ReadWriteOnce`). Nele ficam `users.json` e `memhack_progress.json`. Sem o PVC, os dados somem
ao recriar o pod.

## Observações de segurança

- O container roda como não-root (`runAsUser: 10001`) com `readOnlyRootFilesystem: true`
  (apenas `/app/data` e `/tmp` são graváveis).
- `DROP ALL` capabilities e `allowPrivilegeEscalation: false`.
- Use Ingress com TLS (HTTPS) em produção — necessário para microfone e cookie de sessão.
