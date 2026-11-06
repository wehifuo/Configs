"""GTK4 layer-shell control center."""

from __future__ import annotations

import os
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

try:
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell  # noqa: E402

    LAYER_SHELL_AVAILABLE = True
except (ValueError, ImportError):
    Gtk4LayerShell = None  # type: ignore[assignment]
    LAYER_SHELL_AVAILABLE = False

from . import bt, nm, runner
from . import widgets as w
from .pages import BluetoothPage, OverviewPage, WifiPage

APP_ID = "org.anton.ControlCenter"
PANEL_WIDTH = 410
PANEL_HEIGHT = 640


class ControlCenterWindow(Gtk.Window):
    def __init__(self, app: "ControlCenterApp") -> None:
        super().__init__()
        self.app = app
        self.current_page = "overview"
        self.panel_visible = False
        self.layer_shell = LAYER_SHELL_AVAILABLE and Gtk4LayerShell.is_supported()
        self._toast_timer: Optional[int] = None

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_title("Control Center")
        self.set_default_size(PANEL_WIDTH, PANEL_HEIGHT)
        self.add_css_class("control-center")

        self.panel = w.box(Gtk.Orientation.VERTICAL, 0)
        self.panel.add_css_class("panel")
        self.panel.set_size_request(PANEL_WIDTH, PANEL_HEIGHT)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(220)
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)
        self.panel.append(self.stack)

        self.overview = OverviewPage(app)
        self.wifi_page = WifiPage(app)
        self.bt_page = BluetoothPage(app)
        self.pages = {
            "overview": self.overview,
            "wifi": self.wifi_page,
            "bluetooth": self.bt_page,
        }
        for name, page in self.pages.items():
            self.stack.add_named(page, name)
        self.stack.set_visible_child_name("overview")

        self.root = Gtk.Overlay()
        self.root.set_child(self.panel)
        self.set_child(self.root)

        self.toast_revealer, self.toast_label = w.toast_revealer()
        self.toast_revealer.set_halign(Gtk.Align.FILL)
        self.toast_revealer.set_valign(Gtk.Align.END)
        self.toast_revealer.set_margin_start(18)
        self.toast_revealer.set_margin_end(18)
        self.toast_revealer.set_margin_bottom(18)
        self.root.add_overlay(self.toast_revealer)

        self._setup_layer_shell()
        self._setup_input()
        self._setup_dim()

    # ------------------------------------------------------------------ setup

    def _setup_layer_shell(self) -> None:
        if not self.layer_shell:
            return
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_namespace(self, "control-center")
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.TOP, 10)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.RIGHT, 12)
        Gtk4LayerShell.set_exclusive_zone(self, -1)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)

    def _setup_input(self) -> None:
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._on_key)
        self.add_controller(keys)

    def _setup_dim(self) -> None:
        self.dim = Gtk.Window()
        self.dim.set_application(self.app)
        self.dim.set_decorated(False)
        self.dim.set_title("Control Center overlay")
        self.dim.add_css_class("cc-dim")
        self.dim.set_can_focus(False)

        self.dim_child = w.box(Gtk.Orientation.VERTICAL, 0, hexpand=True, vexpand=True)
        self.dim_child.add_css_class("dim-bg")
        self.dim.set_child(self.dim_child)

        click = Gtk.GestureClick()
        click.connect("pressed", lambda *_args: self.app.hide_panel())
        self.dim_child.add_controller(click)

        if self.layer_shell:
            Gtk4LayerShell.init_for_window(self.dim)
            Gtk4LayerShell.set_namespace(self.dim, "control-center-overlay")
            Gtk4LayerShell.set_layer(self.dim, Gtk4LayerShell.Layer.TOP)
            for edge in (
                Gtk4LayerShell.Edge.TOP,
                Gtk4LayerShell.Edge.BOTTOM,
                Gtk4LayerShell.Edge.LEFT,
                Gtk4LayerShell.Edge.RIGHT,
            ):
                Gtk4LayerShell.set_anchor(self.dim, edge, True)
            Gtk4LayerShell.set_exclusive_zone(self.dim, -1)
            Gtk4LayerShell.set_keyboard_mode(self.dim, Gtk4LayerShell.KeyboardMode.NONE)

    # ------------------------------------------------------------------- show

    def current_widget(self) -> Gtk.Widget:
        return self.pages[self.current_page]

    def show_page(self, page: str) -> None:
        if page not in self.pages:
            page = "overview"
        old_page = self.current_page
        old_widget = self.pages.get(old_page)
        if old_widget is not None and old_page != page:
            on_hide = getattr(old_widget, "on_hide", None)
            if on_hide is not None:
                on_hide()

        self.current_page = page
        self.stack.set_visible_child_name(page)

        if not self.panel_visible:
            self._present()

        on_show = getattr(self.pages[page], "on_show", None)
        if on_show is not None:
            on_show()

        # The stack transition should not steal focus from a password field.
        if page == "wifi":
            GLib.timeout_add(260, self._restore_focus)
        else:
            GLib.idle_add(self._grab_focus)

    def _present(self) -> None:
        self.panel_visible = True
        if self.layer_shell:
            Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.EXCLUSIVE)
        self.dim.present()
        self.present()
        GLib.idle_add(self._grab_focus)

    def hide_panel(self) -> None:
        if not self.panel_visible:
            return
        self.app.window_hidden()
        on_hide = getattr(self.pages[self.current_page], "on_hide", None)
        if on_hide is not None:
            on_hide()
        self.panel_visible = False
        if self.layer_shell:
            Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
        self.hide()
        self.dim.hide()

    def _grab_focus(self) -> bool:
        self.grab_focus()
        return GLib.SOURCE_REMOVE

    def _restore_focus(self) -> bool:
        page = self.wifi_page
        if page.password_ssid:
            row = page.rows.get(page.password_ssid)
            if row is not None:
                row.entry.grab_focus()
                return GLib.SOURCE_REMOVE
        self.grab_focus()
        return GLib.SOURCE_REMOVE

    def _on_key(self, _controller, keyval, _keycode, _state) -> bool:
        if keyval == Gdk.KEY_Escape:
            self.app.hide_panel()
            return True
        return False

    # ------------------------------------------------------------------ toast

    def show_toast(self, message: str, error: bool = False) -> None:
        self.toast_label.set_label(message)
        self.toast_revealer.remove_css_class("error")
        self.toast_revealer.remove_css_class("ok")
        self.toast_revealer.add_css_class("error" if error else "ok")
        self.toast_revealer.set_reveal_child(True)
        if self._toast_timer is not None:
            GLib.source_remove(self._toast_timer)
        self._toast_timer = GLib.timeout_add_seconds(4, self._hide_toast)

    def _hide_toast(self) -> bool:
        self._toast_timer = None
        self.toast_revealer.set_reveal_child(False)
        return GLib.SOURCE_REMOVE


