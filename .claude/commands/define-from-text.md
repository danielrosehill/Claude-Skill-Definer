---
description: Turn a plain text/markdown process description in inbox/text/ into a spec.
---

Read $ARGUMENTS (or list `inbox/text/` if empty) and write a normalized spec to `specs/<name>.md` using the standard spec shape (see CLAUDE.md).

Fastest path — no transcription or vision model needed. After writing the spec, offer to run `/define-from-spec` to author the SKILL.md.
