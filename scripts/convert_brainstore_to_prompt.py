#!/usr/bin/env python3
"""
convert_brainstore_to_prompt.py
Converte anotações de brainstore (markdown) em arquivos de prompt estruturados (JSON/Markdown).

Uso:
  python convert_brainstore_to_prompt.py --input ../brainstore/ideias-brainstore.md --output ../prompts/vendas-report/prompt-base.md --format markdown
  python convert_brainstore_to_prompt.py --input ../brainstore/ideias-brainstore.md --output ../prompts/vendas-report/prompt-base.json --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


SECTIONS = [
    "Habilidade Proposta",
    "Contexto do Usuário",
    "Variáveis Sem Definição",
    "Fluxo de Trabalho Sugerido",
]


def parse_brainstore(md: str) -> Dict[str, str]:
    """Extrai seções conhecidas do markdown de brainstore."""
    sections: Dict[str, List[str]] = {s: [] for s in SECTIONS}
    current: Optional[str] = None
    in_code = False
    for line in md.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        header_match = re.match(r"^##\s+(.+)$", line)
        if header_match:
            header = header_match.group(1).strip()
            current = header if header in SECTIONS else None
            continue
        if current and not in_code:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def build_prompt_markdown(data: Dict[str, str], skill_name: str) -> str:
    ctx = data.get("Contexto do Usuário", "")
    workflow = data.get("Fluxo de Trabalho Sugerido", "")
    vars_undef = data.get("Variáveis Sem Definição", "")
    hab = data.get("Habilidade Proposta", "")

    out = []
    out.append(f"# Prompt base para a skill: {skill_name}")
    out.append("")
    out.append("## Instruções")
    out.append("")
    out.append(f"Você atuará como a skill **{skill_name}**. Siga o fluxo abaixo:")
    out.append("")
    if workflow:
        out.append("### Fluxo de trabalho")
        out.append(workflow)
        out.append("")
    out.append("### Contexto do usuário")
    out.append(ctx or "_(não informado)_")
    out.append("")
    if vars_undef:
        out.append("### Variáveis a definir")
        out.append(vars_undef)
        out.append("")
    out.append("---")
    out.append("*Gerado automaticamente a partir do brainstore.*")
    return "\n".join(out)


def build_prompt_json(data: Dict[str, str], skill_name: str) -> dict:
    return {
        "skill_name": skill_name,
        "instructions": f"Você atuará como a skill **{skill_name}**. Siga o fluxo abaixo:",
        "workflow": data.get("Fluxo de Trabalho Sugerido", "").splitlines(),
        "user_context": data.get("Contexto do Usuário", ""),
        "undefined_variables": data.get("Variáveis Sem Definição", "").splitlines(),
        "meta": {"generated_from": "brainstore"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Converter brainstore em prompt")
    parser.add_argument("--input", "-i", required=True, help="Arquivo markdown do brainstore")
    parser.add_argument("--output", "-o", required=True, help="Arquivo de saída")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--skill-name", "-s", default="minha-skill", help="Nome da skill")
    args = parser.parse_args()

    md_text = Path(args.input).read_text(encoding="utf-8")
    data = parse_brainstore(md_text)

    if args.format == "markdown":
        content = build_prompt_markdown(data, args.skill_name)
    else:
        content = json.dumps(build_prompt_json(data, args.skill_name), indent=2, ensure_ascii=False)

    Path(args.output).write_text(content, encoding="utf-8")
    print(f"Prompt gerado em {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())