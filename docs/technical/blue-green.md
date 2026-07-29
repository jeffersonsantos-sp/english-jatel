# Blue/Green no Kubernetes (JATEL-IA)

Estratégia de deploy sem downtime e com rollback instantâneo para o JATEL-IA.
Dois Deployments compartilham o rótulo `app: english-jatel`, diferenciados por
`slot: blue` (ativo) e `slot: green` (standby). O Service roteia o tráfego para o
slot indicado em `spec.selector.slot` (começa em `blue`).

> Complementa [`docs/technical/deploy-kubernetes.md`](deploy-kubernetes.md). Os
> manifestos ficam em `k8s/` e são aplicados com `kubectl apply -k k8s/`.

## Manifestos

| Arquivo | Papel |
|---------|-------|
| `k8s/deployment-blue.yaml` | slot **ativo** (`slot: blue`), 1 réplica, imagem atual |
| `k8s/deployment-green.yaml` | slot **standby** (`slot: green`), 0 réplicas, aguarda nova versão |
| `k8s/service.yaml` | `ClusterIP` 80→8000; `selector: {app: english-jatel, slot: blue}` |

Ambos os Deployments montam o mesmo PVC (`english-jatel-data` em `/app/data`).

## Promover uma nova versão (green)

```bash
# 1. Aponte o green para a nova imagem e suba 1 replica
kubectl -n english-jatel set image deploy/english-jatel-green \
  english-jatel=updateinformatica/english-jatel:v1.11.0
kubectl -n english-jatel scale deploy/english-jatel-green --replicas=1

# 2. Aguarde o green ficar Ready/saudavel
kubectl -n english-jatel rollout status deploy/english-jatel-green

# 3. Vire o Service para o green (trafego 100% para a nova versao)
kubectl -n english-jatel patch svc english-jatel \
  -p '{"spec":{"selector":{"app":"english-jatel","slot":"green"}}}'

# 4. (opcional) encoste o blue para evitar escritas simultaneas no volume
kubectl -n english-jatel scale deploy/english-jatel-blue --replicas=0
```

## Rollback (voltar para o blue)

```bash
kubectl -n english-jatel patch svc english-jatel \
  -p '{"spec":{"selector":{"app":"english-jatel","slot":"blue"}}}'
kubectl -n english-jatel scale deploy/english-jatel-blue --replicas=1
kubectl -n english-jatel scale deploy/english-jatel-green --replicas=0
```

## Por que Blue/Green (e não Canary) aqui

- **Sem malha (mesh) necessária**: o corte é só um `patch` no seletor do Service.
  Canary de verdade exige divisão de tráfego por peso (Ingress canary/Flagger/Istio),
  ausente neste ambiente (kind de nó único).
- **Rollback instantâneo**: errou na nova versão? Patch de volta. Canary exigiria
  drenar/despromover graduamente.
- **App monolítico e pequeno**: o ganho do canary não justifica a complexidade.

## ⚠️ Volume compartilhado (`/app/data`)

Ambos os slots montam o mesmo PVC; durante a sobreposição (antes de escalar o slot
antigo para 0) ambos podem escrever `users.json`/`memhack_progress.json` — o engine
regrava o arquivo todo a cada mudança, então há corrida de escrita em sobreposição.
Para tráfego baixo é aceitável; em produção de maior risco, mantenha **apenas um slot
ativo por vez** (escale o antigo para 0 logo após o corte).

## Comandos úteis

```bash
kubectl -n english-jatel get pods
kubectl -n english-jatel get svc english-jatel -o yaml   # confere o selector.slot
kubectl -n english-jatel port-forward svc/english-jatel 9090:80   # acesso local
kubectl -n english-jatel get endpoints english-jatel     # endpoints ativos
```
