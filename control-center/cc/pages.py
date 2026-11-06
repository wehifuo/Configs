"""GTK4 pages: overview, Wi-Fi and Bluetooth."""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")

from gi.repository import GLib, Gtk  # noqa: E402

from . import bt, nm, widgets as w
from .runner import Result

# Material Design icons shipped with the installed JetBrainsMono Nerd Font.
ICON_WIFI = "\U000f05a9"
ICON_WIFI_OFF = "\U000f05aa"
ICON_BLUETOOTH = "\U000f00af"
ICON_BLUETOOTH_OFF = "\U000f00b2"
ICON_LOCK = "\U000f033e"
ICON_CHECK = "\U000f05e0"
ICON_CLOSE = "\U000f0156"
ICON_BACK = "\U000f004d"
ICON_REFRESH = "\U000f0450"
ICON_MAGNIFY = "\U000f0349"
ICON_DELETE = "\U000f01b4"
ICON_POWER = "\U000f0425"
ICON_BATTERY = "\U000f0079"
ICON_CHEVRON = "\U000f0142"
ICON_SHIELD = "\U000f0565"
ICON_SETTINGS = "\U000f0493"

SIGNAL_ICONS = [
    "\U000f092f",  # outline / very weak
    "\U000f091f",  # 1
    "\U000f0922",  # 2
    "\U000f0925",  # 3
    "\U000f0928",  # 4
]

ASSET_CLOWN = Path(__file__).resolve().parent.parent / "assets" / "clown-bw.png"

ToastCallback = Callable[[str, bool], None]


def _requires_password(security: str) -> bool:
    value = (security or "").strip().upper()
    return bool(value) and value not in ("--", "OWE")


def _empty_state(
    icon: str,
    title: str,
    subtitle: str,
    button: Optional[Gtk.Widget] = None,
    *,
    top: int = 30,
    bottom: int = 30,
) -> Gtk.Box:
    box = w.box(Gtk.Orientation.VERTICAL, 8, top=top, bottom=bottom)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)
    icon_widget = w.icon_label(icon, "xl")
    icon_widget.add_css_class("muted-icon")
    icon_widget.set_halign(Gtk.Align.CENTER)
    box.append(icon_widget)
    title_widget = w.label(title, "empty-title", xalign=0.5)
    title_widget.set_halign(Gtk.Align.CENTER)
    box.append(title_widget)
    subtitle_widget = w.label(subtitle, "muted", wrap=True, xalign=0.5, max_width=32)
    subtitle_widget.set_halign(Gtk.Align.CENTER)
    subtitle_widget.set_justify(Gtk.Justification.CENTER)
    box.append(subtitle_widget)
    if button is not None:
        button.set_halign(Gtk.Align.CENTER)
        button.set_margin_top(8)
        box.append(button)
    return box


def _page_header(
    title: str,
    subtitle: str,
    *,
    on_back: Optional[Callable[[], None]] = None,
    on_close: Optional[Callable[[], None]] = None,
) -> tuple[Gtk.Box, Gtk.Label, Gtk.Label, Gtk.Button]:
    header = w.box(Gtk.Orientation.HORIZONTAL, 10, bottom=10)
    header.set_valign(Gtk.Align.CENTER)

    if on_back is not None:
        back = w.icon_button(ICON_BACK, "В меню", lambda _b: on_back())
        header.append(back)
    else:
        if ASSET_CLOWN.exists():
            logo = Gtk.Image.new_from_file(str(ASSET_CLOWN))
            logo.set_pixel_size(28)
            logo.add_css_class("brand-logo")
            logo.set_tooltip_text("Control Center")
            header.append(logo)
        else:
            logo = w.label("\U0001f921", "brand-emoji")
            header.append(logo)

    titles = w.box(Gtk.Orientation.VERTICAL, 1, hexpand=True)
    title_label = w.label(title, "page-title", ellipsize=True)
    subtitle_label = w.label(subtitle, "page-subtitle", ellipsize=True)
    titles.append(title_label)
    titles.append(subtitle_label)
    header.append(titles)

    if on_close is not None:
        close = w.icon_button(ICON_CLOSE, "Закрыть (Esc)", lambda _b: on_close())
        header.append(close)

    return header, title_label, subtitle_label, header


class QuickTile(Gtk.Overlay):
    """A large control-center tile. Clicking the body opens a page, the switch toggles power."""

    def __init__(
        self,
        icon_on: str,
        icon_off: str,
        title: str,
        on_open: Callable[[], None],
        on_toggle: Callable[[bool], None],
        key: str = "",
    ) -> None:
        super().__init__()
        self.icon_on = icon_on
        self.icon_off = icon_off

        self.button = Gtk.Button()
        self.button.add_css_class("tile")
        self.button.set_hexpand(True)
        self.button.connect("clicked", lambda _b: on_open())

        content = w.box(Gtk.Orientation.VERTICAL, 8, top=14, bottom=14, start=14, end=14)
        top = w.box(Gtk.Orientation.HORIZONTAL, 0)
        self.icon_box = w.box(Gtk.Orientation.HORIZONTAL, 0)
        self.icon_box.add_css_class("tile-icon")
        self.icon_box.set_size_request(42, 42)
        self.icon_box.set_halign(Gtk.Align.CENTER)
        self.icon_box.set_valign(Gtk.Align.CENTER)
        self.icon = w.icon_label(icon_off, "lg")
        if key:
            self.icon.add_css_class(f"tile-{key}-icon")
            self.icon_box.add_css_class(f"tile-{key}-box")
        self.icon.set_hexpand(True)
        self.icon.set_vexpand(True)
        self.icon.set_xalign(0.5)
        self.icon.set_yalign(0.5)
        self.icon.set_halign(Gtk.Align.CENTER)
        self.icon.set_valign(Gtk.Align.CENTER)
        self.icon_box.append(self.icon)
        top.append(self.icon_box)
        top.append(w.spacer())
        content.append(top)

        self.title = w.label(title, "tile-title")
        self.subtitle = w.label("Выключен", "tile-subtitle", wrap=True, ellipsize=True)
        self.subtitle.set_lines(2)
        content.append(self.title)
        content.append(self.subtitle)
        self.button.set_child(content)
        self.set_child(self.button)

        self.power = w.switch(False, on_toggle)
        self.power.set_halign(Gtk.Align.END)
        self.power.set_valign(Gtk.Align.START)
        self.power.set_margin_top(14)
        self.power.set_margin_end(14)
        self.add_overlay(self.power)

    def update(self, enabled: bool, subtitle: str) -> None:
        w.set_switch(self.power, enabled)
        self.icon.set_label(self.icon_on if enabled else self.icon_off)
        self.subtitle.set_label(subtitle)
        if enabled:
            self.button.add_css_class("on")
            self.icon_box.add_css_class("on")
        else:
            self.button.remove_css_class("on")
            self.icon_box.remove_css_class("on")


