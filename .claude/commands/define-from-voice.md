---
description: Turn a voice note in inbox/voice/ into a process spec.
---

Invoke the `transcription-router` agent on the target voice file.

If $ARGUMENTS is empty, list files in `inbox/voice/` and ask which one.
Otherwise treat $ARGUMENTS as the filename (relative to `inbox/voice/`).

After the spec is written, offer to run `/define-from-spec` to author the SKILL.md.
