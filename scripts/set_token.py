#!/usr/bin/env python3
"""Save the OpenAI API token for the ui-mockups skill.

Run this in your OWN terminal (not inside Claude Code's chat). It prompts
with hidden input and writes the key to:

    ~/.claude/skills/ui-mockups/.token   (mode 0600)

Stdlib only — no extra dependencies.

Usage:
    python3 ~/.claude/skills/ui-mockups/scripts/set_token.py
"""
from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

_DEFAULT_TOKEN_FILE = Path.home() / ".claude" / "skills" / "ui-mockups" / ".token"
TOKEN_FILE = Path(os.environ.get("UI_MOCKUPS_TOKEN_FILE", str(_DEFAULT_TOKEN_FILE)))


def _read_token() -> str:
    if sys.stdin.isatty():
        return getpass.getpass("Paste OpenAI API key (input hidden): ").strip()
    data = sys.stdin.read().strip()
    if not data:
        print(
            "error: no TTY and no piped input.\n"
            "  this script must be run in your own terminal so it can prompt for the key.\n"
            "  do not run it from inside Claude Code — your key would land in the transcript.",
            file=sys.stderr,
        )
        sys.exit(2)
    return data


def main() -> int:
    token = _read_token()
    if not token:
        print("error: empty token", file=sys.stderr)
        return 2

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    # O_CREAT with mode 0600 — file is never world/group readable, even briefly.
    fd = os.open(str(TOKEN_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, token.encode("utf-8"))
    finally:
        os.close(fd)
    # Belt-and-suspenders for filesystems that ignore O_CREAT mode.
    os.chmod(TOKEN_FILE, 0o600)

    redacted = f"{token[:3]}…{token[-4:]}" if len(token) > 10 else "***"
    print(f"saved {redacted} to {TOKEN_FILE} (mode 0600)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