class ControlCenterApp(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.window: Optional[ControlCenterWindow] = None
        self.overview: Optional[OverviewPage] = None
        self._launched = False
        self._summary_timer: Optional[int] = None
        self._summary_nm_busy = False
        self._summary_bt_busy = False
        self.last_wifi = nm.WifiStatus()
        self.last_bt = bt.BtStatus()

    # --------------------------------------------------------------- lifecycle

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        self._load_css()
        self._create_window()

    def _load_css(self) -> None:
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "style.css"
        )
        provider = Gtk.CssProvider()
        try:
            provider.load_from_path(css_path)
        except GLib.Error as exc:
            print(f"Control Center: cannot load {css_path}: {exc}")
            return
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _create_window(self) -> None:
        self.window = ControlCenterWindow(self)
        self.add_window(self.window)
        self.overview = self.window.overview

    @property
    def visible(self) -> bool:
        return bool(self.window and self.window.panel_visible)

    def do_activate(self) -> None:
        GLib.idle_add(self._activate_if_needed)

    def _activate_if_needed(self) -> bool:
        if not self._launched:
            self.launch("overview", toggle=False)
        return GLib.SOURCE_REMOVE

    def do_command_line(self, command_line: Gio.ApplicationCommandLine) -> int:
        args = command_line.get_arguments()[1:]
        page = "overview"
        toggle = True
        index = 0
        while index < len(args):
            arg = args[index]
            if arg.startswith("--page="):
                page = arg.split("=", 1)[1]
                index += 1
            elif arg in ("--page", "-p") and index + 1 < len(args):
                page = args[index + 1]
                index += 2
            elif arg == "--show":
                toggle = False
                index += 1
            elif arg == "--toggle":
                toggle = True
                index += 1
            elif arg == "--quit":
                self.quit()
                return 0
            else:
                index += 1
        if page == "bt":
            page = "bluetooth"
        self.launch(page, toggle=toggle)
        return 0

    def launch(self, page: str, toggle: bool = True) -> None:
        self._launched = True
        if self.window is None:
            self._create_window()
        assert self.window is not None
        if page not in self.window.pages:
            page = "overview"

        if self.window.panel_visible:
            if toggle and (page == "overview" or page == self.window.current_page):
                self.hide_panel()
                return
            self._stop_summary_timer()
            self.window.show_page(page)
        else:
            self.window.show_page(page)

        if page == "overview":
            self.refresh_summary()
            self._start_summary_timer()
        else:
            self._stop_summary_timer()

    def hide_panel(self) -> None:
        if self.window is None or not self.window.panel_visible:
            return
        self._stop_summary_timer()
        self.window.bt_page.stop_scan()
        self.window.hide_panel()

    def show_page(self, page: str) -> None:
        """Internal navigation used by tiles and the back buttons."""
        self._launched = True
        if self.window is None:
            self._create_window()
        assert self.window is not None
        self._stop_summary_timer()
        self.window.show_page(page)
        if page == "overview":
            self.refresh_summary()
            self._start_summary_timer()

    def window_hidden(self) -> None:
        self._stop_summary_timer()

    # ---------------------------------------------------------------- summary

    def _start_summary_timer(self) -> None:
        if self._summary_timer is None:
            self._summary_timer = GLib.timeout_add_seconds(6, self._summary_tick)

    def _stop_summary_timer(self) -> None:
        if self._summary_timer is not None:
            GLib.source_remove(self._summary_timer)
            self._summary_timer = None

    def _summary_tick(self) -> bool:
        if not self.visible or self.window is None or self.window.current_page != "overview":
            self._summary_timer = None
            return GLib.SOURCE_REMOVE
        self.refresh_summary()
        return GLib.SOURCE_CONTINUE

    def refresh_summary(self) -> None:
        if self._summary_nm_busy is False:
            self._summary_nm_busy = True
            nm.get_status(self._on_summary_wifi)
        if self._summary_bt_busy is False:
            self._summary_bt_busy = True
            bt.fetch(self._on_summary_bt)

    def _on_summary_wifi(self, status: nm.WifiStatus) -> None:
        self._summary_nm_busy = False
        self.last_wifi = status
        if self.overview is not None:
            self.overview.update_wifi(status)

    def _on_summary_bt(self, status: bt.BtStatus, devices: list[bt.BtDevice]) -> None:
        self._summary_bt_busy = False
        self.last_bt = status
        if self.overview is not None:
            self.overview.update_bluetooth(status, devices)

    # ---------------------------------------------------------------- actions

    def set_wifi_power(self, active: bool) -> None:
        if self.overview is None:
            return
        tile = self.overview.wifi_tile
        tile.power.set_sensitive(False)

        def done(result) -> None:
            tile.power.set_sensitive(True)
            if not result.ok:
                self.toast(nm.friendly_error(result), True)
            GLib.timeout_add(350, self._refresh_after_power)

        nm.set_enabled(active, done)

    def set_bt_power(self, active: bool) -> None:
        if self.overview is None:
            return
        tile = self.overview.bt_tile
        tile.power.set_sensitive(False)

        def done(result) -> None:
            tile.power.set_sensitive(True)
            if not result.ok:
                self.toast(bt.friendly_error(result), True)
            GLib.timeout_add(350, self._refresh_after_power)

        bt.set_power(active, done)

    def _refresh_after_power(self) -> bool:
        self.refresh_summary()
        return GLib.SOURCE_REMOVE

    def toast(self, message: str, error: bool = False) -> None:
        if self.window is not None:
            self.window.show_toast(message, error)
        if error:
            runner.notify("Control Center", message, "dialog-error")


def main(argv: Optional[list[str]] = None) -> int:
    GLib.set_prgname("control-center")
    GLib.set_application_name("Control Center")
    app = ControlCenterApp()
    return app.run(argv if argv is not None else [])
