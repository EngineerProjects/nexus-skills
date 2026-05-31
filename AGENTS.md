# nexus-skills — Agent Instructions

This repository contains the official Nexus skills collection. It is automatically cloned by Nexus at first boot and updated in the background.

## Structure

Each top-level directory is one skill:

```
nexus-skills/
├── skill-creator/           meta-skill for creating new skills
├── subagent-driven-development/  parallel subagent execution with review gates
├── systematic-debugging/    root-cause-first debugging protocol
├── verification-before-completion/  evidence-before-claims verification gate
├── requesting-code-review/  code review via subagent
├── writing-plans/           implementation plan writing
├── test-driven-development/ TDD protocol
├── brainstorming/           design-before-code exploration (optional Node.js)
└── code-review/             comprehensive multilingual code review
```

## Skill format

Each skill directory contains:
- `SKILL.md` — required entry point (frontmatter + instructions)
- Optional subdirectories: `agents/`, `references/`, `scripts/`, `assets/`

Companion `.md` files referenced from `SKILL.md` are loaded on demand — they are not skills themselves.

## Contributing

- Every skill must have a `SKILL.md` with valid YAML frontmatter (`name`, `description`)
- Keep `SKILL.md` under 500 lines; put extended content in `references/`
- Skills must work without network access during execution (except brainstorming visual companion)
- Do not add platform-specific hooks or bootstrap scripts
