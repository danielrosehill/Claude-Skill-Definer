---
description: Install a staged skill to a plugin, repo, or user-level path.
---

Invoke the `skill-installer` agent.

$ARGUMENTS form: `<skill-name> [target]` where target is one of:
- `user` (install to `~/.claude/skills/`)
- `repo:<path>` (install to `<path>/.claude/skills/`)
- `plugin:<plugin-name>` (install to plugin's `skills/` dir)

If target is omitted, check the spec frontmatter; if still unknown, ask.
