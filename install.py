#!/usr/bin/env python3
"""Install the Terminal Theme Picker menu-bar agent for the current user."""

from __future__ import annotations

import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path


LABEL = "com.terminal-theme-picker.agent"
ROOT = Path(__file__).resolve().parent
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
LOG = Path.home() / "Library" / "Logs" / "terminal-theme-picker-agent.log"


def main() -> int:
    if sys.platform != "darwin":
        print("Terminal Theme Picker needs macOS.", file=sys.stderr)
        return 1

    PLIST.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(ROOT / "theme-picker-agent")],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(LOG),
        "StandardErrorPath": str(LOG),
    }
    PLIST.write_bytes(plistlib.dumps(document))

    domain = f"gui/{os.getuid()}"
    subprocess.run(["launchctl", "bootout", f"{domain}/{LABEL}"], check=False, capture_output=True)
    for _ in range(20):
        stopped = subprocess.run(
            ["launchctl", "print", f"{domain}/{LABEL}"], capture_output=True
        ).returncode != 0
        if stopped:
            break
        time.sleep(0.1)
    else:
        print("Could not stop the existing menu-bar agent.", file=sys.stderr)
        return 1
    subprocess.run(["launchctl", "bootstrap", domain, str(PLIST)], check=True)
    print(f"Installed {LABEL}. Press Option-Shift-P in Apple Terminal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