class OverviewPage(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.app = app
        self.add_css_class("page")

        header, _title, _subtitle, _ = _page_header(
            "Центр управления",
            f"Hyprland · {socket.gethostname()}",
            on_close=self.app.hide_panel,
        )
        self.append(header)

        tiles = w.box(Gtk.Orientation.HORIZONTAL, 10, bottom=14)
        self.wifi_tile = QuickTile(
            ICON_WIFI,
            ICON_WIFI_OFF,
            "Wi-Fi",
            lambda: self.app.show_page("wifi"),
            self.app.set_wifi_power,
            key="wifi",
        )
        self.bt_tile = QuickTile(
            ICON_BLUETOOTH,
            ICON_BLUETOOTH_OFF,
            "Bluetooth",
            lambda: self.app.show_page("bluetooth"),
            self.app.set_bt_power,
            key="bluetooth",
        )
        tiles.append(self.wifi_tile)
        tiles.append(self.bt_tile)
        self.append(tiles)

        self.append(w.section_title("Сейчас"))
        card = w.box(Gtk.Orientation.VERTICAL, 0, top=4, bottom=4)
        card.add_css_class("card")

        self.wifi_row, self.wifi_row_title, self.wifi_row_meta, self.wifi_row_icon = (
            self._status_row(
                ICON_WIFI_OFF,
                "Wi-Fi",
                "Выключен",
                lambda: self.app.show_page("wifi"),
                key="wifi",
            )
        )
        self.bt_row, self.bt_row_title, self.bt_row_meta, self.bt_row_icon = self._status_row(
            ICON_BLUETOOTH_OFF,
            "Bluetooth",
            "Выключен",
            lambda: self.app.show_page("bluetooth"),
            key="bluetooth",
        )
        card.append(self.wifi_row)
        card.append(w.divider(top=2, bottom=2))
        card.append(self.bt_row)
        self.append(card)

        bottom_spacer = Gtk.Box()
        bottom_spacer.set_vexpand(True)
        self.append(bottom_spacer)
        self.append(w.divider(top=14, bottom=8))

        footer = w.box(Gtk.Orientation.HORIZONTAL, 8)
        footer.append(w.label("SUPER + SHIFT + W", "keycap"))
        footer.append(w.label("открыть / закрыть", "muted-small"))
        footer.append(w.spacer())
        footer.append(w.label("Esc — закрыть", "muted-small"))
        self.append(footer)

    def _status_row(
        self,
        icon: str,
        title: str,
        meta: str,
        on_click: Callable[[], None],
        key: str = "",
    ) -> tuple[Gtk.Button, Gtk.Label, Gtk.Label, Gtk.Label]:
        button = Gtk.Button()
        button.add_css_class("row")
        button.set_hexpand(True)
        button.connect("clicked", lambda _b: on_click())

        content = w.box(Gtk.Orientation.HORIZONTAL, 10, top=10, bottom=10, start=10, end=10)
        icon_widget = w.icon_label(icon, "md")
        icon_widget.add_css_class("row-icon")
        if key:
            icon_widget.add_css_class(f"row-{key}-icon")
        content.append(icon_widget)

        labels = w.box(Gtk.Orientation.VERTICAL, 1, hexpand=True)
        title_widget = w.label(title, "row-title", ellipsize=True)
        meta_widget = w.label(meta, "row-meta", ellipsize=True)
        labels.append(title_widget)
        labels.append(meta_widget)
        content.append(labels)
        content.append(w.icon_label(ICON_CHEVRON, "sm"))
        button.set_child(content)
        return button, title_widget, meta_widget, icon_widget

    def update_wifi(self, status: nm.WifiStatus) -> None:
        if not status.enabled:
            self.wifi_tile.update(False, "Выключен")
            self.wifi_row_icon.set_label(ICON_WIFI_OFF)
            self.wifi_row_title.set_label("Wi-Fi")
            self.wifi_row_meta.set_label("Выключен")
            return

        if status.connected:
            subtitle = f"{status.ssid} · {status.signal}%"
            meta = f"{status.ssid} · {status.signal}%"
            if status.ip:
                meta += f" · {status.ip}"
        else:
            subtitle = "Включён · не подключено"
            meta = "Включён · не подключено"
        self.wifi_tile.update(True, subtitle)
        self.wifi_row_icon.set_label(ICON_WIFI)
        self.wifi_row_title.set_label("Wi-Fi")
        self.wifi_row_meta.set_label(meta)

    def update_bluetooth(self, status: bt.BtStatus, devices: list[bt.BtDevice]) -> None:
        if not status.powered:
            self.bt_tile.update(False, "Выключен")
            self.bt_row_icon.set_label(ICON_BLUETOOTH_OFF)
            self.bt_row_title.set_label("Bluetooth")
            self.bt_row_meta.set_label("Выключен")
            return

        connected = [device for device in devices if device.connected]
        if connected:
            first = connected[0]
            subtitle = f"{len(connected)} подключено"
            meta = first.name
            if first.battery is not None:
                meta += f" · {first.battery}%"
        else:
            subtitle = "Включён · нет подключений"
            meta = "Включён · нет подключений"
        self.bt_tile.update(True, subtitle)
        self.bt_row_icon.set_label(ICON_BLUETOOTH)
        self.bt_row_title.set_label("Bluetooth")
        self.bt_row_meta.set_label(meta)


class NetworkRow(Gtk.Box):
    def __init__(self, page: "WifiPage") -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.page = page
        self.network: Optional[nm.WifiNetwork] = None
        self.busy = False

        self.main = Gtk.Button()
        self.main.add_css_class("row")
        self.main.add_css_class("network-row")
        self.main.set_hexpand(True)
        self.main.connect("clicked", self._clicked)

        content = w.box(Gtk.Orientation.HORIZONTAL, 10, top=8, bottom=8, start=8, end=8)
        self.signal = w.icon_label(SIGNAL_ICONS[0], "md")
        self.signal.add_css_class("row-icon")
        content.append(self.signal)

        labels = w.box(Gtk.Orientation.VERTICAL, 1, hexpand=True)
        self.name = w.label("", "row-title", ellipsize=True)
        self.meta = w.label("", "row-meta", ellipsize=True)
        labels.append(self.name)
        labels.append(self.meta)
        content.append(labels)

        self.spinner = Gtk.Spinner()
        self.spinner.set_valign(Gtk.Align.CENTER)
        self.spinner.set_visible(False)
        content.append(self.spinner)

        self.lock = w.icon_label(ICON_LOCK, "sm")
        self.lock.add_css_class("row-lock")
        content.append(self.lock)

        self.check = w.icon_label(ICON_CHECK, "sm")
        self.check.add_css_class("row-check")
        content.append(self.check)

        self.main.set_child(content)
        self.append(self.main)

        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_transition_duration(180)
        self.revealer.set_reveal_child(False)

        password_box = w.box(Gtk.Orientation.VERTICAL, 6, top=6, bottom=8, start=48, end=8)
        self.entry = Gtk.PasswordEntry()
        self.entry.set_property("placeholder-text", "Пароль сети")
        self.entry.set_show_peek_icon(True)
        self.entry.connect("activate", self._submit)
        password_box.append(self.entry)

        self.error = w.label("", "error-text", wrap=True)
        self.error.set_visible(False)
        password_box.append(self.error)

        actions = w.box(Gtk.Orientation.HORIZONTAL, 8)
        actions.append(w.spacer())
        actions.append(w.pill_button("Отмена", on_click=lambda _b: self.close_password()))
        self.connect_button = w.pill_button(
            "Подключить", css="accent", on_click=self._submit
        )
        actions.append(self.connect_button)
        password_box.append(actions)
        self.revealer.set_child(password_box)
        self.append(self.revealer)

    def update(self, network: nm.WifiNetwork) -> None:
        self.network = network
        self.name.set_label(network.ssid)
        security = network.security or "Открытая"
        meta = security
        if network.saved:
            meta += " · Сохранено"
        self.meta.set_label(meta)
        level = nm.signal_level(network.signal)
        self.signal.set_label(SIGNAL_ICONS[level])
        for css in ("signal-weak", "signal-ok", "signal-good"):
            self.signal.remove_css_class(css)
        if level <= 1:
            self.signal.add_css_class("signal-weak")
        elif level <= 2:
            self.signal.add_css_class("signal-ok")
        else:
            self.signal.add_css_class("signal-good")
        self.lock.set_visible(bool(network.security))
        self.check.set_visible(network.active)
        if network.active:
            self.main.add_css_class("active")
            self.main.set_tooltip_text("Подключено")
        else:
            self.main.remove_css_class("active")
            self.main.set_tooltip_text("Нажмите, чтобы подключиться")

    def _clicked(self, _button: Gtk.Button) -> None:
        if self.busy or self.network is None or self.network.active:
            return
        if _requires_password(self.network.security) and not self.network.saved:
            self.open_password()
        else:
            self.page.connect_network(self, None)

    def _submit(self, _widget=None) -> None:
        if self.network is None:
            return
        password = self.entry.get_text()
        if not password:
            self.set_error("Введите пароль")
            return
        self.page.connect_network(self, password)

    def open_password(self, message: str = "") -> None:
        self.revealer.set_reveal_child(True)
        self.page.set_password_row(self)
        if message:
            self.set_error(message)
        else:
            self.error.set_visible(False)
        GLib.idle_add(self._focus_entry)

    def _focus_entry(self) -> bool:
        self.entry.grab_focus()
        return GLib.SOURCE_REMOVE

    def close_password(self) -> None:
        self.revealer.set_reveal_child(False)
        self.entry.set_text("")
        self.error.set_visible(False)
        if self.page.password_ssid == (self.network.ssid if self.network else None):
            self.page.password_ssid = None

    def set_error(self, message: str) -> None:
        self.error.set_label(message)
        self.error.set_visible(True)
        self.revealer.set_reveal_child(True)

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.main.set_sensitive(not busy)
        self.entry.set_sensitive(not busy)
        self.connect_button.set_sensitive(not busy)
        if busy:
            self.spinner.set_visible(True)
            self.spinner.start()
        else:
            self.spinner.stop()
            self.spinner.set_visible(False)


class WifiPage(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.app = app
        self.add_css_class("page")
        self.status = nm.WifiStatus()
        self.networks: list[nm.WifiNetwork] = []
        self.rows: dict[str, NetworkRow] = {}
        self.password_ssid: Optional[str] = None
        self.refreshing = False
        self.scanning = False
        self.scan_pending = False
        self.requested_rescan = False
        self.forget_armed = False
        self.forget_timer: Optional[int] = None
        self.timer_id: Optional[int] = None
        self._power_busy = False

        header, self.title, self.subtitle, _ = _page_header(
            "Wi-Fi",
            "Проверка состояния…",
            on_back=lambda: self.app.show_page("overview"),
        )
        self.power = w.switch(False, self._power_toggled)
        header.append(self.power)
        self.append(header)

        content = w.box(Gtk.Orientation.VERTICAL, 10, bottom=8)
        self.scroll = w.scrolled(content)
        self.append(self.scroll)

        self.status_card = Gtk.Button()
        self.status_card.add_css_class("card")
        self.status_card.add_css_class("status-card")
        self.status_card.connect("clicked", self._status_card_clicked)
        card_content = w.box(Gtk.Orientation.HORIZONTAL, 12, top=14, bottom=14, start=14, end=14)
        self.status_icon = w.icon_label(ICON_WIFI_OFF, "xl")
        self.status_icon.add_css_class("accent-icon")
        card_content.append(self.status_icon)
        status_labels = w.box(Gtk.Orientation.VERTICAL, 2, hexpand=True)
        self.status_title = w.label("Wi-Fi выключен", "card-title", ellipsize=True)
        self.status_meta = w.label("Включите адаптер, чтобы увидеть сети", "row-meta", wrap=True)
        status_labels.append(self.status_title)
        status_labels.append(self.status_meta)
        card_content.append(status_labels)
        self.status_badge = w.badge("ВЫКЛ", "muted")
        card_content.append(self.status_badge)
        self.status_card.set_child(card_content)
        content.append(self.status_card)

        self.actions = w.box(Gtk.Orientation.HORIZONTAL, 8)
        self.scan_button = w.pill_button(
            "Сканировать", icon=ICON_MAGNIFY, css="accent", on_click=lambda _b: self.scan()
        )
        self.actions.append(self.scan_button)
        self.scan_spinner = Gtk.Spinner()
        self.scan_spinner.set_valign(Gtk.Align.CENTER)
        self.scan_spinner.set_visible(False)
        self.actions.append(self.scan_spinner)
        self.actions.append(w.spacer())
        self.disconnect_button = w.pill_button(
            "Отключиться", on_click=lambda _b: self.disconnect()
        )
        self.actions.append(self.disconnect_button)
        self.forget_button = w.pill_button(
            "Забыть", css="danger", on_click=lambda _b: self.forget()
        )
        self.actions.append(self.forget_button)
        content.append(self.actions)

        self.list_header = w.section_title("Доступные сети")
        content.append(self.list_header)

        self.networks_box = w.box(Gtk.Orientation.VERTICAL, 2)
        content.append(self.networks_box)

        self.empty = _empty_state(
            ICON_WIFI_OFF,
            "Wi-Fi выключен",
            "Включите адаптер, чтобы найти доступные сети.",
            w.pill_button("Включить Wi-Fi", css="accent", on_click=lambda _b: self._turn_on()),
        )
        content.append(self.empty)

        self.empty_networks = _empty_state(
            ICON_MAGNIFY,
            "Сети не найдены",
            "Нажмите «Сканировать», чтобы обновить список.",
            top=18,
            bottom=18,
        )
        self.empty_networks.set_visible(False)
        content.append(self.empty_networks)

    # ---------------------------------------------------------------- lifecycle

    def on_show(self) -> None:
        self.refresh(False)
        if self.timer_id is None:
            self.timer_id = GLib.timeout_add_seconds(5, self._tick)

    def on_hide(self) -> None:
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def _tick(self) -> bool:
        if not self.app.visible:
            self.timer_id = None
            return GLib.SOURCE_REMOVE
        if self.password_ssid:
            nm.get_status(self._on_status_only)
        elif not self.refreshing:
            self.refresh(False)
        return GLib.SOURCE_CONTINUE

    # ------------------------------------------------------------------- data

    def refresh(self, rescan: bool = False) -> None:
        if self.refreshing:
            if rescan:
                self.scan_pending = True
            return
        self.refreshing = True
        self.requested_rescan = rescan
        if rescan:
            self._set_scan_ui(True)
        nm.fetch(self._on_data, rescan=rescan)

    def _on_data(self, status: nm.WifiStatus, networks: list[nm.WifiNetwork]) -> None:
        self.refreshing = False
        if self.requested_rescan:
            self.scanning = False
            self.scan_pending = False
            self._set_scan_ui(False)
        self.requested_rescan = False

        self.status = status
        self.networks = networks
        self.app.overview.update_wifi(status)
        self._update_header()
        self._update_status_card()
        self._render_networks(networks)
        if self.scan_pending and not status.enabled:
            self.scan_pending = False
        if self.scan_pending:
            self.scan_pending = False
            self.scan()

    def _on_status_only(self, status: nm.WifiStatus) -> None:
        self.status = status
        self.app.overview.update_wifi(status)
        self._update_header()
        self._update_status_card()

    def _update_header(self) -> None:
        status = self.status
        if not self._power_busy:
            w.set_switch(self.power, status.enabled)
        self.power.set_sensitive(not self._power_busy)
        if not status.enabled:
            self.subtitle.set_label("Выключен")
        elif status.connected:
            self.subtitle.set_label(f"Подключено · {status.ssid}")
        else:
            self.subtitle.set_label("Включён · не подключено")

    def _update_status_card(self) -> None:
        status = self.status
        enabled = status.enabled
        self.scan_button.set_sensitive(enabled and not self.scanning)
        self.status_card.set_visible(enabled)
        self.actions.set_visible(enabled)
        self.empty.set_visible(not enabled)
        self.list_header.set_visible(enabled)
        self.networks_box.set_visible(enabled)

        if not enabled:
            self.disconnect_button.set_visible(False)
            self.forget_button.set_visible(False)
            self.empty_networks.set_visible(False)
            return

        if status.connected:
            self.status_icon.set_label(ICON_WIFI)
            self.status_title.set_label(status.ssid)
            meta_parts = []
            if status.ip:
                meta_parts.append(f"IP {status.ip}")
            if status.signal:
                meta_parts.append(f"Сигнал {status.signal}%")
            if status.security:
                meta_parts.append(status.security)
            self.status_meta.set_label(" · ".join(meta_parts) or "Подключено")
            self.status_badge.set_label("ПОДКЛЮЧЕНО")
            self.status_badge.remove_css_class("muted")
            self.status_badge.add_css_class("success")
            self.disconnect_button.set_visible(True)
            self.forget_button.set_visible(bool(status.connection))
            self.forget_button.set_label("Забыть")
            self.forget_armed = False
        else:
            self.status_icon.set_label(ICON_WIFI)
            self.status_title.set_label("Нет подключения")
            self.status_meta.set_label("Выберите сеть из списка ниже или запустите сканирование")
            self.status_badge.set_label("ВКЛ")
            self.status_badge.remove_css_class("success")
            self.status_badge.add_css_class("muted")
            self.disconnect_button.set_visible(False)
            self.forget_button.set_visible(False)

    def _render_networks(self, networks: list[nm.WifiNetwork]) -> None:
        if not self.status.enabled:
            self.list_header.set_visible(False)
            self.networks_box.set_visible(False)
            self.empty_networks.set_visible(False)
            return
        seen: set[str] = set()
        for network in networks:
            seen.add(network.ssid)
            row = self.rows.get(network.ssid)
            if row is None:
                row = NetworkRow(self)
                self.rows[network.ssid] = row
                self.networks_box.append(row)
            row.update(network)

        for ssid in list(self.rows):
            if ssid not in seen:
                row = self.rows.pop(ssid)
                if row.get_parent() is self.networks_box:
                    self.networks_box.remove(row)

        # Keep sorted order without destroying widgets (password entries stay alive).
        if not self.password_ssid:
            for network in networks:
                row = self.rows.get(network.ssid)
                if row is not None:
                    self.networks_box.reorder_child_after(row, None)

        self.empty_networks.set_visible(not networks)
        self.list_header.set_visible(bool(networks))
        if networks:
            title = self.list_header.get_first_child()
            if isinstance(title, Gtk.Label):
                title.set_label("ДОСТУПНЫЕ СЕТИ")

    # ---------------------------------------------------------------- actions

    def _set_scan_ui(self, active: bool) -> None:
        self.scan_button.set_sensitive(not active and self.status.enabled)
        label = self.scan_button.get_child()
        if isinstance(label, Gtk.Box):
            text = label.get_last_child()
            if isinstance(text, Gtk.Label):
                text.set_label("Сканирование…" if active else "Сканировать")
        if active:
            self.scan_spinner.set_visible(True)
            self.scan_spinner.start()
        else:
            self.scan_spinner.stop()
            self.scan_spinner.set_visible(False)

    def scan(self) -> None:
        if not self.status.enabled:
            self.app.toast("Сначала включите Wi-Fi", True)
            return
        if self.scanning:
            return
        if self.refreshing:
            self.scan_pending = True
            return
        self.scanning = True
        self.refresh(rescan=True)

    def connect_network(self, row: NetworkRow, password: Optional[str]) -> None:
        network = row.network
        if network is None:
            return
        self.password_ssid = network.ssid
        row.set_busy(True)
        row.close_password()

        def done(result: Result) -> None:
            row.set_busy(False)
            if result.ok:
                self.password_ssid = None
                self.app.toast(f"Подключено: {network.ssid}", False)
                self.app.overview.update_wifi(self.status)
                self.refresh(False)
                return

            message = nm.friendly_error(result)
            self.password_ssid = None
            if _requires_password(network.security) and password is None:
                row.open_password(message)
                self.password_ssid = network.ssid
            elif _requires_password(network.security):
                row.set_error(message)
                self.password_ssid = network.ssid
                self.app.toast(message, True)
            else:
                self.app.toast(message, True)
            self.refresh(False)

        nm.connect(network.ssid, password, done)

    def set_password_row(self, row: NetworkRow) -> None:
        for other in self.rows.values():
            if other is not row and other.revealer.get_reveal_child():
                other.close_password()
        self.password_ssid = row.network.ssid if row.network else None

    def disconnect(self) -> None:
        if not self.status.connected:
            return
        self.disconnect_button.set_sensitive(False)

        def done(result: Result) -> None:
            self.disconnect_button.set_sensitive(True)
            if result.ok:
                self.app.toast("Wi-Fi отключён", False)
                self.refresh(False)
            else:
                self.app.toast(nm.friendly_error(result), True)

        nm.disconnect(self.status.iface, done)

    def forget(self) -> None:
        if not self.status.connection:
            return
        if not self.forget_armed:
            self.forget_armed = True
            self.forget_button.set_label("Точно?")
            if self.forget_timer is not None:
                GLib.source_remove(self.forget_timer)
            self.forget_timer = GLib.timeout_add_seconds(3, self._disarm_forget)
            return

        connection = self.status.connection
        self.forget_button.set_sensitive(False)

        def done(result: Result) -> None:
            self.forget_button.set_sensitive(True)
            self.forget_armed = False
            self.forget_button.set_label("Забыть")
            if result.ok:
                self.app.toast(f"Сеть «{connection}» забыта", False)
                self.refresh(False)
            else:
                self.app.toast(nm.friendly_error(result), True)

        nm.forget(connection, done)

    def _disarm_forget(self) -> bool:
        self.forget_armed = False
        self.forget_timer = None
        self.forget_button.set_label("Забыть")
        return GLib.SOURCE_REMOVE

    def _power_toggled(self, active: bool) -> None:
        if self._power_busy:
            return
        self._power_busy = True
        self.power.set_sensitive(False)
        self.subtitle.set_label("Применение…")

        def done(result: Result) -> None:
            self._power_busy = False
            self.power.set_sensitive(True)
            if result.ok:
                if not active:
                    self.networks = []
                    self._render_networks([])
                self.refresh(False)
                self.app.refresh_summary()
            else:
                w.set_switch(self.power, not active)
                self.app.toast(nm.friendly_error(result), True)
                self._update_header()

        nm.set_enabled(active, done)

    def _turn_on(self) -> None:
        w.set_switch(self.power, True)
        self._power_toggled(True)

    def _status_card_clicked(self, _button: Gtk.Button) -> None:
        if not self.status.connected:
            self.scan()


class DeviceRow(Gtk.Box):
    def __init__(self, page: "BluetoothPage", device: bt.BtDevice) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.page = page
        self.device = device
        self.busy = False
        self.remove_armed = False
        self.remove_timer: Optional[int] = None

        self.row = w.box(Gtk.Orientation.VERTICAL, 0)
        self.row.add_css_class("row")
        self.row.add_css_class("device-row")

        top = w.box(Gtk.Orientation.HORIZONTAL, 10, top=9, start=10, end=10)
        self.icon_box = w.box(Gtk.Orientation.HORIZONTAL, 0)
        self.icon_box.add_css_class("device-icon")
        self.icon = w.icon_label(bt.icon_for(device), "md")
        self.icon_box.append(self.icon)
        top.append(self.icon_box)

        labels = w.box(Gtk.Orientation.VERTICAL, 1, hexpand=True)
        self.name = w.label(device.name, "row-title", ellipsize=True)
        labels.append(self.name)
        self.meta = w.label(device.mac, "row-meta", ellipsize=True)
        labels.append(self.meta)
        top.append(labels)

        self.battery = w.badge("", "success")
        self.battery.set_visible(False)
        top.append(self.battery)
        self.row.append(top)

        actions = w.box(Gtk.Orientation.HORIZONTAL, 6, bottom=8, start=10, end=10)
        actions.append(w.spacer())

        self.spinner = Gtk.Spinner()
        self.spinner.set_valign(Gtk.Align.CENTER)
        self.spinner.set_visible(False)
        actions.append(self.spinner)

        self.primary = w.pill_button("", css="accent", on_click=lambda _b: self._primary())
        actions.append(self.primary)

        self.trust_button = w.icon_button(
            ICON_SHIELD, "Доверять", lambda _b: self._trust(), css="trust-icon"
        )
        actions.append(self.trust_button)

        self.remove_button = w.icon_button(
            ICON_DELETE, "Удалить устройство", lambda _b: self._remove(), css="danger-icon"
        )
        actions.append(self.remove_button)
        self.row.append(actions)

        self.append(self.row)

    def update(self, device: bt.BtDevice) -> None:
        self.device = device
        self.name.set_label(device.name)
        self.name.set_tooltip_text(device.name)
        meta = device.mac
        if device.rssi is not None:
            meta += f" · {device.rssi} dBm"
        if device.trusted:
            meta += " · Доверено"
        if device.blocked:
            meta += " · Заблокировано"
        self.meta.set_label(meta)
        self.icon.set_label(bt.icon_for(device))
        self.battery.set_visible(device.battery is not None)
        if device.battery is not None:
            self.battery.set_label(f"{device.battery}%")

        if device.connected:
            self._set_primary("Отключить", ICON_BLUETOOTH_OFF, "danger")
            self.row.add_css_class("connected")
        elif device.paired:
            self._set_primary("Подключить", ICON_POWER, "accent")
            self.row.remove_css_class("connected")
        else:
            self._set_primary("Сопрячь", ICON_SHIELD, "accent")
            self.row.remove_css_class("connected")

        self.trust_button.set_visible(device.paired and not device.trusted)
        self.remove_button.set_visible(device.paired)
        if not device.paired:
            self.remove_armed = False
            self.remove_button.remove_css_class("armed")

    def _set_primary(self, text: str, icon: str, css: str) -> None:
        content = w.box(Gtk.Orientation.HORIZONTAL, 5)
        content.set_halign(Gtk.Align.CENTER)
        content.append(w.icon_label(icon, "xs"))
        content.append(Gtk.Label(label=text))
        self.primary.set_child(content)
        for name in ("accent", "danger"):
            self.primary.remove_css_class(name)
        self.primary.add_css_class(css)

    def _primary(self) -> None:
        if self.busy:
            return
        if self.device.connected:
            self.page.device_action(self, "disconnect")
        elif self.device.paired:
            self.page.device_action(self, "connect")
        else:
            self.page.device_action(self, "pair")

    def _trust(self) -> None:
        if not self.busy:
            self.page.device_action(self, "trust")

    def _remove(self) -> None:
        if self.busy:
            return
        if not self.remove_armed:
            self.remove_armed = True
            self.remove_button.add_css_class("armed")
            self.remove_button.set_tooltip_text("Нажмите ещё раз, чтобы удалить")
            if self.remove_timer is not None:
                GLib.source_remove(self.remove_timer)
            self.remove_timer = GLib.timeout_add_seconds(3, self._disarm_remove)
            return
        self.page.device_action(self, "remove")

    def _disarm_remove(self) -> bool:
        self.remove_armed = False
        self.remove_timer = None
        self.remove_button.remove_css_class("armed")
        self.remove_button.set_tooltip_text("Удалить устройство")
        return GLib.SOURCE_REMOVE

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.primary.set_sensitive(not busy)
        self.trust_button.set_sensitive(not busy)
        self.remove_button.set_sensitive(not busy)
        if busy:
            self.spinner.set_visible(True)
            self.spinner.start()
        else:
            self.spinner.stop()
            self.spinner.set_visible(False)


class BluetoothPage(Gtk.Box):
    def __init__(self, app) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.app = app
        self.add_css_class("page")
        self.status = bt.BtStatus()
        self.devices: list[bt.BtDevice] = []
        self.rows: dict[str, DeviceRow] = {}
        self.busy_macs: set[str] = set()
        self.refreshing = False
        self.scanning = False
        self.scan_proc = None
        self.scan_token = 0
        self.scan_stopped = False
        self.timer_id: Optional[int] = None
        self._power_busy = False
        self._discoverable_busy = False

        header, self.title, self.subtitle, _ = _page_header(
            "Bluetooth",
            "Проверка состояния…",
            on_back=lambda: self.app.show_page("overview"),
        )
        self.power = w.switch(False, self._power_toggled)
        header.append(self.power)
        self.append(header)

        content = w.box(Gtk.Orientation.VERTICAL, 10, bottom=8)
        self.scroll = w.scrolled(content)
        self.append(self.scroll)

        self.adapter_card = w.box(Gtk.Orientation.VERTICAL, 0, top=4, bottom=4)
        self.adapter_card.add_css_class("card")
        top = w.box(Gtk.Orientation.HORIZONTAL, 12, top=12, bottom=12, start=14, end=14)
        self.adapter_icon = w.icon_label(ICON_BLUETOOTH_OFF, "xl")
        self.adapter_icon.add_css_class("accent-icon")
        top.append(self.adapter_icon)
        adapter_labels = w.box(Gtk.Orientation.VERTICAL, 2, hexpand=True)
        self.adapter_title = w.label("Bluetooth выключен", "card-title", ellipsize=True)
        self.adapter_meta = w.label("Адаптер недоступен", "row-meta", ellipsize=True)
        adapter_labels.append(self.adapter_title)
        adapter_labels.append(self.adapter_meta)
        top.append(adapter_labels)
        self.adapter_badge = w.badge("ВЫКЛ", "muted")
        top.append(self.adapter_badge)
        self.adapter_card.append(top)
        self.adapter_card.append(w.divider())
        visibility = w.box(Gtk.Orientation.HORIZONTAL, 10, top=10, bottom=10, start=14, end=14)
        visibility_labels = w.box(Gtk.Orientation.VERTICAL, 1, hexpand=True)
        visibility_labels.append(w.label("Видимость для устройств", "row-title"))
        visibility_labels.append(w.label("Разрешить обнаружение этого компьютера", "row-meta"))
        visibility.append(visibility_labels)
        self.discoverable = w.switch(False, self._discoverable_toggled)
        visibility.append(self.discoverable)
        self.adapter_card.append(visibility)
        content.append(self.adapter_card)

        self.actions = w.box(Gtk.Orientation.HORIZONTAL, 8)
        self.scan_button = w.pill_button(
            "Сканировать", icon=ICON_MAGNIFY, css="accent", on_click=lambda _b: self.scan()
        )
        self.actions.append(self.scan_button)
        self.scan_spinner = Gtk.Spinner()
        self.scan_spinner.set_valign(Gtk.Align.CENTER)
        self.scan_spinner.set_visible(False)
        self.actions.append(self.scan_spinner)
        self.scan_hint = w.label("20 секунд", "muted-small")
        self.actions.append(self.scan_hint)
        self.actions.append(w.spacer())
        content.append(self.actions)

        self.connected_section = w.box(Gtk.Orientation.VERTICAL, 2)
        self.connected_title = w.section_title("Подключённые", 0)
        self.connected_box = w.box(Gtk.Orientation.VERTICAL, 2)
        self.connected_section.append(self.connected_title)
        self.connected_section.append(self.connected_box)
        content.append(self.connected_section)

        self.paired_section = w.box(Gtk.Orientation.VERTICAL, 2)
        self.paired_title = w.section_title("Сопряжённые", 0)
        self.paired_box = w.box(Gtk.Orientation.VERTICAL, 2)
        self.paired_section.append(self.paired_title)
        self.paired_section.append(self.paired_box)
        content.append(self.paired_section)

        self.nearby_section = w.box(Gtk.Orientation.VERTICAL, 2)
        self.nearby_title = w.section_title("Рядом", 0)
        self.nearby_box = w.box(Gtk.Orientation.VERTICAL, 2)
        self.nearby_section.append(self.nearby_title)
        self.nearby_section.append(self.nearby_box)
        content.append(self.nearby_section)

        self.empty = _empty_state(
            ICON_BLUETOOTH_OFF,
            "Bluetooth выключен",
            "Включите адаптер, чтобы подключать наушники, мыши и геймпады.",
            w.pill_button("Включить Bluetooth", css="accent", on_click=lambda _b: self._turn_on()),
        )
        content.append(self.empty)

        self.empty_devices = _empty_state(
            ICON_MAGNIFY,
            "Устройств не найдено",
            "Нажмите «Сканировать» и включите режим сопряжения на устройстве.",
            top=18,
            bottom=18,
        )
        self.empty_devices.set_visible(False)
        content.append(self.empty_devices)

    # ---------------------------------------------------------------- lifecycle

    def on_show(self) -> None:
        self.refresh()
        if self.timer_id is None:
            self.timer_id = GLib.timeout_add_seconds(4, self._tick)

    def on_hide(self) -> None:
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def stop_scan(self) -> None:
        if self.scanning and self.scan_proc is not None:
            self.scan_stopped = True
            self.scan_proc.force_exit()

    def _tick(self) -> bool:
        if not self.app.visible:
            self.timer_id = None
            return GLib.SOURCE_REMOVE
        if not self.refreshing:
            self.refresh()
        return GLib.SOURCE_CONTINUE

    # ------------------------------------------------------------------- data

    def refresh(self) -> None:
        if self.refreshing:
            return
        self.refreshing = True
        bt.fetch(self._on_data)

    def _on_data(self, status: bt.BtStatus, devices: list[bt.BtDevice]) -> None:
        self.refreshing = False
        self.status = status
        self.devices = devices
        self.app.overview.update_bluetooth(status, devices)
        self._update_header()
        self._update_adapter_card()
        self._render_devices(devices)

    def _update_header(self) -> None:
        status = self.status
        if not self._power_busy:
            w.set_switch(self.power, status.powered)
        self.power.set_sensitive(not self._power_busy and status.available)
        if not status.available:
            self.subtitle.set_label("Адаптер недоступен")
        elif not status.powered:
            self.subtitle.set_label("Выключен")
        else:
            connected = sum(1 for device in self.devices if device.connected)
            self.subtitle.set_label(f"Включён · {connected} подключено")

    def _update_adapter_card(self) -> None:
        status = self.status
        self.adapter_card.set_visible(status.available)
        self.actions.set_visible(status.available and status.powered)
        self.empty.set_visible(status.available and not status.powered)
        if not status.available:
            self.empty.set_visible(True)
            self.empty.get_first_child().set_label(ICON_BLUETOOTH_OFF)  # type: ignore[union-attr]
            return

        w.set_switch(self.discoverable, status.discoverable)
        self.discoverable.set_sensitive(status.powered and not self._discoverable_busy)
        self.adapter_icon.set_label(ICON_BLUETOOTH if status.powered else ICON_BLUETOOTH_OFF)
        self.adapter_title.set_label(status.alias)
        meta = status.address or "Bluetooth-адаптер"
        if status.discovering:
            meta += " · идёт поиск"
        self.adapter_meta.set_label(meta)
        if status.powered:
            self.adapter_badge.set_label("ВКЛ")
            self.adapter_badge.remove_css_class("muted")
            self.adapter_badge.add_css_class("success")
        else:
            self.adapter_badge.set_label("ВЫКЛ")
            self.adapter_badge.remove_css_class("success")
            self.adapter_badge.add_css_class("muted")

    def _render_devices(self, devices: list[bt.BtDevice]) -> None:
        connected = [device for device in devices if device.connected]
        paired = [device for device in devices if device.paired and not device.connected]
        nearby = [device for device in devices if not device.paired]

        current = {device.mac for device in devices}
        for mac in list(self.rows):
            if mac not in current:
                row = self.rows.pop(mac)
                if row.get_parent() is not None:
                    row.unparent()

        for device in devices:
            row = self.rows.get(device.mac)
            if row is None:
                row = DeviceRow(self, device)
                self.rows[device.mac] = row
            row.update(device)

        self._sync_section(self.connected_section, self.connected_box, connected, "Подключённые")
        self._sync_section(self.paired_section, self.paired_box, paired, "Сопряжённые")
        self._sync_section(self.nearby_section, self.nearby_box, nearby, "Рядом")

        powered = self.status.powered and self.status.available
        has_any = bool(devices)
        self.empty_devices.set_visible(powered and not has_any and not self.scanning)
        if not powered:
            self.connected_section.set_visible(False)
            self.paired_section.set_visible(False)
            self.nearby_section.set_visible(False)
            self.empty_devices.set_visible(False)

    def _sync_section(
        self,
        section: Gtk.Box,
        container: Gtk.Box,
        devices: list[bt.BtDevice],
        title: str,
    ) -> None:
        section.set_visible(bool(devices))
        for device in devices:
            row = self.rows.get(device.mac)
            if row is None:
                continue
            if row.get_parent() is not container:
                container.append(row)
            else:
                container.reorder_child_after(row, None)
        header = section.get_first_child()
        if isinstance(header, Gtk.Box):
            labels: list[Gtk.Widget] = []
            child = header.get_first_child()
            while child is not None:
                labels.append(child)
                child = child.get_next_sibling()
            if len(labels) >= 2 and isinstance(labels[0], Gtk.Label):
                labels[0].set_label(title.upper())
            if len(labels) >= 2 and isinstance(labels[1], Gtk.Label):
                labels[1].set_label(str(len(devices)))

    # ---------------------------------------------------------------- actions

    def _set_scan_ui(self, active: bool) -> None:
        # Keep the button clickable while scanning so it can act as "Stop".
        self.scan_button.set_sensitive(self.status.powered)
        content = self.scan_button.get_child()
        if isinstance(content, Gtk.Box):
            text = content.get_last_child()
            if isinstance(text, Gtk.Label):
                text.set_label("Остановить" if active else "Сканировать")
            first = content.get_first_child()
            if isinstance(first, Gtk.Label):
                first.set_label(ICON_CLOSE if active else ICON_MAGNIFY)
        if active:
            self.scan_spinner.set_visible(True)
            self.scan_spinner.start()
            self.scan_hint.set_label("Идёт поиск…")
        else:
            self.scan_spinner.stop()
            self.scan_spinner.set_visible(False)
            self.scan_hint.set_label("20 секунд")
        self.empty_devices.set_visible(False)

    def scan(self) -> None:
        if not self.status.powered:
            self.app.toast("Сначала включите Bluetooth", True)
            return
        if self.scanning:
            self.scan_stopped = True
            if self.scan_proc is not None:
                self.scan_proc.force_exit()
            return

        self.scanning = True
        self.scan_stopped = False
        self.scan_token += 1
        token = self.scan_token
        self._set_scan_ui(True)

        def done(result: Result) -> None:
            if token != self.scan_token:
                return
            self.scanning = False
            self.scan_proc = None
            self._set_scan_ui(False)
            if not self.scan_stopped and not result.ok:
                self.app.toast(bt.friendly_error(result), True)
            self.scan_stopped = False
            self.refresh()

        self.scan_proc = bt.start_scan(done, seconds=20)
        self.scan_hint.set_label("Идёт поиск…")

    def device_action(self, row: DeviceRow, action: str) -> None:
        device = row.device
        mac = device.mac
        if mac in self.busy_macs:
            return
        self.busy_macs.add(mac)
        row.set_busy(True)

        def finish(result: Optional[Result], success_message: str, failure: bool = False) -> None:
            self.busy_macs.discard(mac)
            row.set_busy(False)
            if result is None:
                return
            if result.ok:
                if success_message:
                    self.app.toast(success_message, False)
                self.refresh()
            else:
                self.app.toast(bt.friendly_error(result), True)
                self.refresh()

        if action == "connect":
            bt.connect(mac, lambda result: finish(result, f"Подключено: {device.name}"))
        elif action == "disconnect":
            bt.disconnect(mac, lambda result: finish(result, f"Отключено: {device.name}"))
        elif action == "trust":
            bt.trust(mac, True, lambda result: finish(result, f"Доверено: {device.name}"))
        elif action == "pair":
            bt.pair(mac, lambda result: self._pair_finished(row, result))
        elif action == "remove":
            bt.remove(mac, lambda result: finish(result, f"Устройство удалено: {device.name}"))

    def _pair_finished(self, row: DeviceRow, result: Result) -> None:
        device = row.device
        mac = device.mac
        self.busy_macs.discard(mac)
        row.set_busy(False)
        if not result.ok:
            self.app.toast(bt.friendly_error(result), True)
            self.refresh()
            return

        # Trust freshly paired devices so they can reconnect automatically.
        bt.trust(mac, True, lambda _result: None)
        self.app.toast(f"Сопряжено: {device.name}", False)
        self.refresh()

    def _power_toggled(self, active: bool) -> None:
        if self._power_busy:
            return
        self._power_busy = True
        self.power.set_sensitive(False)
        self.subtitle.set_label("Применение…")
        if not active and self.scanning and self.scan_proc is not None:
            self.scan_stopped = True
            self.scan_proc.force_exit()

        def done(result: Result) -> None:
            self._power_busy = False
            self.power.set_sensitive(True)
            if result.ok:
                self.refresh()
                self.app.refresh_summary()
            else:
                w.set_switch(self.power, not active)
                self.app.toast(bt.friendly_error(result), True)
                self._update_header()

        bt.set_power(active, done)

    def _turn_on(self) -> None:
        w.set_switch(self.power, True)
        self._power_toggled(True)

    def _discoverable_toggled(self, active: bool) -> None:
        if self._discoverable_busy or not self.status.powered:
            return
        self._discoverable_busy = True
        self.discoverable.set_sensitive(False)

        def done(result: Result) -> None:
            self._discoverable_busy = False
            self.discoverable.set_sensitive(True)
            if result.ok:
                self.status.discoverable = active
                self.app.toast(
                    "Компьютер видим для устройств" if active else "Видимость отключена",
                    False,
                )
                self.refresh()
            else:
                w.set_switch(self.discoverable, not active)
                self.app.toast(bt.friendly_error(result), True)

        bt.set_discoverable(active, done)
