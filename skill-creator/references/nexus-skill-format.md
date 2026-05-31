# Nexus Skill Format Reference

Complete specification of the Nexus skill format.

## skill.md Structure

```markdown
---
name: "Display Name"
description: "Trigger conditions and capabilities. Be specific and pushy."
argument-hint: "[optional argument description]"
user-invocable: true
model: inherit
effort: medium
context: inline
version: "1.0"
---

# Skill Instructions

Body of instructions for the model...
```

## Frontmatter Fields

### Required

- **`name`** (string): Human-readable display name. Shown in skill lists and UI.
- **`description`** (string): The primary trigger mechanism. Describes when AND what. Used by the model to decide whether to invoke the skill.

### Optional

- **`user-invocable`** (boolean, default: `true`): If `false`, the skill is hidden from user-facing skill lists. Used for internal/agent-only skills.
- **`argument-hint`** (string): Hint displayed when the user invokes the skill with an argument (e.g., `[filename or topic]`).
- **`model`** (string): Model override for this skill. Use `"inherit"` (default) to use the session model.
- **`effort`** (string): Thinking effort level. Values: `"low"`, `"medium"`, `"high"`, `"max"`.
- **`context`** (string): Execution context. `"inline"` (default) runs in the current conversation. `"fork"` creates an isolated context.
- **`version`** (string): Skill version identifier (e.g., `"1.2"`).
- **`agent`** (string): Designates the skill as an agent identity.
- **`allowed-tools`** (list): Restrict the tool surface to specific tools for this skill.
- **`when-to-use`** (string): Additional guidance for the model on when to invoke (supplements description).

## Variable Substitution

The skill body supports variable substitution:

| Variable | Value |
|----------|-------|
| `${NEXUS_SKILL_DIR}` | Absolute path to the skill's directory |
| `${NEXUS_SESSION_ID}` | Current session ID |

Example:
```markdown
The skill data is in `${NEXUS_SKILL_DIR}/references/data.json`.
```

## Directory Layout and Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata only** (`name` + `description`) — always in context (~100 words max)
2. **Full skill.md body** — loaded when the skill is invoked (<500 lines recommended)
3. **References/scripts** — loaded on demand as referenced in the skill body

### references/

Files in `references/` are loaded into context when the skill body instructs the model to read them. Keep them focused.

Use a table of contents for large reference files (>300 lines):

```markdown
## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)
```

### scripts/

Scripts in `scripts/` can be executed via `bash` or referenced by the model. They are NOT loaded automatically into context.

Name scripts descriptively: `validate_output.py`, `generate_report.sh`, etc.

### agents/

Sub-agent definitions in `agents/` are referenced by the skill body. Each `.md` file defines a specialized agent that can be spawned as a sub-task.

## Skill Organization Patterns

### Domain variants (one skill, multiple references)

```
cloud-deploy/
├── skill.md         ← selects the right reference based on user context
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Multi-step workflow (inline steps)

```
data-analysis/
├── skill.md         ← defines the full workflow inline
└── references/
    └── visualization-guide.md
```

### Agent-based skill (spawns specialized agents)

```
research-assistant/
├── skill.md         ← orchestrates sub-agents
└── agents/
    ├── web-researcher.md
    ├── synthesizer.md
    └── formatter.md
```

## Description Quality Checklist

A good description:
- [ ] States the primary domain/task clearly
- [ ] Lists specific user phrases or contexts that should trigger it
- [ ] Mentions what format/output the user gets
- [ ] Includes adjacent use cases (even if the user doesn't name the skill explicitly)
- [ ] Is ≤100 words
- [ ] Uses active voice

## Common Mistakes

**Too vague:**
```yaml
description: "Helps with writing."
```

**Too narrow:**
```yaml
description: "Converts .docx files to PDF format only."
```

**Good:**
```yaml
description: "Assists with writing tasks: drafting, editing, rewriting, tone adjustment, proofreading, and summarizing. Use for any text creation or improvement — emails, reports, blog posts, documentation, or any prose. Activates when the user asks for help with writing, editing, or improving text quality."
```

## Validation Rules

A valid Nexus skill must have:
1. A `skill.md` file at the root of the skill directory
2. Valid YAML frontmatter (parseable, with `name` and `description` fields)
3. Non-empty body (content after the frontmatter)
4. A `description` field ≥ 20 characters
5. A `name` field ≥ 2 characters

Warnings (non-blocking):
- `skill.md` body > 500 lines (consider refactoring into references/)
- `description` < 50 characters (may not trigger reliably)
- No `user-invocable` field (defaults to `true`)
