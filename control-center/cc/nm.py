"""Async NetworkManager backend based on nmcli."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from . import runner
from .runner import Result


@dataclass(slots=True)
class WifiStatus:
    enabled: bool = False
    connected: bool = False
    ssid: str = ""
    signal: int = 0
    ip: str = ""
    iface: str = "wlan0"
    connection: str = ""
    security: str = ""


@dataclass(slots=True)
class WifiNetwork:
    ssid: str
    signal: int = 0
    security: str = ""
    active: bool = False
    saved: bool = False
    device: str = ""


StatusCallback = Callable[[WifiStatus], None]
NetworksCallback = Callable[[list[WifiNetwork]], None]
ActionCallback = Callable[[Result], None]
DataCallback = Callable[[WifiStatus, list[WifiNetwork]], None]


def _split_escaped(line: str) -> list[str]:
    """Split a terse nmcli line on unescaped ':' characters."""
    parts: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            buf.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    if escaped:
        buf.append("\\")
    parts.append("".join(buf))
    return parts


def _lines(result: Result) -> list[str]:
    if not result.ok:
        return []
    return [line for line in result.out.splitlines() if line.strip()]


def _security_label(security: str) -> str:
    value = (security or "").strip()
    if not value or value == "--":
        return ""
    return value.replace("WPA1 WPA2", "WPA/WPA2").replace("WPA2 WPA3", "WPA2/WPA3")


def _find_wifi_device(device_result: Result) -> tuple[str, str, str]:
    """Return (iface, state, connection) for the first Wi-Fi device."""
    for line in _lines(device_result):
        fields = _split_escaped(line)
        if len(fields) >= 4 and fields[1] == "wifi":
            return fields[0], fields[2], fields[3]
    return "wlan0", "", ""


def _parse_wifi_list(result: Result) -> list[WifiNetwork]:
    networks: dict[str, WifiNetwork] = {}
    for line in _lines(result):
        fields = _split_escaped(line)
        if len(fields) < 5:
            continue
        in_use, ssid, signal_text, security, device = fields[:5]
        ssid = ssid.strip()
        if not ssid:
            continue
        try:
            signal = int(signal_text)
        except ValueError:
            signal = 0
        network = WifiNetwork(
            ssid=ssid,
            signal=max(0, min(100, signal)),
            security=_security_label(security),
            active=in_use.strip() == "*",
            device=device.strip(),
        )
        previous = networks.get(ssid)
        if previous is None:
            networks[ssid] = network
        else:
            previous.active = previous.active or network.active
            if network.signal > previous.signal:
                previous.signal = network.signal
                previous.security = network.security
                previous.device = network.device
    return sorted(
        networks.values(),
        key=lambda item: (not item.active, -item.signal, item.ssid.lower()),
    )


def get_status(callback: StatusCallback) -> None:
    """Fetch the current Wi-Fi state without blocking."""

    commands = [
        ["nmcli", "-t", "-f", "WIFI", "general"],
        ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
        ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY,DEVICE", "device", "wifi", "list", "--rescan", "no"],
    ]

    def on_base(results: list[Result]) -> None:
        radio, devices, wifi_list = results
        enabled = radio.ok and radio.out.strip().splitlines()[-1:] == ["enabled"]
        iface, state, connection = _find_wifi_device(devices)
        connected = bool(state.startswith("connected") and connection)
        networks = _parse_wifi_list(wifi_list)
        active = next((item for item in networks if item.active), None)

        status = WifiStatus(
            enabled=enabled,
            connected=connected,
            iface=iface,
            connection=connection,
            ssid=connection if connected else "",
            signal=active.signal if active else 0,
            security=active.security if active else "",
        )

        if not connected:
            callback(status)
            return

        def on_ip(ip_result: Result) -> None:
            for line in _lines(ip_result):
                fields = _split_escaped(line)
                if len(fields) >= 2 and fields[0].startswith("IP4.ADDRESS"):
                    status.ip = fields[1].split("/", 1)[0]
                    break
            callback(status)

        runner.run(
            ["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", iface],
            on_ip,
            timeout=8,
        )

    runner.run_parallel(commands, on_base, timeout=12)


def get_networks(callback: NetworksCallback, rescan: bool = False) -> None:
    """List visible networks. rescan=True asks NetworkManager for a fresh scan."""
    commands = [
        [
            "nmcli",
            "--wait",
            "25",
            "-t",
            "-f",
            "IN-USE,SSID,SIGNAL,SECURITY,DEVICE",
            "device",
            "wifi",
            "list",
            "--rescan",
            "yes" if rescan else "no",
        ],
        ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
    ]

    def on_done(results: list[Result]) -> None:
        wifi_result, connections_result = results
        saved_names: set[str] = set()
        for line in _lines(connections_result):
            fields = _split_escaped(line)
            if len(fields) >= 2 and fields[1] == "802-11-wireless":
                saved_names.add(fields[0])
        networks = _parse_wifi_list(wifi_result)
        for network in networks:
            network.saved = network.ssid in saved_names
        callback(networks)

    runner.run_parallel(commands, on_done, timeout=35)


def fetch(callback: DataCallback, rescan: bool = False) -> None:
    """Fetch status and network list concurrently."""
    state: dict[str, object] = {}

    def maybe_finish() -> None:
        if "status" in state and "networks" in state:
            callback(state["status"], state["networks"])  # type: ignore[arg-type]

    def on_status(status: WifiStatus) -> None:
        state["status"] = status
        maybe_finish()

    def on_networks(networks: list[WifiNetwork]) -> None:
        state["networks"] = networks
        maybe_finish()

    get_status(on_status)
    get_networks(on_networks, rescan=rescan)


def set_enabled(enabled: bool, callback: Optional[ActionCallback] = None) -> None:
    done = callback or (lambda _result: None)

    if not enabled:
        runner.run(["nmcli", "radio", "wifi", "off"], done, timeout=12)
        return

    def on_rfkill(result: Result) -> None:
        if result.ok and "Hard blocked: yes" in result.out:
            done(Result(False, "", "RFKILL_HARD", 1))
            return
        runner.run(["nmcli", "radio", "wifi", "on"], done, timeout=12)

    runner.run(["rfkill", "list", "wifi"], on_rfkill, timeout=5)


def connect(ssid: str, password: Optional[str], callback: ActionCallback) -> None:
    argv = ["nmcli", "--wait", "35", "device", "wifi", "connect", ssid]
    if password:
        argv.extend(["password", password])
    runner.run(argv, callback, timeout=45)


def disconnect(iface: str, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["nmcli", "device", "disconnect", iface],
        callback or (lambda _result: None),
        timeout=15,
    )


def forget(connection: str, callback: Optional[ActionCallback] = None) -> None:
    runner.run(
        ["nmcli", "connection", "delete", "id", connection],
        callback or (lambda _result: None),
        timeout=15,
    )


def signal_level(signal: int) -> int:
    """Map 0..100 to 0..4 for the icon set."""
    if signal >= 80:
        return 4
    if signal >= 60:
        return 3
    if signal >= 40:
        return 2
    if signal >= 20:
        return 1
    return 0


def friendly_error(result: Result) -> str:
    """Translate common nmcli failures into short human-readable messages."""
    raw = (result.err or result.out or "").strip()
    lowered = raw.lower()
    if "rfkill_hard" in lowered:
        return "Wi-Fi заблокирован аппаратно (rfkill)"
    if "secrets were required" in lowered or "no secrets" in lowered:
        return "Неверный пароль или сеть требует пароль"
    if "not authorized" in lowered or "insufficient privileges" in lowered:
        return "Недостаточно прав для управления NetworkManager"
    if "no network with ssid" in lowered or "not found" in lowered:
        return "Сеть не найдена или вне зоны действия"
    if "timeout" in lowered or "timed out" in lowered:
        return "Истекло время ожидания. Попробуйте ещё раз"
    if "rfkill" in lowered or "disabled by" in lowered:
        return "Wi-Fi заблокирован на аппаратном уровне (rfkill)"
    if "connection activation failed" in lowered:
        return "Не удалось подключиться к сети"
    if raw:
        return raw.splitlines()[0][:180]
    return "Неизвестная ошибка NetworkManager"
