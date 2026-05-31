#!/usr/bin/env python3
"""Run trigger evaluation for a skill description against the Nexus API.

For each query in the eval set, asks the Nexus model whether it would invoke
the skill given its description. Reports pass/fail and overall accuracy.

Usage:
  export NEXUS_API_URL=http://localhost:8080
  export NEXUS_API_TOKEN=<your-token>
  python -m scripts.run_eval --eval-set evals/trigger-eval.json --skill-path path/to/skill/

Requires:
  NEXUS_API_URL  (default: http://localhost:8080)
  NEXUS_API_TOKEN (required)
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from scripts.nexus_query import NexusAPIError, query_text
from scripts.utils import parse_skill_md

META_EVAL_PROMPT = """\
You are evaluating whether a skill description would cause an AI assistant to invoke a skill.

Skill name: {skill_name}
Skill description: {description}

User query: {query}

Would an AI assistant invoke this skill when responding to this user query?
Answer with ONLY a single word: yes or no.\
"""


def evaluate_query(query_text_fn, skill_name: str, description: str, query: str, timeout: int) -> bool:
    """Return True if the model says the skill would be triggered for this query."""
    prompt = META_EVAL_PROMPT.format(
        skill_name=skill_name,
        description=description,
        query=query,
    )
    response = query_text_fn(prompt, timeout=timeout).strip().lower()
    # Accept "yes", "yes.", "yes!" etc.
    return response.startswith("yes")


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
) -> dict:
    """Evaluate the full eval set and return structured results."""
    results = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_info: dict = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    evaluate_query,
                    query_text,
                    skill_name,
                    description,
                    item["query"],
                    timeout,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            q = item["query"]
            query_items[q] = item
            if q not in query_triggers:
                query_triggers[q] = []
            try:
                query_triggers[q].append(future.result())
            except (NexusAPIError, RuntimeError) as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[q].append(False)

    for q, triggers in query_triggers.items():
        item = query_items[q]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        did_pass = (trigger_rate >= trigger_threshold) == should_trigger
        results.append({
            "query": q,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to trigger-eval.json")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=5, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=1, help="Runs per query (averaging)")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "skill.md").exists():
        print(f"Error: No skill.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description

    if args.verbose:
        print(f"Evaluating: {description[:80]}...", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
    )

    if args.verbose:
        s = output["summary"]
        print(f"Results: {s['passed']}/{s['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  [{status}] expected={r['should_trigger']} rate={r['trigger_rate']:.0%}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
