# Nexus Skill Creator — JSON Schemas

This document defines the JSON schemas used by the skill-creator workflow.

---

## evals.json

Defines the test cases for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Human-readable description of what a good output looks like",
      "files": [],
      "expectations": [
        "The output includes a valid YAML frontmatter block",
        "The description field is at least 50 characters",
        "The skill body uses the imperative form"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter `name` field
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task prompt to execute
- `evals[].expected_output`: Human-readable description of success (used for qualitative review)
- `evals[].files`: Optional list of input file paths (relative to skill directory)
- `evals[].expectations`: List of verifiable statements that should be true if the skill succeeds

---

## eval_metadata.json

Stores the metadata for a single test run. Located at `{workspace}/iteration-N/{eval-name}/eval_metadata.json`.

```json
{
  "eval_id": 1,
  "eval_name": "skill-frontmatter-validation",
  "prompt": "Create a skill for summarizing research papers",
  "expectations": [
    "The output includes a valid YAML frontmatter block",
    "The description field is at least 50 characters"
  ],
  "variant": "with_skill"
}
```

**Fields:**
- `eval_id`: Matches `evals.json` id
- `eval_name`: Descriptive name for the test (used as directory name too)
- `prompt`: The prompt that was executed
- `expectations`: The list of verifiable expectations
- `variant`: `"with_skill"` or `"baseline"` (baseline = no skill active)

---

## grading.json

Output from the grading step. Located at `{workspace}/iteration-N/{eval-name}/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The output includes a valid YAML frontmatter block",
      "passed": true,
      "evidence": "Output contains '---\\nname: ... description: ...' at the top"
    },
    {
      "text": "The description field is at least 50 characters",
      "passed": false,
      "evidence": "Description is 'Summarizes papers.' — only 18 characters"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  },
  "qualitative_notes": "The skill body is well-written but the frontmatter is incomplete. The baseline produced a plain summary with no structure.",
  "eval_feedback": {
    "suggestions": [
      {
        "expectation": "The description field is at least 50 characters",
        "reason": "A short description would also fail if the output has a description but it's poorly written — consider checking quality not just length"
      }
    ],
    "overall": "Expectations cover structure but not semantic quality."
  }
}
```

**Fields:**
- `expectations[]`: Array of graded expectations
  - `text`: The original expectation statement
  - `passed`: Boolean
  - `evidence`: Quote or description supporting the verdict
- `summary.pass_rate`: Fraction passed (0.0 to 1.0)
- `qualitative_notes`: Freeform observations beyond the expectations
- `eval_feedback`: (optional) Suggestions for improving the expectations themselves

---

## benchmark.md

A human-readable summary of the iteration's benchmark. Written by the model to `{workspace}/iteration-N/benchmark.md`.

Structure (write as freeform markdown, not JSON):

```markdown
# Benchmark — iteration-N — {skill-name}

## Summary

| Config       | Pass rate | Notes |
|--------------|-----------|-------|
| with_skill   | 75%       |       |
| baseline     | 25%       |       |
| delta        | +50%      |       |

## Per-eval breakdown

### {eval-name}

- **with_skill**: [pass/fail for each expectation]
- **baseline**: [pass/fail for each expectation]
- **Qualitative**: [observations]

## Analyst notes

- [Patterns that aggregate stats hide]
- [Flaky expectations, expectations that always pass in both, etc.]
- [What the skill clearly adds, what it doesn't change]
```

---

## comparison.json

Output from a blind A/B comparison (comparator agent). Located at `{workspace}/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "Version A includes concrete examples and explains the why; version B uses rigid rules without rationale.",
  "scores": {
    "A": {
      "content_quality": 8,
      "instruction_clarity": 9,
      "overall": 8.5
    },
    "B": {
      "content_quality": 5,
      "instruction_clarity": 4,
      "overall": 4.5
    }
  },
  "expectation_results": {
    "A": { "passed": 4, "total": 5, "pass_rate": 0.80 },
    "B": { "passed": 2, "total": 5, "pass_rate": 0.40 }
  }
}
```

---

## analysis.json

Output from post-hoc analysis. Located at `{workspace}/analysis-N.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill_version": "iteration-3",
    "loser_skill_version": "iteration-2",
    "comparator_reasoning": "A explains the why; B gives rigid rules"
  },
  "winner_strengths": [
    "Includes concrete examples for edge cases",
    "Explains reasoning behind formatting requirements"
  ],
  "loser_weaknesses": [
    "Uses 'ALWAYS' rules without explanation — model ignores them on ambiguous input",
    "No examples — model invents its own interpretation"
  ],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'ALWAYS add a summary section' with 'Add a summary section so users who share the output with colleagues have context'",
      "expected_impact": "Model will generalize better to edge cases"
    }
  ]
}
```

**Suggestion categories:** `instructions`, `examples`, `references`, `structure`, `error_handling`

**Priority levels:** `high` (likely to change outcomes), `medium` (improves quality), `low` (marginal)

---

## Description trigger eval format

Used during description optimization. Saved as `evals/trigger-eval.json`.

```json
[
  {
    "query": "ok so my boss just sent me this pdf of Q4 financials and she wants a one-pager summary for the board meeting",
    "should_trigger": true
  },
  {
    "query": "write a python script that parses a CSV and computes averages",
    "should_trigger": false
  }
]
```

**Fields:**
- `query`: A realistic user prompt (specific, contextual, not abstract)
- `should_trigger`: Whether this query should cause the model to invoke the skill
