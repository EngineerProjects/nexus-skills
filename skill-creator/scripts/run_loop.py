#!/usr/bin/env python3
"""Run the eval + improve loop for description optimization.

Iterates: evaluate trigger accuracy → improve description → repeat.
Supports a train/test split to avoid overfitting to the eval set.

Usage:
  export NEXUS_API_URL=http://localhost:8080
  export NEXUS_API_TOKEN=<your-token>
  python -m scripts.run_loop \\
    --eval-set evals/trigger-eval.json \\
    --skill-path path/to/skill/ \\
    --max-iterations 5 \\
    --verbose
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

from scripts.generate_report import generate_html
from scripts.improve_description import improve_description
from scripts.run_eval import run_eval
from scripts.utils import parse_skill_md


def split_eval_set(eval_set: list[dict], holdout: float, seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Stratified train/test split by should_trigger."""
    random.seed(seed)
    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]
    random.shuffle(trigger)
    random.shuffle(no_trigger)

    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))

    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]
    return train_set, test_set


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    verbose: bool,
    live_report_path: Path | None = None,
) -> dict:
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description

    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []

    history: list[dict] = []
    exit_reason = "max_iterations"

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}: {current_description[:80]}", file=sys.stderr)

        all_queries = train_set + test_set
        t0 = time.time()
        all_results = run_eval(
            eval_set=all_queries,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
        )
        eval_elapsed = time.time() - t0

        train_queries = {q["query"] for q in train_set}
        train_result_list = [r for r in all_results["results"] if r["query"] in train_queries]
        test_result_list = [r for r in all_results["results"] if r["query"] not in train_queries]

        train_passed = sum(1 for r in train_result_list if r["pass"])
        train_total = len(train_result_list)

        if test_set:
            test_passed = sum(1 for r in test_result_list if r["pass"])
            test_total = len(test_result_list)
        else:
            test_passed = test_total = 0

        entry = {
            "iteration": iteration,
            "description": current_description,
            "train_passed": train_passed,
            "train_total": train_total,
            "test_passed": test_passed if test_set else None,
            "test_total": test_total if test_set else None,
            "score": train_passed / train_total if train_total else 0.0,
            "eval_elapsed": round(eval_elapsed, 1),
            "train_results": train_result_list,
            "test_results": test_result_list if test_set else [],
        }
        history.append(entry)

        if verbose:
            print(f"  Train: {train_passed}/{train_total}", file=sys.stderr)
            if test_set:
                print(f"  Test:  {test_passed}/{test_total}", file=sys.stderr)

        if live_report_path:
            live_report_path.write_text(generate_html(
                {"history": history, "holdout": holdout},
                auto_refresh=True,
                skill_name=name,
            ))

        if train_passed == train_total and (not test_set or test_passed == test_total):
            exit_reason = "perfect_score"
            if verbose:
                print("  All queries pass — stopping", file=sys.stderr)
            break

        if iteration < max_iterations:
            t0 = time.time()
            train_eval_results = {"results": train_result_list, "summary": {"passed": train_passed, "total": train_total}}
            new_description = improve_description(
                skill_name=name,
                skill_content=content,
                current_description=current_description,
                eval_results=train_eval_results,
                history=history,
                timeout=timeout * 2,
            )
            improve_elapsed = time.time() - t0
            if verbose:
                print(f"  Proposed ({improve_elapsed:.1f}s): {new_description[:80]}", file=sys.stderr)
            current_description = new_description

    if test_set:
        best = max(history, key=lambda h: (h["test_passed"] or 0, h["train_passed"]))
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda h: h["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit: {exit_reason}. Best: {best_score} (iteration {best['iteration']})", file=sys.stderr)

    return {
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser(description="Run description optimization loop")
    parser.add_argument("--eval-set", required=True, help="Path to trigger-eval.json")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=5, help="Parallel eval workers")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query (seconds)")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=1, help="Runs per query (for averaging)")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.3, help="Test set fraction (0 to disable)")
    parser.add_argument("--report", default=None, help="Path to write live HTML report")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "skill.md").exists():
        print(f"Error: No skill.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, _, _ = parse_skill_md(skill_path)
    live_report_path = Path(args.report) if args.report else None

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        verbose=args.verbose,
        live_report_path=live_report_path,
    )

    json_output = json.dumps(output, indent=2)
    print(json_output)

    if live_report_path:
        live_report_path.write_text(generate_html(output, auto_refresh=False, skill_name=name))
        print(f"\nReport: {live_report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
