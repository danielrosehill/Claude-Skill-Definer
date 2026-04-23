#!/usr/bin/env python3
"""Scan the local marketplace repos and cache their plugin/skill indexes.

Writes to $CSD_DATA_DIR/public-index.json and private-index.json.

Marketplace layout assumed: a git repo containing one or more plugin directories.
A plugin dir has either .claude-plugin/plugin.json (newer format) or plugin.json
at the root. Plugins may contain a skills/ directory with one subdir per skill
containing SKILL.md.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from csd_config import load  # noqa: E402


def _read_frontmatter(md: Path) -> dict[str, str]:
    if not md.exists():
        return {}
    text = md.read_text(errors="replace")
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---")
    fm, _, _ = rest.partition("---")
    out: dict[str, str] = {}
    for line in fm.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _find_plugin_manifest(plugin_dir: Path) -> Path | None:
    for candidate in [
        plugin_dir / ".claude-plugin" / "plugin.json",
        plugin_dir / "plugin.json",
    ]:
        if candidate.exists():
            return candidate
    return None


def scan_marketplace(root: Path) -> dict:
    if not root or not root.exists():
        return {"root": str(root), "exists": False, "plugins": []}

    plugins = []
    for sub in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        manifest = _find_plugin_manifest(sub)
        if not manifest:
            continue
        try:
            meta = json.loads(manifest.read_text())
        except Exception as e:
            meta = {"_parse_error": str(e)}

        skills = []
        skills_dir = sub / "skills"
        if skills_dir.is_dir():
            for skill_sub in sorted(s for s in skills_dir.iterdir() if s.is_dir()):
                fm = _read_frontmatter(skill_sub / "SKILL.md")
                if fm:
                    skills.append(
                        {
                            "dir": skill_sub.name,
                            "name": fm.get("name", skill_sub.name),
                            "description": fm.get("description", ""),
                        }
                    )

        commands = []
        cmd_dir = sub / "commands"
        if cmd_dir.is_dir():
            commands = sorted(c.stem for c in cmd_dir.glob("*.md"))

        agents = []
        agent_dir = sub / "agents"
        if agent_dir.is_dir():
            agents = sorted(a.stem for a in agent_dir.glob("*.md"))

        plugins.append(
            {
                "dir": sub.name,
                "manifest_path": str(manifest.relative_to(root)),
                "name": meta.get("name", sub.name),
                "version": meta.get("version"),
                "description": meta.get("description", ""),
                "skills": skills,
                "commands": commands,
                "agents": agents,
            }
        )

    return {"root": str(root), "exists": True, "plugins": plugins}


def main() -> int:
    cfg = load()
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "public": {
            "url": cfg.public_url,
            "path": cfg.public_path,
            **scan_marketplace(Path(cfg.public_path)) if cfg.public_path else {},
        },
        "private": {
            "url": cfg.private_url,
            "path": cfg.private_path,
            **scan_marketplace(Path(cfg.private_path)) if cfg.private_path else {},
        },
    }

    Path(cfg.public_index).write_text(
        json.dumps({"generated_at": out["generated_at"], **out["public"]}, indent=2)
    )
    Path(cfg.private_index).write_text(
        json.dumps({"generated_at": out["generated_at"], **out["private"]}, indent=2)
    )
    Path(cfg.state_file).write_text(
        json.dumps({"last_refresh": out["generated_at"]}, indent=2)
    )

    pub_n = len(out["public"].get("plugins", []))
    prv_n = len(out["private"].get("plugins", []))
    print(f"Public  : {pub_n} plugins  → {cfg.public_index}")
    print(f"Private : {prv_n} plugins  → {cfg.private_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
