# JATEL-IA — Expansão Multi-idiomas (Opção C)

**Apresentação para Diretoria / Patrocinadores**
✅ **Aprovado em Julho/2026** — escopo expandido para **Espanhol + Francês**
_Documento de concepção (design só, sem implementação)_

---

## Slide 1 — Contexto e oportunidade

- O **JATEL-IA** é um tutor de inglês full-stack (Listen, Speak, Write, Read,
  Conversação com IA, Grammar, MemHack) já em produção (Render + Docker Hub + k8s).
- **Demanda identificada:** alunos querem treinar **espanhol** e **francês** no mesmo
  produto, sem precisar de apps separados.
- O mercado de idiomas é amplo; suportar múltiplos idiomas eleva o *público alvo*
  e o *valor percebido* sem duplicar a plataforma.

> Pergunta da diretoria: "Como agregar espanhol e francês ao produto sem criar apps separados?"

---

## Slide 2 — Situação atual (o que temos)

- App **funcional e estável** (versão `v1.9.0`), com correção por LLM, TTS neural
  (Edge) e reconhecimento de voz no navegador.
- **Pré-requisito importante:** a interface (UI) é em **português** — a língua do aluno.
- O "cérebro" (LLM OpenRouter) **já fala qualquer idioma**: a Conversação em espanhol
  ou francês funciona só trocando o *prompt* e a *voz*.
- Conteúdo hoje é **inglês-hardcoded** (gramática, frases, bancos de exercícios).

---

## Slide 3 — A ideia (desconstruída)

> "Além do inglês, queremos Espanhol e Francês."

Desconstruindo a premissa:

- **Espanhol:** precisamos definir se é `es-ES` (castelhano) ou espanhol
  latino-americano (`es-MX`, etc.). Afeta voz TTS e exemplos.
- **Francês:** `fr-FR` (francês europeu) como variante inicial.
- **Não é ligar um interruptor.** O app não é multi-idiomas hoje; "adicionar idioma"
  é decidir entre *refatorar para i18n* ou *parametrizar por idioma*.
- **A UI pode continuar em português.** O aluno brasileiro lê instruções em PT e
  pratica o idioma-alvo — logo **não precisamos traduzir a interface**.

---

## Slide 4 — Opções avaliadas

| Opção | Descrição | Esforço | Veredito |
|-------|-----------|---------|----------|
| **A — i18n completo** | UI + conteúdo totalmente parametrizados | Alto (refactor amplo) | Over-engineering p/ o caso |
| **B — instância separada** | Clona código + conteúdo; deploy à parte | Médio p/ 2 idiomas | Duplica manutenção (já rejeitamos esse padrão) |
| **C — parâmetro `lang`** | UI em PT; `lang` seleciona conteúdo, voz e prompts | Médio (foco em conteúdo) | **Recomendada** |

---

## Slide 5 — Proposta: Opção C (design)

- Um **seletor de idioma-alvo** na UI (rótulos em português): `Inglês | Espanhol | Francês`.
- O app ganha uma **dimensão `lang`** (`en | es | fr`) que controla:
  1. **Conteúdo** — gramática, MemHack e bancos Listen/Read específicos do idioma.
  2. **Voz TTS** — `en-US-*` (inglês), `es-ES-*` (espanhol), `fr-FR-*` (francês) — Edge TTS, sem custo.
  3. **Prompts da IA** — "aja como professora de **espanhol**" ou "de **francês**".
- **Inglês permanece o default**; espanhol e francês são os primeiros idiomas adicionais.
- **Um único deploy, um único código-fonte.**

```
┌──────────────┐     lang=es      ┌──────────────────────────┐
│  UI (PT-BR)  │ ───────────────▶ │ engine: conteúdo + voz +  │
│ Seletor      │     lang=fr      │ prompts conforme `lang`   │
│ Ing/Esp/Fr   │                  └──────────────────────────┘
└──────────────┘
```

---

## Slide 6 — Como funciona tecnicamente

| Camada | Hoje (inglês) | Com Opção C |
|--------|---------------|-------------|
| Interface | PT (hardcoded) | PT (inalterado) |
| Gramática | `grammar.json` (EN) | `grammar.json` com chaves por idioma (ou `grammar_es.json`, `grammar_fr.json`) |
| MemHack | `memhack.json` (EN) | bancos por idioma (`es`, `fr`) |
| Listen/Read | frases EN | frases por idioma |
| Conversação/Correção | prompt "prof. de inglês" | prompt "prof. de espanhol/francês" (LLM já suporta) |
| TTS | `en-US-*` | `es-ES-*` / `fr-FR-*` (Edge, sem custo extra) |
| Deploy | 1 serviço | **1 serviço** (parâmetro `lang`) |

