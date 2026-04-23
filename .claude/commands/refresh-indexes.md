---
description: Scan local marketplace repos and refresh the cached plugin/skill indexes.
---

Run `python3 scripts/refresh_indexes.py`.

This reads `CSD_PUBLIC_MARKETPLACE_PATH` and `CSD_PRIVATE_MARKETPLACE_PATH`, walks each marketplace for plugins (with `.claude-plugin/plugin.json` or `plugin.json`), enumerates their skills/commands/agents, and writes caches to `$CSD_DATA_DIR/public-index.json` and `private-index.json` (default `~/.local/share/claude-skill-definer/`).

Run this before `/install-skill plugin:<name>` so `skill-installer` can resolve the plugin's on-disk path without guessing.

If env vars are unset, run `python3 scripts/csd_config.py check` to see what's missing, then edit `.env` (copy from `.env.example`).
