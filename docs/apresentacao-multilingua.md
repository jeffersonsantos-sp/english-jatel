# English JATEL — Expansão Multi-idiomas (Opção C)

**Apresentação para Diretoria / Patrocinadores**
_Documento de concepção (design só, sem implementação)_

---

## Slide 1 — Contexto e oportunidade

- O **English JATEL** é um tutor de inglês full-stack (Listen, Speak, Write, Read,
  Conversação com IA, Grammar, MemHack) já em produção (Render + Docker Hub + k8s).
- **Demanda identificada:** alunos também querem treinar **espanhol** (e, no futuro,
  outros idiomas) no mesmo produto.
- O mercado de idiomas é amplo; suportar múltiplos idiomas eleva o *público alvo*
  e o *valor percebido* sem duplicar a plataforma.

> Pergunta da diretoria: "Como agregar espanhol ao produto sem criar um segundo app?"

---

## Slide 2 — Situação atual (o que temos)

- App **funcional e estável** (versão `v1.8.2`), com correção por LLM, TTS neural
  (Edge) e reconhecimento de voz no navegador.
- **Pré-requisito importante:** a interface (UI) é em **português** — a língua do aluno.
- O "cérebro" (LLM OpenRouter) **já fala qualquer idioma**: a Conversação em espanhol
  funciona só trocando o *prompt* e a *voz*.
- Conteúdo hoje é **inglês-hardcoded** (gramática, frases, bancos de exercícios).

---

## Slide 3 — A ideia (desconstruída)

> "Além do inglês, queremos algo de Espanha para treinar espanhol."

Desconstruindo a premissa:

- **"Espanha" ≠ "espanhol"** — precisamos definir se é `es-ES` (castelhano) ou
  espanhol latino-americano (`es-MX`, etc.). Afeta voz TTS e exemplos.
- **Não é ligar um interruptor.** O app não é multi-idiomas hoje; "adicionar idioma"
  é decidir entre *refatorar para i18n* ou *parametrizar por idioma*.
- **A UI pode continuar em português.** O aluno brasileiro lê instruções em PT e
  pratica o idioma-alvo — logo **não precisamos traduzir a interface**.

---

## Slide 4 — Opções avaliadas

| Opção | Descrição | Esforço | Veredito |
|-------|-----------|---------|----------|
| **A — i18n completo** | UI + conteúdo totalmente parametrizados | Alto (refactor amplo) | Over-engineering p/ o caso |
| **B — instância separada** | Clona código + conteúdo; deploy à parte | Baixo p/ 1 idioma | Duplica manutenção (já rejeitamos esse padrão) |
| **C — parâmetro `lang`** | UI em PT; `lang` seleciona conteúdo, voz e prompts | Médio (foco em conteúdo) | **Recomendada** |

---

## Slide 5 — Proposta: Opção C (design)

- Um **seletor de idioma-alvo** na UI (rótulos em português): `Inglês | Espanhol`.
- O app ganha uma **dimensão `lang`** (`en | es`) que controla:
  1. **Conteúdo** — gramática, MemHack e bancos Listen/Read específicos do idioma.
  2. **Voz TTS** — `en-US-*` para inglês, `es-ES-*` para espanhol (Edge TTS, sem custo).
  3. **Prompts da IA** — "aja como professora de **espanhol**" em vez de inglês.
- **Inglês permanece o default**; espanhol é o primeiro idioma adicional.
- **Um único deploy, um único código-fonte.**

```
┌──────────────┐     lang=es      ┌──────────────────────────┐
│  UI (PT-BR)  │ ───────────────▶ │ engine: conteúdo + voz +  │
│ Seletor      │                  │ prompts conforme `lang`   │
│ Inglês/Espanh│                  └──────────────────────────┘
└──────────────┘
```

---

## Slide 6 — Como funciona tecnicamente

