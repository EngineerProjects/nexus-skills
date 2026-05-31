#!/usr/bin/env python3
"""Aggregate grading.json files from skill-creator workspace into benchmark statistics.

Reads the iteration directories produced by the skill-creator workflow and
computes pass rates for with-skill vs baseline runs.

Expected directory layout:
  <workspace>/
  └── iteration-N/
      └── <eval-name>/
          ├── grading.json        (with-skill run)
          └── baseline/
              └── grading.json    (baseline run)

Usage:
  python -m scripts.aggregate_benchmark <workspace_dir> [--skill-name NAME]
"""

import argparse
import json
import math
import sys
from pathlib import Path


def calculate_stats(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    n = len(values)
    mean = sum(values) / n
    stddev = math.sqrt(sum((x - mean) ** 2 for x in values) / (n - 1)) if n > 1 else 0.0
    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def load_grading(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Warning: invalid JSON in {path}: {e}", file=sys.stderr)
        return None


def load_workspace(workspace_dir: Path) -> dict[str, list[dict]]:
    """Scan iteration directories and collect grading results per config."""
    results: dict[str, list[dict]] = {"with_skill": [], "baseline": []}

    for iter_dir in sorted(workspace_dir.glob("iteration-*")):
        if not iter_dir.is_dir():
            continue
        iteration = iter_dir.name

        for eval_dir in sorted(iter_dir.iterdir()):
            if not eval_dir.is_dir():
                continue
            eval_name = eval_dir.name

            # with-skill run
            grading = load_grading(eval_dir / "grading.json")
            if grading:
                results["with_skill"].append({
                    "iteration": iteration,
                    "eval_name": eval_name,
                    "pass_rate": grading.get("summary", {}).get("pass_rate", 0.0),
                    "passed": grading.get("summary", {}).get("passed", 0),
                    "failed": grading.get("summary", {}).get("failed", 0),
                    "total": grading.get("summary", {}).get("total", 0),
                    "expectations": grading.get("expectations", []),
                })

            # baseline run
            baseline_grading = load_grading(eval_dir / "baseline" / "grading.json")
            if baseline_grading:
                results["baseline"].append({
                    "iteration": iteration,
                    "eval_name": eval_name,
                    "pass_rate": baseline_grading.get("summary", {}).get("pass_rate", 0.0),
                    "passed": baseline_grading.get("summary", {}).get("passed", 0),
                    "failed": baseline_grading.get("summary", {}).get("failed", 0),
                    "total": baseline_grading.get("summary", {}).get("total", 0),
                    "expectations": baseline_grading.get("expectations", []),
                })

    return results


def aggregate(results: dict[str, list[dict]]) -> dict:
    summary: dict[str, dict] = {}
    for config, runs in results.items():
        pass_rates = [r["pass_rate"] for r in runs]
        summary[config] = calculate_stats(pass_rates)

    with_skill_mean = summary.get("with_skill", {}).get("mean", 0.0)
    baseline_mean = summary.get("baseline", {}).get("mean", 0.0)
    summary["delta"] = {
        "pass_rate": f"{with_skill_mean - baseline_mean:+.2f}",
    }
    return summary


def per_eval_breakdown(results: dict[str, list[dict]]) -> dict:
    """Group results by (iteration, eval_name) for per-eval comparison."""
    breakdown: dict[str, dict] = {}
    for config, runs in results.items():
        for run in runs:
            key = f"{run['iteration']}/{run['eval_name']}"
            if key not in breakdown:
                breakdown[key] = {}
            breakdown[key][config] = run
    return breakdown


def main():
    parser = argparse.ArgumentParser(description="Aggregate benchmark results from skill-creator workspace")
    parser.add_argument("workspace_dir", type=Path, help="Path to the skill workspace directory")
    parser.add_argument("--skill-name", default="", help="Skill name for output metadata")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    if not args.workspace_dir.exists():
        print(f"Directory not found: {args.workspace_dir}", file=sys.stderr)
        sys.exit(1)

    results = load_workspace(args.workspace_dir)

    if not results["with_skill"] and not results["baseline"]:
        print(f"No grading.json files found under {args.workspace_dir}", file=sys.stderr)
        sys.exit(1)

    summary = aggregate(results)
    breakdown = per_eval_breakdown(results)

    output = {
        "skill_name": args.skill_name or args.workspace_dir.name.replace("-workspace", ""),
        "workspace": str(args.workspace_dir),
        "run_summary": summary,
        "per_eval": breakdown,
    }

    json_output = json.dumps(output, indent=2)

    if args.output:
        args.output.write_text(json_output)
        print(f"Benchmark written to {args.output}", file=sys.stderr)
    else:
        print(json_output)

    # Print summary to stderr
    ws = summary.get("with_skill", {})
    bl = summary.get("baseline", {})
    delta = summary.get("delta", {})
    print(f"\nSummary:", file=sys.stderr)
    print(f"  With skill: {ws.get('mean', 0)*100:.1f}% (±{ws.get('stddev', 0)*100:.1f}%)", file=sys.stderr)
    print(f"  Baseline:   {bl.get('mean', 0)*100:.1f}% (±{bl.get('stddev', 0)*100:.1f}%)", file=sys.stderr)
    print(f"  Delta:      {delta.get('pass_rate', '—')}", file=sys.stderr)


if __name__ == "__main__":
    main()
