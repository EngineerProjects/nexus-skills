# Post-hoc Analyzer

Unblind a comparison result and generate actionable improvement suggestions.

## Role

After the blind comparator picks a winner, read both skill versions and both outputs to explain WHY the winner won and what the losing skill should change. The goal is specific, actionable suggestions — not a restatement of what the comparator said.

## Inputs

You receive:
- **winner**: "A" or "B" (from comparison.json)
- **winner_skill_path**: Path to the skill.md that produced the winning output
- **winner_output_path**: Path to the winning output file
- **loser_skill_path**: Path to the skill.md that produced the losing output
- **loser_output_path**: Path to the losing output file
- **comparison_path**: Path to the comparator's comparison.json
- **workspace_dir**: Directory for saving the result

## Process

### Step 1: Read the Comparison

Read comparison.json. Note: which side won, the comparator's reasoning, the scores, and expectation pass rates. This is your anchor — the analysis should explain and deepen these findings, not contradict them.

### Step 2: Read Both Skills

Read winner skill.md and loser skill.md. Identify structural differences:
- How do the instructions compare in specificity and clarity?
- Does one explain reasoning behind the rules? Does the other just give commands?
- What examples does each include?
- How do they handle edge cases?
- Are there sections in the winner that the loser lacks entirely?

### Step 3: Read Both Outputs

Read the actual outputs. With the comparison findings in mind:
- Find the specific passages in each output that the comparator flagged
- Trace them back to the skill instructions that produced them — or the lack of instructions that led to poor behavior
- Look for places where the loser's output was close but missed something — these reveal fixable instruction gaps, not fundamental limits

### Step 4: Identify Winner Strengths

List what made the winner better. For each strength, trace it to a specific part of the skill that caused it. Be concrete — quote from the skill or output.

Examples of what to look for:
- Instructions that explain the *why* behind a rule → model generalizes better
- Concrete examples → model applies the pattern correctly
- Output format template → consistent, well-structured results
- Edge case guidance → model doesn't improvise badly under ambiguity

### Step 5: Identify Loser Weaknesses

List what held the loser back. For each weakness, explain what the skill does (or doesn't do) that caused the problem in the output.

Focus on fixable issues — things that could be addressed with changes to the skill. Don't list weaknesses that are just "the winner did it better" without a root cause.

### Step 6: Generate Improvement Suggestions

Produce concrete, actionable suggestions for improving the loser skill. For each suggestion:
- State the specific change (what to add, remove, or rewrite)
- Explain the expected impact (why this would change the output)
- Assign a priority and category

Prioritize by impact: which changes would most likely have changed the comparison outcome?

### Step 7: Write analysis.json

Save to `{workspace_dir}/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill_version": "iteration-3",
    "loser_skill_version": "iteration-2",
    "comparator_reasoning": "A explains the why; B gives rigid rules without rationale"
  },
  "winner_strengths": [
    "Includes concrete examples for each output type — model applies the pattern without inventing its own",
    "Instructions explain reasoning: 'add a summary section so users who share the output have context' — model generalizes correctly to edge cases",
    "Output template is explicit with section headers — output is consistently structured"
  ],
  "loser_weaknesses": [
    "Uses 'ALWAYS include X' rules without explanation — model ignores them when input is ambiguous",
    "No examples — model invents its own interpretation of 'structured format'",
    "Missing guidance on short inputs — model produces a padded, low-quality output instead of flagging the issue"
  ],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'ALWAYS add a summary section' with 'Add a summary section so users who share the output with colleagues have context for the findings'",
      "expected_impact": "Model will generalize correctly when input is ambiguous rather than applying the rule mechanically or ignoring it"
    },
    {
      "priority": "high",
      "category": "examples",
      "suggestion": "Add a concrete before/after example showing what 'structured format' means for a typical input",
      "expected_impact": "Eliminates the ambiguity that caused the model to invent its own interpretation"
    },
    {
      "priority": "medium",
      "category": "error_handling",
      "suggestion": "Add a section: 'If the input is fewer than 200 words, note this to the user and ask whether to proceed or supplement with additional context'",
      "expected_impact": "Prevents low-quality padded outputs on thin inputs"
    }
  ]
}
```

## Guidelines

- **Trace to causes**: Don't just say "the loser output was worse." Find the specific instruction (or gap) that caused it.
- **Quote from sources**: Back up each strength and weakness with evidence from the skill text or output.
- **Prioritize by impact**: Suggestions that would have changed the comparison outcome come first.
- **Think generalization**: Would the improvement help on prompts you haven't seen, not just on this eval?
- **Be specific**: "Replace X with Y because Z" beats "improve clarity."

## Suggestion Categories

| Category | Description |
|---|---|
| `instructions` | Changes to the skill's prose instructions |
| `examples` | Concrete before/after examples to add |
| `references` | Reference files or external docs to include |
| `structure` | Reorganization of the skill content |
| `error_handling` | Guidance for edge cases and failures |

## Priority Levels

- **high**: Would likely have changed the comparison outcome
- **medium**: Would improve output quality but may not change win/loss
- **low**: Nice to have, marginal improvement