| Camada | Hoje (inglês) | Com Opção C |
|--------|---------------|-------------|
| Interface | PT (hardcoded) | PT (inalterado) |
| Gramática | `grammar.json` (EN) | `grammar.json` com chaves por idioma (ou `grammar_es.json`) |
| MemHack | `memhack.json` (EN) | bancos por idioma (`es`) |
| Listen/Read | frases EN | frases por idioma |
| Conversação/Correção | prompt "prof. de inglês" | prompt "prof. de espanhol" (LLM já suporta) |
| TTS | `en-US-*` | `es-ES-*` (Edge, sem custo extra) |
| Deploy | 1 serviço | **1 serviço** (parâmetro `lang`) |

> A Conversação e a Correção são "de graça" — o LLM já faz qualquer idioma;
> o trabalho real está no **conteúdo** (gramática e frases em espanhol).

---

## Slide 7 — Esforço (estimativa)

Divisão do trabalho:

| Frente | Tipo | Esforço | Dono |
|--------|------|---------|------|
| Parametrizar `lang` no backend/frontend | Engenharia | **Baixo** | Tech |
| Selecionar voz TTS por idioma | Engenharia | **Baixo** | Tech |
| Ajustar prompts da IA por idioma | Engenharia | **Baixo** | Tech |
| **Conteúdo espanhol** (gramática CEFR, frases MemHack, Listen/Read) | **Editorial / curadoria** | **Médio–Alto** | Conteúdo + Tech |
| Validação pedagógica (es-ES vs LatAm) | Revisão | Baixo | Conteúdo |

**Conclusão de esforço:** o *código* é pequeno; o *conteúdo* é o custo real.
Entregar a Conversação em espanhol é quase imediato; o pacote completo depende
da produção de material.

---

## Slide 8 — Benefícios

- **Sem duplicação:** 1 código, 1 deploy, 1 manutenção (evita o erro das "pastas cópia").
- **Time-to-market rápido:** Conversação em espanhol pode sair em dias.
- **Custo marginal baixo:** TTS é grátis (Edge) e o LLM já cobre vários idiomas.
- **Escalável:** frances/italiano/deutsch depois = **só mais conteúdo**, sem refactoring.
- **Coerência de produto:** o aluno aprende vários idiomas na mesma jornada/UX.
- **Diferencial comercial:** plataforma multi-idiomas eleva o ticket e o apelo.

---

## Slide 9 — Roadmap sugerido (fases)

1. **Fase 1 — Conversação em espanhol** (esforço mínimo): seletor `lang` + prompt/ voz.
2. **Fase 2 — Grammar & MemHack em espanhol** (exige conteúdo curado).
3. **Fase 3 — Listen/Read em espanhol** (bancos de frases em espanhol).
4. **Fase 4 — Novos idiomas** (reaproveita 100% da Fase 1–3).

---

## Slide 10 — Riscos e mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Volume de conteúdo espanhol | Médio | Fasear; começar por Conversação (sem conteúdo) |
| `es-ES` vs LatAm não definido | Baixo | Decisão de produto antes do Fase 2 |
| Qualidade da correção em espanhol | Baixo | LLM já robusto; validar amostras |
| Expansão sem demanda real | Médio | Lançar espanhol como bet, medir adoção |

---

## Slide 11 — Decisões pendentes (fechamento pré-execução)

1. **Variante de espanhol:** `es-ES` (castelhano) ou `es-MX`/LatAm?
2. **Escopo do primeiro lançamento:** só Conversação, ou pacote completo?
3. **Conteúdo:** a equipe redige o material espanhol, ou gera via referências/LLM?

---

## Slide 12 — Conclusão

- A Opção **C** entrega espanhol **sem duplicar o app** e prepara o produto para
  vários idiomas com esforço incremental.
- O **risco técnico é baixo**; o **esforço real é conteúdo**, que pode ser faseado.
- Próximo passo (após aprovação): consolidar o *design detalhado* de implementação
  e o cronograma da Fase 1.

> _Documento de concepção — nenhuma alteração de código foi realizada._
