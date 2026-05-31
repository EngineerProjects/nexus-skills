# nexus-skills

Official skill collection for [Nexus](https://github.com/EngineerProjects/Nexus_ai). Automatically installed at first boot — skills are available without any manual setup.

## Skills

| Skill | Description |
|---|---|
| `skill-creator` | Create, test, and iteratively improve Nexus skills with evaluations |
| `brainstorming` | Design-before-code exploration (optional visual companion — requires Node.js) |
| `writing-plans` | Write comprehensive implementation plans before touching code |
| `subagent-driven-development` | Execute plans using fresh subagents per task with spec + quality review gates |
| `systematic-debugging` | Root-cause-first debugging protocol — never guess, always investigate |
| `verification-before-completion` | Evidence-before-claims gate: run verification before any success claim |
| `requesting-code-review` | Dispatch a code reviewer subagent with precisely crafted context |
| `test-driven-development` | Red-Green-Refactor TDD cycle with anti-patterns reference |
| `code-review` | Comprehensive code review for 18+ languages and frameworks |

## Structure

Each top-level directory is one skill:

```
nexus-skills/
├── <skill-name>/
│   ├── SKILL.md          # required — frontmatter + instructions
│   ├── agents/           # optional — sub-role definitions (read on demand)
│   ├── references/       # optional — extended reference docs
│   └── scripts/          # optional — executable utilities
```

Skills are installed to `.nexus/skills/repos/nexus-skills/` and updated in the background (at most once per hour).

## Credits and Licenses

This collection brings together content from several open-source projects. Each source is listed below with its original license and the skills derived from it.

---

### obra/superpowers — MIT License

> **Copyright (c) 2025 Jesse Vincent**
> [https://github.com/obra/superpowers](https://github.com/obra/superpowers)

The following skills are adapted from superpowers:

- `brainstorming/` — adapted (paths updated, Node.js `requires` added)
- `subagent-driven-development/` — adapted (`superpowers:` skill refs → `nexus-skills:`)
- `systematic-debugging/` — adapted (minor wording)
- `verification-before-completion/` — used as-is
- `requesting-code-review/` — used as-is
- `writing-plans/` — adapted (plan storage path updated)
- `test-driven-development/` — used as-is

Modifications: cross-skill references updated from `superpowers:` to `nexus-skills:`, storage paths updated from `docs/superpowers/` to `docs/nexus/`, platform-specific hooks and bootstrap removed, `requires` frontmatter added where applicable.

Full MIT license text: [superpowers/LICENSE](https://github.com/obra/superpowers/blob/main/LICENSE)

---

### awesome-skills/code-review-skill — MIT License

> **Copyright (c) 2025 tt-a1i**
> [https://github.com/awesome-skills/code-review-skill](https://github.com/awesome-skills/code-review-skill)

The following skill is adapted from code-review-skill:

- `code-review/` — adapted (placed in a subdirectory for Nexus repo layout compatibility)

Full MIT license text: [code-review-skill/LICENSE](https://github.com/awesome-skills/code-review-skill/blob/main/LICENSE)

---

### EngineerProjects/Nexus_ai (nexus-engine) — original work

The following skill was originally written for the Nexus engine and is maintained in this repository going forward:

- `skill-creator/` — original work, © 2026 KPOVIESSI Stéphane

---

## License

This repository is released under the MIT License — see [LICENSE](LICENSE).

Skills derived from third-party sources retain attribution to their original authors as described above.
