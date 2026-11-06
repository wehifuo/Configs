#!/usr/bin/env python3
"""Entry point for the GTK4 layer-shell control center."""

from __future__ import annotations

import os
import sys

PRELOAD_LIBRARY = "/usr/lib/libgtk4-layer-shell.so"


def _ensure_layer_shell_preload() -> None:
    """gtk4-layer-shell must be linked before libwayland-client.

    When the interpreter imports GTK first, layer-shell silently refuses to
    initialise. Re-exec once with LD_PRELOAD set, which is the fix recommended
    by upstream for Python/GTK applications.
    """
    if not os.path.exists(PRELOAD_LIBRARY):
        return
    current = os.environ.get("LD_PRELOAD", "")
    if PRELOAD_LIBRARY in current.split():
        return
    env = os.environ.copy()
    env["LD_PRELOAD"] = f"{PRELOAD_LIBRARY} {current}".strip()
    os.execve(
        sys.executable,
        [sys.executable, os.path.abspath(__file__), *sys.argv[1:]],
        env,
    )


_ensure_layer_shell_preload()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cc.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
