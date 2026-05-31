#!/usr/bin/env python3
"""Improve a skill description based on eval results via the Nexus API.

Usage:
  export NEXUS_API_URL=http://localhost:8080
  export NEXUS_API_TOKEN=<your-token>
  python -m scripts.improve_description \\
    --skill-path path/to/skill/ \\
    --eval-results results.json \\
    --history history.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.nexus_query import query_text
from scripts.utils import parse_skill_md

IMPROVE_PROMPT = """\
You are optimizing the description field of a Nexus skill so that an AI model correctly decides when to invoke it.

Current skill name: {skill_name}
Current description: {current_description}

Skill body (for context):
{skill_body}

Eval results:
- Queries that SHOULD trigger this skill but DON'T (false negatives):
{false_negatives}

- Queries that SHOULD NOT trigger but DO (false positives):
{false_positives}

- Queries that are correctly classified:
{correct}

Previous descriptions tried (most recent first):
{history}

Write an improved description that fixes the failures. The description should:
1. Clearly state WHEN to invoke the skill (contexts, triggers, user intents)
2. Clearly state WHAT the skill does
3. Be specific enough to avoid false positives
4. Be broad enough to catch all true positives
5. Be at most 200 words

Reply with ONLY the new description text, nothing else.\
"""


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    timeout: int = 120,
) -> str:
    """Call the Nexus API to generate an improved description."""
    results = eval_results.get("results", [])

    false_negatives = [
        f"  - {r['query']}"
        for r in results
        if r["should_trigger"] and not r["pass"]
    ]
    false_positives = [
        f"  - {r['query']}"
        for r in results
        if not r["should_trigger"] and not r["pass"]
    ]
    correct = [
        f"  - {r['query']} ({'✓ triggers' if r['should_trigger'] else '✓ does not trigger'})"
        for r in results
        if r["pass"]
    ]

    history_lines = [
        f"  {i+1}. {h['description']} (score: {h.get('score', '?')})"
        for i, h in enumerate(reversed(history[-5:]))
    ]

    # Extract skill body (content after frontmatter)
    parts = skill_content.split("---", 2)
    skill_body = parts[2].strip() if len(parts) >= 3 else skill_content

    prompt = IMPROVE_PROMPT.format(
        skill_name=skill_name,
        current_description=current_description,
        skill_body=skill_body[:2000],  # cap to avoid huge prompts
        false_negatives="\n".join(false_negatives) if false_negatives else "  (none)",
        false_positives="\n".join(false_positives) if false_positives else "  (none)",
        correct="\n".join(correct[:5]) if correct else "  (none)",
        history="\n".join(history_lines) if history_lines else "  (none — this is the first attempt)",
    )

    new_description = query_text(prompt, timeout=timeout).strip()

    # Strip any accidental surrounding quotes
    new_description = re.sub(r'^["\']|["\']$', "", new_description).strip()

    return new_description


def main():
    parser = argparse.ArgumentParser(description="Improve a skill description via Nexus API")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--eval-results", required=True, help="Path to run_eval.py output JSON")
    parser.add_argument("--history", default=None, help="Path to history JSON (list of prior attempts)")
    parser.add_argument("--timeout", type=int, default=120, help="API timeout in seconds")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "skill.md").exists():
        print(f"Error: No skill.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, description, content = parse_skill_md(skill_path)
    eval_results = json.loads(Path(args.eval_results).read_text())
    history = json.loads(Path(args.history).read_text()) if args.history else []

    new_desc = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=description,
        eval_results=eval_results,
        history=history,
        timeout=args.timeout,
    )

    print(new_desc)


if __name__ == "__main__":
    main()
