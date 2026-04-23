#!/usr/bin/env python3
"""Scan the marketplace.json in each configured marketplace repo, enumerate
each plugin it lists, and (where a local clone is found) catalog the plugin's
skills/commands/agents. Results are cached outside the repo.

Marketplace shape (Claude Code standard):
  <marketplace-root>/.claude-plugin/marketplace.json
    { "plugins": [ { "name", "source": {"repo": "owner/Name"}, ... } ] }

Each plugin is typically a separate GitHub repo. We look for a local clone at
the sibling path (same parent as the marketplace repo) by the repo's short
name. If found, we read the plugin's SKILL.md files, commands/*.md, agents/*.md.
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


def _scan_plugin_dir(plugin_dir: Path) -> dict:
    skills = []
    skills_dir = plugin_dir / "skills"
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
    cmd_dir = plugin_dir / "commands"
    if cmd_dir.is_dir():
        commands = sorted(c.stem for c in cmd_dir.glob("*.md"))

    agents = []
    agent_dir = plugin_dir / "agents"
    if agent_dir.is_dir():
        agents = sorted(a.stem for a in agent_dir.glob("*.md"))

    return {"skills": skills, "commands": commands, "agents": agents}


def _find_local_clone(repo_full: str, marketplace_root: Path) -> Path | None:
    """Given 'owner/RepoName', look for a local clone in sibling dirs of the
    marketplace_root (same parent), matching the repo short name."""
    if not repo_full or "/" not in repo_full:
        return None
    short = repo_full.split("/", 1)[1]
    parent = marketplace_root.parent
    candidate = parent / short
    if candidate.is_dir():
        return candidate
    # Also try ~/.claude/plugins/<short>
    alt = Path.home() / ".claude" / "plugins" / short
    if alt.is_dir():
        return alt
    return None


def scan_marketplace(root: Path) -> dict:
    if not root or not root.exists():
        return {"root": str(root), "exists": False, "plugins": []}

    mf = root / ".claude-plugin" / "marketplace.json"
    if not mf.exists():
        return {"root": str(root), "exists": True, "marketplace_json": None, "plugins": []}

    try:
        manifest = json.loads(mf.read_text())
    except Exception as e:
        return {"root": str(root), "exists": True, "parse_error": str(e), "plugins": []}

    plugins_out = []
    for entry in manifest.get("plugins", []):
        name = entry.get("name", "")
        source = entry.get("source", {}) or {}
        repo_full = source.get("repo", "")
        local = _find_local_clone(repo_full, root)

        record = {
            "name": name,
            "repo": repo_full,
            "description": entry.get("description", ""),
            "version": entry.get("version"),
            "tags": entry.get("tags", []),
            "local_path": str(local) if local else None,
        }
        if local:
            record.update(_scan_plugin_dir(local))
        else:
            record.update({"skills": [], "commands": [], "agents": []})
        plugins_out.append(record)

    # Also scan any inline plugins shipped inside the marketplace repo itself
    # under plugins/<name>/ (some marketplaces colocate a few).
    inline_dir = root / "plugins"
    if inline_dir.is_dir():
        for sub in sorted(p for p in inline_dir.iterdir() if p.is_dir()):
            # Skip if already listed above by a matching name
            if any(p["name"] == sub.name for p in plugins_out):
                continue
            rec = {
                "name": sub.name,
                "repo": None,
                "description": "(inline plugin in marketplace repo)",
                "version": None,
                "tags": [],
                "local_path": str(sub),
            }
            rec.update(_scan_plugin_dir(sub))
            plugins_out.append(rec)

    return {
        "root": str(root),
        "exists": True,
        "marketplace_name": manifest.get("name"),
        "marketplace_version": manifest.get("metadata", {}).get("version"),
        "plugins": plugins_out,
    }


def main() -> int:
    cfg = load()
    generated_at = datetime.now(timezone.utc).isoformat()
    public_scan = scan_marketplace(Path(cfg.public_path)) if cfg.public_path else {"plugins": []}
    private_scan = scan_marketplace(Path(cfg.private_path)) if cfg.private_path else {"plugins": []}

    Path(cfg.public_index).write_text(
        json.dumps(
            {"generated_at": generated_at, "url": cfg.public_url, "path": cfg.public_path, **public_scan},
            indent=2,
        )
    )
    Path(cfg.private_index).write_text(
        json.dumps(
            {"generated_at": generated_at, "url": cfg.private_url, "path": cfg.private_path, **private_scan},
            indent=2,
        )
    )
    Path(cfg.state_file).write_text(json.dumps({"last_refresh": generated_at}, indent=2))

    pub_n = len(public_scan.get("plugins", []))
    prv_n = len(private_scan.get("plugins", []))
    pub_local = sum(1 for p in public_scan.get("plugins", []) if p.get("local_path"))
    prv_local = sum(1 for p in private_scan.get("plugins", []) if p.get("local_path"))
    print(f"Public  : {pub_n} plugins ({pub_local} with local clones)  → {cfg.public_index}")
    print(f"Private : {prv_n} plugins ({prv_local} with local clones)  → {cfg.private_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
