#!/usr/bin/env python3
"""Waybar JSON module: Bluetooth adapter / connected device summary."""

from __future__ import annotations

import json
import re
import subprocess
import sys

ICON_ON = "\U000f00af"       # md-bluetooth
ICON_OFF = "\U000f00b2"      # md-bluetooth-off
BATTERY_RE = re.compile(
    r"Battery Percentage:\s*(?:0x[0-9A-Fa-f]+\s*\(\s*(\d+)\s*\)|(\d+))",
    re.IGNORECASE,
)


def run(*args: str, timeout: float = 3.0) -> str:
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return completed.stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def main() -> int:
    show = run("bluetoothctl", "show")
    if not show:
        print(
            json.dumps(
                {
                    "text": ICON_OFF,
                    "tooltip": "Bluetooth недоступен",
                    "class": "disabled",
                },
                ensure_ascii=False,
            )
        )
        return 0

    powered = bool(re.search(r"^\s*Powered:\s*yes\s*$", show, re.MULTILINE))
    if not powered:
        print(
            json.dumps(
                {
                    "text": ICON_OFF,
                    "tooltip": "Bluetooth выключен\nЛКМ — открыть центр управления",
                    "class": "disabled",
                },
                ensure_ascii=False,
            )
        )
        return 0

    devices = run("bluetoothctl", "devices", "Connected")
    connected: list[tuple[str, str]] = []
    for line in devices.splitlines():
        match = re.match(r"^Device\s+([0-9A-Fa-f:]{17})\s+(.*)$", line.strip())
        if not match:
            continue
        mac, name = match.group(1), match.group(2) or match.group(1)
        info = run("bluetoothctl", "info", mac)
        connected.append((name, info))

    text = ICON_ON
    tooltip_lines = ["Bluetooth включён"]
    if connected:
        text = f"{ICON_ON} {len(connected)}"
        for name, info in connected:
            battery = BATTERY_RE.search(info)
            value = ""
            if battery:
                value = f" · {battery.group(1) or battery.group(2)}%"
            tooltip_lines.append(f"{name}{value}")
        css_class = "connected"
    else:
        tooltip_lines.append("Нет подключённых устройств")
        css_class = "on"

    tooltip_lines.append("ЛКМ — открыть центр управления")
    print(
        json.dumps(
            {
                "text": text,
                "tooltip": "\n".join(tooltip_lines),
                "class": css_class,
                "alt": css_class,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
