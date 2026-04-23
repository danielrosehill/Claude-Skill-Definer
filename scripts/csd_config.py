#!/usr/bin/env python3
"""Shared config loader for Claude-Skill-Definer.

Reads env vars (and optionally a .env in the repo root), resolves the data dir,
and exposes paths for cached marketplace indexes.

Usage from Bash:
  eval "$(python3 scripts/csd_config.py export)"
  # then $CSD_DATA_DIR, $CSD_PUBLIC_INDEX, $CSD_PRIVATE_INDEX, etc. are set

Usage from Python:
  from csd_config import load
  cfg = load()
  print(cfg.public_index)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _env(key: str, dotenv: dict[str, str], default: str = "") -> str:
    return os.environ.get(key) or dotenv.get(key) or default


@dataclass
class Config:
    public_url: str
    public_path: str
    private_url: str
    private_path: str
    data_dir: str

    @property
    def public_index(self) -> str:
        return str(Path(self.data_dir) / "public-index.json")

    @property
    def private_index(self) -> str:
        return str(Path(self.data_dir) / "private-index.json")

    @property
    def state_file(self) -> str:
        return str(Path(self.data_dir) / "state.json")


def load() -> Config:
    dotenv = _read_dotenv(REPO_ROOT / ".env")
    data_dir = _env(
        "CSD_DATA_DIR",
        dotenv,
        str(Path.home() / ".local" / "share" / "claude-skill-definer"),
    )
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return Config(
        public_url=_env("CSD_PUBLIC_MARKETPLACE_URL", dotenv),
        public_path=_env("CSD_PUBLIC_MARKETPLACE_PATH", dotenv),
        private_url=_env("CSD_PRIVATE_MARKETPLACE_URL", dotenv),
        private_path=_env("CSD_PRIVATE_MARKETPLACE_PATH", dotenv),
        data_dir=data_dir,
    )


def _cmd_export(cfg: Config) -> None:
    pairs = {
        "CSD_PUBLIC_MARKETPLACE_URL": cfg.public_url,
        "CSD_PUBLIC_MARKETPLACE_PATH": cfg.public_path,
        "CSD_PRIVATE_MARKETPLACE_URL": cfg.private_url,
        "CSD_PRIVATE_MARKETPLACE_PATH": cfg.private_path,
        "CSD_DATA_DIR": cfg.data_dir,
        "CSD_PUBLIC_INDEX": cfg.public_index,
        "CSD_PRIVATE_INDEX": cfg.private_index,
        "CSD_STATE_FILE": cfg.state_file,
    }
    for k, v in pairs.items():
        safe = v.replace('"', '\\"')
        print(f'export {k}="{safe}"')


def _cmd_show(cfg: Config) -> None:
    print(json.dumps({**asdict(cfg), "public_index": cfg.public_index,
                      "private_index": cfg.private_index,
                      "state_file": cfg.state_file}, indent=2))


def _cmd_check(cfg: Config) -> int:
    missing = []
    for label, val in [
        ("CSD_PUBLIC_MARKETPLACE_URL", cfg.public_url),
        ("CSD_PUBLIC_MARKETPLACE_PATH", cfg.public_path),
        ("CSD_PRIVATE_MARKETPLACE_URL", cfg.private_url),
        ("CSD_PRIVATE_MARKETPLACE_PATH", cfg.private_path),
    ]:
        if not val:
            missing.append(label)
    for label, val in [
        ("CSD_PUBLIC_MARKETPLACE_PATH", cfg.public_path),
        ("CSD_PRIVATE_MARKETPLACE_PATH", cfg.private_path),
    ]:
        if val and not Path(val).exists():
            print(f"WARN  {label}={val} does not exist on disk", file=sys.stderr)
    if missing:
        print("MISSING env vars: " + ", ".join(missing), file=sys.stderr)
        return 1
    print(f"OK    config loaded; data_dir={cfg.data_dir}")
    return 0


def main(argv: list[str]) -> int:
    cfg = load()
    cmd = argv[1] if len(argv) > 1 else "show"
    if cmd == "export":
        _cmd_export(cfg)
        return 0
    if cmd == "show":
        _cmd_show(cfg)
        return 0
    if cmd == "check":
        return _cmd_check(cfg)
    print(f"unknown command: {cmd} (use: export | show | check)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
