---
name: skill-creator
description: Create new Nexus skills, improve and optimize existing skills, run evaluations to test skill quality, and optimize skill descriptions for better triggering accuracy. Use whenever the user wants to build a skill from scratch, refine an existing one, test a skill against sample prompts, compare two versions, or get a skill ready for real-world use.
user-invocable: true
---

# Skill Creator

A skill for creating, testing, and iteratively improving Nexus skills.

The process, at a high level:

1. Understand what the user wants the skill to do
2. Write a draft of the skill
3. Run the skill on a few test prompts and examine the outputs
4. Evaluate results qualitatively (and quantitatively if the outputs are verifiable)
5. Improve the skill based on what you observe
6. Repeat until satisfied
7. Optimize the description for better triggering accuracy

Your job is to figure out where the user is in this process and jump in from there.

---

## Communicating with the User

Skills are created by people with very different technical backgrounds — from engineers to domain experts who've never seen a terminal. Read the context carefully and adjust your language:

- Default to accessible language; explain technical terms if you use them
- "evaluation" and "benchmark" are OK for most users
- For "JSON" or "assertions", check for signals the user is technical before using them unexplained

---

## Creating a Skill

### Capture Intent

Start by understanding what the user wants. If the current conversation already shows a workflow they want to capture (e.g., they say "turn this into a skill"), extract the intent from the conversation history first — the tools used, the steps taken, the corrections they made.

Ask if needed:
1. What should this skill enable the model to do?
2. When should it be invoked? (what user phrases or contexts)
3. What does a good output look like?
4. Should we set up test cases? Skills with verifiable outputs (file transforms, data extraction, code generation, step-by-step workflows) benefit from test cases. Skills with subjective outputs (writing style, creative work) often don't need them.

### Interview and Research

Ask about edge cases, input/output formats, example content, success criteria, dependencies. Use `web_search`, `web_fetch`, or `wikipedia` to research the domain if it would improve the skill. Don't rush to the first draft — context makes better skills.

Use `nexus_list_skills` to see what skills already exist. Use `nexus_read_skill` to read similar skills for inspiration and to avoid duplication.

### Write the skill.md

Skill files live at: `${NEXUS_SKILL_DIR}/../{skill-name}/skill.md`

Write to: the user skills directory, typically `~/.nexus/skills/users/{userID}/{skill-name}/skill.md`

Fill in:
- **`name`**: Human-readable display name
- **`description`**: When to trigger + what it does. This is the primary trigger mechanism — include both the capability AND the specific contexts where it should activate, even when the user doesn't name the skill explicitly. Be slightly "pushy" — better to over-describe when to use it than under-describe.
- **The body**: Instructions for the model

Use `file_write` to create the skill directory and `skill.md`.

---

## Anatomy of a Skill

```
skill-name/
├── skill.md           (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources  (optional)
    ├── references/    — docs loaded into context as needed
    ├── scripts/       — utilities the model can execute
    └── agents/        — sub-agent definitions
```

### Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words max)
2. **skill.md body** — in context when the skill triggers (<500 lines is ideal)
3. **Bundled resources** — loaded on demand

Key patterns:
- Keep skill.md under 500 lines; if it's getting long, add references/ and point to them
- Reference files clearly from the skill body: "Read `references/aws.md` for AWS-specific steps"
- For large reference files (>300 lines), include a table of contents

When a skill supports multiple variants (e.g., cloud providers, programming languages), organize by variant:

```
cloud-deploy/
├── skill.md           ← workflow + variant selection
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

---

## Writing Guide

### Principle of Least Surprise

A skill's contents must not surprise the user if they read the description. Don't create skills that facilitate unauthorized access, data exfiltration, or deceptive behavior. Roleplay skills are fine.

### Writing Style

Explain WHY things matter, not just WHAT to do. Today's models are smart — when they understand the reasoning, they generalize better than when given rigid rules.

If you find yourself writing ALWAYS or NEVER in all caps, or using very rigid structures, that's a yellow flag. Try to reframe: "Do X because Y" beats "ALWAYS do X".

Use the imperative form: "Summarize the key findings" not "You should summarize the key findings".

### Defining Output Formats

```markdown
## Report structure
Use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

### Including Examples

```markdown
## Commit message format
**Example:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

---

## Test Cases

After writing the skill draft, come up with 2–3 realistic test prompts — the kind a real user would actually type. Share them with the user: "Here are the test cases I want to try — do these look right, or would you add something?"

Save test cases to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "expectations": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `expectations` field, which you'll add while the runs are in progress).

---

## Running and Evaluating Test Cases

This is one continuous sequence — don't stop partway through.

Put results in `{skill-name}-workspace/` as a sibling to the skill directory. Within the workspace, organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory.

### Step 1: Run each test case

For each test case, run the skill inline:

1. Read the skill's `skill.md`
2. Follow its instructions to accomplish the test prompt as the skill would
3. Save the output to `{workspace}/iteration-N/{eval-name}/output.md` (or the appropriate format)
4. Write a brief `eval_metadata.json` for each run:

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name",
  "prompt": "The user's task prompt",
  "expectations": []
}
```

