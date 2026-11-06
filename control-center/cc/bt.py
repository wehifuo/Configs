"""Async BlueZ backend based on bluetoothctl."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

from . import runner
from .runner import Result

_MAC_RE = re.compile(r"^Device\s+([0-9A-Fa-f:]{17})\s*(.*)$")
_BATTERY_RE = re.compile(
    r"Battery Percentage:\s*(?:0x[0-9A-Fa-f]+\s*\(\s*(\d+)\s*\)|(\d+))",
    re.IGNORECASE,
)
_RSSI_RE = re.compile(r"RSSI:\s*(?:0x[0-9A-Fa-f]+\s*\(\s*(-?\d+)\s*\)|(-?\d+))", re.IGNORECASE)


@dataclass(slots=True)
class BtStatus:
    available: bool = False
    powered: bool = False
    discovering: bool = False
    discoverable: bool = False
    alias: str = "Bluetooth"
    address: str = ""


@dataclass(slots=True)
class BtDevice:
    mac: str
    name: str = ""
    paired: bool = False
    trusted: bool = False
    connected: bool = False
    blocked: bool = False
    icon: str = ""
    battery: Optional[int] = None
    rssi: Optional[int] = None


StatusCallback = Callable[[BtStatus], None]
DevicesCallback = Callable[[list[BtDevice]], None]
ActionCallback = Callable[[Result], None]
DataCallback = Callable[[BtStatus, list[BtDevice]], None]


def _parse_show(text: str) -> BtStatus:
    values: dict[str, str] = {}
    controller = ""
    for line in text.splitlines():
        match = re.match(r"^\s*Controller\s+([0-9A-Fa-f:]{17})", line)
        if match:
            controller = match.group(1)
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()

    address = values.get("address") or controller
    available = bool(address)
    return BtStatus(
        available=available,
        powered=values.get("powered", "no") == "yes",
        discovering=values.get("discovering", "no") == "yes",
        discoverable=values.get("discoverable", "no") == "yes",
        alias=values.get("alias") or values.get("name") or "Bluetooth",
        address=address,
    )


def _parse_device_info(mac: str, fallback_name: str, text: str) -> BtDevice:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()

    battery = None
    for match in _BATTERY_RE.finditer(text):
        battery = int(match.group(1) or match.group(2))
        break

    rssi = None
    for match in _RSSI_RE.finditer(text):
        rssi = int(match.group(1) or match.group(2))
        break

    return BtDevice(
        mac=mac,
        name=values.get("alias") or values.get("name") or fallback_name or mac,
        paired=values.get("paired", "no") == "yes",
        trusted=values.get("trusted", "no") == "yes",
        connected=values.get("connected", "no") == "yes",
        blocked=values.get("blocked", "no") == "yes",
        icon=values.get("icon", ""),
        battery=battery,
        rssi=rssi,
    )


def get_status(callback: StatusCallback) -> None:
    def on_done(result: Result) -> None:
        if not result.ok:
            callback(BtStatus(available=False))
            return
        callback(_parse_show(runner.strip_ansi(result.out)))

    runner.run(["bluetoothctl", "show"], on_done, timeout=10)


def get_devices(callback: DevicesCallback) -> None:
    def on_list(result: Result) -> None:
        if not result.ok:
            callback([])
            return

        devices: list[tuple[str, str]] = []
        for line in runner.strip_ansi(result.out).splitlines():
            match = _MAC_RE.match(line.strip())
            if match:
                devices.append((match.group(1).upper(), match.group(2).strip()))

        if not devices:
            callback([])
            return

        commands = [["bluetoothctl", "info", mac] for mac, _name in devices]

        def on_infos(results: list[Result]) -> None:
            parsed: list[BtDevice] = []
            for (mac, name), info in zip(devices, results):
                if info.ok:
                    parsed.append(_parse_device_info(mac, name, runner.strip_ansi(info.out)))
                else:
                    parsed.append(BtDevice(mac=mac, name=name or mac))
            parsed.sort(key=lambda item: (not item.connected, not item.paired, item.name.lower()))
            callback(parsed)

        runner.run_parallel(commands, on_infos, timeout=12)

    runner.run(["bluetoothctl", "devices"], on_list, timeout=10)


def fetch(callback: DataCallback) -> None:
    state: dict[str, object] = {}

    def maybe_finish() -> None:
        if "status" in state and "devices" in state:
            callback(state["status"], state["devices"])  # type: ignore[arg-type]

    def on_status(status: BtStatus) -> None:
        state["status"] = status
        maybe_finish()

    def on_devices(devices: list[BtDevice]) -> None:
        state["devices"] = devices
        maybe_finish()

    get_status(on_status)
    get_devices(on_devices)


def start_scan(callback: ActionCallback, seconds: int = 20):
    """Start a 20-second LE/BRedR scan. Returns the process so it can be stopped."""
    return runner.run(
        ["bluetoothctl", "--timeout", str(seconds), "scan", "on"],
        callback,
        timeout=seconds + 8,
    )


def set_power(enabled: bool, callback: Optional[ActionCallback] = None) -> None:
    done = callback or (lambda _result: None)

    if not enabled:
        runner.run(["bluetoothctl", "power", "off"], done, timeout=15)
        return

    def on_rfkill(result: Result) -> None:
        if result.ok and "Hard blocked: yes" in result.out:
            done(Result(False, "", "RFKILL_HARD", 1))
            return
        runner.run(["bluetoothctl", "power", "on"], done, timeout=15)

    runner.run(["rfkill", "list", "bluetooth"], on_rfkill, timeout=5)


def set_discoverable(enabled: bool, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["bluetoothctl", "discoverable", "on" if enabled else "off"],
        callback or (lambda _result: None),
        timeout=15,
    )


def pair(mac: str, callback: ActionCallback) -> None:
    runner.run(
        ["bluetoothctl", "--timeout", "30", "pair", mac],
        callback,
        timeout=40,
    )


def connect(mac: str, callback: ActionCallback) -> None:
    runner.run(
        ["bluetoothctl", "--timeout", "25", "connect", mac],
        callback,
        timeout=35,
    )


def disconnect(mac: str, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["bluetoothctl", "disconnect", mac],
        callback or (lambda _result: None),
        timeout=15,
    )


def trust(mac: str, trusted: bool, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["bluetoothctl", "trust" if trusted else "untrust", mac],
        callback or (lambda _result: None),
        timeout=12,
    )


def remove(mac: str, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["bluetoothctl", "remove", mac],
        callback or (lambda _result: None),
        timeout=15,
    )


def icon_for(device: BtDevice) -> str:
    icon = (device.icon or "").lower()
    if "headset" in icon or "headphone" in icon:
        return "\U000f02cb"  # md-headphones
    if "audio" in icon or "speaker" in icon:
        return "\U000f04c3"  # md-speaker
    if "mouse" in icon:
        return "\U000f037d"  # md-mouse
    if "keyboard" in icon:
        return "\U000f030c"  # md-keyboard
    if "game" in icon or "joystick" in icon:
        return "\U000f0296"  # md-gamepad
    if "phone" in icon:
        return "\U000f03ba"  # md-cellphone
    if "computer" in icon or "laptop" in icon:
        return "\U000f0322"  # md-laptop
    if "watch" in icon:
        return "\U000f0589"  # md-watch
    return "\U000f00af"  # md-bluetooth


def friendly_error(result: Result) -> str:
    raw = (result.err or result.out or "").strip()
    lowered = raw.lower()
    if "rfkill_hard" in lowered:
        return "Bluetooth заблокирован аппаратно (rfkill)"
    if "authenticationfailed" in lowered or "authentication failed" in lowered:
        return "Ошибка аутентификации. Попробуйте сопрячь устройство заново"
    if "authenticationcanceled" in lowered or "authentication canceled" in lowered:
        return "Сопряжение отменено на устройстве"
    if "alreadyexists" in lowered or "already exists" in lowered:
        return "Устройство уже сопряжено"
    if "br-connection-profile-unavailable" in lowered:
        return "Профиль устройства недоступен"
    if "failed to connect" in lowered or "connection failed" in lowered:
        return "Не удалось подключить устройство"
    if "not available" in lowered or "does not exist" in lowered:
        return "Устройство не найдено"
    if "not powered" in lowered or "powered: no" in lowered:
        return "Bluetooth-адаптер выключен"
    if "timeout" in lowered or "timed out" in lowered:
        return "Истекло время ожидания"
    if raw:
        return raw.splitlines()[0][:180]
    return "Неизвестная ошибка BlueZ"
