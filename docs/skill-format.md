# SKILL.md format notes

Reference for the authoring agents — what a well-formed skill looks like and what the harness looks at.

## Required frontmatter

```yaml
---
name: kebab-case-name
description: One-sentence trigger description.
---
```

- `name` — must match the containing directory. Kebab-case.
- `description` — load-bearing. The harness uses it to decide when to fire.

## Optional frontmatter

- `allowed-tools` — restrict what the harness can invoke while this skill is active.
- `model` — pin a model family (rarely useful).

## Body conventions

- Start with a 1-2 line "what this does".
- Use a `## Steps` or `## Process` section with an ordered list.
- Include file paths and concrete commands where relevant.
- A `## Gotchas` or `## Edge cases` section catches common failure modes.
- Keep under ~150 lines. Split into supporting files if the skill is complex.

## Description anti-patterns

- "A skill that does X" — too vague.
- Missing trigger verbs — harness can't tell when to match.
- Listing multiple unrelated triggers — split into separate skills.

## Good descriptions (examples)

- "Use when the user drops a .wav/.mp3 into ./inbox and asks to transcribe, clean, or summarize it."
- "Triggered when the user asks to install a staged skill to a plugin, repo, or user-level path."
- "Use when the user wants to scan a dataset for PII (names, emails, phone numbers, addresses)."

## Install paths

| Target | Path |
|---|---|
| User | `~/.claude/skills/<name>/SKILL.md` |
| Repo | `<repo>/.claude/skills/<name>/SKILL.md` |
| Plugin | `<plugin-root>/skills/<name>/SKILL.md` |