Also run a **baseline**: do the same task WITHOUT the skill (just your general capabilities, no skill instructions). Save to a sibling `baseline/` directory. This reveals the skill's actual contribution.

### Step 2: While writing outputs, draft expectations

Don't wait until after the runs — draft quantitative expectations for each test case and explain them to the user. Expectations work best for skills with objectively verifiable outputs (file transforms, data extraction, code generation). For subjective skills, focus on qualitative review.

Update `evals/evals.json` and `eval_metadata.json` with expectations once drafted.

Good expectations are:
- Objectively verifiable (pass or fail, no ambiguity)
- Discriminating (would fail if the skill didn't do its job correctly)
- Descriptive (clear name that says what it checks)

```json
{
  "expectations": [
    "The output contains a valid YAML frontmatter block",
    "The description field is at least 50 characters",
    "The skill body includes at least one concrete example"
  ]
}
```

### Step 3: Grade and present results

Once all runs are done:

1. **Grade each run** — read `agents/grader.md` and evaluate each expectation against the output. Save results to `grading.json` in each run directory.

2. **Aggregate** — compare with-skill vs. baseline: pass rates, qualitative differences. Write a brief `benchmark.md` with your analysis.

3. **Present to the user** — show the results directly in the conversation:
   - For each test case: the prompt, the with-skill output, the baseline output, the grades
   - Overall: what the skill adds, what's missing, what failed

4. **Ask for feedback** — "How does this look? What would you change?"

### Step 4: Use nexus_validate_skill

Run `nexus_validate_skill` to catch structural issues (missing fields, frontmatter errors, quality warnings) before finalizing.

---

## Improving the Skill

This is the core of the loop. You've seen the outputs, you have user feedback — now make the skill better.

### How to Think About Improvements

1. **Generalize from feedback.** You're creating a skill that will be used across many different prompts by many different users. The test cases are a proxy. Avoid narrow, over-fitted fixes — aim for improvements that would help on prompts you haven't seen yet.

2. **Keep the skill lean.** Remove things that aren't pulling their weight. Read your test transcripts — if the skill caused the model to do something unproductive or unnecessary, remove that part.

3. **Explain the why.** If you find yourself adding rigid rules, try instead to explain the reasoning behind them. "Include a summary section because users often share outputs with colleagues who weren't in the conversation" is more powerful than "ALWAYS include a summary section".

4. **Look for repeated work.** If every test case resulted in the model writing the same helper script or taking the same multi-step approach to something, that's a signal the skill should bundle it. Write it once in `scripts/`, reference it from the skill body.

### The Iteration Loop

After improving:
1. Apply improvements to the skill
2. Re-run all test cases into `iteration-N+1/`
3. Grade, aggregate, present
4. Get feedback, improve again
5. Repeat until the user is satisfied

---

## Description Optimization

The `description` field in the frontmatter determines whether the model invokes the skill. After creating or improving a skill, offer to optimize it.

### Step 1: Generate trigger eval queries

Create 20 eval queries — mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

**Realistic queries only.** Not abstract, but specific: file paths, personal context, column names, company names, URLs. Mix of lengths, casual speech, typos. Focus on edge cases, not obvious ones.

**Should-trigger queries (8–10):** Different phrasings of the same intent. Some where the user doesn't name the skill explicitly but clearly needs it. Uncommon use cases. Cases where this skill competes with another but should win.

**Should-not-trigger queries (8–10):** The most valuable are near-misses — queries sharing keywords with the skill but needing something different. Adjacent domains, ambiguous phrasing where naive keyword matching would trigger but shouldn't.

### Step 2: Review with user

Present the eval set to the user for review. Let them edit queries, toggle should-trigger, add or remove entries.

### Step 3: Iterative optimization

For each candidate description, test it against the eval set:

1. For each query, reason: would this description cause the model to invoke this skill?
2. Count true positives (should-trigger and would trigger) and true negatives (should-not-trigger and would not trigger)
3. Propose a revised description that fixes the failures
4. Repeat up to 5 iterations, tracking scores

Report the best description found, with before/after scores. Use `nexus_validate_skill` to check the updated skill.

### How Skill Triggering Works

Skills appear in the model's `available_skills` list with name + description. The model decides whether to consult a skill based on that description. Important: the model only consults skills for tasks it can't handle easily on its own — simple one-step queries often won't trigger a skill even if the description matches. Your eval queries should be substantive.

---

## Reference Files

- `agents/grader.md` — How to grade expectations against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two skill versions
- `agents/analyzer.md` — How to analyze benchmark results

- `references/schemas.md` — JSON schemas for evals.json, grading.json, benchmark output
- `references/nexus-skill-format.md` — Complete Nexus skill format spec (frontmatter fields, variable substitution, directory layout, validation rules)

---

The core loop, one more time:

1. Understand what the skill should do
2. Draft or edit the skill
3. Run test prompts through the skill
4. Evaluate with the user
5. Improve and repeat
6. When done, optimize the description

Good luck.
