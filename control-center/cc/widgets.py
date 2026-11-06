"""Small GTK4 building blocks shared by all pages."""

from __future__ import annotations

from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Pango  # noqa: E402


def box(
    orientation: Gtk.Orientation = Gtk.Orientation.VERTICAL,
    spacing: int = 0,
    *,
    top: int = 0,
    bottom: int = 0,
    start: int = 0,
    end: int = 0,
    hexpand: bool = False,
    vexpand: bool = False,
    halign: Optional[Gtk.Align] = None,
    valign: Optional[Gtk.Align] = None,
) -> Gtk.Box:
    widget = Gtk.Box(orientation=orientation, spacing=spacing)
    widget.set_margin_top(top)
    widget.set_margin_bottom(bottom)
    widget.set_margin_start(start)
    widget.set_margin_end(end)
    widget.set_hexpand(hexpand)
    widget.set_vexpand(vexpand)
    if halign is not None:
        widget.set_halign(halign)
    if valign is not None:
        widget.set_valign(valign)
    return widget


def label(
    text: str,
    css: Optional[str] = None,
    *,
    wrap: bool = False,
    xalign: float = 0.0,
    ellipsize: bool = False,
    max_width: int = 0,
) -> Gtk.Label:
    widget = Gtk.Label(label=text)
    widget.set_xalign(xalign)
    if css:
        for name in css.split():
            widget.add_css_class(name)
    widget.set_wrap(wrap)
    if wrap:
        widget.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    if ellipsize:
        widget.set_ellipsize(Pango.EllipsizeMode.END)
    if max_width:
        widget.set_max_width_chars(max_width)
    return widget


def icon_label(glyph: str, size: str = "md") -> Gtk.Label:
    widget = Gtk.Label(label=glyph)
    widget.add_css_class("icon")
    if size:
        widget.add_css_class(f"icon-{size}")
    return widget


def spacer(hexpand: bool = True) -> Gtk.Box:
    widget = Gtk.Box()
    widget.set_hexpand(hexpand)
    return widget


def divider(*, top: int = 0, bottom: int = 0) -> Gtk.Separator:
    widget = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    widget.add_css_class("divider")
    widget.set_margin_top(top)
    widget.set_margin_bottom(bottom)
    return widget


def pill_button(
    text: str = "",
    *,
    icon: str = "",
    css: str = "",
    tooltip: str = "",
    on_click: Optional[Callable[[Gtk.Button], None]] = None,
) -> Gtk.Button:
    button = Gtk.Button()
    button.add_css_class("pill")
    for name in css.split():
        button.add_css_class(name)
    content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    content.set_halign(Gtk.Align.CENTER)
    if icon:
        content.append(icon_label(icon, "sm"))
    if text:
        content.append(Gtk.Label(label=text))
    button.set_child(content)
    if tooltip:
        button.set_tooltip_text(tooltip)
    if on_click is not None:
        button.connect("clicked", on_click)
    return button


def icon_button(
    glyph: str,
    tooltip: str,
    on_click: Optional[Callable[[Gtk.Button], None]] = None,
    *,
    css: str = "",
) -> Gtk.Button:
    button = Gtk.Button()
    button.add_css_class("icon-btn")
    for name in css.split():
        button.add_css_class(name)
    button.set_child(icon_label(glyph, "sm"))
    button.set_tooltip_text(tooltip)
    if on_click is not None:
        button.connect("clicked", on_click)
    return button


def switch(
    active: bool = False,
    on_change: Optional[Callable[[bool], None]] = None,
) -> Gtk.Switch:
    widget = Gtk.Switch()
    widget.set_active(active)
    widget.add_css_class("toggle")
    widget.set_valign(Gtk.Align.CENTER)
    if on_change is not None:
        connect_switch(widget, on_change)
    return widget


def set_switch(control: Gtk.Switch, active: bool) -> None:
    """Update a switch without invoking its callback."""
    signal_id = getattr(control, "_cc_signal", None)
    if signal_id:
        control.handler_block(signal_id)
    control.set_active(active)
    if signal_id:
        control.handler_unblock(signal_id)


def connect_switch(control: Gtk.Switch, callback: Callable[[bool], None]) -> None:
    signal_id = control.connect(
        "notify::active", lambda item, _param: callback(item.get_active())
    )
    setattr(control, "_cc_signal", signal_id)


def section_title(text: str, count: Optional[int] = None) -> Gtk.Box:
    row = box(Gtk.Orientation.HORIZONTAL, 8, top=4, bottom=2)
    row.append(label(text.upper(), "section-title"))
    if count is not None:
        row.append(label(str(count), "count-badge"))
    return row


def badge(text: str, css: str = "") -> Gtk.Label:
    widget = label(text, "badge")
    for name in css.split():
        widget.add_css_class(name)
    widget.set_valign(Gtk.Align.CENTER)
    return widget


def clear(container: Gtk.Box) -> None:
    child = container.get_first_child()
    while child is not None:
        container.remove(child)
        child = container.get_first_child()


def scrolled(child: Gtk.Widget, *, vexpand: bool = True) -> Gtk.ScrolledWindow:
    window = Gtk.ScrolledWindow()
    window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    window.set_child(child)
    window.set_vexpand(vexpand)
    window.set_hexpand(True)
    window.add_css_class("page-scroll")
    window.set_overlay_scrolling(True)
    return window


def toast_revealer() -> tuple[Gtk.Revealer, Gtk.Label]:
    revealer = Gtk.Revealer()
    revealer.add_css_class("toast")
    revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
    revealer.set_transition_duration(180)
    revealer.set_reveal_child(False)
    text = Gtk.Label(label="", wrap=True, xalign=0.0)
    text.add_css_class("toast-text")
    inner = box(Gtk.Orientation.HORIZONTAL, 8, top=10, bottom=10, start=12, end=12)
    inner.append(text)
    revealer.set_child(inner)
    return revealer, text