> A Conversação e a Correção são "de graça" — o LLM já faz qualquer idioma;
> o trabalho real está no **conteúdo** (gramática e frases em cada idioma).

---

## Slide 7 — Esforço (estimativa)

Divisão do trabalho:

| Frente | Tipo | Esforço | Dono |
|--------|------|---------|------|
| Parametrizar `lang` no backend/frontend | Engenharia | **Baixo** | Tech |
| Selecionar voz TTS por idioma | Engenharia | **Baixo** | Tech |
| Ajustar prompts da IA por idioma | Engenharia | **Baixo** | Tech |
| **Conteúdo espanhol** (gramática CEFR, frases MemHack, Listen/Read) | **Editorial / curadoria** | **Médio–Alto** | Conteúdo + Tech |
| **Conteúdo francês** (gramática CEFR, frases MemHack, Listen/Read) | **Editorial / curadoria** | **Médio–Alto** | Conteúdo + Tech |
| Validação pedagógica (es-ES vs LatAm; fr-FR) | Revisão | Baixo | Conteúdo |

**Conclusão de esforço:** o *código* é pequeno e atende **ambos**; o *conteúdo*
é o custo real. Entregar a Conversação em espanhol e francês é quase imediato;
o pacote completo depende da produção de material.

---

## Slide 8 — Benefícios

- **Sem duplicação:** 1 código, 1 deploy, 1 manutenção (evita o erro das "pastas cópia").
- **Time-to-market rápido:** Conversação em espanhol e francês pode sair em dias.
- **Custo marginal baixo:** TTS é grátis (Edge) e o LLM já cobre vários idiomas.
- **Escalável:** italiano/deutsch/japonês depois = **só mais conteúdo**, sem refactoring.
- **Coerência de produto:** o aluno aprende vários idiomas na mesma jornada/UX.
- **Diferencial comercial:** plataforma multi-idiomas (3 idiomas no lançamento) eleva o ticket e o apelo.

---

## Slide 9 — Roadmap sugerido (fases)

1. **Fase 1 — Conversação em espanhol e francês** (esforço mínimo): seletor `lang` + prompt/voz para `es` e `fr`.
2. **Fase 2 — Grammar & MemHack em espanhol** (conteúdo curado em espanhol).
3. **Fase 3 — Grammar & MemHack em francês** (conteúdo curado em francês).
4. **Fase 4 — Listen/Read em espanhol e francês** (bancos de frases).
5. **Fase 5 — Novos idiomas** (reaproveita 100% das fases anteriores).

---

## Slide 10 — Riscos e mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Volume de conteúdo (espanhol + francês) | Médio | Fasear; Fase 1 só Conversação (sem conteúdo) |
| `es-ES` vs LatAm não definido | Baixo | Decisão antes da Fase 2 |
| Variante do francês (`fr-FR` vs `fr-CA`) | Baixo | Optar por `fr-FR` como default |
| Qualidade da correção nos 2 idiomas | Baixo | LLM já robusto; validar amostras |
| Expansão sem demanda real | Médio | Lançar como beta, medir adoção por idioma |

---

## Slide 11 — Decisões pendentes (fechamento pré-execução)

1. **Variante de espanhol:** `es-ES` (castelhano) ou `es-MX`/LatAm?
2. **Variante de francês:** `fr-FR` (europeu), ou também `fr-CA` (Canadá)?
3. **Escopo do primeiro lançamento:** só Conversação (Fase 1), ou pacote completo?
4. **Conteúdo:** a equipe redige o material, ou gera via LLM com revisão?

---

## Slide 12 — Conclusão

- A Opção **C** entrega espanhol e francês **sem duplicar o app** e prepara o produto
  para novos idiomas com esforço incremental.
- O **risco técnico é baixo**; o **esforço real é conteúdo**, que pode ser faseado.
- **Próximo passo:** consolidar o *design detalhado* de implementação e o cronograma
  das Fases 1–5.

> _Documento de concepção — nenhuma alteração de código foi realizada._
