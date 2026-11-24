"""Small dependency-free environment loader for local demos."""

import os
from pathlib import Path


def load_local_env(path: str = ".env") -> None:
    """Load simple KEY=VALUE pairs without overriding existing environment values."""
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
