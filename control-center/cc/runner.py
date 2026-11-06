"""Non-blocking subprocess helpers built on Gio.

Every external command is executed asynchronously through Gio.Subprocess, so the
GTK main loop (and therefore Hyprland) never blocks while nmcli/bluetoothctl run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence

import gi

gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gio, GLib  # noqa: E402


@dataclass(slots=True)
class Result:
    """Result of a finished subprocess."""

    ok: bool
    out: str = ""
    err: str = ""
    code: int = 0

    @property
    def text(self) -> str:
        """Best-effort output: stdout, falling back to stderr."""
        return self.out if self.out.strip() else self.err


Callback = Callable[[Result], None]

_FLAGS = Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE


def _spawn(argv: Sequence[str], flags: Gio.SubprocessFlags) -> Gio.Subprocess:
    """Spawn a process without leaking the layer-shell LD_PRELOAD into it."""
    launcher = Gio.SubprocessLauncher.new(flags)
    try:
        launcher.unsetenv("LD_PRELOAD")
    except GLib.Error:
        pass
    return launcher.spawnv([str(part) for part in argv])


def run(
    argv: Sequence[str],
    callback: Optional[Callback] = None,
    timeout: int = 30,
    cancellable: Optional[Gio.Cancellable] = None,
) -> Optional[Gio.Subprocess]:
    """Run a command asynchronously.

    Returns the Gio.Subprocess (useful to stop long-running scans) and invokes
    *callback* exactly once on the GTK main loop when the process exits or the
    timeout is reached.
    """
    args = [str(part) for part in argv]
    try:
        proc = _spawn(args, _FLAGS)
    except GLib.Error as exc:
        if callback is not None:
            result = Result(False, "", str(exc), -1)

            def deliver_failure() -> bool:
                callback(result)
                return GLib.SOURCE_REMOVE

            GLib.idle_add(deliver_failure)
        return None

    delivered = False
    timer_id: Optional[int] = None

    def deliver(result: Result) -> None:
        nonlocal delivered
        if delivered:
            return
        delivered = True
        if timer_id is not None:
            try:
                GLib.source_remove(timer_id)
            except GLib.Error:
                pass
        if callback is not None:
            callback(result)

    def on_timeout() -> bool:
        proc.force_exit()
        return GLib.SOURCE_REMOVE

    def on_finished(process: Gio.Subprocess, res: Gio.AsyncResult) -> None:
        try:
            _ok, out, err = process.communicate_utf8_finish(res)
        except GLib.Error as exc:
            out, err = "", str(exc)
        code = process.get_exit_status()
        deliver(Result(code == 0, out or "", err or "", code))

    proc.communicate_utf8_async(None, cancellable, on_finished)

    if timeout and timeout > 0:
        timer_id = GLib.timeout_add_seconds(timeout, on_timeout)

    return proc


def run_parallel(
    commands: Iterable[Sequence[str]],
    callback: Callable[[list[Result]], None],
    timeout: int = 30,
) -> None:
    """Run several commands concurrently and call back with all results in order."""
    cmds = list(commands)
    if not cmds:
        callback([])
        return

    results: list[Optional[Result]] = [None] * len(cmds)
    remaining = [len(cmds)]

    def make_done(index: int) -> Callback:
        def done(result: Result) -> None:
            results[index] = result
            remaining[0] -= 1
            if remaining[0] == 0:
                callback([item for item in results if item is not None])

        return done

    for index, cmd in enumerate(cmds):
        run(cmd, make_done(index), timeout=timeout)


def fire_and_forget(argv: Sequence[str]) -> None:
    """Start a command without waiting for it (used for notifications)."""
    try:
        _spawn(
            argv,
            Gio.SubprocessFlags.STDOUT_SILENCE | Gio.SubprocessFlags.STDERR_SILENCE,
        )
    except GLib.Error:
        pass


def notify(summary: str, body: str = "", icon: str = "dialog-information") -> None:
    """Send a desktop notification without blocking."""
    args = ["notify-send", "-a", "Control Center", "-i", icon]
    if body:
        args.extend([summary, body])
    else:
        args.append(summary)
    fire_and_forget(args)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences (bluetoothctl may colorise its output)."""
    import re

    return re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)
